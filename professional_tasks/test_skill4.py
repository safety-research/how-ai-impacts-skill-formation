import pytest
import trio
import sys
import os
import pandas as pd 
from io import StringIO
from contextlib import redirect_stdout
import shutil
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from conftest import solution_module


### pytest test_skill4.py --solution-file=student_solution.py -m task1 

@pytest.mark.task1
@pytest.mark.trio
async def test_task1_output():
    """Test that task1 produces the expected output."""
    # Capture stdout
    with trio.move_on_after(3) as cancel_scope:
        captured_output = StringIO()
        with redirect_stdout(captured_output):
            await solution_module.task1()
        
        # Get the output as a string
        output = captured_output.getvalue().strip()
        expected_output = "Starting...\n1 second has passed\n2 seconds have passed\nHello, World!\nCompleted!"
        
        # Compare the actual output with the expected output
        assert output == expected_output, f"Expected:\n{expected_output}\n\nGot:\n{output}"
    
    if cancel_scope.cancelled_caught: 
        pytest.fail("Test timed out")

@pytest.mark.task1
@pytest.mark.trio
async def test_timer_output():
    """Test the timer function in isolation."""
    captured_output = StringIO()
    with redirect_stdout(captured_output):
        with trio.move_on_after(2.5):
            await solution_module.timer()
    
    output = captured_output.getvalue().strip()
    expected_lines = [
        "1 second has passed",
        "2 seconds have passed"
    ]
    
    # Check if all expected lines are in the output
    for line in expected_lines:
        assert line in output, f"Expected output to contain '{line}'"
    
    # Check that we don't have more output than expected
    output_lines = output.split('\n')
    assert len(output_lines) == 2, f"Expected 2 lines of output, got {len(output_lines)}"

@pytest.mark.task1
@pytest.mark.trio
async def test_delayed_hello():
    """Test the delayed_hello function in isolation."""
    captured_output = StringIO()
    start_time = trio.current_time()
    with trio.move_on_after(3):
        
        with redirect_stdout(captured_output):
            await solution_module.delayed_hello()
        
        end_time = trio.current_time()
    elapsed_time = end_time - start_time
    
    # Check the output
    output = captured_output.getvalue().strip()
    assert output == "Hello, World!", f"Expected 'Hello, World!', got '{output}'"
    
    # Check the timing (should be roughly 2 seconds, with some tolerance)
    assert 2.0 <= elapsed_time <= 2.2, f"Expected delay of ~2 seconds, got {elapsed_time:.2f} seconds"

@pytest.mark.task1
@pytest.mark.trio
async def test_task1_timing():
    """Test that task1 completes in the expected time."""
    with trio.move_on_after(3):
        start_time = trio.current_time()
        await solution_module.task1()
        end_time = trio.current_time()
        
    elapsed_time = end_time - start_time
    # We expect task1 to take about 2.5 seconds (the TIMEOUT value)
    assert 2.4 <= elapsed_time <= 2.6, f"Expected task1 to take ~2.5 seconds, got {elapsed_time:.2f} seconds"


# Test get_user_id function
@pytest.mark.task2
@pytest.mark.trio
async def test_get_user_id_success():
    """Test get_user_id with even user_id (success case)"""

    result = await solution_module.get_user_id(2)
    assert result == {"id": 2, "username": "User 2"}

@pytest.mark.task2
@pytest.mark.trio
async def test_get_user_id_failure():
    """Test get_user_id with odd user_id (failure case)"""
    with pytest.raises(ValueError, match="User 1 not found"):
        await solution_module.get_user_id(1)

@pytest.mark.task2
@pytest.mark.trio
async def test_get_user_data_all_valid():
    """Test get_user_data with all valid (even) user IDs"""
    with trio.move_on_after(3) as cancel_scope:
        user_ids = [2, 4, 6, 8, 10]
        results = await solution_module.get_user_data(user_ids)
        
        # Check all results are successful
        for user_id in user_ids:
            assert results[user_id]["status"] == "success"
            assert results[user_id]["data"] == {"id": user_id, "username": f"User {user_id}"}
    
    if cancel_scope.cancelled_caught: 
        pytest.fail("Test timed out")

@pytest.mark.task2
@pytest.mark.trio
async def test_get_user_data_all_invalid():
    """Test get_user_data with all invalid (odd) user IDs"""
    with trio.move_on_after(3) as cancel_scope:
        user_ids = [1, 3, 5, 7, 9]
        results = await solution_module.get_user_data(user_ids)
        
        # Check all results are errors
        for user_id in user_ids:
            assert results[user_id]["status"] == "error"
            assert f"User {user_id} not found" in results[user_id]["error"]
    if cancel_scope.cancelled_caught: 
        pytest.fail("Test timed out")

