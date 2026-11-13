# End to End Movie Recommendation Pipeline

This is my Assignment 2 project for Data Management for Machine Learning. It demonstrates
all eight pipeline stages using explicitly synthetic data. Results establish
pipeline correctness on a controlled dataset, not real-world movie performance.

## Setup and execution

Verified locally on macOS arm64 with Python 3.14.10, NumPy 2.3.5 and pandas 2.3.3.
The GitHub Actions workflow targets Python 3.14. From this repository directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python dags/workflow.py
python -m unittest discover -s tests -v
python -m src.predict --user-id 1
```

No external credentials, data downloads or GPU are required. The workflow takes
seconds on this small dataset. It overwrites current data/model/report snapshots,
and appends a unique immutable experiment directory on every successful run.
Run one workflow at a time; concurrent writers are not supported.

## Data and validation

`configs/pipeline.json` contains the complete configuration. With seed 42, the
generator makes 180 users, 120 synthetic movies in six genres and 6,480 unique
user-item ratings with timestamps in 2024. Users have one hidden favored genre;
ratings tend to be higher in that genre. A weaker shared item popularity effect
influences exposure. The hidden preference is never supplied to the models.
Seven malformed records plus three duplicates are deliberately added. CSVs are
written to `data/raw/` and then actually read for ingestion. No real personal
data or externally sourced movie titles are used.

Validation checks required columns, nulls, integer types, positive IDs, ratings
1-5, timestamps parseable and no later than configured as-of, duplicate keys and
user/item foreign keys. All three entities are validated. Invalid rows are
quarantined with reasons in `data/errors/`; `reports/validation.json` records
counts. Required fields are rejected rather than silently imputed. Metadata
whitespace and category case are normalized after validation.

## Time and features

A global approximately 80/20 chronological split uses the 80th percentile
observed timestamp. All rows equal to the cutoff stay in train; test timestamps
are strictly later. There is no random split. Aggregates and profiles use only
train. Both models see the same catalog, training history, test users and split.
`data/processed/` holds train/test, user activity, item popularity and a
compressed user-item rating matrix with ID mappings. Zero in that matrix means
unobserved. All registered items are assumed available before the cutoff.

The feature catalog is `reports/feature_catalog.csv` (a table). Features reside
in `data/features/`. `src/features.py:user_profile` is reused during evaluation
and reloaded inference. Models use positive-count popularity, item category and
user category affinity; other summaries support audit and future models. The
feature snapshot is copied into each experiment to preserve inference inputs.
Unseen user profiles are zero, which produces popularity fallback. Unobserved
items have zero popularity and can receive category-based scores. This is a
file-based feature layer, not an online service or historical point-in-time
feature store.

## Models and tracking

Popularity ranks items by the number of training ratings >=4. The personalized
content model averages `(rating - 3)` by user and genre and scores each candidate:
`0.95 * category_affinity + 0.05 * normalized_popularity`.
Previously seen training items are excluded. Ties use ascending item ID.
The weight is fixed in config, not selected from test results. No rating
prediction is produced; RMSE and MAE therefore do not apply.

`src/tracking.py` provides a custom local experiment tracker (the assignment
allows an alternative to MLflow). Each `experiments/<run_id>/run.json` stores
parameters, metrics, environment versions and data/source SHA256 hashes. The
same directory contains model JSONs, feature profiles and evaluation CSV.
No external tracking server is needed. Limitations: no tracking UI, registry,
concurrent-write protection or automatic model promotion.

## Evaluation protocol

K=10. A relevant item has a held-out rating >=4 and is unseen in training.
Metrics are macro-averaged over test users with at least one eligible relevant
item; excluded-user count is disclosed in the report. Rank against the entire
120-item catalog after filtering seen items, with no negative sampling.

- Precision@10 = hits / 10, even when fewer than 10 candidates are available.
- Recall@10 = hits / number of eligible relevant items for that user.
- NDCG@10 = binary discounted gain / ideal gain, with log2(rank+1) discount.
- Coverage = distinct recommended items / all 120 catalog items.
- Diversity = mean pairwise category inequality within each recommendation
  list, then mean across users (0 for lists shorter than 2).

`reports/evaluation.csv` compares both models. `reports/recommendations.json`
contains every user's recommendations and held-out relevant items for audit.
High offline recall on synthetic category preferences is expected and does not
establish production utility. Diversity measures genre spread, not semantic
quality. Results illustrate a relevance versus diversity tradeoff.

## Workflow and evidence

`dags/workflow.py` is a structured, fail-fast Python workflow, permitted by the
assignment. It logs every stage to stdout and `reports/workflow_run.json`.
`.github/workflows/pipeline.yml` schedules Mondays at 02:00 UTC and supports
manual runs. On a repository's default branch, enable Actions to activate the
schedule. Local scheduling alternative (replace the absolute path):

```cron
0 2 * * 1 cd /absolute/path/recommendation-pipeline && .venv/bin/python dags/workflow.py >> reports/scheduled.log 2>&1
```

`reports/architecture.md` renders the architecture diagram on GitHub.
`reports/successful_run.png` shows my successful macOS run
`20261113T145310-bd72a082` and all four passing tests.
`reports/mac_run_evidence.md` documents this evidence. The precomputed CSVs,
model artifacts and experiment manifests are reproducibility reference outputs;
the screenshot is separate evidence of the macOS run. Running the workflow
regenerates these current outputs and appends a new experiment. Remote GitHub
Actions execution has not been verified.

## Final report and project details

The three-page PDF is `reports/final_report.pdf`. Its first page has editable
fields populated with Khushbu Judal, roll number 2025ag05901, institutional
email and the repository URL. Use Preview or a PDF form reader to revise them
if necessary. No student details are required in the model code.

For reproducible report generation, edit `submission_details.json` and run:

```bash
python -m pip install -r requirements-report.txt
python scripts/build_report.py
```

The report builder reads those details and the measured evaluation outputs.
The standalone Markdown source is also saved at `reports/final_report.md`.
`SUBMISSION.md` contains exact Git setup commands and the remaining submission
checklist. Configure Git with your actual name and your GitHub verified or
GitHub-provided private email; do not publish your student ID unless required.

## Structure

Each stage has its own module under `src/`: ingestion, validation, preparation,
transformation, features, training and evaluation. Also included are prediction
and tracking modules, configs, workflow, tests, data, models and reports.

The tests cover known-answer ranking metrics, invalid-data quarantine, temporal
separation, train-only feature counts, persisted model reload, seen filtering
and cold-user fallback. No claim is made of production deployment or live data.

## Student details

| Field | Value |
| --- | --- |
| Name | Khushbu Judal |
| Roll number | 2025ag05901 |
| Email | 2025ag05901@wilp.bits-pilani.ac.in |
| Repository | https://github.com/khushbujudal/recommendation-pipeline |
