# While I Sleep (wis)

`wis` is a lightweight overnight research queue for Hermes.

Drop `.md` or `.txt` files into `inbox/`, or add them through the small FastAPI/HTMX dashboard. A nightly Hermes cron job processes each item, creates a standalone HTML report in a dated outbox folder, records a run note in `runs/`, moves the source file to `inbox/complete/`, and regenerates static outbox indexes.

## Directory layout

```text
wis/
├── app/                    # FastAPI + HTMX dashboard
│   ├── main.py
│   └── templates/
├── inbox/                  # Active queue: add .md or .txt files here
│   └── complete/           # Processed inbox items are moved here
├── outbox/                 # Generated reports and static indexes
│   ├── index.html          # Static all-days index, regenerated after runs
│   └── YYYY-MM-DD/         # Reports for a single processing day
│       ├── index.html      # Static day index
│       └── slug.html       # Standalone HTML report
├── runs/                   # Nightly run logs / summaries
├── prompts/
│   └── nightly-run.md      # Self-contained prompt for Hermes cron
├── scripts/
│   ├── add_item.py         # Convenience helper to add queue items
│   ├── generate_static_index.py
│   ├── organize_outbox.py  # Move legacy root reports into date folders
│   ├── queue_status.py     # Show inbox/outbox status
│   ├── run_once.sh         # Manual Hermes run using the nightly prompt
│   └── wislib.py           # Shared filesystem helpers
├── templates/
│   └── report.css          # CSS the agent should inline into reports
├── Dockerfile
├── docker-compose.yml
└── examples/
    └── example-topic.md    # Example inbox item format
```

## Adding items

### Dashboard

```bash
cd /home/j/workspace/wis
docker compose up -d --build
```

Open `http://localhost:8765/`.

The dashboard lets you:

- add new inbox entries with a title and body
- view active and completed inbox files
- browse reports by day
- open generated reports directly
- regenerate static indexes
- normalize any legacy root-level outbox reports into date folders

### Manually

Create a text or markdown file directly under `inbox/`:

```bash
$EDITOR /home/j/workspace/wis/inbox/my-topic.md
```

Suggested format:

```markdown
# Topic title

Research prompt or task description.

## Focus
- What should the report answer?
- Any sources, constraints, or style preferences?
```

### Via helper

```bash
cd /home/j/workspace/wis
python scripts/add_item.py "AI agent evals" "Research current practical evaluation methods for autonomous coding agents."
```

## Checking status

```bash
cd /home/j/workspace/wis
python scripts/queue_status.py
```

## Outbox organization

Reports now live under dated folders:

```text
outbox/2026-06-27/my-report.html
```

Normalize older root-level reports and regenerate static HTML indexes with:

```bash
cd /home/j/workspace/wis
python scripts/organize_outbox.py
python scripts/generate_static_index.py
```

The nightly prompt also instructs the runner to generate reports into `outbox/YYYY-MM-DD/` and refresh the static index after processing.

## Manual run

```bash
cd /home/j/workspace/wis
scripts/run_once.sh
```

This invokes Hermes with the `while-i-sleep` skill and `prompts/nightly-run.md`.

## Cron setup

Recommended nightly schedule: `30 4 * * *` (4:30 AM local time).

The cron job should:

- run with workdir `/home/j/workspace/wis`
- load the `while-i-sleep` skill
- use the prompt in `prompts/nightly-run.md`
- enable at least terminal + web toolsets
- use local/file output; CLI sessions do not receive live cron delivery

The project remains file-based, so the queue can be edited by Hermes, scripts, the dashboard, sync tools, or manually in a normal editor.
