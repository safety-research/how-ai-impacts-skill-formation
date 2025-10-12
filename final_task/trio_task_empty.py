import trio
import time
import httpx
import os
import requests
import pandas as pd

import trio
import time
import httpx
import os
import requests
import pandas as pd

############## TASK 1 ###################
async def timer() -> None: 
    """Prints the number of seconds that have passed starting at '1s' """
    raise NotImplementedError("timer") 

async def delayed_hello() -> None: 
    """Sleeps for 2.1 seconds and the prints 'Hello, World!' """
    raise NotImplementedError("delayed_hello")  

async def task1():
    """
    In this task, you will use the trio library to write two async functions. 
    Your task is to complete the timer and delayed_hello functions. 
    """
    print("Starting...")
    TIMEOUT = 2.5
    with trio.move_on_after(TIMEOUT): 
        # TODO: start trio nursery
        # TODO: start timer function
        # TODO: start delayed_hello
        pass 
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
    raise NotImplementedError("Implement get_user_data") 
    
    
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
    raise NotImplementedError("Implement download_and_save_text") 
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
    raise NotImplementedError("Implement task")

############## END TASK 3 ###################

############## TASK 4 #######################
import trio
import time
import httpx
import os
import requests
import pandas as pd

############## TASK 4 #######################
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
    raise NotImplementedError("Implement get_json_from_url_with_semaphore")

async def close_after_timeout(send_channel: trio.MemorySendChannel):
    await trio.sleep(3) 
    print("Closing channel after timeout")
    send_channel.close()

async def task4a(): 
    """
    In this task, you will use trio's async functionality to assemble an economic database while limiting the number of concurrents.
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
    
    raise NotImplementedError("Implement task3a")

    ### YOUR CODE ENDS HERE
    final_df = pd.concat(all_dfs)

    for id in country_ids: 
        group = final_df[final_df["countryiso3code"]==id]
        if len(group) ==0 or len(group[group['date'].isin(['1999', '2019'])]) < 2: 
            print(country_mapping[id], 'Missing data')
        else: 
            GDP1 = int(group[group['date'] == '1999']['value'].iloc[0])
            GDP2 = int(group[group['date'] == '2019']['value'].iloc[0])
            print(country_mapping[id], f"GDP Growth: {(GDP2-GDP1)/GDP1*100:.3f}%")

async def consume_data(receive_channel: trio.MemoryReceiveChannel, all_dfs: list):
    """
    This consumer function will append new dataframes on the channel to the all_dfs list 
    """
    raise NotImplementedError("Implement consume_data")


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
    
    raise NotImplementedError("Implement task3b")
            
    ### YOUR CODE ENDS HERE
    final_df = pd.concat(all_dfs)

    for id in country_ids: 
        group = final_df[final_df["countryiso3code"]==id]
        if len(group) ==0 or len(group[group['date'].isin(['1999', '2019'])]) < 2: 
            print(country_mapping[id], 'Missing data')
        else: 
            GDP1 = int(group[group['date'] == '1999']['value'].iloc[0])
            GDP2 = int(group[group['date'] == '2019']['value'].iloc[0])
            print(country_mapping[id], f"GDP Growth: {(GDP2-GDP1)/GDP1*100:.3f}%")

############## END TASK 4 ###################

############## TASK 5 #######################
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
        raise NotImplementedError("Implement init")

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
        raise NotImplementedError("Implement add_task")
        
    async def run(self):
        """
        Execute tasks in priority order (1-5, highest to lowest)
        """
        raise NotImplementedError("Implement run")
        
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
        raise NotImplementedError("Implement init")

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
        raise NotImplementedError("Implement add_task")

    async def cancel_task(self, task_id): 
        """
        Task cancellation with proper clean up 
        """
        raise NotImplementedError("Implement cancel_task")

    async def reschedule(self, task_id, new_priority):
        """
        Priority level changes for existing tasks 
        """
        raise NotImplementedError("Implement reschedule_task")

    async def run(self): 
        raise NotImplementedError("Implement run")
            

    async def shutdown(self): 
        """
        Graceful shutdown of all running tasks
        """
        raise NotImplementedError("Implement shutdown")

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