# Test task2 function (optional, as it's mainly for demonstration)
@pytest.mark.task2
@pytest.mark.trio
async def test_task2_timing():
    """Test that task2 can be executed without errors"""
    # This is a basic test to ensure task2 runs without raising exception
    with trio.move_on_after(3):
        start_time = trio.current_time()
        await solution_module.task2()
    end_time = trio.current_time()
    
    elapsed_time = end_time - start_time
    # We expect task1 to take about 2.5 seconds (the TIMEOUT value)
    assert elapsed_time <= 2, f"Expected task2 to take ~2.5 seconds, got {elapsed_time:.2f} seconds"

@pytest.mark.task3
@pytest.mark.trio
async def test_task3_execution():
    """
    Test that task3 can be executed successfully.
    
    This test:
    1. Creates a temporary download directory
    2. Runs task3
    3. Checks that files are downloaded
    4. Cleans up the download directory
    """
    # Define the download directory
    download_dir = "downloads"
    with trio.move_on_after(4) as cancel_scope:
        try:
            # Run task3
            await solution_module.task3()
            
            # Check that files were downloaded
            assert os.path.exists(download_dir), "Download directory was not created"
            
            # Check that files exist
            downloaded_files = os.listdir(download_dir)
            assert len(downloaded_files) == 3, "Unexpected number of downloaded files"
            
            # Verify file extensions
            assert all(file.endswith('.txt') for file in downloaded_files), "Not all files are .txt"
            
            # Verify file names match expected books
            expected_books = [
                "War and Peace.txt",
                "Pride and Prejudice.txt",
                "The Adventures of Sherlock Holmes.txt"
            ]
            assert set(downloaded_files) == set(expected_books), "Unexpected files downloaded"
        
        finally:
            # Clean up: remove the download directory after the test
            if os.path.exists(download_dir):
                shutil.rmtree(download_dir)
    
    if cancel_scope.cancelled_caught: 
        pytest.fail("Test timed out")

# Test task3 function
@pytest.mark.task3
@pytest.mark.trio
async def test_task3_timing():
    """Test that task3 can be executed under 3 seconds"""
    # This is a basic test to ensure task2 runs without raising exception
    with trio.move_on_after(3):
        start_time = trio.current_time()
        await solution_module.task3()
    end_time = trio.current_time()
    
    elapsed_time = end_time - start_time
    # We expect task1 to take about 2.5 seconds (the TIMEOUT value)
    assert elapsed_time <= 3, f"Expected task 3 to take less than 3 seconds, got {elapsed_time:.2f} seconds"

@pytest.mark.task4
@pytest.mark.trio
async def test_get_json_from_url_with_semaphore():
    """Test the get_json_from_url_with_semaphore function with mocked responses.
    
    Note: We use MagicMock for response.json() because it's a regular method,
    not a coroutine. Only the client.get() is an async function.
    """
    # Create mocks
    semaphore = trio.Semaphore(1)
    send_channel = AsyncMock()
    url = "https://api.worldbank.org/v2/country/USA/indicator/NY.GDP.MKTP.CD?date=1999:2019&format=json"
    
    # Mock response data
    mock_response_data = [
        {"page": 1, "pages": 1, "per_page": 50, "total": 1},
        [
            {
                "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
                "country": {"id": "USA", "value": "United States"},
                "countryiso3code": "USA",
                "date": "2019",
                "value": 21433225000000,
                "unit": "",
                "obs_status": "",
                "decimal": 0
            },
            {
                "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
                "country": {"id": "USA", "value": "United States"},
                "countryiso3code": "USA",
                "date": "2018",
                "value": 20611861000000,
                "unit": "",
                "obs_status": "",
                "decimal": 0
            }
        ]
    ]
    
    # Create a mock client
    mock_client = AsyncMock()
    mock_response = MagicMock()  # Use MagicMock, not AsyncMock for response
    mock_response.json.return_value = mock_response_data
    mock_client.get.return_value = mock_response  # get() is async, but json() is not
    
    with trio.move_on_after(3) as cancel_scope:
        # Call the function
        await solution_module.get_json_from_url_with_semaphore(semaphore, send_channel, url, mock_client)
    
    # Assert client.get was called with the correct URL
    mock_client.get.assert_called_once_with(url)
    
    # Assert the send_channel.send was called with the correct DataFrame
    expected_df = pd.DataFrame.from_dict(mock_response_data[1]).dropna()[['countryiso3code', 'date', 'value']]
    # We can't directly compare DataFrames in the assertion, so check if it was called
    assert send_channel.send.called
    
    # Verify semaphore was used correctly
    assert semaphore._value == 1  # Semaphore should be released after use
    
    if cancel_scope.cancelled_caught: 
        pytest.fail("Test timed out")

