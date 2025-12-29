"""Tests for configuration loading."""

import tempfile
from pathlib import Path

import pytest

from mcp_server.routing.config_loader import load_backends_config
from mcp_server.routing.exceptions import ConfigurationError


class TestConfigLoader:
    """Test YAML configuration loading."""

    def test_load_valid_config(self):
        """Test loading valid configuration."""
        config = load_backends_config("tests/fixtures/test_backends.yaml")

        assert len(config) == 4
        assert config[0].name == "db"
        assert config[0].url == "http://localhost:8001"
        assert config[0].namespace == "db"
        assert config[0].priority == 10

    def test_config_with_routes(self):
        """Test config parsing with routes."""
        config = load_backends_config("tests/fixtures/test_backends.yaml")
        db_backend = config[0]

        assert len(db_backend.routes) == 2
        assert db_backend.routes[0].pattern == "*_user"
        assert db_backend.routes[0].strategy == "path"

    def test_config_with_health_check(self):
        """Test config parsing with health check settings."""
        config = load_backends_config("tests/fixtures/test_backends.yaml")
        db_backend = config[0]

        assert db_backend.health_check.enabled is True
        assert db_backend.health_check.interval_seconds == 30
        assert db_backend.health_check.timeout_seconds == 5

    def test_config_with_circuit_breaker(self):
        """Test config parsing with circuit breaker settings."""
        config = load_backends_config("tests/fixtures/test_backends.yaml")
        db_backend = config[0]

        assert db_backend.circuit_breaker.failure_threshold == 5
        assert db_backend.circuit_breaker.timeout_seconds == 60
        assert db_backend.circuit_breaker.half_open_attempts == 3

    def test_config_file_not_found(self):
        """Test error when config file doesn't exist."""
        with pytest.raises(ConfigurationError, match="not found"):
            load_backends_config("/nonexistent/path/config.yaml")

    def test_config_missing_backends_key(self):
        """Test error when 'backends' key is missing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as f:
            f.write("some_other_key: value\n")
            f.flush()

            with pytest.raises(ConfigurationError, match="backends"):
                load_backends_config(f.name)

    def test_config_empty_backends(self):
        """Test error when backends list is empty."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as f:
            f.write("backends: []\n")
            f.flush()

            with pytest.raises(ConfigurationError, match="At least one"):
                load_backends_config(f.name)

    def test_config_missing_required_field(self):
        """Test error when required backend field is missing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as f:
            f.write("""
backends:
  - name: test
    url: http://localhost:8001
    # missing namespace
""")
            f.flush()

            with pytest.raises(ConfigurationError, match="namespace"):
                load_backends_config(f.name)

    def test_config_invalid_priority(self):
        """Test error when priority is invalid."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as f:
            f.write("""
backends:
  - name: test
    url: http://localhost:8001
    namespace: test
    priority: -1
""")
            f.flush()

            with pytest.raises(
                ConfigurationError, match="non-negative integer"
            ):
                load_backends_config(f.name)

    def test_config_invalid_yaml(self):
        """Test error when YAML is malformed."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as f:
            f.write("backends: [invalid yaml: }: content")
            f.flush()

            with pytest.raises(ConfigurationError, match="Invalid YAML"):
                load_backends_config(f.name)

    def test_config_invalid_strategy(self):
        """Test error when route strategy is invalid."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as f:
            f.write("""
backends:
  - name: test
    url: http://localhost:8001
    namespace: test
    routes:
      - pattern: "*_user"
        strategy: invalid_strategy
""")
            f.flush()

            with pytest.raises(ConfigurationError, match="Invalid strategy"):
                load_backends_config(f.name)

    def test_config_fallback_route(self):
        """Test config with fallback route."""
        config = load_backends_config("tests/fixtures/test_backends.yaml")
        analytics_backend = config[2]  # analytics-primary

        assert analytics_backend.routes[0].strategy == "fallback"
        assert analytics_backend.routes[0].fallback_to == "analytics-secondary"

    def test_config_backend_priorities(self):
        """Test that backends have correct priorities."""
        config = load_backends_config("tests/fixtures/test_backends.yaml")

        priorities = {b.name: b.priority for b in config}
        assert priorities["db"] == 10
        assert priorities["api"] == 20
        assert priorities["analytics-primary"] == 10
        assert priorities["analytics-secondary"] == 20

    def test_config_multiple_routes(self):
        """Test backend with multiple routes."""
        config = load_backends_config("tests/fixtures/test_backends.yaml")
        api_backend = config[1]

        assert len(api_backend.routes) == 2
        assert api_backend.routes[0].pattern == "fetch_*"
        assert api_backend.routes[1].pattern == "get_*"
