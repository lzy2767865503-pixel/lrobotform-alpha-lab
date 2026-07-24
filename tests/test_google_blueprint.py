import unittest

from lrobotform_alpha.forms_schema import questionnaire_from_google_blueprint


class GoogleBlueprintTests(unittest.TestCase):
    def test_read_only_blueprint_normalization(self):
        questionnaire = questionnaire_from_google_blueprint(
            {
                "title": "Authorized pilot",
                "items": [
                    {
                        "id": "11",
                        "title": "Satisfaction",
                        "type": "SCALE",
                        "lowerBound": 1,
                        "upperBound": 5,
                        "required": True,
                    },
                    {
                        "id": "12",
                        "title": "Service quality",
                        "type": "GRID",
                        "rows": ["Reliable", "Clear"],
                        "columns": ["1", "2", "3", "4", "5"],
                    },
                    {
                        "id": "13",
                        "title": "Programme",
                        "type": "MULTIPLE_CHOICE",
                        "choices": ["Undergraduate", "Postgraduate"],
                    },
                ],
            }
        )
        self.assertEqual(questionnaire.title, "Authorized pilot")
        self.assertEqual(len(questionnaire.questions), 4)
        self.assertEqual(len(questionnaire.scale_questions), 3)


if __name__ == "__main__":
    unittest.main()
