# Asynchronous Programming with Trio 

**Setup**: To begin make sure you run: ```pip install trio``` in the terminal.  

## Task 1: Concurrent Execution

### Task 1a: Beginner Async Functions

Implement the missing code in the `timer` and `delayed_hello` functions to create a concurrent program.

- `timer()`:  Creates a function that prints how many seconds have passed every second and uses `trio.sleep(1)` to wait between prints
- `delayed_hello()` creates a function that waits for 2.1 seconds and then after the delay, prints "Hello, World!"

Copy the below task to test your code and include this function in your final code. 
```python
import trio 
async def task1a():
    """
    In this task, you will use the trio library to write two async functions. 
    Your task is to complete the timer and delayed_hello functions. 

    """
    print("Starting...")
    TIMEOUT = 2.5
    with trio.move_on_after(TIMEOUT): 
        async with trio.open_nursery() as nursery: 
            nursery.start_soon(timer) # implement the timer function 
            nursery.start_soon(delayed_hello) # implement the delayed hello function 
    print("Completed!")
    return 
```

**Expected Output**: 
```
Starting...
1 second has passed
2 seconds have passed
Hello, World!
Completed!
```

### Task 1b: Error Handling in Async Code

Implement error handling in an asynchronous context to fetch user data with simulated network delays and errors.

- `get_user_id(user_id: int)`: Returns a dictionary `{"id": user_id, "username": f"User {user_id}"}` if user_id is even and raises `ValueError(f"User {user_id} not found")` if user_id is odd
- `get_user_data(user_ids: list[int])`: Implements a helper function `_fetch_and_store` that uses a try/except block to call `get_user_id(user_id)` and stores and returns successful results and errors through a results dictionary. 

Copy the below task to test your code and include this function in your final code. 
```python
async def task1b(): 
    """
    In this task, you will implement error handling in using the trio library. In this test case, we create a list of 5 user IDs (mix of even and odd numbers). We call get_user_data() with this list
    Prints "Results:" followed by the results dictionary
    """
    user_ids = [1, 2, 3, 4, 5]
    results= await get_user_data(user_ids)
    print("Results:") 
    for user_id, result in results.items(): 
        print(f"User {user_id}: {result}")
```

**Expected Output**: Results can be in any order for this question.  
```
Results:
User 5: {'status': 'error', 'error': 'User 5 not found'}
User 4: {'status': 'success', 'data': {'id': 4, 'username': 'User 4'}}
User 3: {'status': 'error', 'error': 'User 3 not found'}
User 2: {'status': 'success', 'data': {'id': 2, 'username': 'User 2'}}
User 1: {'status': 'error', 'error': 'User 1 not found'}
```

## Task 2: Parallel File Downloads with Trio and httpx
In this task, you'll implement a solution to download multiple files concurrently using Python Trio. This is a common real-world scenario where async programming shines - when you need to perform multiple I/O-bound operations (like downloading files) in parallel. You will implement the following:

- ```download_file(url: str, client: httpx.AsyncClient, name: str, download_dir: str)```: This function downloads a single file asynchronously
- ```task2()```: This function will set up an async HTTP client and download multiple files in parallel using a trio nursery. Here is the starter code: 

```python 
import os
import trio
import httpx

async def task2(): 
    """Download multiple classic books in parallel using trio and httpx.
    
    This function will set up an async HTTP client and use trio to download multiple files concurrently
    """
    # Dictionary mapping book names to their download URLs
    FILES_TO_DOWNLOAD = {
        "War and Peace": "https://www.gutenberg.org/files/2600/2600-0.txt",
        "Pride and Prejudice": "https://www.gutenberg.org/cache/epub/1342/pg1342.txt",
        "The Adventures of Sherlock Holmes": "https://www.gutenberg.org/files/1661/1661-0.txt",
    }
    DOWNLOAD_DIR = "downloads"
    ### YOUR CODE STARTS HERE

```
**Expected Output**: 
```
(1) Downloading War and Peace...
(2) Downloading Pride and Prejudice...
(3) Downloading The Adventures of Sherlock Holmes...
Finished downloading Pride and Prejudice
Finished downloading The Adventures of Sherlock Holmes
Finished downloading War and Peace
```
You'll notice that files don't necessarily finish downloading in the order they started - this demonstrates the concurrent nature of async programming!

