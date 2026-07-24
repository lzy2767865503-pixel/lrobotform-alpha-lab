# Architecture

```mermaid
flowchart LR
    F["Authorized Google Form"] --> E["Read-only Apps Script exporter"]
    E --> J["Questionnaire blueprint JSON"]
    J --> N["Schema normalizer"]
    N --> G["Seeded synthetic-data generator"]
    G --> A["Cronbach's Alpha calibration"]
    A --> Q["Completeness and distribution checks"]
    Q --> C["Local CSV"]
    Q --> R["Local JSON report"]
    B["Browser simulator"] --> G
```

## Trust Boundary

The public system ends at local artifacts. It does not contain an HTTP client,
browser runner, or POST adapter for live Google Forms.

## Determinism

Each run uses an explicit integer seed. The same questionnaire, parameters, and
seed produce the same synthetic dataset and Alpha result. This supports
repeatable demonstrations and test comparisons.

## Reliability Calibration

The generator models a shared latent trait with item-specific noise, maps the
continuous values onto ordered response options, calculates Cronbach's Alpha,
and searches for the closest candidate inside the requested range.

Non-scale choices are generated independently. Ordered choices may use a
normal-shaped distribution; nominal choices use equal or declared custom
weights. Every exported cell is generated locally and labelled as synthetic.
