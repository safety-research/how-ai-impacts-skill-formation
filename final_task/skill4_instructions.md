# Asynchronous Programming with Trio 



## Task 1: Concurrent Execution
**Setup**: To begin make sure you run: ```pip install trio``` in the terminal.  
### Introduction to Trio

Trio is a Python library designed for asynchronous programming. It provides a structured and easy-to-use approach to handling concurrency. Trio is particularly known for its focus on simplicity and correctness, making it a great choice for developers who want to write reliable asynchronous code without getting bogged down by the complexities often associated with concurrency.

One of the core features of Trio is its use of "nurseries", which allow you to manage multiple asynchronous tasks concurrently. This structured concurrency model ensures that all tasks are properly managed and that any errors are handled gracefully.

For example, consider the following usage of a nursery in Trio:
```python
async def parent():
    print("parent: started!")
    async with trio.open_nursery() as nursery:
        print("parent: spawning child1...")
        nursery.start_soon(child1)

        print("parent: spawning child2...")
        nursery.start_soon(child2)

        print("parent: waiting for children to finish...")
        # -- we exit the nursery block here --
    print("parent: all done!")
trio.run(parent)
```
The code above demonstrates handling multiple asynchronous tasks concurrently using Trio's structured concurrency model. It utilizes `trio.open_nursery()` to create an asynchronous context, and `nursery.start_soon(...)` to initiate functions that run asynchronously. The context is maintained until all functions within it have completed execution.

#### Trio's `sleep` Function

In asynchronous programming, it's common to introduce delays or pauses in the execution of tasks. Trio provides the `trio.sleep()` function to achieve this. Unlike the traditional `time.sleep()` function, which blocks the entire thread, `trio.sleep()` is non-blocking and allows other tasks to run while waiting.

The `trio.sleep()` function takes a single argument, the number of seconds to sleep, and is used with the `await` keyword. This allows the event loop to continue running other tasks during the sleep period, making it an essential tool for writing efficient asynchronous code.

For example, using `await trio.sleep(1)` will pause the current task for 1 second, allowing other tasks to proceed during this time. This is particularly useful in scenarios where you need to wait for a certain condition or simply introduce a delay without halting the entire program.

### Task 1: Beginner Async Functions

Implement the missing code in the `timer`, `delayed_hello`, and `task1` functions to create a concurrent program.

- `timer`:  This function prints how many seconds have passed every second and uses `trio.sleep` to wait between prints. This function should never return and always keep a count of seconds. 
- `delayed_hello`: This function waits for 2.1 seconds and then after the delay, prints "Hello, World!"
- `task1`: This function starts a nursery context and calls the `timer` and then the `delayed_hello` function.  

Once you've completed these these three functions, you can compare your code to the expected output. For this warm-up task none of the functions return any values, they simply print statements. Make sure you run: ```pip install trio``` in the terminal before you test out your trio code. 

**Expected Output**: 
```
Starting...
1s 
2s
Hello, World!
Completed!
```

## Task 2: Error Handling in Async Code

**Setup**: To begin make sure you run: ```pip install trio``` in the terminal.  

When using async libraries such as Trio, proper error handling is crucial to ensure that if one task fails, the other tasks can continue running independently. In asynchronous programming, multiple tasks often run concurrently, and an unhandled exception in one task can potentially cause the entire group of tasks to fail or terminate early if not managed correctly. To prevent this, you can use try/except blocks inside each async task. This way, you can catch and handle exceptions locally, record the error, and allow the rest of the tasks to continue running. This approach leads to more robust and fault-tolerant async programs.

In this task, you will practice error handling in async functions by implementing the following:
- `get_user_data`: This function should implement a helper function `_fetch_and_store` that uses a try/except block to call `get_user_id(user_id)`. If the call is successful, it stores the result in a results dictionary; if an exception occurs, it stores the string `'error'` for that user ID. The function should return the results dictionary. For example:
  - `get_user_data([2, 3, 4])` returns `{2: 'User-2', 3: 'error', 4: 'User-4'}`

Here is an example of how `get_user_data` will be called: 
```python
async def task2(): 
    user_ids = [1, 2, 3, 4, 5]
    results= await get_user_data(user_ids)
    print("Results:") 
    for user_id, result in results.items(): 
        print(f"User {user_id}: {result}")
```

**Expected Output**: Results can be in any order for this question.  
```
Results:
User 5: 'error'
User 4: 'User-4'
User 3: 'error'
User 2: 'User-2'
User 1: 'error'
```

**Hint:** If you encouter a `Execution time limit exceeded` error, you might not be fetching user ids asynchronously. 

## Task 3: Parallel File Downloads with Trio and httpx
**Setup**: To begin make sure you run: ```pip install trio``` in the terminal.  

In this task, you'll implement a solution to download multiple files concurrently using Python Trio. This is a common real-world scenario where async programming shines - when you need to perform multiple I/O-bound operations (like downloading files) in parallel. 

