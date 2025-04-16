import trio
import time
import httpx
import os
import requests
import pandas as pd

async def timer(): 
    """
    Implement a timer function that prints how many seconds have passed every second
    """
    ### YOUR CODE STARTS HERE
    i = 1 
    while True: 
        await trio.sleep(1)
        if i ==1: 
            print(f"{i} second has passed")
        else: 
            print(f"{i} seconds have passed")
        i+=1 
    ### YOUR CODE ENDS HERE

async def delayed_hello(): 
    """
    Implement a delayed hello function which waits for 2.1 seconds before printing "Hello World"
    """
    ### YOUR CODE STARTS HERE
    await trio.sleep(2.1)
    print("Hello, World!")
    ### YOUR CODE ENDS HERE

async def task1():
    """
    In this task, you will use the trio library to write two async functions. 
    Your task is to complete the timer and delayed_hello functions. 

    Expected Output: 
    
    Starting...
    1 second has passed
    2 seconds have passed
    Hello, World!
    Completed!
    
    """
    print("Starting...")
    TIMEOUT = 2.5
    with trio.move_on_after(TIMEOUT): 
        async with trio.open_nursery() as nursery: 
            nursery.start_soon(timer) # implement the timer function 
            nursery.start_soon(delayed_hello) # implement the delayed hello function 
    print("Completed!")
    return 

async def get_user_id(user_id: int):
    """
    Takes a user_id (integer) as a parameter
    Prints f"Fetching user {user_id}..."
    Uses trio.sleep(1) to simulate network delay
    Randomly succeeds or fails:

    If user_id is even, return a dictionary {"id": user_id, "username": f"User {user_id}"}
    If user_id is odd, raise an exception ValueError(f"User {user_id} not found")
    """
    ### YOUR CODE STARTS HERE
    await trio.sleep(1)
    if user_id % 2 == 0: 
        return {"id": user_id, "username": f"User {user_id}"}
    else: 
        raise ValueError(f"User {user_id} not found")
    ### YOUR CODE ENDS HERE

async def get_user_data(user_ids: list[int]):
    """
    1. Takes a list of user_ids as a parameter
    2. Creates an empty results dictionary 
    3. implements a helper function _fetch_and_store that: 
        - takes a user_id as a parameter
        - uses a try/except block to call get_user_id(user_id)
        - stores the result in the results dictionary
        - if an exception is raised, it stores the error in the results dictionary
    4. uses trio.open_nursery() to run _fetch_and_store for each user_id in parallel
    """
    
    results = {}
    
    async def _fetch_and_store(user_id): 
        ### YOUR CODE STARTS HERE
        try: 
            result = await get_user_id(user_id)
            results[user_id] = {"status": "success", "data": result}
        except ValueError as e: 
            results[user_id] = {"status": "error", "error": str(e)}
        ### YOUR CODE ENDS HERE
    
    ### YOUR CODE STARTS HERE
    async with trio.open_nursery() as nursery: 
        for user_id in user_ids: 
            nursery.start_soon(_fetch_and_store, user_id)
    
    return results
    ### YOUR CODE ENDS HERE 

async def task2(): 
    """
    In this task, you will implement error handling in using the trio library. 
    Import the asyncio and random libraries

    In this function, we create a list of 5 user IDs (mix of even and odd numbers)
    Calls get_user_data() with this list
    Prints "Results:" followed by the results dictionary
    Prints "Errors:" followed by the errors list

    Expected Output: 
    Results:
    User 5: {'status': 'error', 'error': 'User 5 not found'}
    User 4: {'status': 'success', 'data': {'id': 4, 'username': 'User 4'}}
    User 3: {'status': 'error', 'error': 'User 3 not found'}
    User 2: {'status': 'success', 'data': {'id': 2, 'username': 'User 2'}}
    User 1: {'status': 'error', 'error': 'User 1 not found'}
    """
    user_ids = [1, 2, 3, 4, 5]
    results= await get_user_data(user_ids)
    print("Results:") 
    for user_id, result in results.items(): 
        print(f"User {user_id}: {result}")


