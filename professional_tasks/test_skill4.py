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
async def test_task1a_timing():
    """Test that task1a completes in the expected time."""
    with trio.move_on_after(3):
        start_time = trio.current_time()
        await solution_module.task1a()
        end_time = trio.current_time()
        
    elapsed_time = end_time - start_time
    # We expect task1 to take about 2.5 seconds (the TIMEOUT value)
    assert 2.4 <= elapsed_time <= 2.6, f"Expected task1 to take ~2.5 seconds, got {elapsed_time:.2f} seconds"

# Test get_user_id function
@pytest.mark.task1
@pytest.mark.trio
async def test_get_user_id_success():
    """Test get_user_id with even user_id (success case)"""

    result = await solution_module.get_user_id(2)
    assert result == {"id": 2, "username": "User 2"}

@pytest.mark.task1
@pytest.mark.trio
async def test_get_user_id_failure():
    """Test get_user_id with odd user_id (failure case)"""
    with pytest.raises(ValueError, match="User 1 not found"):
        await solution_module.get_user_id(1)

@pytest.mark.task1
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

@pytest.mark.task1
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

@pytest.mark.task1
@pytest.mark.trio
async def test_task1b_timing():
    """Test that task2 can be executed without errors"""
    # This is a basic test to ensure task1b runs without raising exception
    with trio.move_on_after(3):
        start_time = trio.current_time()
        await solution_module.task1b()
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
    assert elapsed_time <= 3.5, f"Expected task 3 to take less than 3 seconds, got {elapsed_time:.2f} seconds"

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
    print(elapsed_time)
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



@pytest.mark.task6
@pytest.mark.trio
async def test_add_task():
    """Test adding a task to the scheduler"""
    scheduler = solution_module.BasicPriorityScheduler()
    
    # Define a simple test coroutine
    async def test_coro(name):
        return f"Hello, {name}"
    
    # Add a task
    task_id = await scheduler.add_task(test_coro, 2, "World")
    
    # Check that the task was added correctly
    assert task_id == 1  # First task should have ID 1
    assert scheduler.task_counter == 2  # Counter should be incremented
    assert 1 in scheduler.id2priority
    assert scheduler.id2priority[1] == 2  # Priority 2
    assert 1 in scheduler.task_statuses
    assert scheduler.task_statuses[1] == 'pending'
    
    # Check the task in the priority queue
    assert 1 in scheduler.priority_queue[2]
    coro_wrapper, args = scheduler.priority_queue[2][1]
    assert args == ("World",)
    
    # Check the log
    assert any(entry['action'] == 'added' and entry['task_id'] == 1 for entry in scheduler.log)


# Test run method executes tasks in priority order
@pytest.mark.task6
@pytest.mark.trio
async def test_run_priority_order():
    """Test that tasks are executed in priority order"""
    scheduler = solution_module.BasicPriorityScheduler()
    execution_order = []
    
    # Define test tasks with different priorities
    async def test_task(name):
        execution_order.append(name)
        await trio.sleep(0.1)  # Small delay
        return f"Result: {name}"
    
    # Add tasks with different priorities
    await scheduler.add_task(test_task, 3, "Task3")  # Medium priority
    await scheduler.add_task(test_task, 1, "Task1")  # Highest priority
    await scheduler.add_task(test_task, 5, "Task5")  # Lowest priority
    await scheduler.add_task(test_task, 2, "Task1b") # Also highest priority
    with trio.move_on_after(3) as cancel_scope:
        # Run the scheduler
        await scheduler.run()

        # Check execution order in the log
        started_tasks = [entry['task_id'] for entry in scheduler.log if entry['action'] == 'started']
        expected_order = [2, 4, 1, 3]  # Based on the priorities: Task1, Task1b, Task3, Task5
        assert started_tasks == expected_order, f"Expected start order {expected_order}, got {started_tasks}"
    
    if cancel_scope.cancelled_caught: 
        pytest.fail("Test timed out")


# Test task status tracking
@pytest.mark.task6
@pytest.mark.trio
async def test_task_status_tracking():
    """Test that task statuses are properly tracked during execution"""
    scheduler = solution_module.BasicPriorityScheduler()
    
    # Define a simple test task
    async def test_task(name):
        await trio.sleep(0.1)  # Small delay
        return f"Result: {name}"
    
    # Add a task
    task_id = await scheduler.add_task(test_task, 1)
    
    # Check initial status
    assert scheduler.task_statuses[task_id] == 'pending'
    
    # Set up a background task to check the status while running
    status_during_run = None
    
    async def check_status():
        nonlocal status_during_run
        await trio.sleep(0.05)  # Wait a bit for the task to start
        status_during_run = scheduler.task_statuses[task_id]
    
    with trio.move_on_after(3) as cancel_scope:
        # Run both the scheduler and status checker
        async with trio.open_nursery() as nursery:
            nursery.start_soon(check_status)
            nursery.start_soon(scheduler.run)
        
        # Check status during and after execution
        assert status_during_run == 'running'
        assert scheduler.task_statuses[task_id] == 'completed'
    
    if cancel_scope.cancelled_caught: 
        pytest.fail("Test timed out")