## Task 3: Asynchronous API Calls with Trio 

### Task 3a: 
In this part, you will implement an asynchronous function to fetch economic data from the World Bank API while controlling concurrency.
Your task is to implement: 
- ```get_json_from_url_with_semaphore(semaphore:trio.Semaphore, send_channel: trio.MemorySendChannel, url: str, client: httpx.AsyncClient)```: A function that uses a semaphore to control the number of concurrent requests (i.e. API Calls), fetches JSON data from a given URL and turns it into pandas DataFrame, and sends the processed DataFrame through a memory channel
- ```close_after_timeout(send_channel: trio.MemorySendChannel)```: A function that waits 3 seconds and then closes the memory channel. 
- ```task3a()```: The main task function that 
    1. Sets up memory channels for data flow
    2. Creates an HTTP client for making requests
    3. Uses a nursery to spawn multiple asynchronous tasks
    4. Controls concurrency with a semaphore
    5. Collects results from the channel after a timeout

Here is code to get you started: 
```python 
import trio
import httpx
import requests 
import pandas as pd 


async def task3a(): 
    all_countries_url = "https://api.worldbank.org/v2/country?format=json"

    response = requests.get(all_countries_url)
    all_countries = pd.DataFrame.from_dict(response.json()[1]).head(20) # gets the first 20 countries
    country_ids = all_countries['id']
    country_mapping = dict(zip(all_countries['id'], all_countries['name']))

    MAX_THREADS = 5
    NUM_RESULTS = len(country_ids)

    base_gdp_url = 'https://api.worldbank.org/v2/country/{country_str}/indicator/NY.GDP.MKTP.CD?date=1999:2019&format=json'

    ## Create memory channel for results 
    send_channel, receive_channel = trio.open_memory_channel(NUM_RESULTS)
    all_dfs = [] 
    ### YOUR CODE STARTS HERE

    ### YOUR CODE ENDS HERE
    final_df = pd.concat(all_dfs)

    for id in country_ids: 
        group = final_df[final_df["countryiso3code"]==id]
        if len(group) ==0 or len(group[group['date'].isin(['1999', '2019'])]) < 2: 
            # skip countries with missing data
            print(country_mapping[id], 'Missing data')
        else: 
            # print GDP growth of 20 countries
            GDP1 = int(group[group['date'] == '1999']['value'].iloc[0])
            GDP2 = int(group[group['date'] == '2019']['value'].iloc[0])
            print(country_mapping[id], f"GDP Growth: {(GDP2-GDP1)/GDP1*100:.2f}%")

```

### Task 3b: 
Building on Part 1, you'll now implement a more efficient producer-consumer pattern for data processing. Your task is to complete: 
- ```consume_data(receive_channel: trio.MemoryReceiveChannel, all_dfs: list)```: This function continuously receives data from a memory channel and appends each received DataFrame to a list
- ```task3b()```: This function 
    - creates nested nurseries for producers and consumers, 
    - starts a consumer task to process data as it becomes available, 
    - spawns multiple producer tasks to fetch data from URLs,
    - properly closes the send channel when all producers complete, and 
    - eliminates the need for timeout-based channel closing. 

Here is code to get you started: 
```python 
async def task3b(): 
    all_countries_url = "https://api.worldbank.org/v2/country?format=json"

    response = requests.get(all_countries_url)
    all_countries = pd.DataFrame.from_dict(response.json()[1]).head(20) 
    country_ids = all_countries['id']
    country_mapping = dict(zip(all_countries['id'], all_countries['name']))

    MAX_THREADS = 5
    NUM_RESULTS = 5 # we now limit the maximum size of the channel

    base_gdp_url = 'https://api.worldbank.org/v2/country/{country_str}/indicator/NY.GDP.MKTP.CD?date=1999:2019&format=json'

    ## Create memory channel for results 
    send_channel, receive_channel = trio.open_memory_channel(NUM_RESULTS)
    all_dfs = [] 
    ### YOUR CODE STARTS HERE
   
    ### YOUR CODE ENDS HERE
    final_df = pd.concat(all_dfs)

    for id in country_ids: 
        group = final_df[final_df["countryiso3code"]==id]
        if len(group) ==0 or len(group[group['date'].isin(['1999', '2019'])]) < 2: 
            # skip countries with missing data
            print(country_mapping[id], 'Missing data')
        else: 
            # print GDP growth of 20 countries
            GDP1 = int(group[group['date'] == '1999']['value'].iloc[0])
            GDP2 = int(group[group['date'] == '2019']['value'].iloc[0])
            print(country_mapping[id], f"GDP Growth: {(GDP2-GDP1)/GDP1*100:.2f}%")
```