async def download_file(url: str, client: httpx.AsyncClient, name: str, download_dir: str):
    """Implement an async function for downloading a file from an url.
    This function takes in a httpx.AsyncClient object which you can used to make the download request directly. 
    The function should: 
    1. download the file from the url using client.get 
    2. save the file to the download_dir directory as .txt tiles
    """
    ### YOUR CODE STARTS HERE
    response = await client.get(url)
    with open(os.path.join(download_dir, f'{name}.txt'), "wb") as f:
        f.write(response.content)
    ### YOUR CODE ENDS HERE
    print(f"Finished downloading {name}")

async def task3(): 
    """
    In this task, you will use the trio library to download a few books from the Internet. 
    The list of books as urls is provided in the FILES_TO_DOWNLOAD variable. 
    In this function, you will: 
    1. create a directory based on the DOWNLOAD_DIR variable. 
    2. use httpx.AsyncClient() to create a client object. You do not needs to specify any configurations.
    3. use trio.open_nursery() to run download_file for each book in parallel. 

    Expected Output: 
    (1) Downloading War and Peace...
    (2) Downloading Pride and Prejudice...
    (3) Downloading The Adventures of Sherlock Holmes...
    Finished downloading Pride and Prejudice
    Finished downloading The Adventures of Sherlock Holmes
    Finished downloading War and Peace
    """
    FILES_TO_DOWNLOAD = {
    "War and Peace": "https://www.gutenberg.org/files/2600/2600-0.txt",
    "Pride and Prejudice": "https://www.gutenberg.org/cache/epub/1342/pg1342.txt",
    "The Adventures of Sherlock Holmes": "https://www.gutenberg.org/files/1661/1661-0.txt",
}
    DOWNLOAD_DIR = "downloads"

   ### YOUR CODE STARTS HERE

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    async with httpx.AsyncClient() as client:
        async with trio.open_nursery() as nursery:
            for i, (name, url) in enumerate(FILES_TO_DOWNLOAD.items()):
                    print(f"({i+1}) Downloading {name}...")
                    nursery.start_soon(download_file, url, client, name, DOWNLOAD_DIR)
    ### YOUR CODE ENDS HERE


async def get_json_from_url_with_semaphore(semaphore:trio.Semaphore, 
                                           send_channel: trio.MemorySendChannel, 
                                           url: str, 
                                           client: httpx.AsyncClient): 
    """
    This is a helper function that will get the individual web responses. It is important to control the number 
    of concurrent threads to not overwhelm the API server. In this fuction you will
    1. Use the semaphore to control the number of total threads - specified in the parent function 
    2. Get response from each url and convert into json and then into a dataframe (select the 'countryiso3code', 'date' and 'value')
    3. Send the final df into the send_channel
    """
    ### YOUR CODE STARTS HERE
    async with semaphore: 
        response = await client.get(url)
        df = pd.DataFrame.from_dict(response.json()[1]).dropna()
        if len(df) == 0: 
            pass 
        else: 
            await send_channel.send(df[['countryiso3code', 'date', 'value']])
    
    ### YOUR CODE ENDS HERE

async def close_after_timeout(send_channel: trio.MemorySendChannel):
    await trio.sleep(3)  # 10 seconds should be enough for 20 requests
    print("Closing channel after timeout")
    send_channel.close()

