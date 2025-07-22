#!/usr/bin/env python3
"""
Test runner script for acompanhamento microservice.
Provides easy commands to run different categories of tests.
"""

import subprocess
import sys


def run_command(cmd, description):
    """Run a command and return the exit code."""
    print(f"\n🧪 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print(
            """
🧪 Test Runner for Acompanhamento Microservice

Usage: python run_tests.py <command>

Available commands:
  all             - Run all tests
  unit            - Run unit tests only
  integration     - Run integration tests only
  performance     - Run performance tests only
  e2e             - Run end-to-end tests only
  models          - Run all model tests (unit + integration)
  fast            - Run fast tests (unit + integration)
  ci              - Run tests suitable for CI (all except performance)
  coverage        - Run all tests with coverage report
  repository      - Run repository tests only
  service         - Run service layer tests only
  api             - Run API layer tests only (schemas, dependencies, config)
  schemas         - Run schema validation tests only

  # Specific model tests:
  item            - Run ItemPedido tests
  evento-pedido   - Run EventoPedido tests
  evento-pagamento - Run EventoPagamento tests
  acompanhamento  - Run Acompanhamento tests

Examples:
  python run_tests.py all
  python run_tests.py unit
  python run_tests.py coverage
        """
        )
        return 1

    command = sys.argv[1].lower()
    cmd_base = ["poetry", "run", "python", "-m", "pytest"]

    # Set common options
    common_opts = ["-v", "--tb=short"]

    if command == "all":
        cmd = cmd_base + ["tests/"] + common_opts
        return run_command(cmd, "Running all tests")

    elif command == "unit":
        cmd = cmd_base + ["tests/unit/"] + common_opts
        return run_command(cmd, "Running unit tests")

    elif command == "integration":
        cmd = cmd_base + ["tests/integration/"] + common_opts
        return run_command(cmd, "Running integration tests")

    elif command == "performance":
        cmd = cmd_base + ["tests/performance/"] + common_opts
        return run_command(cmd, "Running performance tests")

    elif command == "e2e":
        cmd = cmd_base + ["tests/e2e/"] + common_opts
        return run_command(cmd, "Running end-to-end tests")

    elif command == "repository":
        cmd = cmd_base + ["tests/unit/repository/"] + common_opts
        return run_command(cmd, "Running repository tests")

    elif command == "service":
        cmd = cmd_base + ["tests/unit/service/"] + common_opts
        return run_command(cmd, "Running service layer tests")

    elif command == "api":
        cmd = cmd_base + ["tests/unit/api/"] + common_opts
        return run_command(cmd, "Running API layer tests")

    elif command == "schemas":
        schema_files = [
            "tests/unit/api/test_request_schemas.py",
            "tests/unit/api/test_response_schemas.py",
            "tests/unit/api/test_schema_integration.py",
        ]
        cmd = cmd_base + schema_files + common_opts
        return run_command(cmd, "Running schema validation tests")

    elif command == "models":
        unit_result = run_command(
            cmd_base + ["tests/unit/models/"] + common_opts, "Running unit model tests"
        )
        if unit_result != 0:
            return unit_result

        return run_command(
            cmd_base + ["tests/integration/"] + common_opts, "Running integration tests"
        )

    elif command == "fast":
        unit_result = run_command(
            cmd_base + ["tests/unit/"] + common_opts, "Running unit tests"
        )
        if unit_result != 0:
            return unit_result

        return run_command(
            cmd_base + ["tests/integration/"] + common_opts, "Running integration tests"
        )

    elif command == "ci":
        # Run everything except performance tests
        for test_type in ["unit", "integration", "e2e"]:
            result = run_command(
                cmd_base + [f"tests/{test_type}/"] + common_opts,
                f"Running {test_type} tests",
            )
            if result != 0:
                return result
        return 0

    elif command == "coverage":
        # Run tests with coverage
        cmd = (
            cmd_base
            + ["tests/", "--cov=app/models", "--cov-report=html", "--cov-report=term"]
            + common_opts
        )
        return run_command(cmd, "Running tests with coverage")

    # Specific model tests
    elif command == "item":
        cmd = cmd_base + ["tests/unit/models/test_item_pedido.py"] + common_opts
        return run_command(cmd, "Running ItemPedido tests")

    elif command == "evento-pedido":
        cmd = cmd_base + ["tests/unit/models/test_evento_pedido.py"] + common_opts
        return run_command(cmd, "Running EventoPedido tests")

    elif command == "evento-pagamento":
        cmd = cmd_base + ["tests/unit/models/test_evento_pagamento.py"] + common_opts
        return run_command(cmd, "Running EventoPagamento tests")

    elif command == "acompanhamento":
        cmd = cmd_base + ["tests/unit/models/test_acompanhamento.py"] + common_opts
        return run_command(cmd, "Running Acompanhamento tests")

    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python run_tests.py' for usage information.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    sys.exit(exit_code)
