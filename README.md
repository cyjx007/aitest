# aitest

A small, dependency-free AI evaluation harness for prompt and model regression testing.

## What it does

- Define test cases as JSON.
- Run a model adapter against those cases.
- Apply deterministic assertions to outputs.
- Produce a machine-readable JSON report and a human-friendly summary.
- Keep the core protocol independent of any model provider.

## Quick start

```bash
python -m aitest --help
python -m unittest discover -s tests -v
```

A test case looks like:

```json
{
  "id": "greeting",
  "input": "Say hello",
  "expected_contains": ["hello"]
}
```

The built-in `echo` adapter is useful for smoke tests. Provider integrations can implement the `ModelAdapter` protocol without changing the evaluator. A generic JSON-over-HTTP adapter is included for simple services.

## Design

`aitest` deliberately separates:

1. **Adapter** — talks to a model.
2. **Case** — describes one evaluation.
3. **Evaluator** — checks the returned text.
4. **Reporter** — serializes results for CI and humans.

The project is intentionally small so it can become a foundation for provider-specific adapters, LLM-as-judge evaluators, latency/cost metrics, datasets, and CI gates later.

### HTTP model endpoint

Point the CLI at an endpoint that accepts a JSON body containing the prompt field and returns a JSON object containing output or text:

```bash
PYTHONPATH=src python -m aitest examples/http-model.json --url http://localhost:8000/generate
```

Use `--json` to emit a CI-friendly report.