async def task4(): 
    """
    In this task, you will use trio's async functionality to assemble an economic database while limiting the number of concurrents.
    In this implementation, you will need two key concepts
    trio.Semaphore: Controls concurrency - limits how many HTTP requests run simultaneously
    trio.open_memory_channel: memory channel buffer that controls data flow between producers and consumers
    
    For this task you need to: 
    1. Set up the send_channel and recieve_channel buffers to store webscrapping info
    2. Set up, httpx.AsyncClient, trio.open_nursery, and trio.Semaphore(MAX_THREADS) to deploy web scrapping while controlling the max number of threads.
    3. Start all the url coroutines. 
    4. Implement helper function get_json_from_url_with_semaphore 
    5. Use close_after_timeout to wait before closing the channel
    6. Reveived all the results from the recieve channel. 

    """
    all_countries_url = "https://api.worldbank.org/v2/country?format=json"

    response = requests.get(all_countries_url)
    all_countries = pd.DataFrame.from_dict(response.json()[1]).head(20) 
    country_ids = all_countries['id']
    country_mapping = dict(zip(all_countries['id'], all_countries['name']))

    MAX_THREADS = 5
    NUM_RESULTS = len(country_ids)

    base_gdp_url = 'https://api.worldbank.org/v2/country/{country_str}/indicator/NY.GDP.MKTP.CD?date=1999:2019&format=json'

    ## Create memory channel for results 
    send_channel, receive_channel = trio.open_memory_channel(NUM_RESULTS)


    ### YOUR CODE STARTS HERE
    
    all_dfs = [] 
    async with httpx.AsyncClient() as client:
        async with trio.open_nursery() as nursery:
            semaphore = trio.Semaphore(MAX_THREADS)
            for i, country in enumerate(country_ids):
                    url = base_gdp_url.format(country_str=country)
                    nursery.start_soon(get_json_from_url_with_semaphore, semaphore, 
                                                      send_channel, url, client)
    
            nursery.start_soon(close_after_timeout, send_channel)
            
    async for df in receive_channel: 
        all_dfs.append(df)


    ### YOUR CODE ENDS HERE
    final_df = pd.concat(all_dfs)

    for id in country_ids: 
        group = final_df[final_df["countryiso3code"]==id]
        if len(group) ==0 or len(group[group['date'].isin(['1999', '2019'])]) < 2: 
            print(country_mapping[id], 'Missing data')
        else: 
            GDP1 = int(group[group['date'] == '1999']['value'].iloc[0])
            GDP2 = int(group[group['date'] == '2019']['value'].iloc[0])
            print(country_mapping[id], f"GDP Growth: {(GDP2-GDP1)/GDP1*100}%")

async def consume_data(receive_channel: trio.MemoryReceiveChannel, all_dfs: list):
    """
    This consumer function will append new dfs on the channel to the all_dfs list 
    Since lists are mutable, this function does not need to return anything.
    """
    async for df in receive_channel:
        all_dfs.append(df)


async def task5(): 
    """
    Task 5 will be an extension of Task 4. Now, instead of sleeping for a few seconds to wait for the send channel to close, 
    you will use a consume data function to ingest data as data is added to the channel and implement the outer nursery. 
    You are making a simpler and faster implementation without using a timeout function.

    1. Implement consume_data function that uses async for to add every df to the all_dfs list
    2. Implement an outer nursery where the consume_data function is called. 
    3. Implement an producer nursery where the url's are fetched: you can use the sma url function as task 4
    4. close the send channel after the producer nursery exits 
    """
    all_countries_url = "https://api.worldbank.org/v2/country?format=json"

    response = requests.get(all_countries_url)
    all_countries = pd.DataFrame.from_dict(response.json()[1]).head(20) 
    country_ids = all_countries['id']
    country_mapping = dict(zip(all_countries['id'], all_countries['name']))

    MAX_THREADS = 5
    NUM_RESULTS = 5

    base_gdp_url = 'https://api.worldbank.org/v2/country/{country_str}/indicator/NY.GDP.MKTP.CD?date=1999:2019&format=json'

    ## Create memory channel for results 
    send_channel, receive_channel = trio.open_memory_channel(NUM_RESULTS)

    ### YOUR CODE STARTS HERE
    
    all_dfs = [] 
    async with httpx.AsyncClient() as client:
        async with trio.open_nursery() as outer_nursery:
            outer_nursery.start_soon(consume_data, receive_channel, all_dfs)
            async with trio.open_nursery() as producer_nursery: 
                semaphore = trio.Semaphore(MAX_THREADS)
                for country in country_ids:
                    url = base_gdp_url.format(country_str=country)
                    producer_nursery.start_soon(get_json_from_url_with_semaphore, semaphore, 
                                                    send_channel, url, client)
            send_channel.close() 
            
    ### YOUR CODE ENDS HERE
    final_df = pd.concat(all_dfs)

    for id in country_ids: 
        group = final_df[final_df["countryiso3code"]==id]
        if len(group) ==0 or len(group[group['date'].isin(['1999', '2019'])]) < 2: 
            print(country_mapping[id], 'Missing data')
        else: 
            GDP1 = int(group[group['date'] == '1999']['value'].iloc[0])
            GDP2 = int(group[group['date'] == '2019']['value'].iloc[0])
            print(country_mapping[id], f"GDP Growth: {(GDP2-GDP1)/GDP1*100}%")


