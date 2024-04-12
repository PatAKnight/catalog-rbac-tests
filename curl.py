import requests
import time
import os

AUTH_TOKEN = os.environ.get('TOKEN')

ENDPOINT_URL = "http://localhost:7007/api/catalog/entities"
NUM_REQUESTS = 15
NUM_REQUESTS_TWO = 10
total_time = 0

for i in range(NUM_REQUESTS_TWO):
    total_time_inner = 0
    print(f"Iteration {i+1}:")
    
    for j in range(NUM_REQUESTS):
        start_time_inner = time.time()
        response = requests.get(ENDPOINT_URL, headers={"Authorization": "Bearer " + AUTH_TOKEN})
        end_time_inner = time.time()
        elapsed_time_inner = end_time_inner - start_time_inner
        total_time_inner += elapsed_time_inner
    
    average_time_inner = total_time_inner / NUM_REQUESTS
    print(f"Average time taken to complete 1 request: {average_time_inner:.3f} seconds")
    print(f"Total time it took to complete {NUM_REQUESTS} requests: {total_time_inner:.3f} seconds")
    total_time += total_time_inner

average_time = total_time / NUM_REQUESTS_TWO
print(f"Average time taken for {NUM_REQUESTS} requests over {NUM_REQUESTS_TWO} iterations: {average_time:.3f} seconds")
print(f"Total time taken for {NUM_REQUESTS} requests of {NUM_REQUESTS_TWO} iterations: {total_time:.3f} seconds")
