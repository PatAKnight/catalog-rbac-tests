import asyncio
import aiohttp
import time
import sys

PERMISSION_ENDPOINT_URL = "http://localhost:7007/api/permission/authorize"
CATALOG_ENDPOINT_URL = "http://localhost:7007/api/catalog/entities"
NUM_REQUESTS = 10
NUM_REQUESTS_TWO = 5
total_time = 0

LIST_OF_USERS = [
  "INSERT_USER",
]
LIST_OF_USERS_LENGTH = len(LIST_OF_USERS)
TOKENS = [
  "INSERT_TOKEN",
]
EXPECTED_RESULT = [
  "ALLOW",
]

async def fetch_permission(session, i, auth_token):
    """Make a single async POST request to the Permission API."""
    start_time_inner = time.time()
    payload = '{"items":[{"id":"9c43936f-4bc1-44e5-9ff0-9b9139cce546",' \
              '"permission":{"attributes":{"action":"read"},' \
              '"name":"catalog.entity.read","type":"resource",' \
              '"resourceType":"catalog-entity"}}]}'

    async with session.post(
        PERMISSION_ENDPOINT_URL,
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        },
        data=payload
    ) as response:
        end_time_inner = time.time()

        if response.status == 401:
            print(await response.json())
            print(f"ERROR: Update token for user: {LIST_OF_USERS[i]}!")
            sys.exit(1)
        if response.status != 200:
            print(f"Unexpected error. Status code is {response.status}.")
            sys.exit(1)

        result = (await response.json())['items'][0]['result']
        if (result != EXPECTED_RESULT[i]):
          print(f"Expected result: ${EXPECTED_RESULT[i]} does not match result: ${result}")

        return end_time_inner - start_time_inner

async def fetch_catalog(session, i, auth_token):
    """Make a single async GET request to the Catalog API."""
    start_time_inner = time.time()

    async with session.get(
        CATALOG_ENDPOINT_URL,
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    ) as response:
        end_time_inner = time.time()

        if response.status == 401:
            print(f"ERROR: Update token for user: {LIST_OF_USERS[i]}!")
            sys.exit(1)
        if response.status != 200:
            print(f"Unexpected error. Status code is {response.status}.")
            sys.exit(1)

        return end_time_inner - start_time_inner

async def run_tests_for_user(i, session):
    """Run both Permission and Catalog API tests for a specific user."""
    print(f"Performance test of user: {LIST_OF_USERS[i]}")
    print(f"Expected result should be: {EXPECTED_RESULT[i]}")
    print("-" * 95)
    print("\n")

    total_time = 0
    average_time = 0
    average_time_single_request = 0

    print("-" * 95)
    print("Permission API tests")
    print(f"Calling {NUM_REQUESTS} request over {NUM_REQUESTS_TWO} iterations")
    for j in range(NUM_REQUESTS_TWO):
        tasks = [fetch_permission(session, i, TOKENS[i]) for _ in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)

        total_time_inner = sum(results)
        average_time_inner = total_time_inner / NUM_REQUESTS

        total_time += total_time_inner
    
    average_time = total_time / NUM_REQUESTS_TWO
    average_time_single_request = total_time / NUM_REQUESTS_TWO / NUM_REQUESTS

    print("-" * 95)
    print(f"Permission tests completed for user: {LIST_OF_USERS[i]}")
    print(f"Average time taken for a single request: {average_time_single_request:.3f} seconds")
    print(f"Average time taken for {NUM_REQUESTS} requests over {NUM_REQUESTS_TWO} iterations: {average_time:.3f} seconds")
    print(f"Total time taken for {NUM_REQUESTS} requests of {NUM_REQUESTS_TWO} iterations: {total_time:.3f} seconds")
    print("-" * 95)
    print("\n")

    total_time = 0
    average_time = 0
    average_time_single_request = 0

    print("-" * 95)
    print("Catalog API tests")
    print(f"Calling {NUM_REQUESTS} request over {NUM_REQUESTS_TWO} iterations")
    for j in range(NUM_REQUESTS_TWO):
        tasks = [fetch_catalog(session, i, TOKENS[i]) for _ in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)

        total_time_inner = sum(results)
        average_time_inner = total_time_inner / NUM_REQUESTS

        total_time += total_time_inner

    average_time = total_time / NUM_REQUESTS_TWO
    average_time_single_request = total_time / NUM_REQUESTS_TWO / NUM_REQUESTS

    print("-" * 95)
    print(f"Catalog tests completed for user: {LIST_OF_USERS[i]}")
    print(f"Average time taken for a single request: {average_time_single_request:.3f} seconds")
    print(f"Average time taken for {NUM_REQUESTS} requests over {NUM_REQUESTS_TWO} iterations: {average_time:.3f} seconds")
    print(f"Total time taken for {NUM_REQUESTS} requests of {NUM_REQUESTS_TWO} iterations: {total_time:.3f} seconds")
    print("-" * 95)
    print("\n")

async def main():
    """Entry point to run tests for all users."""
    async with aiohttp.ClientSession() as session:
        tasks = [run_tests_for_user(i, session) for i in range(LIST_OF_USERS_LENGTH)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