class BasicPriorityScheduler:
    """
    A basic priority-based task scheduler using Python's Trio library.
    
    This scheduler can add tasks with different priority levels (1-5, where 1 is highest priority),
    execute tasks in order of priority, and track basic task information and execution status.
    """
    def __init__(self): 
        """
        Initialize the BasicPriorityScheduler with necessary data structures.
        
        Sets up:
        - Task counter for generating unique IDs
        - Priority queues for tasks (levels 1-5)
        - Task status tracking
        - Logging mechanism with timestamps
        """  
        self.task_counter = 1
        self.current_priority = 1 
        self.priority_queue = {}
        self.id2priority = {} 
        self.task_statuses  = {}
        self.nursery = None 
        self.log = [] 
        self.start_time = time.time() 
        for i in range(1, 6): 
            self.priority_queue[i] = {} 

    def get_current_time(self) -> float: 
        """
        Get the elapsed time since the scheduler was initialized.
        """
        elapsed_time = time.time() - self.start_time 
        return elapsed_time

    def get_tasks_by_status(self, status):
        """Return a list of task IDs that have the specified status."""
        return [task_id for task_id, task_status in self.task_statuses.items() 
                if task_status == status]
    
    def log_event(self, action:str, id:int) -> None: 
        """
        Log an event with the current timestamp.
        
        Args:
            action (str): Description of the action (e.g., 'added', 'started', 'completed')
            id (int): Task ID or priority level associated with the action
        """
        current_time = self.get_current_time()
        self.log.append({
            'time': current_time,
            'action': action, 
            'task_id': id
        })
        
    async def add_task(self, coroutine, priority, *args) -> int:
        """
        Add a coroutine to the scheduler with the specified priority.
        
        Creates a wrapper around the provided coroutine to track its status
        during execution. If the scheduler is already running tasks at the
        current priority level or higher, the task will start immediately.
        
        Args:
            coroutine (Callable): The coroutine function to schedule
            priority (int): Priority level (1-5, where 1 is highest)
            *args: Arguments to pass to the coroutine when executed
            
        Returns:
            int: Unique task ID that can be used to reference this task
        """
        task_id = self.task_counter

        # Create a wrapper coroutine that updates status
        async def task_with_status_tracking(*wrapped_args):
            result = None 
            self.task_statuses[task_id] = 'running'
            self.log_event(action='started', id=task_id)

            result = await coroutine(*wrapped_args)
            self.task_statuses[task_id] = 'completed'
            self.log_event(action='completed', id=task_id)
            return result

        self.priority_queue[priority][task_id] = (task_with_status_tracking, args) 
        self.task_counter += 1 
        self.id2priority[task_id] = priority
        self.task_statuses[task_id] = 'pending'
        self.log_event(action='added', id=task_id)

        # when it is already running - start task immediately 
        if priority <= self.current_priority and self.nursery is not None: 
                coro, args = self.priority_queue[priority][task_id]
                self.nursery.start_soon(coro, args)
        
        return task_id
        
    async def run(self):
        """
        Execute all tasks according to priority levels.
        
        Processes tasks in order of priority (1-5), starting with the highest
        priority (1) and only moving to the next priority level when all tasks
        in the current level have completed.
        
        Each priority level is executed within its own nursery, allowing for
        concurrent execution of tasks with the same priority.
        """
        for i in range(1, 6): 
            self.current_priority = i 
            self.log_event(action="Starting Priority Level", id=i)
            async with trio.open_nursery() as nursery: 
                self.nursery = nursery
                for task in self.priority_queue[i]: 
                    coro, args = self.priority_queue[i][task]
                    nursery.start_soon(coro, args)
            self.log_event(action="Finished Priority Level", id=i)
        
    def print_statistics(self): 
        """
        Print execution statistics from the task log.
        
        Displays chronological events with timestamps, including:
        - Task additions, starts, and completions
        - Priority level transitions
        - Any shutdown events
        """
        for row in self.log: 
            if row['action'].endswith("Level"): 
                print(f"Time: {row['time']:.1f}s - {row['action']} {row['task_id']}")
            elif row['action'].endswith("Shutdown"): 
                print(f"Time: {row['time']:.1f}s - {row['action']}")
            else: 
                print(f"Time: {row['time']:.1f}s - Action: Task {row['task_id']} {row['action']}")