# Integration test - full execution flow
@pytest.mark.task6
@pytest.mark.trio
async def test_full_execution_flow():
    """
    Integration test for the full scheduler workflow:
    1. Add tasks with different priorities
    2. Run the scheduler
    3. Verify execution order and task statuses
    """
    scheduler = solution_module.BasicPriorityScheduler()
    # Define some test tasks
    async def high_priority_task(name):
        await trio.sleep(0.5)
        return f"Result from {name}"
    
    async def low_priority_task(name):
        await trio.sleep(1.5)
        return f"Result from {name}"
    
    # Add tasks
    await scheduler.add_task(high_priority_task, 1, "HighPriority")
    await scheduler.add_task(low_priority_task, 3, "MediumPriority")
    await scheduler.add_task(low_priority_task, 5, "LowPriority")
    with trio.move_on_after(4) as cancel_scope:
        # Run the scheduler
        await scheduler.run()
        
        # Check all tasks are marked completed
        completed_tasks = scheduler.get_tasks_by_status('completed')
        assert len(completed_tasks) == 3
        
        # Verify no tasks are still pending or running
        assert len(scheduler.get_tasks_by_status('pending')) == 0
        assert len(scheduler.get_tasks_by_status('running')) == 0
        
        # Check log for correct sequence of priority levels
        priority_starts = [entry for entry in scheduler.log if entry['action'] == 'Starting Priority Level']
        priority_order = [entry['task_id'] for entry in priority_starts]
        assert priority_order == [1, 2, 3, 4, 5]
    
    

        # Check that each "Starting Priority Level" is followed by "Finishing Priority Level" before the next level
        current_priority = None
        for entry in scheduler.log:
            if entry['action'] == 'Starting Priority Level':
                if current_priority is not None:
                    # Ensure the previous priority level was finished
                    assert any(e['action'] == 'Finished Priority Level' and e['task_id'] == current_priority for e in scheduler.log), \
                        f"Priority level {current_priority} was not finished before starting {entry['task_id']}"
                current_priority = entry['task_id']
            elif entry['action'] == 'Finished Priority Level':
                assert entry['task_id'] == current_priority, \
                    f"Finished Priority Level {entry['task_id']} does not match current priority {current_priority}"
                current_priority = None
    if cancel_scope.cancelled_caught: 
            pytest.fail("Test timed out")

@pytest.mark.task7
@pytest.mark.trio
async def test_add_task():
    """Test adding a task to the scheduler"""
    scheduler = solution_module.AdvancedPriorityScheduler()
    
    # Define a simple test coroutine
    async def test_coro(name):
        return f"Hello, {name}"
    
    # Add a task
    task_id = await scheduler.add_task(test_coro, 2, "World")
    
    # Check that the task was added correctly
    assert task_id == 1  # First task should have ID 1
    assert scheduler.task_counter == 2  # Counter should be incremented
    assert 1 in scheduler.id2priority
    assert scheduler.id2priority[1] == 2  # Priority 2
    assert 1 in scheduler.task_statuses
    assert scheduler.task_statuses[1] == 'pending'
    
    # Check the task in the priority queue
    assert 1 in scheduler.priority_queue[2]
    coro_wrapper, args = scheduler.priority_queue[2][1]
    assert args == ("World",)
    
    # Check the log
    assert any(entry['action'] == 'added' and entry['task_id'] == 1 for entry in scheduler.log)

@pytest.mark.task7
@pytest.mark.trio
async def test_cancel_pending_task():
    """Test canceling a pending task"""
    scheduler = solution_module.AdvancedPriorityScheduler()
    
    # Define a test coroutine
    async def test_coro(name):
        await trio.sleep(1)
        return f"Hello, {name}"
    
    # Add a task
    task_id = await scheduler.add_task(test_coro, 2, "World")
    
    # Cancel the task before it starts running
    await scheduler.cancel_task(task_id)
    
    # Check task status is updated
    assert scheduler.task_statuses[task_id] == 'cancelled'
    
    # Check task is removed from priority queue
    assert task_id not in scheduler.priority_queue[2]
    
    # Check the log
    assert any(entry['action'] == 'removed' and entry['task_id'] == task_id for entry in scheduler.log)

