import csv
import json
import tempfile
import unittest
from pathlib import Path

from lrobotform_alpha.generator import simulate
from lrobotform_alpha.models import Questionnaire
from lrobotform_alpha.report import write_csv, write_report


ROOT = Path(__file__).resolve().parents[1]


class ReportingProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = json.loads(
            (ROOT / "examples" / "questionnaire.json").read_text(encoding="utf-8")
        )
        cls.questionnaire = Questionnaire.from_dict(raw)

    def test_csv_and_report_preserve_synthetic_provenance(self):
        result = simulate(self.questionnaire, response_count=12, seed=20260724)
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "responses.csv"
            report_path = Path(directory) / "report.json"
            write_csv(csv_path, self.questionnaire, result)
            write_report(report_path, self.questionnaire, result)

            with csv_path.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(len(rows), 12)
        self.assertEqual(rows[0]["synthetic_record_id"], "SIM-000001")
        self.assertTrue(
            all(row["data_origin"] == "synthetic_simulation" for row in rows)
        )
        self.assertTrue(all(row["simulation_seed"] == "20260724" for row in rows))
        self.assertIn("Synthetic local test data only", report["notice"])


if __name__ == "__main__":
    unittest.main()