**Expected Output** For both part 3a and 3b. Results may appear in different order 
```
Aruba GDP Growth: 97.10%
Africa Eastern and Southern GDP Growth: 280.41%
Afghanistan Missing data
Africa Missing data
Africa Western and Central GDP Growth: 492.60%
Angola GDP Growth: 1052.26%
Albania GDP Growth: 385.20%
Andorra GDP Growth: 154.39%
Arab World GDP Growth: 335.67%
United Arab Emirates GDP Growth: 394.98%
Argentina GDP Growth: 57.93%
Armenia GDP Growth: 637.98%
American Samoa Missing data
Antigua and Barbuda GDP Growth: 106.50%
Australia GDP Growth: 257.43%
Austria GDP Growth: 104.69%
Azerbaijan GDP Growth: 951.55%
Burundi GDP Growth: 218.85%
East Asia & Pacific (IBRD-only countries) Missing data
Europe & Central Asia (IBRD-only countries) Missing data
```


## Task 4: Trio Priority Queue

### Task 4a: Basic Priority Scheduler

In this first part, you will implement a basic priority-based task scheduler that can add tasks with different priority levels, execute tasks in order of priority and track task information and execution status. You will implement the class ```BasicPriorityScheduler``` with the following capabilities:
- Task management (adding, scheduling, and executing tasks)
- Priority queue organization (5 levels)
- Execution statistics 

Here are the basic components of the class you should implement. 
```python
    class BasicPriorityScheduler:
        # Required Methods:
        def __init__(self):
            self.log = [] 
            self.start_time = time.time() 
            # Initializes any counters/ dictionaries you need
            pass
            
        async def add_task(self, coroutine, priority, *args) -> int:
            # Add a coroutine with specified priority, return task ID
            pass
            
        async def run(self):
            # Execute tasks in priority order (1-5, highest to lowest)
            pass

        def print_statistics(self): 
            for row in self.log: 
                if row['action'].endswith("Level"): 
                    print(f"Time: {row['time']:.1f}s - {row['action']} {row['task_id']}")
                elif row['action'].endswith("Shutdown"): 
                    print(f"Time: {row['time']:.1f}s - {row['action']}")
                else: 
                    print(f"Time: {row['time']:.1f}s - Action: Task {row['task_id']} {row['action']}")

        def log_event(self, action, id): 
            current_time = time.time() - self.start_time 
            self.log.append({
                'time': current_time,
                'action': action, 
                'task_id': id
            })
```

You are also provided with helper functions: ```print_statistics``` and ```log_event``` to keep your implementation simple. 

Use the provided ```task4a()``` function to test your implementation. 
```python 
import trio
import time

async def task4a(): 
    """
    Test function for BasicPriorityScheduler
    """
    scheduler = BasicPriorityScheduler()
    
    # Define some test tasks
    async def high_priority_task(name):
        await trio.sleep(1)
        return f"Result from {name}"
    
    async def low_priority_task(name):
        await trio.sleep(2)
        return f"Result from {name}"

    # Add initial tasks
    task1_id = await scheduler.add_task(high_priority_task, 1, "Task1")
    task2_id = await scheduler.add_task(low_priority_task, 3, "Task2")
    task3_id = await scheduler.add_task(low_priority_task, 5, "Task3")
    
    # Start the scheduler
    async with trio.open_nursery() as nursery:
        nursery.start_soon(scheduler.run)
    
    # Print statistics
    scheduler.print_statistics()
``` 

