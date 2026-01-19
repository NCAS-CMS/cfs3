"""
Test internal piping functionality between s3cmd commands.
"""
import pytest
from unittest.mock import MagicMock, patch
from cfs3.s3cmd import s3cmd
import io
import json

# Note: ANSI styling configuration was removed in cmd2 3.1.0
# The API has changed from cmd2.ansi.allow_style to different configuration methods

dummy_config = '{"aliases":{"loc1":{"url":"https://blah.com","accessKey":"a key","secretKey":"b key","api":"S3v4"}}}'


@pytest.fixture
def mock_s3cmd(mocker):
    """Create a mock s3cmd instance with necessary dependencies."""
    mocker.patch('cfs3.s3cmd.get_client')
    mocker.patch('cfs3.s3cmd.get_locations', 
                 return_value=json.loads(dummy_config)['aliases']['loc1'])
    
    app = s3cmd(path='loc1')
    app.client = MagicMock()
    app.bucket = 'test-bucket'
    app.path = '/test/path'
    
    # Redirect stdout/stderr to StringIO
    app.stdout = io.StringIO()

    
    return app


def test_drsview_to_ls_pipe_producers_consumers(mock_s3cmd):
    """Test that drsview and ls are registered in the correct pipe lists."""
    assert 'drsview' in mock_s3cmd.pipe_producers
    assert 'ls' in mock_s3cmd.pipe_consumers


def test_drsview_to_ls_piping(mock_s3cmd):
    """Test piping from drsview list output to ls."""
    
    # Mock the _recurse method to return test files
    test_files = [
        {'n': 'tas_HadGEM3-GC31-LM_historical_r1i1p1f3_6hrPt_1950-01_N96.nc', 's': 1024, 'd': '2024-01-01'},
        {'n': 'tas_HadGEM3-GC31-LM_historical_r1i1p1f3_6hrPt_1950-02_N96.nc', 's': 2048, 'd': '2024-01-02'},
        {'n': 'pr_HadGEM3-GC31-LM_historical_r1i1p1f3_6hrPt_1950-01_N96.nc', 's': 1536, 'd': '2024-01-01'},
    ]
    
    mock_s3cmd._recurse = MagicMock(return_value=(
        3072,  # volume
        3,     # nfiles
        0,     # ndirs
        [],    # mydirs
        test_files  # myfiles
    ))
    
    # Mock the output_handler to return cached data
    mock_cache = [
        'Header',
        'tas_HadGEM3-GC31-LM_historical_r1i1p1f3_6hrPt_1950-01_N96.nc',
        'tas_HadGEM3-GC31-LM_historical_r1i1p1f3_6hrPt_1950-02_N96.nc',
    ]
    
    with patch.object(mock_s3cmd, 'output_handler') as mock_handler:
        mock_handler.start_method.return_value = None
        mock_handler.last_cache = mock_cache
        
        # Simulate the piping by calling precmd with :: syntax
        statement = mock_s3cmd.statement_parser.parse('drsview -s Variable=tas -o list :: ls')
        
        # Execute the LHS (drsview)
        result = mock_s3cmd.precmd(statement)
        
        # Verify that __pipe_input was set to the cached data
        assert mock_s3cmd._s3cmd__pipe_input == mock_cache
        
        # Verify the returned statement is for ls (result is a string)
        assert 'ls' in result


def test_ls_handles_piped_input(mock_s3cmd):
    """Test that ls correctly handles piped input."""
    
    # Simulate piped input (what drsview would produce)
    piped_files = [
        'Header line',  # First line is typically a header
        'tas_HadGEM3-GC31-LM_historical_r1i1p1f3_6hrPt_1950-01_N96.nc',
        'tas_HadGEM3-GC31-LM_historical_r1i1p1f3_6hrPt_1950-02_N96.nc',
    ]
    
    mock_s3cmd._s3cmd__pipe_input = piped_files
    
    # Execute ls command through cmd2's command processing
    mock_s3cmd.onecmd('ls')
    
    # Get the output
    output = mock_s3cmd.stdout.getvalue()
    
    # Verify that the piped files are displayed
    assert 'Received 2 files' in output
    assert 'tas_HadGEM3-GC31-LM_historical_r1i1p1f3_6hrPt_1950-01_N96.nc' in output
    assert 'tas_HadGEM3-GC31-LM_historical_r1i1p1f3_6hrPt_1950-02_N96.nc' in output


def test_precmd_validates_pipe_commands(mock_s3cmd):
    """Test that precmd validates both sides of the pipe."""
    
    # Test invalid producer
    statement = mock_s3cmd.statement_parser.parse('invalid_cmd :: ls')
    result = mock_s3cmd.precmd(statement)
    
    output = mock_s3cmd.stdout.getvalue()
    assert 'cannot produce output' in output or result.raw == ''
    
    # Reset output
    mock_s3cmd.stdout = io.StringIO()
    
    # Test invalid consumer
    statement = mock_s3cmd.statement_parser.parse('drsview -o list :: invalid_cmd')
    result = mock_s3cmd.precmd(statement)
    
    output = mock_s3cmd.stdout.getvalue()
    assert 'does not know how to consume' in output or result.raw == ''


def test_ls_pipe_consumer(mock_s3cmd):
    """Test that ls is correctly listed as a pipe consumer."""
    assert 'ls' in mock_s3cmd.pipe_consumers


def test_drsview_pipe_producer(mock_s3cmd):
    """Test that drsview is correctly listed as a pipe producer."""
    assert 'drsview' in mock_s3cmd.pipe_producers
