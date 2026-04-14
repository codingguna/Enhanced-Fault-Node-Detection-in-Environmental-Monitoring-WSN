"""
Pytest configuration and fixtures for WSN project tests
"""
import sys
import os
import pytest
import tempfile
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS, ensure_dirs


@pytest.fixture(scope="function")
def temp_db():
    """Create a fresh temporary database for each test."""
    original_db = PATHS['db']
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_db = tmp.name

    # Override DB path for testing
    PATHS['db'] = tmp_db
    os.environ['WSN_TEST_DB'] = tmp_db

    yield tmp_db

    # Cleanup: close all DB connections and remove files
    import gc
    gc.collect()  # Try to close any lingering connections

    try:
        # Close WAL files by ensuring no connections remain
        import sqlite3
        # Force close any connections to this temp_db
        for obj in gc.get_objects():
            if isinstance(obj, sqlite3.Connection) and hasattr(obj, 'database') and tmp_db in str(obj):
                try:
                    obj.close()
                except:
                    pass
    except:
        pass

    # Delete database files
    for suffix in ['', '-wal', '-shm']:
        try:
            fname = tmp_db + suffix
            if os.path.exists(fname):
                os.unlink(fname)
        except (FileNotFoundError, PermissionError):
            pass

    PATHS['db'] = original_db


@pytest.fixture(scope="function")
def db_connection(temp_db):
    """Create a fresh database connection for each test."""
    # Close any existing connections first (important on Windows)
    try:
        import gc
        gc.collect()  # Force garbage collection to close lingering connections
    except:
        pass

    conn = sqlite3.connect(temp_db, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    yield conn
    conn.close()
    # Explicitly clear connection reference
    conn = None


@pytest.fixture(scope="function")
def initialized_db(db_connection):
    """Initialize database schema before each test that needs it."""
    from database.db_manager import init_db
    init_db()
    yield db_connection
    # Cleanup handled by db_connection fixture


@pytest.fixture(scope="session")
def detector():
    """Create a hybrid detector instance for testing."""
    from detection_system.hybrid_detector import get_detector
    return get_detector()


@pytest.fixture
def sample_node():
    """Provide a valid sample node reading."""
    return {
        'node_id': 1,
        'cluster_id': 1,
        'battery_level': 85.5,
        'signal_strength': -65.0,
        'temperature': 25.0,
        'humidity': 50.0,
        'data_redundancy_flag': 0,
        'data_packet_size': 256,
        'latency_ms': 100.0,
        'energy_consumed_mJ': 0.5,
        'optimized_path_flag': 1,
        'load_on_node': 0.6,
        'recovery_time_ms': 0.0,
        'pdr': 0.95,
        'transmission_success': 1
    }


@pytest.fixture
def sample_peers():
    """Provide sample peer nodes for cluster-level detection."""
    return [
        {'node_id': 2, 'temperature': 24.5, 'humidity': 48.0, 'battery_level': 88.0},
        {'node_id': 3, 'temperature': 25.5, 'humidity': 52.0, 'battery_level': 86.0},
        {'node_id': 4, 'temperature': 25.0, 'humidity': 50.0, 'battery_level': 87.0},
    ]


@pytest.fixture
def flask_app():
    """Create Flask app for testing."""
    from server import app
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(flask_app):
    """Flask test client."""
    with flask_app.test_client() as client:
        yield client
