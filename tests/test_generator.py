import json
import unittest
from pathlib import Path

from lrobotform_alpha.generator import simulate
from lrobotform_alpha.models import Questionnaire


ROOT = Path(__file__).resolve().parents[1]


class SimulationTests(unittest.TestCase):
    def setUp(self):
        raw = json.loads(
            (ROOT / "examples" / "questionnaire.json").read_text(encoding="utf-8")
        )
        self.questionnaire = Questionnaire.from_dict(raw)

    def test_target_alpha_and_complete_rows(self):
        result = simulate(
            self.questionnaire,
            response_count=200,
            seed=20260724,
            target_min=0.7,
            target_max=0.9,
        )
        self.assertIsNotNone(result.alpha)
        self.assertGreaterEqual(result.alpha, 0.7)
        self.assertLessEqual(result.alpha, 0.9)
        self.assertEqual(len(result.rows), 200)
        self.assertTrue(
            all(
                set(row) == {question.id for question in self.questionnaire.questions}
                for row in result.rows
            )
        )

    def test_reproducible_seed(self):
        first = simulate(self.questionnaire, response_count=50, seed=21)
        second = simulate(self.questionnaire, response_count=50, seed=21)
        self.assertEqual(first.rows, second.rows)
        self.assertEqual(first.alpha, second.alpha)

    def test_target_band_at_supported_boundaries(self):
        for response_count, item_count in ((20, 2), (20, 20), (1000, 2), (1000, 20)):
            with self.subTest(response_count=response_count, item_count=item_count):
                questionnaire = Questionnaire.from_dict(
                    {
                        "title": "Boundary test",
                        "questions": [
                            {
                                "id": f"Q{index + 1}",
                                "title": f"Scale {index + 1}",
                                "type": "linear_scale",
                                "options": ["1", "2", "3", "4", "5"],
                            }
                            for index in range(item_count)
                        ],
                    }
                )
                result = simulate(
                    questionnaire,
                    response_count=response_count,
                    seed=20260724,
                    target_min=0.7,
                    target_max=0.9,
                )
                self.assertTrue(result.alpha_passed)


if __name__ == "__main__":
    unittest.main()
