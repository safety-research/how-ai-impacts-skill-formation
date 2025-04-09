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
    raise NotImplementedError("Implement the timer function")

    ### YOUR CODE ENDS HERE

async def delayed_hello(): 
    """
    Implement a delayed hello function which waits for 2.1 seconds before printing "Hello World"
    """
    ### YOUR CODE STARTS HERE
    raise NotImplementedError("Implement the delayed_hello function")

    ### YOUR CODE ENDS HERE

async def task1():
    """
    In this task, you will use the trio library to write a async function. 
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
    Uses asyncio.sleep(1) to simulate network delay
    Randomly succeeds or fails:

    If user_id is even, return a dictionary {"id": user_id, "name": f"User {user_id}"}
    If user_id is odd, raise an exception ValueError(f"User {user_id} not found")
    """
    ### YOUR CODE STARTS HERE
    raise NotImplementedError("Implement the get_user_id function")

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
        raise NotImplementedError("Implement the get_user_data function")
        ### YOUR CODE ENDS HERE
    
    async with trio.open_nursery() as nursery: 
        for user_id in user_ids: 
            nursery.start_soon(_fetch_and_store, user_id)
    
    return results

async def task2(): 
    """
    In this task, you will implement error handling in using the trio library. 
    Import the asyncio and random libraries

    In this function, we create a list of 5 user IDs (mix of even and odd numbers)
    Calls get_user_data() with this list
    Prints "Successful results:" followed by the results dictionary
    Prints "Errors:" followed by the errors list

    Expected Output: 
    Results:
    User 5: {'status': 'error', 'error': 'User 5 not found'}
    User 4: {'status': 'success', 'data': {'id': 4, 'name': 'User 4'}}
    User 3: {'status': 'error', 'error': 'User 3 not found'}
    User 2: {'status': 'success', 'data': {'id': 2, 'name': 'User 2'}}
    User 1: {'status': 'error', 'error': 'User 1 not found'}
    """
    user_ids = [1, 2, 3, 4, 5]
    results= await get_user_data(user_ids)
    print("Results:") 
    for user_id, result in results.items(): 
        print(f"User {user_id}: {result}")


async def download_file(url: str, client: httpx.AsyncClient, name: str, download_dir: str):
    """Implement an async function for downloading a file and track progress.
    This function takes in a httpx.AsyncClient object which you can used to make the download request directly. 
    The function should: 
    1. download the file from the url using client.get 
    2. save the file to the download_dir directory
    """
    ### YOUR CODE STARTS HERE
    raise NotImplementedError("Implement the download_file function")

    ### YOUR CODE ENDS HERE
    print(f"Finished downloading {name}")

async def task3(): 
    """
    In this task, you will use the trio library to download a few books from the Internet. 
    The list of books as urls are provided in the FILES_TO_DOWNLOAD variable. 
    In this function, you will: 
    1. create a directory based on the the DOWNLOAD_DIR variable. 
    2. use httpx.AsyncClient() to create a client object. 
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

    raise NotImplementedError("Implement task3 function")

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
    raise NotImplementedError("Implement the get_json_from_url_with_semaphore function")

    
    ### YOUR CODE ENDS HERE

async def close_after_timeout(send_channel: trio.MemorySendChannel):
    await trio.sleep(3)  # 10 seconds should be enough for 20 requests
    print("Closing channel after timeout")
    send_channel.close()

async def task4(): 
    """
    In this task you will combine with a maximum amount web requests. To put together an economic database. 
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

    ### YOUR CODE STARTS HERE
    ## Create memory channel for results 
    send_channel, receive_channel = trio.open_memory_channel(NUM_RESULTS)
    
    ## Implement httpx, nursery, and get_json_from_url_with_semaphore loop
    raise NotImplementedError("Implement task4 function")

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
    ### YOUR CODE STARTS HERE
    raise NotImplementedError("Implement consume_data function")
    ### YOUR CODE ENDS HERE


async def task5(): 
    """
    Task 5 will be an extension of task 4. Now instead of sleeping for a few seconds to wait for the send channel to close. 
    In this task, you will build use a consume data function to ingest data as data is added to the channel and implement and outer nursery. 
    You are making a simpler implementation without using a timeout function. 

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



    ### YOUR CODE STARTS HERE
    raise NotImplementedError("Implement task 5 function")
            
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


if __name__ == "__main__":
    # Here we will test the code you have written for each task
    print("Running Task 1: Delayed Hello")
    trio.run(task1)

    print("Running Task 2: Error Handling")
    trio.run(task2)

    print("Running Task 3: Download Files")
    trio.run(task3)

    print("Running Task 4: Max Threads")
    trio.run(task4)

    print("Running Task 5")
    trio.run(task5)