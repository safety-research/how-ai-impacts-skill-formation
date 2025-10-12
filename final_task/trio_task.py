import trio
import time
import httpx
import os
import requests
import pandas as pd

############## TASK 1 ###################
async def timer() -> None: 
    """Prints the number of seconds that have passed starting at '1s' """
    seconds = 1
    while True: 
        await trio.sleep(1)
        print(f"{seconds}s")
        seconds += 1


async def delayed_hello() -> None: 
    """Sleeps for 2.1 seconds and the prints 'Hello, World!' """
    await trio.sleep(2.1)
    print('Hello, World!') 

async def task1():
    """
    In this task, you will use the trio library to write two async functions. 
    Your task is to complete the timer and delayed_hello functions. 
    """
    print("Starting...")
    TIMEOUT = 2.5
    with trio.move_on_after(TIMEOUT): 
        async with trio.open_nursery() as nursery: 
            nursery.start_soon(timer)
            nursery.start_soon(delayed_hello)
    print("Completed!")
    return 

############## END TASK 1 ###################


############## TASK 2 #######################
async def get_user_id(user_id: int) -> str:
    await trio.sleep(1)
    if user_id % 2 == 0: 
        return f"User-{user_id}"
    else: 
        raise ValueError(f"User {user_id} not found")

async def get_user_data(user_ids: list[int]) -> dict[str]:
    """
    Asynchronously fetch user_ids using get_user_id. Store the result as 'error' if 
    an error is encountered. 
    """
    results = {} 
    async def _fetch_and_store(user_id): 
        try: 
            result = await get_user_id(user_id)
        except: 
            result = 'error'
        results[user_id] = result
    
    async with trio.open_nursery() as nursery: 
        for id in user_ids: 
            nursery.start_soon(_fetch_and_store, id)
    return results 

async def task2(): 
    """
    In this task, you will implement error handling . In this test case, we create a list of 5 user IDs (mix of even and odd numbers). We call get_user_data() with this list. 
    """
    user_ids = [1, 2, 3, 4, 5]
    results= await get_user_data(user_ids)
    print("Results:") 
    for user_id, result in results.items(): 
        print(f"User {user_id}: {result}")

############## END TASK 2 ###################

############## TASK 3 #######################
async def download_and_save_text(url: str, client: httpx.AsyncClient, name: str, download_dir: str) -> None:
    """Implement an async function for downloading a file from an url.
    """
    print(f"Downloading {name}...")
    ### YOUR CODE STARTS HERE
    result = await client.get(url)
    with open(f"{download_dir}/{name}.txt" , 'wb') as f: 
        f.write(result.content)
    ### YOUR CODE ENDS HERE
    print(f"Finished downloading {name}")


async def task3(): 
    """Download multiple classic books in parallel using trio and httpx.
    
    This function will set up an async HTTP client and use trio to download multiple pages concurrently
    """
    # Dictionary mapping book names to their download URLs
    download_books = {
        "War and Peace": "https://www.gutenberg.org/files/2600/2600-0.txt",
        "Pride and Prejudice": "https://www.gutenberg.org/cache/epub/1342/pg1342.txt",
        "The Adventures of Sherlock Holmes": "https://www.gutenberg.org/files/1661/1661-0.txt",
    }
    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    async with httpx.AsyncClient() as client: 
        async with trio.open_nursery() as nursery:
            for name, url in download_books.items(): 
                nursery.start_soon(download_and_save_text, 
                                   url, client, name, DOWNLOAD_DIR)      

############## END TASK 3 ###################

############## BEGIN TASK 4 ###################

def get_gdp_from_response(response) -> dict | None:
    """
    Extracts GDP data from a World Bank API response.

    Args:
        response: The HTTP response object from the World Bank API.

    Returns:
        dict: Dictionary with 'country' and 'gdp' keys if data is present.
        None: If no data is available in the response.
    """
    data = response.json()
    if not isinstance(data, list) or len(data) < 2 or not isinstance(data[1], list):
        return None
    df = pd.DataFrame.from_dict(data[1]).dropna()
    if len(df) == 0:
        return None
    results = {
        'country': df['countryiso3code'].values[0],
        'gdp': df['value'].values[0]
    }
    return results

async def get_response_with_semaphore(
    semaphore: trio.Semaphore,
    send_channel: trio.MemorySendChannel,
    url: str,
    client: httpx.AsyncClient
):
    """
    Fetches a single URL using a semaphore to limit concurrency, processes the response,
    and sends the result through a Trio memory channel.

    Args:
        semaphore (trio.Semaphore): Semaphore to control concurrency.
        send_channel (trio.MemorySendChannel): Channel to send results.
        url (str): The URL to fetch.
        client (httpx.AsyncClient): The HTTP client to use for requests.
    """
    ### YOUR CODE STARTS HERE
    async with semaphore: 
        response = await client.get(url)
        
        gdp_dict = get_gdp_from_response(response)
        if gdp_dict is not None: 
            await send_channel.send(gdp_dict)
    
    ### YOUR CODE ENDS HERE

async def close_after_timeout(send_channel: trio.MemorySendChannel):
    """
    Waits for 3 seconds and then closes the provided send channel.

    Args:
        send_channel (trio.MemorySendChannel): The channel to close.
    """
    await trio.sleep(3)
    print("Closing channel after timeout")
    send_channel.close()

