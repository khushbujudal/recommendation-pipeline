# Final submission steps

## Details to add

| Detail | Where to enter it |
| --- | --- |
| Full name | First page of `reports/final_report.pdf`, or `submission_details.json` before rebuilding |
| Roll number or student ID | First page of the report, or `submission_details.json`; include publicly only if the course requires it |
| Actual GitHub repository URL | First page of the report, or `submission_details.json`; also paste into the submission portal |
| Git author name and verified or private GitHub email | Local `git config` commands below |

No personal detail is required in the Python modules, dataset or model config.
The report fields now contain the supplied student name, roll number, email
and actual repository URL. Verify these details before final submission.
To keep the PDF and Markdown consistent, edit `submission_details.json` and run:

```bash
python -m pip install -r requirements-report.txt
python scripts/build_report.py
```

Alternatively, open the PDF in Preview, click each field, fill and save it.
The three-page technical report is complete; only identity and URL fields remain.
Review your course's assistance and disclosure policy before submission.

## GitHub setup on macOS

Use this folder as a new project, or copy its updated files into your existing
project while preserving its `.git` directory and `.venv`. Do not overwrite
local unpublished code changes without reviewing them. Do not replace your
existing Git history. The package contains no fabricated Git history or author.

Create an empty repository named `recommendation-pipeline` on GitHub. Leave
initial README, license and gitignore options unchecked. Choose visibility
according to the course instructions. Then open Terminal in this project folder.

Replace YOUR NAME and YOUR VERIFIED OR PRIVATE GITHUB EMAIL with your actual
Git author identity. These commands set identity for this repository only.

```bash
git init
git config user.name "YOUR NAME"
git config user.email "YOUR VERIFIED OR PRIVATE GITHUB EMAIL"
git add .
git status
```

Check that `.venv` and credentials are not staged. Then commit:

```bash
git commit -m "Implement end-to-end movie recommendation pipeline"
git branch -M main
```

Replace YOUR_GITHUB_USERNAME below with your actual GitHub username:

```bash
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/recommendation-pipeline.git
git push -u origin main
```

If the folder already has an origin, first inspect `git remote -v`; reuse it
when it is correct. If it points elsewhere, stop and check the intended
repository before changing it. GitHub may prompt you to authenticate. Do not
enter your GitHub account password as a Git HTTPS password; follow the supported
authentication prompt or use your existing Git credential manager.

Once the URL exists, update `submission_details.json`, rebuild the report, and
commit and push the final details. Use your course's privacy requirements when
choosing whether a student ID belongs in the repository.

## Remote workflow verification

1. Open the repository's Actions tab.
2. Select Recommendation pipeline and click Run workflow on the main branch.
3. Wait for success. Download the pipeline-evidence artifact if needed.
4. Optionally save a screenshot as `reports/github_actions_success.png` and commit it.
5. Do not describe the remote run as successful until the green check is visible.

The schedule runs Mondays at 02:00 UTC, which is 07:30 in Asia/Kolkata.

## Final checks

- Run `python dags/workflow.py` and `python -m unittest discover -s tests -v`.
- Confirm `reports/successful_run.png` shows the successful local run.
- Review `reports/feature_catalog.csv`, `reports/validation.json`,
  `reports/evaluation.csv` and `reports/architecture.md`.
- Fill the report details and ensure it remains three pages.
- Check that the repository includes `.github/workflows/pipeline.yml`.
- Submit the actual repository link and the final PDF.
- Check the deadline in the course announcement.
