# Read-only Google Forms Adapter

`google_forms_schema_exporter.gs` exports question structure from the active
Google Form to the Apps Script execution log.

## Use

1. Open a Google Form you own or are authorized to test.
2. Open **Extensions > Apps Script**.
3. Add the exporter code.
4. Run `exportLrobotformAlphaBlueprint`.
5. Copy the logged JSON into a local file.
6. Run the Alpha Lab CLI with `--google-blueprint`.

The script does not request participant responses, edit the form, or submit
answers.
