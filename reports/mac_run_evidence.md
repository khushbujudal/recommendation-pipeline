# Successful macOS execution

The attached terminal screenshot in `successful_run.png` records the actual
local execution of `python -X faulthandler dags/workflow.py` followed by
`python -m unittest discover -s tests -v`.

- Platform: macOS, arm64.
- Python: 3.14.10 (reported by the local interpreter).
- Dependencies after compatibility update: NumPy 2.3.5 and pandas 2.3.3.
- Workflow run ID: `20261113T145310-bd72a082`.
- Workflow result: all eight stages succeeded.
- Checks: four tests passed in 0.022 seconds, ending in `OK`.
- Evaluated users: 177 for each model.

| Model | Precision at 10 | Recall at 10 | NDCG at 10 | Coverage | Diversity |
| --- | ---: | ---: | ---: | ---: | ---: |
| Popularity | 0.040678 | 0.118577 | 0.072216 | 0.191667 | 0.820213 |
| Personalized | 0.254802 | 0.754459 | 0.564886 | 1.000000 | 0.220088 |

The screenshot establishes this local execution. No claim is made that a
GitHub Actions run has already completed. Structured manifests in the project
are preserved reference runs, rather than fabricated copies of the macOS run.
