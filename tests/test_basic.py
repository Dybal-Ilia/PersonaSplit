"""Basic tests to verify the project structure."""

import pytest


def test_imports():
    """Test that main modules can be imported."""
    from src.core.agents import agent
    from src.core.schemas import state
    from src.utils import loaders, logger
    
    assert agent is not None
    assert state is not None
    assert loaders is not None
    assert logger is not None
