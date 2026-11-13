# Movie Recommendation Data Pipeline

Data Management for Machine Learning | Assignment 2

Student name: Khushbu Judal

Roll number: 2025ag05901

Email: 2025ag05901@wilp.bits-pilani.ac.in

Repository URL: https://github.com/khushbujudal/recommendation-pipeline

Data Management for Machine Learning | Assignment 2

I implemented a reproducible pipeline from raw CSV ingestion through validation, time-based preparation, feature management, training, evaluation and automated orchestration. A content-based personalized recommender improves held-out relevance over a popularity baseline on a controlled synthetic movie dataset, while reducing genre diversity.

## Data and design decisions

The seeded generator creates 180 users, 120 fictional movies across six categories and 6,480 distinct user-item interactions. Each user has one hidden preferred category; preferred-category ratings tend to be higher. Exposure also has a weaker shared item-popularity effect. Ratings are integers from 1 to 5 and timestamps fall in 2024. No personal data or external dataset is used. The hidden preference is excluded from model inputs.

Synthetic data is permitted by the brief and keeps execution self-contained. Seven malformed rows and three duplicate rows are deliberately injected to demonstrate quality controls. The generator writes three CSV files, which ingestion then reads. A fixed seed of 42 and pinned NumPy and Pandas versions make input generation and metrics repeatable.

## Validation and temporal preparation

Every entity is checked for required fields, nulls, duplicates, numeric identifier types and valid keys. Interactions also require integer ratings in [1, 5], valid timestamps no later than the configured as-of date, and existing user and item references. Invalid records retain reason codes in an error dataset. Required invalid fields are rejected; derived aggregate defaults are handled separately.

| Entity | Input | Accepted | Rejected |
| --- | --- | --- | --- |
| users | 180 | 180 | 0 |
| items | 120 | 120 | 0 |
| interactions | 6490 | 6480 | 10 |

The global 80th-percentile timestamp cutoff is 2024-10-20T04:07:23+00:00. Training contains 5,184 interactions and test contains 1,296. Ties at the cutoff stay in training, so every test timestamp is strictly later. Formats are normalized before deriving user activity summaries, item popularity and a compressed user-item rating matrix with ID mappings.

## Reusable feature management

Features are computed solely from the training partition. Snapshot CSVs are reusable in training, evaluation and reloaded prediction. The experiment stores the category profiles alongside model artifacts. The full catalog, including definitions, grain, types, source and defaults, is provided as reports/feature_catalog.csv.

| Entity | Features | Use and default |
| --- | --- | --- |
| User | Activity count, average rating, last interaction, recency | Audit summaries; zero activity and training global mean for missing averages |
| User category | Mean of rating minus 3; preferred category | Personalized scores; unseen category affinities are zero |
| Item | Category, activity, average rating, positive count, normalized popularity | Model candidates and baseline; zero count for unobserved items |
| Interaction | Affinity = rating minus 3 | Reusable training event feature; invalid source ratings rejected |

The shared user_profile function is used during scoring and reloaded prediction. A cold user has an all-zero profile, which falls back to popularity ranking. An item without training interactions can still receive a category-based score. This is a small file-based feature layer; it does not provide online serving, historical feature version queries or production concurrency controls.

## Models and experiment tracking

Popularity baseline. Rank unseen catalog items by the count of training ratings at least 4. Divide by the maximum item positive count to normalize scores to [0, 1].

Personalized content model. Compute the user's mean centered rating within each category. Score a candidate as 0.95 times its category affinity plus 0.05 times normalized popularity. Filter all items previously interacted with in training. Break score ties by ascending item ID. The fixed weight is configured in advance and is not tuned using test results.

A custom local experiment tracker records run ID, parameters, all model metrics, Python and package versions, source and raw-data SHA256 hashes, model JSONs and the feature snapshot. Unique timestamp-and-UUID directories retain independent experiments without an external server. This meets the experiment tracking requirement with an inspectable alternative to MLflow, but offers no registry UI or automatic promotion.

## Evaluation definitions

K is 10. Relevance means a held-out rating of at least 4 for an item unseen in training. Evaluation ranks against the entire registered catalog after seen-item filtering, without negative sampling. Precision, recall and NDCG are macro averages over users with at least one eligible relevant test item. Both models use exactly the same cohort.

Precision is hits divided by 10; recall is hits divided by that user's eligible relevant set size. Binary NDCG discounts each hit by log2(rank + 1) and divides by ideal discounted gain. Coverage is distinct recommended items divided by 120. Diversity is mean pairwise category inequality within each list, averaged across users. Lists with fewer than two items have diversity zero. These rankers do not predict explicit ratings, so RMSE and MAE are not applicable.

## Measured results and interpretation

| Model | Precision at 10 | Recall at 10 | NDCG at 10 | Coverage | Diversity |
| --- | --- | --- | --- | --- | --- |
| popularity | 0.0407 | 0.1186 | 0.0722 | 0.1917 | 0.8202 |
| personalized | 0.2548 | 0.7545 | 0.5649 | 1.0000 | 0.2201 |

Both models were evaluated on 177 of the 180 users; three users had no eligible relevant test item. The personalized model increases precision from 0.0407 to 0.2548, recall from 0.1186 to 0.7545, and NDCG from 0.0722 to 0.5649. Catalog coverage rises from 19.17% to 100%. Coverage describes the union across users, not the breadth of each individual list.

Mean diversity falls from 0.8202 to 0.2201 because category preferences concentrate recommendations. The result demonstrates a relevance-versus-diversity tradeoff. A diversity re-ranking layer could be evaluated later using a separate validation period. The personalized model is favored by the synthetic category-preference construction; this is not evidence of comparable improvement on real movie data.

## Orchestration and verification

The workflow executes ingestion, validation, preparation, transformation, feature generation, training, evaluation and experiment tracking in dependency order. Each task logs status and runtime; a failure stops dependent tasks and records the exception. A weekly GitHub Actions schedule and manual trigger are included, plus a documented local cron alternative. Remote GitHub execution has not been verified.

My macOS arm64 run used Python 3.14.10, NumPy 2.3.5 and pandas 2.3.3. Run 20261113T145310-bd72a082 completed all eight tasks. The supplied terminal screenshot shows four tests passing in 0.022 seconds: known-answer ranking metrics; invalid-data quarantine; temporal separation and training-only features; persisted model reload, seen-item filtering and cold-user fallback. Reference experiment outputs reproduce the same metrics. The dependency was updated from pandas 2.2.3 for Python 3.14 compatibility.

## Limitations and next steps

The dataset is small and intentionally stationary, with one category per item, no delayed arrivals, no real exposure bias correction and no item availability timestamps. All registered items are assumed available before the cutoff. Evaluation excludes users without positive test items and does not measure online behavior, uncertainty intervals or robustness across seeds. Synthetic users do not demonstrate generalization to real users.

Operational limits include sequential single-process execution, no automatic retry or partial-stage resume, file-based storage and a dense interaction matrix that will not scale to large catalogs. The next useful extensions are a real dataset, rolling temporal validation, richer content features, sparse storage and a managed orchestrator. The pipeline demonstrates the complete data management lifecycle while keeping data lineage, feature definitions, model comparison and execution evidence inspectable.

