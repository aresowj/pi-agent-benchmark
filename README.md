# agentbench

A small background-job and notification service used as a controlled coding-agent benchmark fixture.

## Development

Requires Python 3.12+.

```sh
python -m pip install -e '.[test]'
python -m pytest
```

The repository has six benchmark cases. Case-specific starting commits and hidden evaluators are managed by the benchmark harness, not shipped with this fixture.
