"""
Downgrade a Live set (.als) saved by a newer Live 12 so an older Live 12 opens it.

Live refuses sets from a newer minor version, even 12.3 -> 12.0. Bumping the header is
not enough: the older parser stops on every element, attribute or class it does not know,
and a few structural differences crash it after parsing. Instead of hard-coding what each
version added, this uses a set saved by the *target* Live as the schema reference:

  1. copy the reference header (MinorVersion, SchemaChangeCount, Creator)
  2. rename fields that changed name (ScaleInformation Root -> RootNote, ...)
  3. drop child elements the reference never has under that parent
  4. add fields the reference always writes, copied with fresh pointee ids
  5. drop the main track's clip slots (12.0 has none; 12.3 adds them, 12.0 crashes)
  6. drop attributes the reference never has on that tag

Use a reference set with as much content as possible (MIDI tracks, devices, clips):
anything the reference lacks is treated as unknown and removed.

Usage:
  python tools/als_downgrade.py NEWER.als REFERENCE_SAVED_BY_TARGET.als OUT.als
"""

import argparse
import copy
import gzip
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

SCALES = [
    "Major", "Minor", "Dorian", "Mixolydian", "Lydian", "Phrygian", "Locrian",
    "Whole Tone", "Half-whole Dim.", "Whole-half Dim.", "Minor Blues",
    "Minor Pentatonic", "Major Pentatonic", "Harmonic Minor", "Harmonic Major",
    "Dorian #4", "Phrygian Dominant", "Melodic Minor", "Lydian Augmented",
    "Lydian Dominant", "Super Locrian", "8-Tone Spanish", "Bhairav",
    "Hungarian Minor", "Hirajoshi", "In-Sen", "Iwato", "Kumoi", "Pelog Selisir",
    "Pelog Tembung", "Messiaen 3", "Messiaen 4", "Messiaen 5", "Messiaen 6",
    "Messiaen 7",
]


def read_als(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    return ET.ElementTree(ET.fromstring(data))


def write_als(tree, path):
    ET.indent(tree, space="\t")
    body = ET.tostring(tree.getroot(), encoding="unicode")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n"
    with open(path, "wb") as f:
        f.write(gzip.compress(xml.encode("utf-8")))


class Schema:
    """What the target Live writes, learned from one of its sets."""

    def __init__(self, ref_root):
        self.children = defaultdict(set)            # parent tag -> child tags seen
        self.order = defaultdict(list)              # parent tag -> child tags, in order
        self.count = Counter()                      # tag -> instances
        self.child_count = defaultdict(Counter)     # parent tag -> child tag -> instances having it
        self.sample = {}                            # (parent, child) -> first element
        self.attrs = defaultdict(set)               # tag -> attribute names seen
        for el in ref_root.iter():
            self.count[el.tag] += 1
            self.attrs[el.tag].update(el.attrib)
            kids = []
            for c in el:
                self.children[el.tag].add(c.tag)
                if c.tag not in self.order[el.tag]:
                    self.order[el.tag].append(c.tag)
                if c.tag not in kids:
                    kids.append(c.tag)
                self.sample.setdefault((el.tag, c.tag), c)
            for k in kids:
                self.child_count[el.tag][k] += 1

    def knows(self, tag):
        return tag in self.count

    def always_has(self, parent, child):
        # List items (anything with an Id) are content, never a required field.
        return (self.child_count[parent][child] == self.count[parent]
                and self.sample[(parent, child)].get("Id") is None)


def downgrade(root, ref_root):
    schema = Schema(ref_root)
    log = []

    for key in ("MinorVersion", "SchemaChangeCount", "Creator"):
        root.set(key, ref_root.get(key))

    for si in root.iter("ScaleInformation"):
        r = si.find("Root")
        if r is not None:
            r.tag = "RootNote"
        n = si.find("Name")
        if n is not None and n.get("Value", "").isdigit():
            i = int(n.get("Value"))
            n.set("Value", SCALES[i] if i < len(SCALES) else "Major")
    for m in root.iter("Mixer"):
        for c in m.findall("ViewStateSessionTrackWidth"):
            c.tag = "ViewStateSesstionTrackWidth"   # sic: 12.0 spells it this way
    for c in root.findall("LiveSet/ViewStateSessionMixerVolumeSectionHeight"):
        c.tag = "ViewStateSessionMixerHeight"

    def prune(el):
        for c in list(el):
            if schema.knows(el.tag) and c.tag not in schema.children[el.tag]:
                el.remove(c)
                log.append(f"removed {el.tag} > {c.tag}")
            else:
                prune(c)
    prune(root)

    next_id = root.find("LiveSet/NextPointeeId")

    def fresh_ids(e):
        for x in e.iter():
            if x.tag in ("AutomationTarget", "ModulationTarget", "Pointee") and x.get("Id") is not None:
                v = int(next_id.get("Value"))
                x.set("Id", str(v))
                next_id.set("Value", str(v + 1))

    def fill(el):
        for c in el:
            fill(c)
        if not schema.knows(el.tag):
            return
        order = schema.order[el.tag]
        have = {c.tag for c in el}
        for k in order:
            if k in have or not schema.always_has(el.tag, k):
                continue
            new = copy.deepcopy(schema.sample[(el.tag, k)])
            fresh_ids(new)
            idx = 0
            for i, c in enumerate(el):
                if c.tag in order and order.index(c.tag) < order.index(k):
                    idx = i + 1
            el.insert(idx, new)
            have.add(k)
            log.append(f"added {el.tag} > {k}")
    fill(root)

    for csl in root.findall("LiveSet/MainTrack/DeviceChain/FreezeSequencer/AudioSequencer/ClipSlotList"):
        for c in list(csl):
            csl.remove(c)
            log.append("removed MainTrack freeze ClipSlot")

    for e in root.iter():
        if e is root or not schema.knows(e.tag):
            continue
        for a in list(e.attrib):
            if a not in schema.attrs[e.tag]:
                del e.attrib[a]
                log.append(f"removed attribute {e.tag}@{a}")

    return log


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", help=".als saved by the newer Live")
    p.add_argument("reference", help=".als saved by the Live you want to open it in")
    p.add_argument("output", help="where to write the downgraded .als")
    args = p.parse_args(argv)

    tree = read_als(args.source)
    ref_root = read_als(args.reference).getroot()
    print(f"{tree.getroot().get('Creator')} -> {ref_root.get('Creator')}", file=sys.stderr)
    log = downgrade(tree.getroot(), ref_root)
    write_als(tree, args.output)
    for line, n in sorted(Counter(log).items()):
        print(f"{n:4d}x {line}", file=sys.stderr)


if __name__ == "__main__":
    main()