async def task6(): 
    """
    In this first part, you will build the foundation of a priority-based task scheduler using Python's Trio library. Your scheduler should be able to:

    Add tasks with different priority levels (1-5, where 1 is highest priority)
    Execute tasks in order of priority
    Track basic task information and execution status

    1. Create a PriorityScheduler class with the following methods:
    - __init__(): Initialize necessary data structures
    - add_task(coroutine, priority, *args): Add a coroutine with specified priority
    - run(): Execute all tasks according to priority levels

    2. Implement task tracking:
    - assign a unique ID to each task
    - Track task status (pending, running, completed)
    - Log basic events (task added, started, completed)

    EXPECTED OUTPUT: 
    Running Task 6
    Time: 0.0s-Action: Task 1 added
    Time: 0.0s-Action: Task 2 added
    Time: 0.0s-Action: Task 3 added
    Time: 0.0s-Starting Priority Level 1
    Time: 0.0s-Action: Task 1 started
    Time: 2.0s-Action: Task 1 completed
    Time: 2.0s-Finished Priority Level 1
    Time: 2.0s-Starting Priority Level 2
    Time: 2.0s-Finished Priority Level 2
    Time: 2.0s-Starting Priority Level 3
    Time: 2.0s-Action: Task 2 started
    Time: 7.0s-Action: Task 2 completed
    Time: 7.0s-Finished Priority Level 3
    Time: 7.0s-Starting Priority Level 4
    Time: 7.0s-Finished Priority Level 4
    Time: 7.0s-Starting Priority Level 5
    Time: 7.0s-Action: Task 3 started
    Time: 12.0s-Action: Task 3 completed
    Time: 12.0s-Finished Priority Level 5

    """
    scheduler = BasicPriorityScheduler()
    
    # Define some test tasks
    async def high_priority_task(name):
        await trio.sleep(2)
        return f"Result from {name}"
    
    async def low_priority_task(name):
        await trio.sleep(5)
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

