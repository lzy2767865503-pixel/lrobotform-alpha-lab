/**
 * Lrobotform Alpha Lab read-only Google Forms schema exporter.
 *
 * Run this script only from a Google Form you own or are authorized to test.
 * It reads question structure and writes JSON to the Apps Script execution log.
 * It does not read responses and cannot submit responses.
 */
function exportLrobotformAlphaBlueprint() {
  const form = FormApp.getActiveForm();
  const items = form.getItems();
  const blueprint = {
    title: form.getTitle(),
    source: "google_forms_schema_export",
    exportedAt: new Date().toISOString(),
    items: items.map(function (item) {
      return exportItem(item);
    }).filter(Boolean)
  };

  console.log(JSON.stringify(blueprint, null, 2));
}

function exportItem(item) {
  const type = String(item.getType());
  const base = {
    id: String(item.getId()),
    title: item.getTitle(),
    type: type,
    required: false
  };

  if (type === "MULTIPLE_CHOICE") {
    const typed = item.asMultipleChoiceItem();
    base.required = typed.isRequired();
    base.choices = typed.getChoices().map(function (choice) {
      return choice.getValue();
    });
    return base;
  }

  if (type === "CHECKBOX") {
    const typed = item.asCheckboxItem();
    base.required = typed.isRequired();
    base.choices = typed.getChoices().map(function (choice) {
      return choice.getValue();
    });
    return base;
  }

  if (type === "LIST") {
    const typed = item.asListItem();
    base.required = typed.isRequired();
    base.choices = typed.getChoices().map(function (choice) {
      return choice.getValue();
    });
    return base;
  }

  if (type === "SCALE") {
    const typed = item.asScaleItem();
    base.required = typed.isRequired();
    base.lowerBound = typed.getLowerBound();
    base.upperBound = typed.getUpperBound();
    return base;
  }

  if (type === "GRID") {
    const typed = item.asGridItem();
    base.required = typed.isRequired();
    base.rows = typed.getRows();
    base.columns = typed.getColumns();
    return base;
  }

  if (type === "CHECKBOX_GRID") {
    const typed = item.asCheckboxGridItem();
    base.required = typed.isRequired();
    base.rows = typed.getRows();
    base.columns = typed.getColumns();
    return base;
  }

  if (type === "TEXT") {
    base.required = item.asTextItem().isRequired();
    return base;
  }

  if (type === "PARAGRAPH_TEXT") {
    base.required = item.asParagraphTextItem().isRequired();
    return base;
  }

  return null;
}
