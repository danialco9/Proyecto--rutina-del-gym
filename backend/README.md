# gym-tracker (backend)

Python package with the training analytics that will power the web app's API.

## Features

- **Loader**: reads the CSV training log in [`../data`](../data) into typed pandas DataFrames.
- **Metrics**: estimated 1RM (Epley), personal records, weekly hard sets and tonnage per
  muscle group, body weight rolling trend and weekly rate of change, plateau detection.
- **Recommendations**: rule-based double progression. Add load when every target set hits
  the target reps at RPE <= 8, repeat when the effort was too high, chase reps otherwise,
  and deload 10% after three sessions without a new best e1RM.

## Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync                 # install dependencies
uv run gym-report       # print the training report (Spanish output)
uv run pytest --cov     # tests with coverage
uv run ruff check .     # lint
uv run ruff format .    # format
uv run mypy             # strict type checking
```
