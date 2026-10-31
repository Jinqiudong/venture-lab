import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import generate_dashboard as dashboard


class IncubationIdeaTests(unittest.TestCase):
    def write_record(self, folder: Path, issue: int, **extra) -> None:
        record = {"idea_issue": issue, "stage": "VALIDATE", "title": f"Idea {issue}", **extra}
        (folder / f"{issue}.json").write_text(json.dumps(record))

    def test_idea_with_repo_project_is_shown_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write_record(folder, 9)
            self.write_record(folder, 10)
            with mock.patch.object(dashboard, "INCUBATION_RECORDS", folder):
                ideas = dashboard.incubation_projects({9})
        self.assertEqual([idea["name"] for idea in ideas], ["Idea 10"])

    def test_idea_with_product_repo_is_hidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.write_record(folder, 11, product_repo="Jinqiudong/example")
            with mock.patch.object(dashboard, "INCUBATION_RECORDS", folder):
                self.assertEqual(dashboard.incubation_projects(), [])


if __name__ == "__main__":
    unittest.main()
