"""
Unit tests for timing utilities in cfs3.logging_utils
"""

import pytest
import time
from cfs3.logging_utils import (
    timed, 
    timing, 
    enable_timing, 
    disable_timing, 
    is_timing_enabled
)


@pytest.fixture
def reset_timing_state():
    """Reset timing state before and after each test."""
    disable_timing()
    yield
    disable_timing()


def test_enable_disable_timing(reset_timing_state):
    """Test that global timing flag can be enabled and disabled."""
    assert not is_timing_enabled()
    
    enable_timing()
    assert is_timing_enabled()
    
    disable_timing()
    assert not is_timing_enabled()


def test_timed_decorator_with_global_enabled(reset_timing_state, capsys):
    """Test @timed decorator when global timing is enabled."""
    enable_timing()
    
    @timed
    def test_func():
        time.sleep(0.01)
        return "result"
    
    result = test_func()
    captured = capsys.readouterr()
    
    assert result == "result"
    assert "[TIMING]" in captured.out
    assert "test_func" in captured.out
    assert "s" in captured.out


def test_timed_decorator_with_global_disabled(reset_timing_state, capsys):
    """Test @timed decorator when global timing is disabled."""
    disable_timing()
    
    @timed
    def test_func():
        time.sleep(0.01)
        return "result"
    
    result = test_func()
    captured = capsys.readouterr()
    
    assert result == "result"
    assert "[TIMING]" not in captured.out


def test_timed_decorator_with_enabled_true(reset_timing_state, capsys):
    """Test @timed decorator with enabled=True overrides global flag."""
    disable_timing()  # Global is disabled
    
    @timed(enabled=True)
    def test_func():
        time.sleep(0.01)
        return "result"
    
    result = test_func()
    captured = capsys.readouterr()
    
    assert result == "result"
    assert "[TIMING]" in captured.out


def test_timed_decorator_with_enabled_false(reset_timing_state, capsys):
    """Test @timed decorator with enabled=False overrides global flag."""
    enable_timing()  # Global is enabled
    
    @timed(enabled=False)
    def test_func():
        time.sleep(0.01)
        return "result"
    
    result = test_func()
    captured = capsys.readouterr()
    
    assert result == "result"
    assert "[TIMING]" not in captured.out


def test_timed_decorator_with_custom_name(reset_timing_state, capsys):
    """Test @timed decorator with custom operation name."""
    @timed(name="Custom Operation", enabled=True)
    def test_func():
        time.sleep(0.01)
        return "result"
    
    result = test_func()
    captured = capsys.readouterr()
    
    assert result == "result"
    assert "[TIMING]" in captured.out
    assert "Custom Operation" in captured.out


def test_timed_decorator_with_threshold(reset_timing_state, capsys):
    """Test @timed decorator with threshold parameter."""
    @timed(threshold=0.1, enabled=True)
    def fast_func():
        time.sleep(0.01)
        return "fast"
    
    @timed(threshold=0.01, enabled=True)
    def slow_func():
        time.sleep(0.05)
        return "slow"
    
    # Fast function should not report (below threshold)
    result1 = fast_func()
    captured1 = capsys.readouterr()
    assert result1 == "fast"
    assert "[TIMING]" not in captured1.out
    
    # Slow function should report (above threshold)
    result2 = slow_func()
    captured2 = capsys.readouterr()
    assert result2 == "slow"
    assert "[TIMING]" in captured2.out


def test_timed_decorator_with_custom_output(reset_timing_state):
    """Test @timed decorator with custom output function."""
    output = []
    
    @timed(output_func=lambda msg: output.append(msg), enabled=True)
    def test_func():
        time.sleep(0.01)
        return "result"
    
    result = test_func()
    
    assert result == "result"
    assert len(output) == 1
    assert "[TIMING]" in output[0]


def test_timing_context_manager_with_global_enabled(reset_timing_state, capsys):
    """Test timing context manager when global timing is enabled."""
    enable_timing()
    
    with timing("test operation"):
        time.sleep(0.01)
    
    captured = capsys.readouterr()
    assert "[TIMING]" in captured.out
    assert "test operation" in captured.out


