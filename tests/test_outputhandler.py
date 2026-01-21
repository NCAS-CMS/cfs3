import pytest
from unittest.mock import MagicMock
from argparse import Namespace


@pytest.fixture
def mock_cmd_instance():
    """Create a mock cmd2 instance for OutputHandler testing"""
    mock = MagicMock()
    mock.poutput = MagicMock()
    mock.log = MagicMock()
    return mock


@pytest.fixture
def output_handler(mock_cmd_instance):
    """Create an OutputHandler instance for testing"""
    from cfs3.s3cmd import OutputHandler
    return OutputHandler(mock_cmd_instance)


def test_output_handler_signature_same_path(output_handler):
    """Test that same method, args, and path produce the same signature"""
    arg_namespace = Namespace(option1="value1", option2="value2")
    path = "/bucket/path"
    
    sig1 = output_handler._OutputHandler__make_signature("test_method", arg_namespace, path)
    sig2 = output_handler._OutputHandler__make_signature("test_method", arg_namespace, path)
    
    assert sig1 == sig2
    # Verify path is included in signature
    assert path in sig1


def test_output_handler_signature_different_paths(output_handler):
    """Test that different paths produce different signatures"""
    arg_namespace = Namespace(option1="value1", option2="value2")
    path1 = "/bucket/path1"
    path2 = "/bucket/path2"
    
    sig1 = output_handler._OutputHandler__make_signature("test_method", arg_namespace, path1)
    sig2 = output_handler._OutputHandler__make_signature("test_method", arg_namespace, path2)
    
    assert sig1 != sig2
    assert path1 in sig1
    assert path2 in sig2


def test_output_handler_cache_respects_path(output_handler, mock_cmd_instance):
    """Test that cache is keyed by method name, args, AND path"""
    arg_namespace = Namespace(option1="value1")
    path1 = "/bucket/path1"
    path2 = "/bucket/path2"
    
    # Start method with path1
    result1 = output_handler.start_method("test_cmd", arg_namespace, path1)
    assert result1 is None  # First call, not in cache
    
    # Add some lines to cache
    output_handler.houtput = lambda x: output_handler.lines.append(x)
    output_handler.lines = ["result from path1"]
    output_handler.end_method_and_cache()
    
    # Start method with path2 (same method, same args, different path)
    result2 = output_handler.start_method("test_cmd", arg_namespace, path2)
    assert result2 is None  # Not in cache because path is different
    
    # Start method again with path1 (should retrieve from cache)
    result3 = output_handler.start_method("test_cmd", arg_namespace, path1)
    assert result3 is not None
    assert result3 == ["result from path1"]


def test_output_handler_cache_respects_method_name(output_handler, mock_cmd_instance):
    """Test that different method names produce different cache entries"""
    arg_namespace = Namespace(option1="value1")
    path = "/bucket/path"
    
    # Cache result for method1
    result1 = output_handler.start_method("method1", arg_namespace, path)
    assert result1 is None
    output_handler.lines = ["result from method1"]
    output_handler.end_method_and_cache()
    
    # Start method2 with same args
    result2 = output_handler.start_method("method2", arg_namespace, path)
    assert result2 is None  # Not in cache because method name is different
    
    # Start method1 again (should retrieve from cache)
    result3 = output_handler.start_method("method1", arg_namespace, path)
    assert result3 is not None
    assert result3 == ["result from method1"]


def test_output_handler_cache_respects_arguments(output_handler, mock_cmd_instance):
    """Test that different arguments produce different cache entries"""
    path = "/bucket/path"
    
    # Cache result with args1
    args1 = Namespace(option1="value1")
    result1 = output_handler.start_method("test_method", args1, path)
    assert result1 is None
    output_handler.lines = ["result with value1"]
    output_handler.end_method_and_cache()
    
    # Try with different args
    args2 = Namespace(option1="value2")
    result2 = output_handler.start_method("test_method", args2, path)
    assert result2 is None  # Not in cache because args are different
    
    # Retrieve with original args
    result3 = output_handler.start_method("test_method", args1, path)
    assert result3 is not None
    assert result3 == ["result with value1"]