async def task4(): 
    """
    Fetches GDP data for a list of countries from the World Bank API concurrently,
    limiting the number of concurrent requests, and prints the results.

    Uses a semaphore to control concurrency and a memory channel to collect results.
    """
    country_ids = [
        'ABW', 'AFE', 'AFG', 'AFR', 'AFW', 'AGO', 'ALB', 'AND', 'ARB', 'ARE',
        'ARG', 'ARM', 'ASM', 'ATG', 'AUS', 'AUT', 'AZE', 'BDI', 'BEA', 'BEC'
    ]
    MAX_THREADS = 5
    BUFFER_SIZE = len(country_ids)

    base_gdp_url = 'https://api.worldbank.org/v2/country/{country_str}/indicator/NY.GDP.MKTP.CD?date=2019&format=json'

    ## Create memory channel for results 
    
    ### YOUR CODE STARTS HERE
    send_channel, receive_channel = trio.open_memory_channel(BUFFER_SIZE)
    all_results = []

    async with httpx.AsyncClient() as client:
        async with trio.open_nursery() as nursery:
            semaphore = trio.Semaphore(MAX_THREADS)
            for country in country_ids:
                url = base_gdp_url.format(country_str=country)
                nursery.start_soon(
                    get_response_with_semaphore, semaphore, send_channel, url, client
                )
            nursery.start_soon(close_after_timeout, send_channel)
            
    async for country_gdp in receive_channel: 
        all_results.append(country_gdp)

    ### YOUR CODE ENDS HERE
    for country_gdp in all_results: 
        print(f"country: {country_gdp['country']} GDP: {country_gdp['gdp'] / 1_000_000_000:.1f}B")

async def consume_data(receive_channel: trio.MemoryReceiveChannel, all_dfs: list):
    """
    This consumer function will append new dataframes on the channel to the all_dfs list 
    """
    async for df in receive_channel:
        all_dfs.append(df)

async def task4b(): 
    """
    This task will extend the previous step to a more efficient producer-consumer pattern for data processing
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

############## END TASK 4 ###################

############## BEGIN TASK 5 ###################

class BasicPriorityScheduler:
    """
    A basic priority-based task scheduler using Python's Trio library.
    """
    def __init__(self): 
        """
        Initialize the BasicPriorityScheduler with necessary data structures.
        """  
        self.log = [] 
        self.start_time = time.time() 
        ## YOUR CODE STARTS HERE
        self.task_counter = 1
        self.current_priority = 1 
        self.priority_queue = {}
        self.id2priority = {} 
        self.task_statuses  = {}
        self.nursery = None 

        for i in range(1, 6): 
            self.priority_queue[i] = {} 

    def get_tasks_by_status(self, status):
        """Return a list of task IDs that have the specified status."""
        return [task_id for task_id, task_status in self.task_statuses.items() 
                if task_status == status]
    
    def log_event(self, action:str, id:int) -> None: 
        current_time = time.time() - self.start_time 
        self.log.append({
            'time': current_time,
            'action': action, 
            'task_id': id
        })

    def print_statistics(self): 
        for row in self.log: 
            if row['action'].endswith("Level"): 
                print(f"Time: {row['time']:.1f}s - {row['action']} {row['task_id']}")
            elif row['action'].endswith("Shutdown"): 
                print(f"Time: {row['time']:.1f}s - {row['action']}")
            else: 
                print(f"Time: {row['time']:.1f}s - Action: Task {row['task_id']} {row['action']}")

        
    async def add_task(self, coroutine, priority, *args) -> int:
        """
        Add a coroutine with specified priority, return task ID
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
        Execute tasks in priority order (1-5, highest to lowest)
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

class AdvancedPriorityScheduler: 
    def __init__(self): 
        self.log = [] 
        self.start_time = time.time()

        self.task_counter = 1
        self.current_priority = 1 
        self.priority_queue = {}
        self.id2priority = {} 
        self.running_tasks = {} 
        self.task_statuses = {} 
        self.nursery = None     
        
        for i in range(1, 6): 
            self.priority_queue[i] = {} 

    def log_event(self, action, id): 
        current_time = time.time() - self.start_time 
        self.log.append({
            'time': current_time,
            'action': action, 
            'task_id': id
        })

    def get_tasks_by_status(self, status):
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
        """
        Task cancellation with proper clean up 
        """
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
        """
        Priority level changes for existing tasks 
        """
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
        """
        Graceful shutdown of all running tasks
        """
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

############## END TASK 5 ###################

if __name__ == "__main__":
    # Here we will test the code you have written for each task
    # print("Running Task 1: Delayed Hello")
    # trio.run(task1)

    # print("Running Task 2: Error Handling")
    # trio.run(task2)

    # print("Running Task 3: Download Files")
    # trio.run(task3)

    print("Running Task 4: API Download")
    trio.run(task4)

    # print("Running Task 5: API Download Producer-Consumer")
    # trio.run(task3b)

    # print("Running Task 6")
    # trio.run(task4a)

    # print("Running Task 7")
    # trio.run(task4b)