def test_timing_context_manager_with_global_disabled(reset_timing_state, capsys):
    """Test timing context manager when global timing is disabled."""
    disable_timing()
    
    with timing("test operation"):
        time.sleep(0.01)
    
    captured = capsys.readouterr()
    assert "[TIMING]" not in captured.out


def test_timing_context_manager_with_enabled_true(reset_timing_state, capsys):
    """Test timing context manager with enabled=True overrides global flag."""
    disable_timing()
    
    with timing("test operation", enabled=True):
        time.sleep(0.01)
    
    captured = capsys.readouterr()
    assert "[TIMING]" in captured.out


def test_timing_context_manager_with_enabled_false(reset_timing_state, capsys):
    """Test timing context manager with enabled=False overrides global flag."""
    enable_timing()
    
    with timing("test operation", enabled=False):
        time.sleep(0.01)
    
    captured = capsys.readouterr()
    assert "[TIMING]" not in captured.out


def test_timing_context_manager_with_threshold(reset_timing_state, capsys):
    """Test timing context manager with threshold parameter."""
    # Fast operation should not report
    with timing("fast op", threshold=0.1, enabled=True):
        time.sleep(0.01)
    
    captured1 = capsys.readouterr()
    assert "[TIMING]" not in captured1.out
    
    # Slow operation should report
    with timing("slow op", threshold=0.01, enabled=True):
        time.sleep(0.05)
    
    captured2 = capsys.readouterr()
    assert "[TIMING]" in captured2.out


def test_timing_context_manager_with_custom_output(reset_timing_state):
    """Test timing context manager with custom output function."""
    output = []
    
    with timing("test operation", output_func=lambda msg: output.append(msg), enabled=True):
        time.sleep(0.01)
    
    assert len(output) == 1
    assert "[TIMING]" in output[0]
    assert "test operation" in output[0]


def test_timing_context_manager_with_exception(reset_timing_state, capsys):
    """Test that timing still reports when exception occurs in context."""
    enable_timing()
    
    with pytest.raises(ValueError):
        with timing("failing operation"):
            time.sleep(0.01)
            raise ValueError("test error")
    
    captured = capsys.readouterr()
    assert "[TIMING]" in captured.out
    assert "failing operation" in captured.out


def test_timed_decorator_preserves_function_metadata(reset_timing_state):
    """Test that @timed decorator preserves function name and docstring."""
    @timed(enabled=True)
    def documented_function():
        """This is a docstring."""
        return "result"
    
    assert documented_function.__name__ == "documented_function"
    assert documented_function.__doc__ == "This is a docstring."


def test_nested_timing(reset_timing_state, capsys):
    """Test nested timing contexts."""
    enable_timing()
    
    with timing("outer"):
        time.sleep(0.01)
        with timing("inner"):
            time.sleep(0.01)
    
    captured = capsys.readouterr()
    assert captured.out.count("[TIMING]") == 2
    assert "outer" in captured.out
    assert "inner" in captured.out


def test_timed_with_arguments_and_return_value(reset_timing_state, capsys):
    """Test that @timed works correctly with function arguments and return values."""
    @timed(enabled=True)
    def add(a, b, c=0):
        time.sleep(0.01)
        return a + b + c
    
    result = add(1, 2, c=3)
    captured = capsys.readouterr()
    
    assert result == 6
    assert "[TIMING]" in captured.out


def test_timing_reports_accurate_duration(reset_timing_state, capsys):
    """Test that timing reports reasonably accurate duration."""
    enable_timing()
    
    sleep_duration = 0.05
    with timing("test"):
        time.sleep(sleep_duration)
    
    captured = capsys.readouterr()
    # Extract the timing value from output
    # Format is "[TIMING] test: 0.0500s"
    assert "[TIMING]" in captured.out
    
    # Check that the reported time is close to actual sleep time
    # (allowing for some overhead)
    import re
    match = re.search(r'(\d+\.\d+)s', captured.out)
    assert match
    reported_time = float(match.group(1))
    assert sleep_duration <= reported_time < sleep_duration + 0.02