**Expected Output**: 
```
Time: 0.0s - Action: Task 1 added
Time: 0.0s - Action: Task 2 added
Time: 0.0s - Action: Task 3 added
Time: 0.0s - Starting Priority Level 1
Time: 0.0s - Action: Task 1 started
Time: 1.0s - Action: Task 1 completed
Time: 1.0s - Finished Priority Level 1
Time: 1.0s - Starting Priority Level 2
Time: 1.0s - Finished Priority Level 2
Time: 1.0s - Starting Priority Level 3
Time: 1.0s - Action: Task 2 started
Time: 3.0s - Action: Task 2 completed
Time: 3.0s - Finished Priority Level 3
Time: 3.0s - Starting Priority Level 4
Time: 3.0s - Finished Priority Level 4
Time: 3.0s - Starting Priority Level 5
Time: 3.0s - Action: Task 3 started
Time: 5.0s - Action: Task 3 completed
Time: 5.0s - Finished Priority Level 5
```

### Part 4b: Advanced Priority Scheduler
In this part, you will create an ```AdvancedPriorityScheduler``` that adds dynamic task management while the scheduler is running, task cancellation, task priority rescheduling, shutdown. You will need ot implement: 
- ```cancel_task(self, task_id)```: Task cancellation with proper clean up 
- ```reschedule(self, task_id, new_priority```: Priority level changes for existing tasks 
- ```shutdown(self)```: Graceful shutdown of all running tasks


Use the provided ```task4b()``` function to test your implementation. 
```python 
import trio
import time

async def task4b(): 
    """
    Test function for AdvancedPriorityScheduler
    """
    scheduler = AdvancedPriorityScheduler()
    
    # Define some test tasks
    async def high_priority_task(name):
        await trio.sleep(1)
        return f"Result from {name}"
    
    async def low_priority_task(name):
        await trio.sleep(2)
        return f"Result from {name}"

    # Add initial tasks
    task1_id = await scheduler.add_task(high_priority_task, 1, "Task1")
    task2_id = await scheduler.add_task(low_priority_task, 3, "Task2")
    task3_id = await scheduler.add_task(low_priority_task, 5, "Task3")
    
    # Start the scheduler
    async with trio.open_nursery() as nursery:
        nursery.start_soon(scheduler.run)
        
        # Add more tasks while scheduler is running
        await trio.sleep(0.5)
        task4_id = await scheduler.add_task(high_priority_task, 2, "Task4")
        
        # Cancel a task
        await trio.sleep(0.5)
        await scheduler.cancel_task(task3_id)
        
        # Reschedule a task
        await trio.sleep(0.5)
        await scheduler.reschedule(task2_id, new_priority=1)
        
        # After 10 seconds, request scheduler shutdown
        task6_id = await scheduler.add_task(low_priority_task, 5, "Task5")
        await trio.sleep(6)
        await scheduler.shutdown()
    
    # Print statistics
    scheduler.print_statistics()
``` 

**Expected Output**
```
Time: 0.0s - Action: Task 1 added
Time: 0.0s - Action: Task 2 added
Time: 0.0s - Action: Task 3 added
Time: 0.0s - Starting Priority Level 1
Time: 0.0s - Action: Task 1 started
Time: 0.5s - Action: Task 4 added
Time: 1.0s - Action: Task 1 completed
Time: 1.0s - Finished Priority Level 1
Time: 1.0s - Starting Priority Level 2
Time: 1.0s - Action: Task 3 removed
Time: 1.0s - Action: Task 4 started
Time: 1.5s - Action: Task 2 rescheduled
Time: 1.5s - Action: Task 5 added
Time: 1.5s - Action: Task 2 started
Time: 2.0s - Action: Task 4 completed
Time: 3.5s - Action: Task 2 completed
Time: 3.5s - Finished Priority Level 2
Time: 3.5s - Starting Priority Level 3
Time: 3.5s - Finished Priority Level 3
Time: 3.5s - Starting Priority Level 4
Time: 3.5s - Finished Priority Level 4
Time: 3.5s - Starting Priority Level 5
Time: 3.5s - Action: Task 5 started
Time: 5.5s - Action: Task 5 completed
Time: 5.5s - Finished Priority Level 5
Time: 7.5s - Starting Shutdown
Time: 7.6s - Finished Shutdown
```