"""Pytest configuration and shared fixtures."""

import os
import pytest


@pytest.fixture
def repo_root():
    """Return the repository root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def cli_script(repo_root):
    """Return path to the CLI script."""
    return os.path.join(repo_root, "usd_opinion_trace.py")


@pytest.fixture
def fixtures_dir(repo_root):
    """Return path to test fixtures directory."""
    return os.path.join(repo_root, "tests", "fixtures")


@pytest.fixture
def shared_dir(fixtures_dir):
    """Return path to shared fixtures directory."""
    return os.path.join(fixtures_dir, "shared")


@pytest.fixture
def stages_dir(fixtures_dir):
    """Return path to stages directory."""
    return os.path.join(fixtures_dir, "stages")
