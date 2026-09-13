# Measurement plan

The synthetic CSV is a smoke/evaluation fixture, not proof of operational improvement. Each row is an invented interaction. No original conversation, customer records, or production data is included.

For a real pilot, collect pseudonymous customer ID, issue ID, event ID, timestamp, final validated intent, initial/final queue, misdirected-transfer events, resolution status, handling time, and subsequent same-issue contacts. Define labels and a repeat-contact window (for example, seven days) before starting. Deduplicate events and compare equivalent cohorts with complete follow-up windows.

- Misdirected-transfer rate: interactions with at least one adjudicated misdirected transfer divided by eligible interactions.
- Seven-day repeat-contact rate: resolved index issues followed by a same-issue contact within seven days divided by resolved index issues with seven complete days of observation.
- Relative reduction: `(baseline_rate - new_rate) / baseline_rate`; undefined for a zero baseline. Distinguish this from percentage-point change.
- Track per-intent recall, especially fraud, fallback rate, latency, human overrides, and queue load alongside average metrics.

Prefer a controlled rollout; report sample sizes, uncertainty, cohort changes, and possible confounding. Do not attribute changes to Polly or to routing alone without evidence. A queue with many repeat signals suggests where to investigate, not a proven root cause. Actual business outcomes are outside the scope of the shipped synthetic report.
