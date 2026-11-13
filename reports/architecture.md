# Pipeline architecture

```mermaid
flowchart TD
 A[Seeded raw CSV generation and ingestion] --> B[Validate all entities]
 B --> X[Quarantined rows and reason codes]
 B --> C[Normalize and split by global time]
 C --> D[Training summaries and matrix]
 D --> E[Versioned reusable feature snapshot]
 E --> F[Popularity model]
 E --> G[Personalized content model]
 F --> H[Full catalog evaluation]
 G --> H
 H --> I[Experiment artifacts and metrics]
 E --> J[Reload for prediction]
 G --> J
```

The workflow targets Python 3.14 with pandas 2.3.3.

`dags/workflow.py` enforces the ordered dependencies, fails immediately on errors,
and writes task status after each stage. GitHub Actions runs it weekly and on
manual dispatch. `experiments/<run_id>/` preserves parameters, metrics, feature
profiles, both models, environment versions and SHA256 input/source hashes.
