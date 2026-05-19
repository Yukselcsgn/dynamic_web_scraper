# Tests Package

The `tests/` directory contains the full, enterprise-grade test
architecture for the **Dynamic Web Scraper** project.\
📌 *Note:* The directory layout comes from `feature/test-setup`. Most files
are still **skeletons**; the first implemented suites live under
`unit/core`, `unit/anti_bot`, and `unit/site_detection`.

### Quick run (implemented unit tests)

```bash
pip install -r requirements/testing.txt
PYTHONPATH=. pytest -c tests/pytest.ini tests/unit/core tests/unit/anti_bot tests/unit/site_detection
```

This test suite is designed to support:

-   Unit testing\
-   Integration testing\
-   End-to-End (E2E) testing\
-   Performance & stress testing\
-   Security testing\
-   Compatibility & reliability testing\
-   Regression testing\
-   Smoke testing\
-   Benchmarking

It follows a production-level QA/Test Automation architecture similar to
large-scale scraping and data pipeline systems.

## Test Structure Overview

    tests/
    ├── run_tests.py
    ├── pytest.ini
    ├── conftest.py
    ├── unit/
    ├── integration/
    ├── e2e/
    ├── smoke/
    ├── qa/
    │   ├── performance/
    │   ├── reliability/
    │   ├── compatibility/
    │   ├── security/
    │   ├── scalability/
    │   └── usability/
    ├── regression/
    ├── benchmark/
    ├── fixtures/
    ├── helpers/
    ├── reports/
    └── logs/

## Test Categories (Detailed)

### Unit Tests (`unit/`)

Covers individual modules and components.\
(These are currently scaffolds.)

### Integration Tests (`integration/`)

Validates combined workflows.

### End-to-End Tests (`e2e/`)

Simulates real-world scraping.

### QA Test Suites (`qa/`)

Performance, reliability, security, usability, compatibility &
scalability testing.

### Regression Tests (`regression/`)

Ensures old bugs do not return.

### Benchmark Tests (`benchmark/`)

Performance and latency measurements.

### Smoke Tests (`smoke/`)

Fast sanity checks.

### Fixtures & Mocks

Sample HTML/JSON/CSV files, mock responses, fake servers.

## Running Tests

    python tests/run_tests.py --all
    python tests/run_tests.py --quick
    python tests/run_tests.py --category integration
    pytest --cov=scraper --cov-report=html

## Test Markers

Defined in `pytest.ini`: `unit`, `integration`, `e2e`, `smoke`,
`performance`, `slow`, etc.

## Status

✔ Full architecture\
✔ Fixtures, mocks, helpers\
✖ Test logic not yet written (skeleton stage)
