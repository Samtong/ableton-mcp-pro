import os
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from als_downgrade import downgrade  # noqa: E402

REFERENCE = """
<Ableton MajorVersion="5" MinorVersion="12.0_12049" SchemaChangeCount="12" Creator="Ableton Live 12.0.15">
  <LiveSet>
    <NextPointeeId Value="100" />
    <Tracks>
      <AudioTrack Id="1">
        <VelocityDetail Value="0" />
        <DeviceChain><Mixer><ViewStateSesstionTrackWidth Value="93" /></Mixer></DeviceChain>
      </AudioTrack>
    </Tracks>
    <MainTrack>
      <DeviceChain><FreezeSequencer><AudioSequencer><ClipSlotList /></AudioSequencer></FreezeSequencer></DeviceChain>
    </MainTrack>
    <ScaleInformation><RootNote Value="0" /><Name Value="Major" /></ScaleInformation>
  </LiveSet>
</Ableton>
"""

NEWER = """
<Ableton MajorVersion="5" MinorVersion="12.0_12300" SchemaChangeCount="1" Creator="Ableton Live 12.3.6">
  <LiveSet>
    <NextPointeeId Value="500" />
    <SelectedDocumentViewInMainWindow Value="0" />
    <Tracks>
      <AudioTrack Id="15" SelectedToolPanel="3">
        <TakeLanesListWrapper LomId="0" />
        <DeviceChain><Mixer><ViewStateSessionTrackWidth Value="93" /></Mixer></DeviceChain>
      </AudioTrack>
    </Tracks>
    <MainTrack>
      <DeviceChain><FreezeSequencer><AudioSequencer><ClipSlotList>
        <ClipSlot Id="0" /><ClipSlot Id="1" />
      </ClipSlotList></AudioSequencer></FreezeSequencer></DeviceChain>
    </MainTrack>
    <ScaleInformation><Root Value="2" /><Name Value="1" /></ScaleInformation>
  </LiveSet>
</Ableton>
"""


class DowngradeTest(unittest.TestCase):
    def setUp(self):
        self.root = ET.fromstring(NEWER)
        downgrade(self.root, ET.fromstring(REFERENCE))
        self.track = self.root.find("LiveSet/Tracks/AudioTrack")

    def test_header_matches_reference(self):
        self.assertEqual(self.root.get("MinorVersion"), "12.0_12049")
        self.assertEqual(self.root.get("Creator"), "Ableton Live 12.0.15")

    def test_unknown_elements_and_attributes_removed(self):
        self.assertIsNone(self.root.find("LiveSet/SelectedDocumentViewInMainWindow"))
        self.assertIsNone(self.track.find("TakeLanesListWrapper"))
        self.assertNotIn("SelectedToolPanel", self.track.attrib)
        self.assertEqual(self.track.get("Id"), "15")

    def test_required_fields_added(self):
        self.assertIsNotNone(self.track.find("VelocityDetail"))

    def test_renames(self):
        self.assertIsNotNone(self.track.find("DeviceChain/Mixer/ViewStateSesstionTrackWidth"))
        si = self.root.find("LiveSet/ScaleInformation")
        self.assertEqual(si.find("RootNote").get("Value"), "2")
        self.assertEqual(si.find("Name").get("Value"), "Minor")

    def test_main_track_clip_slots_removed(self):
        slots = self.root.findall("LiveSet/MainTrack/DeviceChain/FreezeSequencer/AudioSequencer/ClipSlotList/ClipSlot")
        self.assertEqual(slots, [])

    def test_track_list_not_padded_from_reference(self):
        self.assertEqual(len(self.root.find("LiveSet/Tracks")), 1)


if __name__ == "__main__":
    unittest.main()