class AdvancedPriorityScheduler: 
    def __init__(self): 
        self.task_counter = 1
        self.current_priority = 1 
        self.priority_queue = {}
        self.id2priority = {} 
        self.running_tasks = {} 
        self.task_statuses = {} 
        self.nursery = None 
        self.log = [] 
        self.start_time = time.time() 
        for i in range(1, 6): 
            self.priority_queue[i] = {} 

    def get_current_time(self): 
        elapsed_time = time.time() - self.start_time 
        return elapsed_time

    def log_event(self, action, id): 
        current_time = self.get_current_time()
        self.log.append({
            'time': current_time,
            'action': action, 
            'task_id': id
        })

    def get_tasks_by_status(self, status):
        """Return a list of task IDs that have the specified status."""
        return [task_id for task_id, task_status in self.task_statuses.items() 
                if task_status == status]
    
    async def add_task(self, coroutine, priority, *args) -> int:
        task_id = self.task_counter

        # Create a wrapper coroutine that updates status
        async def task_with_status_tracking(*wrapped_args):
            result = None
            with trio.CancelScope() as cancel_scope: 
                self.running_tasks[task_id] = cancel_scope
                self.task_statuses[task_id] = 'running'
                self.log_event(action='started', id=task_id)

                try: 
                    result = await coroutine(*wrapped_args)
                    self.task_statuses[task_id] = 'completed'
                    self.log_event(action='completed', id=task_id)
                finally: 
                    if task_id in self.running_tasks: 
                        del self.running_tasks[task_id]

            return result


        self.priority_queue[priority][task_id] = (task_with_status_tracking, args) 
        self.task_counter += 1 
        self.id2priority[task_id] = priority
        self.task_statuses[task_id] = 'pending'
        self.log_event(action='added', id=task_id)

        # when it is already running - start task immediately 
        if priority <= self.current_priority and self.nursery is not None: 
                coro, args = self.priority_queue[priority][task_id]
                self.nursery.start_soon(coro, args)
        
        return task_id

    async def cancel_task(self, task_id): 
        priority = self.id2priority[task_id]

        # cancel scope of async task if it is currently running
        if task_id in self.running_tasks: 
            self.running_tasks[task_id].cancel() 
            self.log_event(action='stopped', id=task_id)
        else: 
            self.log_event(action='removed', id=task_id)
        
        # remove task from priority queue
        if task_id in self.priority_queue[priority]: 
            del self.priority_queue[priority][task_id]
        
        self.task_statuses[task_id] = 'cancelled'

    async def reschedule(self, task_id, new_priority):
        priority = self.id2priority[task_id]

        # add to new priority 
        self.priority_queue[new_priority][task_id] = self.priority_queue[priority][task_id]
        
        # remove task from priority queue
        del self.priority_queue[priority][task_id]
        self.log_event(action='rescheduled', id=task_id)

        self.id2priority[task_id] = new_priority

        # when if task is high priority enough to be running 
        if new_priority <= self.current_priority: 
                coro, args = self.priority_queue[new_priority][task_id]
                self.nursery.start_soon(coro, args)

    async def run(self): 
        for i in range(1, 6): 
            self.current_priority = i 
            self.log_event(action="Starting Priority Level", id=i)
            async with trio.open_nursery() as nursery: 
                self.nursery = nursery
                for task in self.priority_queue[i]: 
                    coro, args = self.priority_queue[i][task]
                    nursery.start_soon(coro, args)
            self.log_event(action="Finished Priority Level", id=i)
            

    async def shutdown(self): 
        self.log_event(action="Starting Shutdown", id=None)
        # Cancel all running tasks
        for task_id in self.running_tasks:
            # Cancel the task's scope
            await self.cancel_task(task_id)
        
        # Wait a moment for cancellations to propagate
        await trio.sleep(0.1)
        
        # Clear the running tasks dictionary
        self.running_tasks.clear()

        # Handle any pending tasks that haven't started yet
        for priority in self.priority_queue:
            for task_id in self.priority_queue[priority]:
                if self.task_statuses[task_id] == 'pending':
                    self.log_event(action='cancelled_pending', id=task_id)

        self.log_event(action="Finished Shutdown", id=None)
        

    def print_statistics(self): 
        for row in self.log: 
            if row['action'].endswith("Level"): 
                print(f"Time: {row['time']:.1f}s - {row['action']} {row['task_id']}")
            elif row['action'].endswith("Shutdown"): 
                print(f"Time: {row['time']:.1f}s - {row['action']}")
            else: 
                print(f"Time: {row['time']:.1f}s - Action: Task {row['task_id']} {row['action']}")

