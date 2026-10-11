# BROBS reviewed macro-event entry pause (optional)

This is a local, **paper-only entry pause** for an operator-reviewed high-impact event, not an AI trade signal and not an automatic world-news verification engine. It is deliberately opt-in and does not replace the existing price/volatility controls.

## Configure

Save a JSON file (update the times to a current, timezone-aware window):

```json
{
  "schema": "brobs-macro-v1",
  "as_of": "2026-10-11T17:00:00Z",
  "reviewed": true,
  "holds": [
    {
      "symbols": ["EUR_USD", "GBP_USD"],
      "starts_at": "2026-10-11T16:45:00Z",
      "ends_at": "2026-10-11T17:45:00Z",
      "source_urls": ["https://example.org/official-economic-calendar"]
    }
  ]
}
```

Here the URL is only a **placeholder**; replace it with an actual trustworthy HTTPS source you have checked. The flag `reviewed:true` is a statement by the local operator, **not proof** of independent source verification.

Then start the local runner with `--macro-report C:\path\to\macro.json` (together with normal paper arguments). BROBS checks the report for each attempted new position. If a report is missing, old (more than 1 hour), future-dated, invalid or unreviewed, it blocks new paper entries rather than relying on an unknown safety state.

When there is a matching active hold window it sets the new-entry signal to `hold`. Existing local positions continue through normal quote polling and stop/target management. When no report is configured, the original runner behavior is unchanged. There is no automatic economic-calendar ingestion or news-prediction claim.

## Test

```powershell
python -m unittest tests.test_macro_guard -v
python -m unittest discover -s tests -v
```

**Limits:** Protective exits still depend on polling and valid live quotes, gaps can cause losses, paper results are not broker execution, and this filter has no established positive effect on win rate.
