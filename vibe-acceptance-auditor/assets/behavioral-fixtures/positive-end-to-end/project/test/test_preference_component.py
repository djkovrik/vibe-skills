import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.preference_component import PreferenceComponent


class PreferenceComponentContractTest(unittest.TestCase):
    def test_create_preference_is_observable(self):
        component = PreferenceComponent()
        component.create_preference("compact")
        self.assertEqual("compact", component.read_preference())

    def test_read_preference_returns_current_value(self):
        component = PreferenceComponent()
        component.create_preference("compact")
        self.assertEqual("compact", component.read_preference())

    def test_update_preference_replaces_value(self):
        component = PreferenceComponent()
        component.create_preference("compact")
        component.update_preference("expanded")
        self.assertEqual("expanded", component.read_preference())

    def test_delete_preference_restores_empty_state(self):
        component = PreferenceComponent()
        component.create_preference("compact")
        component.delete_preference()
        self.assertIsNone(component.read_preference())


if __name__ == "__main__":
    unittest.main()