@pytest.mark.task4
@pytest.mark.trio
async def test_task4_integration():
    """Integration test for task4 with mocked HTTP responses."""
    # Mock the requests.get call to get country data
    mock_countries_data = [
        {"page": 1, "pages": 1, "per_page": 50, "total": 3},
        [
            {"id": "USA", "name": "United States"},
            {"id": "CAN", "name": "Canada"},
            {"id": "MEX", "name": "Mexico"}
        ]
    ]
    
    # Mock country GDP data
    mock_gdp_data = {
        "USA": [
            {"page": 1, "pages": 1, "per_page": 50, "total": 2},
            [
                {"countryiso3code": "USA", "date": "2019", "value": 21433225000000},
                {"countryiso3code": "USA", "date": "2018", "value": 20611861000000}
            ]
        ],
        "CAN": [
            {"page": 1, "pages": 1, "per_page": 50, "total": 2},
            [
                {"countryiso3code": "CAN", "date": "2019", "value": 1736426000000},
                {"countryiso3code": "CAN", "date": "2018", "value": 1725399000000}
            ]
        ],
        "MEX": [
            {"page": 1, "pages": 1, "per_page": 50, "total": 2},
            [
                {"countryiso3code": "MEX", "date": "2019", "value": 1269432000000},
                {"countryiso3code": "MEX", "date": "2018", "value": 1222053000000}
            ]
        ]
    }
    
    # Patch the external functions
    with patch('requests.get') as mock_requests_get, \
         patch('httpx.AsyncClient') as mock_async_client_class:
        
        # Setup mock for countries request
        mock_countries_response = MagicMock()
        mock_countries_response.json.return_value = mock_countries_data
        mock_requests_get.return_value = mock_countries_response
        
        # Setup mock for httpx.AsyncClient
        mock_client = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client
        
        # Configure the mock client to return different responses for different URLs
        async def mock_get(url):
            # Extract the country code from the URL
            import re
            country_match = re.search(r'country/([A-Z]{3})', url)
            if country_match:
                country_code = country_match.group(1)
                if country_code in mock_gdp_data:
                    mock_response = MagicMock()  # Use MagicMock for response
                    mock_response.json.return_value = mock_gdp_data[country_code]
                    return mock_response
            # Default empty response
            mock_response = MagicMock()  # Use MagicMock for response
            mock_response.json.return_value = [{"page": 1}, []]
            return mock_response
            
        mock_client.get.side_effect = mock_get
        with trio.move_on_after(5) as cancel_scope:
        # Call task4
            result = await solution_module.task4()
        if cancel_scope.cancelled_caught: 
            pytest.fail("Test timed out")
        # Assertions
        # - Verify the number of HTTP requests made (1 for each country)
        assert mock_client.get.call_count == 3
 
@pytest.mark.task4
@pytest.mark.trio
async def test_task4_timing():
    """Test that task4 can be executed under 4 seconds"""
    # This is a basic test to ensure task4 runs under 4 seconds
    start_time = trio.current_time()
    with trio.move_on_after(4):
        await solution_module.task4()
    end_time = trio.current_time()
    
    elapsed_time = end_time - start_time
    # We expect task1 to take about 2.5 seconds (the TIMEOUT value)
    assert elapsed_time <= 4, f"Expected task 4 to take less than 4 seconds, got {elapsed_time:.2f} seconds"


@pytest.mark.task5
@pytest.mark.trio
async def test_task5_timing():
    """Test that task5 can be executed under 4 seconds"""
    # This is a basic test to ensure task4 runs under 4 seconds
    with trio.move_on_after(3):
        start_time = trio.current_time()
        await solution_module.task5()
    end_time = trio.current_time()
    
    elapsed_time = end_time - start_time
    # We expect task1 to take about 2.5 seconds (the TIMEOUT value)
    assert elapsed_time <= 2, f"Expected task 5 to take less than 2 seconds, got {elapsed_time:.2f} seconds"

@pytest.mark.task5
@pytest.mark.trio
async def test_consume_data():
    """Test the consume_data function with mock data."""
    # Create a channel
    send_channel, receive_channel = trio.open_memory_channel(5)
    
    # Create sample dataframes to send
    dfs = [
        pd.DataFrame({
            'countryiso3code': ['USA', 'USA'],
            'date': ['2019', '2018'],
            'value': [21433225000000, 20611861000000]
        }),
        pd.DataFrame({
            'countryiso3code': ['CAN', 'CAN'],
            'date': ['2019', '2018'],
            'value': [1736426000000, 1725399000000]
        }),
        pd.DataFrame({
            'countryiso3code': ['MEX', 'MEX'],
            'date': ['2019', '2018'],
            'value': [1269432000000, 1222053000000]
        })
    ]
    
    # List to collect results
    all_dfs = []
    with trio.move_on_after(3) as cancel_scope:
        # Create nursery to run both sender and consumer
        async with trio.open_nursery() as nursery:
            # Start consumer
            nursery.start_soon(solution_module.consume_data, receive_channel, all_dfs)
            
            # Send data
            for df in dfs:
                await send_channel.send(df)
                # Small delay to ensure processing
                await trio.sleep(0.01)
            
            # Close channel to signal end of data
            send_channel.close()
    
    if cancel_scope.cancelled_caught: 
        pytest.fail("Test timed out")
    # Verify all dataframes were collected
    assert len(all_dfs) == len(dfs)
    
    # Verify content matches
    for i, df in enumerate(dfs):
        assert df.to_string() == all_dfs[i].to_string()

if __name__ == "__main__":
    pytest.main(["-v", __file__])