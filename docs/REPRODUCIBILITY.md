# Reproducibility Guide

Lrobotform Alpha Lab is designed to be reproduced without private forms,
participant data, browser credentials, API keys, or external services.

## Reference Environment

- Python 3.12 (minimum supported version: Python 3.10)
- A POSIX shell for the one-command verifier
- Any modern browser for the optional static demo

The core package has no third-party runtime dependencies.

## Clean-Clone Verification

```bash
git clone https://github.com/lzy2767865503-pixel/lrobotform-alpha-lab.git
cd lrobotform-alpha-lab
chmod +x scripts/verify.sh
./scripts/verify.sh
```

The verifier:

1. creates an isolated `.venv`;
2. installs the package in editable mode;
3. runs the complete unit, safety, and schema-adapter test suite;
4. generates 200 synthetic rows from the committed example with seed
   `20260724`;
5. checks that the report labels the data as synthetic;
6. confirms the static browser demo contains its required files.

Expected generated artifacts:

- `output/synthetic_responses.csv`
- `output/alpha_report.json`

The command exits non-zero if any required check fails.

## Manual Verification

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m unittest discover -s tests -v
lrobotform-alpha examples/questionnaire.json \
  --responses 200 \
  --seed 20260724 \
  --target-min 0.70 \
  --target-max 0.90
```

Serve the browser demo separately:

```bash
python3 -m http.server 8080 --directory web
```

Then open `http://127.0.0.1:8080`.

## Reproduction Boundary

- `examples/questionnaire.json` is synthetic and safe to publish.
- Every generated CSV row carries `data_origin=synthetic_simulation`, a
  synthetic record ID, and the simulation seed.
- Generated rows are instrument-design simulations, not participant evidence.
- No live form submission is included or required.
- A successful Cronbach's Alpha target check does not establish construct
  validity, sampling quality, representativeness, or research ethics approval.
- Use a Google Forms blueprint only when you own the form or have written
  authorization to test it.

GitHub Actions repeats the package installation, tests, and deterministic
sample generation on every push and pull request.
