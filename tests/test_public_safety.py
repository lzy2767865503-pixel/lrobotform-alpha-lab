import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = [ROOT / "src", ROOT / "adapters", ROOT / "web"]
DISALLOWED = (
    "formresponse",
    "submit_google",
    "requests.post(",
    "urllib.request.urlopen",
    "browser_submit",
)


class PublicSafetyTests(unittest.TestCase):
    def test_public_source_has_no_live_submission_implementation(self):
        findings = []
        for source_root in SOURCE_ROOTS:
            for path in source_root.rglob("*"):
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
                for marker in DISALLOWED:
                    if marker in text:
                        findings.append(f"{path.relative_to(ROOT)}: {marker}")
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
