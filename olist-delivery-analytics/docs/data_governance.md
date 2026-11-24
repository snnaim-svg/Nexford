# Data governance and privacy

- **Purpose/access:** use solely for course analysis of delivery performance. Access limited to project owner/reviewer; no credentialed or row-level data sent to dashboards or external systems.
- **Minimization:** read only required columns; exclude review text, IDs from publication, city, postal code, and precise geolocation. Derive broad state-based macroregions for operational QA.
- **Retention:** keep raw source files locally only while completing the course; keep aggregate outputs and run metadata for assessment; delete raw local files when no longer needed. Raw files, audit logs and generated outputs are git-ignored where appropriate.
- **Publishing:** aggregate-only feed; suppress groups under 100 orders; no automated seller/customer decisions. Users investigate operational patterns with context.
- **Oversight:** the course project reviewer/instructor is the review body for scope, ethics, and publication decisions; changes to data fields, thresholds, or intended use require review before release.
- **Audit:** JSONL metadata log records UTC time, run id, actor, action, basename, file hash, row count, and status; never logs cell values or secrets.
- **Ethics/limitations:** dataset is anonymized but re-identification risk cannot be ruled out. No protected attributes are available; state/region comparisons do not establish demographic fairness. Review score coverage and data selection may bias conclusions.
