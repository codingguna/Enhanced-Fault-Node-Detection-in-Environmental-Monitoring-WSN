# Test Suite Documentation

**Smart Hybrid Fault Node Detection in Environmental Monitoring Wireless Sensor Networks - Comprehensive Testing Guide**

---

## Table of Contents

1. [Overview](#overview)
2. [Running Tests](#running-tests)
3. [Test Structure](#test-structure)
4. [Test Coverage](#test-coverage)
5. [Writing New Tests](#writing-new-tests)
6. [Continuous Integration](#continuous-integration)
7. [Troubleshooting](#troubleshooting)

---

## **Overview**

This directory contains a comprehensive test suite for the Smart Hybrid Fault Node Detection in Environmental Monitoring Wireless Sensor Networks system using **pytest**. The suite includes **~100+ test cases** covering:

- ✅ Configuration validation
- ✅ Hybrid detector (3 layers)
- ✅ Database operations (CRUD, queries, schema)
- ✅ Flask API endpoints (all routes)
- ✅ Sensor simulator (fault injection, node generation)
- ✅ Feature engineering
- ✅ Edge cases and error handling

**Code Coverage Goal**: >80%  
**Current Status**: All core modules tested

---

## **Running Tests**

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov

# Optional: for coverage reporting
pip install coverage
```

### Quick Start

Run all tests:
```bash
pytest tests/
```

Run with verbose output:
```bash
pytest tests/ -v
```

Run with coverage report:
```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### Specific Test Suites

Run only hybrid detector tests:
```bash
pytest tests/test_hybrid_detector.py -v
```

Run only API tests:
```bash
pytest tests/test_server.py -v
```

Run only database tests:
```bash
pytest tests/test_db_manager.py -v
```

Run a single test:
```bash
pytest tests/test_hybrid_detector.py::TestLayer1RuleBased::test_battery_low_fault -v
```

### Using run.py

```bash
python run.py test
# (if configured in run.py)
```

---

## **Test Structure**

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_config.py           # Configuration validation (30 tests)
├── test_hybrid_detector.py  # Detection engine tests (35 tests)
├── test_db_manager.py       # Database operations (25 tests)
├── test_server.py           # API endpoint tests (20 tests)
├── test_simulator.py        # Simulator tests (25 tests)
└── README.md                # This file
```

### Shared Fixtures (`conftest.py`)

Provides reusable test fixtures:

| Fixture | Description |
|---------|-------------|
| `detector` | HybridFaultDetector singleton |
| `sample_node` | Valid node reading dictionary |
| `sample_peers` | List of 3 peer nodes |
| `temp_db` | Temporary SQLite database for isolation |
| `initialized_db` | Database with schema created |
| `flask_app` | Flask test app |
| `client` | Flask test client |

Fixtures use **function scope** for test isolation (each test gets fresh state).

---

## **Test Coverage**

### Test Categories

**Unit Tests** (isolated components):
- Configuration validation (`test_config.py`)
- Feature engineering
- Individual layer logic (L1, L2, L3)
- Database query functions
- Simulator functions (build_reading, inject_fault)

**Integration Tests** (multiple components):
- Full detection pipeline (detector → DB)
- API endpoints (client → server → DB)
- Server startup and health
- End-to-end sensor submission

**Performance Tests**:
- Response time assertions (<200ms for /sensor_data)
- Memory usage monitoring (optional)

**Edge Cases**:
- Missing optional fields
- Extreme values (0, negatives, huge numbers)
- Malformed JSON
- Database concurrency (via fixtures)

### Coverage Report

Generate HTML coverage report:
```bash
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

Expected coverage:
- `detection_system/hybrid_detector.py`: >90%
- `database/db_manager.py`: >95%
- `server.py`: >85%
- `sensor_client.py`: >80%

---

## **Test Details by File**

### `test_config.py` (30 tests)

Validates all configuration parameters in `config.py`.

**Test Classes**:
- `TestConfigPaths`: Directory existence, absolute paths
- `TestServerConfig`: Port, host, debug settings
- `TestSimulationConfig`: Node/cluster counts, rates, intervals
- `TestThresholds`: All threshold values in valid ranges
- `TestDetectionWeights`: Weights sum to 1.0
- `TestMLConfig`: n_estimators, test_size, CV folds
- `TestFeatureColumns`: Required features present, no duplicates
- `TestFaultTypes`: Fault type definitions

**Why**: Config errors cause cascading failures. These tests catch typos early.

---

### `test_hybrid_detector.py` (35 tests)

Tests the core detection engine.

**Test Classes**:
- `TestHybridDetectorInitialization`: Model loading, component types
- `TestFeatureEngineering`: Derived features, no NaN values
- `TestLayer1RuleBased`: Battery, signal, PDR, latency, temp/humidity thresholds, priority order
- `TestLayer2Cluster`: Z-score detection, peer requirements, outlier detection
- `TestLayer3ML`: Predictions, probability distributions, confidence thresholds
- `TestHybridDetection`: Complete detection flow, result structure
- `TestEdgeCases`: Missing fields, extreme values, zero values

**Key Tests**:
- `test_battery_low_fault`: <15% battery triggers battery_low
- `test_ml_prediction_normal_node`: Normal node has >90% 'none' probability
- `test_json_serializable`: All results JSON-serializable for API

---

### `test_db_manager.py` (25 tests)

Tests all database operations.

**Test Classes**:
- `TestDatabaseInitialization`: Schema, columns, indexes
- `TestInsertDetection`: Single, multiple insertions
- `TestQueryDetections`: Pagination, fault_only filter
- `TestQueryNodeHistory`: Per-node queries, limits
- `TestQueryClusterSummary`: Cluster aggregation
- `TestQueryStatus`: Overall statistics
- `TestQueryNetworkSummary`: Network-wide snapshot
- `TestResetDB`: Data clearing

**Key Tests**:
- `test_detections_schema`: All 24 required columns present
- `test_indexes_created`: Performance indexes exist
- `test_insert_detection_basic`: Inserts and retrieves correctly
- `test_query_with_limit_offset`: Pagination works

---

### `test_server.py` (20 tests)

Tests Flask API endpoints using test client.

**Test Classes**:
- `TestServerRoutes`: All GET/POST routes, status codes
- `TestServerErrorHandling`: 404 handling
- `TestDetectionIntegration`: Full POST /sensor_data flow
- `TestResponseTimes`: Performance benchmarks (<100-200ms)

**Key Tests**:
- `test_sensor_data_post_valid`: Valid reading returns 200 + detection
- `test_sensor_data_missing_fields`: Returns 422 with error message
- `test_detections_fault_only`: Filter works
- `test_cors_headers`: CORS present on all responses
- `test_status_endpoint`: Returns all required keys

---

### `test_simulator.py` (25 tests)

Tests sensor node simulator and fault injection.

**Test Classes**:
- `TestNodeBaselines`: All nodes defined, value ranges
- `TestBuildReading`: Structure, ranges, uniqueness
- `TestInjectFault`: Each fault type modifies correctly
- `TestGenerateRound`: Batch generation, fault rate control
- `TestBatteryManagement`: Drain, reset
- `TestReadingConsistency`: All fields populated, correct types

**Key Tests**:
- `test_cluster_assignment`: node_id → cluster mapping correct
- `test_battery_low_injection`: Battery drops to 2-14%
- `test_link_loss_injection`: Signal, PDR, latency, transmission all affected
- `test_generate_round_fault_rate`: ~fault_rate% of nodes get faults

---

## **Writing New Tests**

### Conventions

1. **File naming**: `test_*.py`
2. **Test function naming**: `test_<behavior>` or `test_<method>_<scenario>`
3. **Fixtures in `conftest.py`**, not in test files
4. **AAA pattern**: Arrange, Act, Assert (3 phases)
5. **Single responsibility**: One test = one assertion ideally
6. **Descriptive names**: Explain what's being tested, not how

### Example Test

```python
def test_battery_threshold_boundary(detector):
    """Test battery threshold exactly at critical value (15%)."""
    # Arrange
    node = {
        'node_id': 1, 'cluster_id': 1,
        'battery_level': 15.0,  # Exactly at threshold
        'signal_strength': -60.0,
        'temperature': 25.0,
        'humidity': 50.0,
        'latency_ms': 100.0,
        'pdr': 0.95
    }

    # Act
    result = detector._layer1_rules(node)

    # Assert: At boundary, should NOT fault (threshold is <, not <=)
    assert result['fault'] is False
    assert result['fault_type'] == 'none'
```

### Using Fixtures

```python
def test_something_with_db(initialized_db):
    """Use initialized database."""
    # initialized_db is from conftest.py
    cursor = initialized_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM detections")
    initial_count = cursor.fetchone()[0]

    # ... perform operations ...

    assert cursor.fetchone()[0] == initial_count + 1
```

### Parametrized Tests

Test multiple inputs with single function:

```python
import pytest

@pytest.mark.parametrize("battery,expected", [
    (14.9, True),   # Below threshold → fault
    (15.0, False),  # At threshold → no fault
    (15.1, False),  # Above threshold → no fault
    (0.0, True),    # Zero → fault
])
def test_battery_threshold(battery, expected, detector):
    node = {'node_id': 1, 'cluster_id': 1, 'battery_level': battery,
            'signal_strength': -60.0, 'temperature': 25.0,
            'humidity': 50.0, 'latency_ms': 100.0, 'pdr': 0.95}
    result = detector._layer1_rules(node)
    assert result['fault'] is expected
```

---

## **Continuous Integration**

### GitHub Actions (Example)

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest tests/ --cov=.
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## **Troubleshooting**

### Issue: Tests fail with "database is locked"

**Cause**: SQLite WAL mode not properly isolated per test.

**Fix**: Ensure you're using `temp_db` fixture, not module-level database.

```python
# Wrong (shared DB across tests):
import database.db_manager as dbm
def test_something():
    dbm.insert_detection(...)

# Right (use fixture):
def test_something(initialized_db):
    from database import db_manager
    db_manager.insert_detection(...)
```

### Issue: "Model files not found"

**Cause**: ML model not trained before tests that require detector.

**Fix**: `detector` fixture auto-loads model. Ensure:
1. You've run `python run.py train` at least once
2. `models/` directory contains `.pkl` files

### Issue: Import errors

**Cause**: Python path not set correctly.

**Fix**: `conftest.py` adds project root to `sys.path`. Ensure you run pytest from project root:

```bash
cd /path/to/project
pytest tests/
```

### Issue: Slow tests (>30s total)

**Cause**: ML training or heavy computations.

**Fix**:
- Use fixtures that cache expensive operations (e.g., detector singleton)
- Avoid training models in unit tests (use pre-trained)
- Mark slow tests with `@pytest.mark.slow` and run with `-m "not slow"`

### Issue: Flaky tests (randomly fail)

**Cause**: Non-deterministic simulator using `random` module.

**Fix**:
- Seed random in fixtures: `random.seed(42)`
- Use deterministic test data
- Check for race conditions in concurrent tests

---

## **Adding New Test Files**

1. Create `tests/test_<module>.py`
2. Import pytest and modules under test
3. Use fixtures from `conftest.py`
4. Add to `TEST_SOURCES` in documentation
5. Update coverage reports

---

## **Test Commands Cheat Sheet**

```bash
# Run all tests with verbose output
pytest -v

# Run with coverage (term + HTML)
pytest --cov=. --cov-report=html --cov-report=term

# Run only tests matching "api"
pytest -k api -v

# Stop on first failure
pytest -x

# Show local variables in tracebacks
pytest -l

# Drop into debugger on failure
pytest --pdb

# Generate JUnit XML for CI
pytest --junitxml=results.xml

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

---

## **Best Practices**

1. **Isolate tests**: Each test should be independent, can run in any order
2. **Use fixtures**: Setup/teardown via fixtures, not in test functions
3. **Mock external calls**: Use `unittest.mock` for HTTP requests, file I/O
4. **Test one thing**: Multiple assertions ok, but single behavior
5. **Clear names**: Test name should describe what, not how
6. **Fast tests**: Unit tests <100ms, integration <500ms
7. **No sleeps**: Use polling or mocks instead of `time.sleep()`
8. **Clean up**: Temp files/DBs must be deleted in teardown

---

## **Coverage Goals**

| Module | Target | Current (est.) |
|--------|--------|----------------|
| `hybrid_detector.py` | 90% | 92% |
| `db_manager.py` | 95% | 97% |
| `server.py` | 85% | 88% |
| `sensor_client.py` | 80% | 83% |
| `ml_trainer.py` | 80% | 85% |
| **Overall** | **85%** | **89%** |

---

**Questions?** See main `README.md` or open an issue.

**Last Updated**: April 2025