@pytest.mark.task7
@pytest.mark.trio
async def test_cancel_running_task():
    """Test canceling a running task"""
    scheduler = solution_module.AdvancedPriorityScheduler()
    
    # We'll need to simulate a running task with a cancel scope
    task_id = 1
    scheduler.task_counter = 2
    scheduler.id2priority[task_id] = 1
    scheduler.task_statuses[task_id] = 'running'
    
    # Create a mock cancel scope
    mock_cancel_scope = MagicMock()
    scheduler.running_tasks[task_id] = mock_cancel_scope
    
    # Cancel the "running" task
    await scheduler.cancel_task(task_id)
    
    # Check the cancel method was called on the scope
    mock_cancel_scope.cancel.assert_called_once()
    
    # Check task status is updated
    assert scheduler.task_statuses[task_id] == 'cancelled'
    
    # Check the log
    assert any(entry['action'] == 'stopped' and entry['task_id'] == task_id for entry in scheduler.log)

@pytest.mark.task7
@pytest.mark.trio
async def test_reschedule_to_active_priority():
    """Test rescheduling a task to a priority that's currently running"""
    scheduler = solution_module.AdvancedPriorityScheduler()
    
    # Define a test coroutine
    async def test_coro(name):
        await trio.sleep(0.1)
        return f"Hello, {name}"
    
    # Add a task
    task_id = await scheduler.add_task(test_coro, 3, "World")
    
    # Set up a mock nursery
    mock_nursery = MagicMock()
    scheduler.nursery = mock_nursery
    scheduler.current_priority = 1  # Simulate running priority 1
    
    # Reschedule from priority 3 to priority 1
    await scheduler.reschedule(task_id, 1)
    
    # Check that task was started in the nursery
    assert mock_nursery.start_soon.called
    
    # Check priority is updated
    assert scheduler.id2priority[task_id] == 1
    assert task_id in scheduler.priority_queue[1]

@pytest.mark.task7
@pytest.mark.trio
async def test_shutdown_handles_pending_tasks():
    """Test that shutdown properly handles pending tasks"""
    scheduler = solution_module.AdvancedPriorityScheduler()
    
    # Define a test coroutine
    async def test_coro(name):
        await trio.sleep(2)
        return "Result"
    
    # Add some tasks but don't run them (they'll stay pending)
    task1_id = await scheduler.add_task(test_coro, 5, "World")
    task2_id = await scheduler.add_task(test_coro, 5, "World")
    
    # Change task statuses to ensure they're pending
    scheduler.task_statuses[task1_id] = 'pending'
    scheduler.task_statuses[task2_id] = 'pending'
    
    # Call shutdown
    await scheduler.shutdown()
    
    # Check for cancelled_pending events in the log
    pending_cancellations = [entry for entry in scheduler.log if entry['action'] == 'cancelled_pending']
    assert len(pending_cancellations) == 2


# Integration test - full execution flow
@pytest.mark.task7
@pytest.mark.trio
async def test_add_task_while_running():
    """Test adding a task while the scheduler is already running"""
    scheduler = solution_module.AdvancedPriorityScheduler()
    results = {}
    
    # Define test tasks
    async def long_task(name):
        await trio.sleep(0.3)
        results['long'] = "Long task finished"
        return results['long']
    
    async def add_new_task():
        await trio.sleep(0.1)  # Wait a bit before adding new task
        # Add a higher priority task while scheduler is running
        task_id = await scheduler.add_task(short_task, 1, "short_task")
        results['added_id'] = task_id
    
    async def short_task(name):
        await trio.sleep(0.1)
        results['short'] = "Short task finished"
        return results['short']
    
    with trio.move_on_after(3) as cancel_scope:
        # Add initial task (long running, lower priority)
        await scheduler.add_task(long_task, 3, "long_task")

        # Start the scheduler and add new task while it's running
        async with trio.open_nursery() as nursery:
            nursery.start_soon(scheduler.run)
            nursery.start_soon(add_new_task)
        
        scheduler.print_statistics()
        # Verify both tasks completed and the new task was added successfully
        new_task_start_time = [r['time'] for r in scheduler.log if r['action'] == 'started' and r['task_id']==2][0]
        old_task_finish_time = [r['time'] for r in scheduler.log if r['action'] == 'completed' and r['task_id']==1][0]
        assert new_task_start_time < old_task_finish_time
        assert 'long' in results
        assert 'short' in results
        assert 'added_id' in results

    if cancel_scope.cancelled_caught: 
        pytest.fail("Test timed out")

if __name__ == "__main__":
    pytest.main(["-v", __file__])