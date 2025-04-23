import trio
import time
import httpx
import os
import requests
import pandas as pd

async def timer() -> None: 
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

async def delayed_hello() -> None: 
    ### YOUR CODE STARTS HERE
    await trio.sleep(2.1)
    print("Hello, World!")
    ### YOUR CODE ENDS HERE

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

async def get_user_id(user_id: int) -> dict:
    ### YOUR CODE STARTS HERE
    await trio.sleep(1)
    if user_id % 2 == 0: 
        return {"id": user_id, "username": f"User {user_id}"}
    else: 
        raise ValueError(f"User {user_id} not found")
    ### YOUR CODE ENDS HERE 

async def get_user_data(user_ids: list[int]) -> dict[dict]:
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

async def task1b(): 
    """
    In this task, you will implement error handling in using the trio library. In this test case, we create a list of 5 user IDs (mix of even and odd numbers). We call get_user_data() with this list
    Prints "Results:" followed by the results dictionary
    Prints "Errors:" followed by the errors list
    """
    user_ids = [1, 2, 3, 4, 5]
    results= await get_user_data(user_ids)
    print("Results:") 
    for user_id, result in results.items(): 
        print(f"User {user_id}: {result}")


async def download_file(url: str, client: httpx.AsyncClient, name: str, download_dir: str) -> None:
    """Implement an async function for downloading a file from an url.
    """
    ### YOUR CODE STARTS HERE
    response = await client.get(url)
    with open(os.path.join(download_dir, f'{name}.txt'), "wb") as f:
        f.write(response.content)
    ### YOUR CODE ENDS HERE
    print(f"Finished downloading {name}")

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

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    async with httpx.AsyncClient() as client:
        async with trio.open_nursery() as nursery:
            for i, (name, url) in enumerate(FILES_TO_DOWNLOAD.items()):
                    print(f"({i+1}) Downloading {name}...")
                    nursery.start_soon(download_file, url, client, name, DOWNLOAD_DIR)


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
    await trio.sleep(3) 
    print("Closing channel after timeout")
    send_channel.close()

async def task3a(): 
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
    This consumer function will append new dataframes on the channel to the all_dfs list 
    """
    async for df in receive_channel:
        all_dfs.append(df)


async def task3b(): 
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


if __name__ == "__main__":
    # Here we will test the code you have written for each task
    print("Running Task 1: Delayed Hello")
    trio.run(task1a)

    print("Running Task 2: Error Handling")
    trio.run(task1b)

    print("Running Task 3: Download Files")
    trio.run(task2)

    print("Running Task 4: API Download")
    trio.run(task3a)

    print("Running Task 5: API Download Producer-Consumer")
    trio.run(task3b)

    print("Running Task 6")
    trio.run(task4a)

    print("Running Task 7")
    trio.run(task4b)