async def task7(): 
    """
    Building on your implementation from Part 1, enhance your priority scheduler with dynamic task management and more sophisticated tracking.
    AdvancedPriorityScheduler should have all the features fo the basic scheduler and the following requirments. 

    1. Add these new methods to your PriorityScheduler class:
    - cancel_task(task_id): Cancel a scheduled or running task
    - reschedule(task_id, new_priority): Change a task's priority
    - shutdown(): Gracefully stop all tasks and clean up

    2. Dynamic Task Management: 
    - Allow adding tasks while the scheduler is running
    - Handle priority changes correctly
    - Manage task cancellation with proper cleanup

    Hints: use CancelScope to be able to cancel running tasks, 

    EXPECTED OUTPUT: 
    Running Task 7
    Time: 0.000s - Action: Task 1 added
    Time: 0.000s - Action: Task 2 added
    Time: 0.000s - Action: Task 3 added
    Time: 0.000s - Starting Priority Level 1
    Time: 0.000s - Action: Task 1 started
    Time: 1.001s - Action: Task 4 added
    Time: 1.503s - Action: Task 3 removed
    Time: 2.001s - Action: Task 1 completed
    Time: 2.002s - Finished Priority Level 1
    Time: 2.002s - Starting Priority Level 2
    Time: 2.002s - Action: Task 4 started
    Time: 2.003s - Action: Task 2 rescheduled
    Time: 2.003s - Action: Task 5 added
    Time: 2.003s - Action: Task 2 started
    Time: 4.003s - Action: Task 4 completed
    Time: 7.004s - Action: Task 2 completed
    Time: 7.004s - Finished Priority Level 2
    Time: 7.004s - Starting Priority Level 3
    Time: 7.004s - Finished Priority Level 3
    Time: 7.004s - Starting Priority Level 4
    Time: 7.004s - Finished Priority Level 4
    Time: 7.004s - Starting Priority Level 5
    Time: 7.004s - Action: Task 5 started
    Time: 11.005s - Starting Shutdown
    Time: 11.005s - Action: Task 5 stopped
    Time: 11.005s - Finished Priority Level 5
    Time: 11.106s - Finished Shutdown
    """
    scheduler = AdvancedPriorityScheduler()
    
    # Define some test tasks
    async def high_priority_task(name):
        await trio.sleep(2)
        return f"Result from {name}"
    
    async def low_priority_task(name):
        await trio.sleep(5)
        return f"Result from {name}"

    # Add initial tasks
    task1_id = await scheduler.add_task(high_priority_task, 1, "Task1")
    task2_id = await scheduler.add_task(low_priority_task, 3, "Task2")
    task3_id = await scheduler.add_task(low_priority_task, 5, "Task3")
    
    # Start the scheduler
    async with trio.open_nursery() as nursery:
        nursery.start_soon(scheduler.run)
        
        # Add more tasks while scheduler is running
        await trio.sleep(1)
        task4_id = await scheduler.add_task(high_priority_task, 2, "Task4")
        
        # Cancel a task
        await trio.sleep(0.5)
        await scheduler.cancel_task(task3_id)
        
        # Reschedule a task
        await trio.sleep(0.5)
        await scheduler.reschedule(task2_id, new_priority=1)
        
        # After 10 seconds, request scheduler shutdown
        task6_id = await scheduler.add_task(low_priority_task, 5, "Task5")
        await trio.sleep(9)
        await scheduler.shutdown()
    
    # Print statistics
    scheduler.print_statistics()


if __name__ == "__main__":
    # Here we will test the code you have written for each task
    # print("Running Task 1: Delayed Hello")
    # trio.run(task1)

    # print("Running Task 2: Error Handling")
    # trio.run(task2)

    # print("Running Task 3: Download Files")
    # trio.run(task3)

    # print("Running Task 4: Max Threads")
    # trio.run(task4)

    # print("Running Task 5")
    # trio.run(task5)

    # print("Running Task 6")
    # trio.run(task6)

    print("Running Task 7")
    trio.run(task7)