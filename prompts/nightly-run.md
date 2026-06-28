# While I Sleep — Nightly Queue Runner

You are running the `while-i-sleep` overnight research workflow from `/home/j/workspace/wis`.

Process every `.md` and `.txt` file directly under `inbox/`, excluding `inbox/complete/` and hidden files. If the inbox is empty, write a short dated no-op run note in `runs/`, run `python scripts/generate_static_index.py`, and stop.

Before processing, run `python scripts/organize_outbox.py` to normalize any legacy root-level reports into dated folders.

For each inbox item:

1. Read the item and infer a concise report title.
2. Do enough research or analysis to answer the request well. Use web tools for current or external facts; use the item text itself for private/speculative/project-local prompts.
3. Produce one standalone HTML document in `outbox/YYYY-MM-DD/<filesystem-safe-slug>.html`, where `YYYY-MM-DD` is the processing date.
4. Move the original inbox item to `inbox/complete/` only after the HTML exists.
5. Track processed output paths and any failures for the final run note.

After all items are processed:

1. Run `python scripts/generate_static_index.py` to refresh `outbox/index.html` and per-day `outbox/YYYY-MM-DD/index.html` pages.
2. Write one run note under `runs/YYYY-MM-DD-HHMM-nightly-run.md` listing what was processed, where reports were written, failures, and any items left in the inbox.

Operational rules:

- Treat the filesystem as the source of truth.
- Do not process files inside `inbox/complete/`.
- Use stable, filesystem-safe slugs for output filenames.
- Include the original inbox filename, processing timestamp, and source prompt excerpt in each HTML report.
- Make each HTML report self-contained: inline CSS from `templates/report.css`; no required external assets.
- Prefer writing report files via a short Python script executed through the terminal tool, rather than large `write_file` tool calls, because scheduled jobs can time out during large direct file writes.
- Keep the final chat response short: report how many items were processed and list output paths.
- If one item fails, write the error in the run note, leave that item in `inbox/`, and continue with the next item.

Suggested report sections:

- Executive Summary
- Key Findings
- Detailed Notes
- Sources / Further Reading (when web research was used)
- Open Questions / Next Steps

Before finishing, verify that every processed item has all of:

- an HTML file in `outbox/YYYY-MM-DD/`
- a moved source file in `inbox/complete/`
- refreshed static indexes under `outbox/index.html` and the relevant day folder