### httpx: a library with support for asynchronous web reqests
httpx is a powerful HTTP client library for Python that supports both synchronous and asynchronous requests. The `httpx.Client()` class provides a convenient way to manage HTTP connections efficiently, allowing you to make multiple requests while reusing the same underlying connection pool. This is especially useful for downloading multiple files or making repeated API calls. Here is a link to the documentation: [HTTPX Async](https://www.python-httpx.org/async/). 

You will implement the following:

- ```download_and_save_text```: This function downloads the content from a single url asynchronously. 
- ```task3```: This function will set up an async HTTP client and download multiple files in parallel using a trio nursery. You can use `httpx.Client()` to pass a client to the `dowload_and_save_text` function. 

**Expected Output**: 
```
Downloading War and Peace...
Downloading Pride and Prejudice...
Downloading The Adventures of Sherlock Holmes...
Finished downloading Pride and Prejudice
Finished downloading The Adventures of Sherlock Holmes
Finished downloading War and Peace
```
You'll notice that files don't necessarily finish downloading in the order they started - this demonstrates the concurrent nature of async programming!

## Task 4: Asynchronous API Calls with Trio 

### Task 4a: 
In this part, you will implement an asynchronous functions to fetch economic data from the World Bank API while controlling concurrency.

**Semaphores**
A **semaphore** is a tool for limiting how many tasks run at the same time. When calling APIs, using a semaphore helps prevent sending too many requests in parallel, which can avoid hitting rate limits or overloading the server.

**Example with Trio:**
```python 
MAX_THREADS = 2
semaphore = trio.Semaphore(MAX_THREADS)

async def some_function(i, semaphore):
    async with semaphore:
        # Do the work here
        print(f"Task {i} running")
        await trio.sleep(1)

async with trio.open_nursery() as nursery:
    for i in range(100):
        nursery.start_soon(some_function, i, semaphore)
```
In this code snippet, the semaphore ensures that only 2 threads are running at a time even though 100 tasks are started in the nursery. The function is described in detail here: [Trio Semaphore](https://trio.readthedocs.io/en/stable/reference-core.html#trio.Semaphore). 

**Memory Channels**

A **memory channel** in Trio is a way for tasks to communicate safely and efficiently between producers (which send data) and consumers (which receive data). Think of it as a thread-safe queue for async code. You create a channel with `trio.open_memory_channel(max_buffer_size)`, which returns a pair: a `send_channel` and a `receive_channel`. Producers use `await send_channel.send(item)` to put data into the channel, and consumers use `async for item in receive_channel:` to receive data as it arrives. When the producer is done sending, it should call `send_channel.close()` to signal to consumers that no more data will be sent. This pattern is especially useful for coordinating work between multiple concurrent tasks, such as downloading data and processing it as it becomes available. These functions are described in more detail here: [Trio Memory Channel](https://trio.readthedocs.io/en/stable/reference-core.html#trio.open_memory_channel)


Your task is to implement: 
- `get_json_from_url_with_semaphore`: A function that uses a semaphore to control the number of concurrent requests (i.e. API Calls), fetches JSON data from a given URL and turns it into pandas DataFrame, and sends the processed DataFrame through a memory channel
- `close_after_timeout`: A function that waits 3 seconds and then closes the memory channel. 
- `task4a`: The main task function that 
    1. Sets up memory channels for data flow
    2. Creates an HTTP client for making requests
    3. Uses a nursery to spawn multiple asynchronous tasks
    4. Controls concurrency with a semaphore
    5. Collects results from the channel after a timeout

### Task 4b: 
Building on Part 4a, you'll now implement a more efficient producer-consumer pattern for data processing. Your task is to complete: 
- ```consume_data```: This function continuously receives data from a memory channel and appends each received DataFrame to a list
- ```task4b```: This function 
    - creates nested nurseries for producers and consumers, 
    - starts a consumer task to process data as it becomes available, 
    - spawns multiple producer tasks to fetch data from URLs,
    - properly closes the send channel when all producers complete, and 
    - eliminates the need for timeout-based channel closing. 

**Expected Output** For both part 4a and 4b. Results may appear in different order 
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

## Task 5: Trio Priority Queue

### Task 5a: Basic Priority Scheduler

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

Use the provided ```task5a()``` function to test your implementation. 
```python 
import trio
import time

async def task5a(): 
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

### Part 5b: Advanced Priority Scheduler
In this part, you will create an ```AdvancedPriorityScheduler``` that adds dynamic task management while the scheduler is running, task cancellation, task priority rescheduling, shutdown. You will need ot implement: 
- ```cancel_task(self, task_id)```: Task cancellation with proper clean up 
- ```reschedule(self, task_id, new_priority```: Priority level changes for existing tasks 
- ```shutdown(self)```: Graceful shutdown of all running tasks


Use the provided ```task5b()``` function to test your implementation. 
```python 
import trio
import time

async def task5b(): 
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