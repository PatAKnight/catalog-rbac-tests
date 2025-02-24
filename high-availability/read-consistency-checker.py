# The purpose of this script is to check the consistency of read data since we created a new role.
# It also checks the response delay.
# This script allows making a large number of parallel read requests to simulate a small DoS attack on the API
# and ensures the backend can handle a high volume of requests without failing.
# In the newer RBAC backend, we will try to keep data in sync between several pod replicas.
# We need to ensure that read operations are consistent and stable, even with a large number of requests.
#
# Prerequisites:
# RHDH deployed on OpenShift with replicas > 1
# The route should contain the annotation "haproxy.router.openshift.io/balance": "roundrobin"
# You may also need to provide a higher limit for maximum PostgreSQL connections. You can do this inside the pod:
# $ psql -h 127.0.0.1 -p 5432 -U postgres
# To provide more connections:
# ALTER SYSTEM SET max_connections = 200;
# Restart the PostgreSQL StatefulSet. You can rescale it to 0 and then back to 1.
# To check the current limit:
# $ psql -h 127.0.0.1 -p 5432 -U postgres
# $ SHOW max_connections;
#
# Example of how to run the script: 
# python3 read-consistency-checker.py > ~/log-fix-1000-request-10iterations.txt 2>&1

import traceback
import asyncio
import json
import ssl
import aiohttp # type: ignore
import time
import argparse
import sys

BASE_URL = "<base backstage url>"
DEFAULT_NUM_REQUESTS = 1000
NUM_ITERATIONS = 10

ADMIN_TOKEN = "<your_admin_token_here>"

# Set up an SSL context that disables certificate verification
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

successful_read_requests = 0
counter_lock = asyncio.Lock()

async def createPermission(permission, session):
    print(f"Create permission: {permission}")
    createRoleEndpoint = f"{BASE_URL}/api/permission/policies"
    try:
        async with session.post(
            createRoleEndpoint,
            headers={
                "Authorization": f"Bearer {ADMIN_TOKEN}",
                "Content-Type": "application/json"
            },
            data=permission,
            ssl=ssl_context
        ) as response:
            if response.status == 401:
                print(f"ERROR: Update token for user!")
                sys.exit(1)
            if response.status != 201:
                print(await response.json())
                raise ValueError(f"Unexpected error. Status code is {response.status}.")
            print(f"Permission was created: {permission}")
    except asyncio.TimeoutError:
        print(f"Request timed out while creating permission: {permission}")

async def deletePermission(role, permission, session):
    print(f"Delete permission: {permission}")
    deleteRoleEndpoint = f"{BASE_URL}/api/permission/policies/{role.replace(':', '/')}"

    try:
        async with session.delete(
            deleteRoleEndpoint,
            headers={
                "Authorization": f"Bearer {ADMIN_TOKEN}",
                "Content-Type": "application/json"
            },
            data=permission,
            ssl=ssl_context
        ) as response:
            if response.status == 401:
                print(f"ERROR: Update token for user!")
                sys.exit(1)
            if response.status != 204:
                raise ValueError(f"Unexpected error. Status code is {response.status}.")
    except asyncio.TimeoutError:
        print(f"Request timed out while deleting permission: {permission}")

async def createRole(role, roleContent, session):
    print(f"Create role: {role}")
    createRoleEndpoint = f"{BASE_URL}/api/permission/roles"

    try:
        async with session.post(
            createRoleEndpoint,
            headers={
                "Authorization": f"Bearer {ADMIN_TOKEN}",
                "Content-Type": "application/json"
            },
            data=roleContent,
            ssl=ssl_context
        ) as response:
            if response.status == 401:
                print(f"ERROR: Update token for user!")
                sys.exit(1)
            if response.status != 201:
                print(await response.json())
                raise ValueError(f"Unexpected error. Status code is {response.status}.")
            print(f"Role was created: {role}")
    except asyncio.TimeoutError:
        print(f"Request timed out while creating role: {role}")

async def deleteRole(role, session):
    print(f"Delete role: {role}")
    deleteRoleEndpoint = f"{BASE_URL}/api/permission/roles/{role.replace(':', '/')}"

    try:
        async with session.delete(
            deleteRoleEndpoint,
            headers={
                "Authorization": f"Bearer {ADMIN_TOKEN}",
                "Content-Type": "application/json"
            },
            ssl=ssl_context
        ) as response:
            if response.status == 401:
                print(f"ERROR: Update token for user!")
                sys.exit(1)
            if response.status != 204:
                raise ValueError(f"Unexpected error. Status code is {response.status}.")
    except asyncio.TimeoutError:
        print(f"Request timed out while deleting role: {role}")

async def getRole(role, iteration, session):
    global successful_read_requests
    start_time = time.time()
    getRolesEndpoint = f"{BASE_URL}/api/permission/roles/{role.replace(':', '/')}"
    print(f"{getRolesEndpoint} Iteration number was {iteration}")

    try:
        async with session.get(
            getRolesEndpoint,
            headers={
                "Authorization": f"Bearer {ADMIN_TOKEN}",
                "Content-Type": "application/json"
            },
            ssl=ssl_context
        ) as response:
            end_time = time.time()
            print(f"Request iteration: {iteration}")

            if response.status == 401:
                print(f"ERROR: Update token for user!")
                sys.exit(1)
            if response.status == 200:
                responseBody = (await response.json())[0]
                print(f"Response body: {responseBody}")
                async with counter_lock:
                    successful_read_requests += 1
                return end_time - start_time
            else:
                print(f"Failed to get role {role}. Status code is: {response.status}.")
                return 0
    except asyncio.TimeoutError:
        print(f"Request timed out while getting role: {role}")
        return 0

async def main(reuse_session, num_requests):
    role = "role:default/test-role"
    roleMembers = '[ "user:default/test-user"]'
    roleRaw = '{ "memberReferences":  ' + roleMembers + ', "name": "' + role + '" }'
    permission = '[{"entityReference": "' + role + '", "permission": "policy-entity", "policy": "read", "effect":"allow"}]'
    total_time = 0
    total_average_time = 0

    if reuse_session:
        shared_session = aiohttp.ClientSession()
    else:
        shared_session = None

    try:
        for iteration in range(NUM_ITERATIONS):
            try:
                session = shared_session or aiohttp.ClientSession()
                await createRole(role, roleRaw, session)
                await createPermission(permission, session)

                # Measure time for NUM_REQUESTS in this iteration
                tasks = [getRole(role, i, session) for i in range(num_requests)]
                results = await asyncio.gather(*tasks)
                valid_results = [r for r in results if isinstance(r, (int, float))]
                iteration_time = sum(valid_results)
                average_time = iteration_time / num_requests

                # Accumulate total and average times
                total_time += iteration_time
                total_average_time += average_time

                print("-" * 80)
                print(f"Iteration {iteration + 1}/{NUM_ITERATIONS}")
                print(f"Average time per request: {average_time:.3f} seconds")
                print(f"Total time for {num_requests} requests: {iteration_time:.3f} seconds")
                print("-" * 80)

            finally:
                await deleteRole(role, session)
                await deletePermission(role, permission, session)
                if not reuse_session:
                    await session.close()

            # Final metrics
            average_iteration_time = total_time / NUM_ITERATIONS
            average_time_per_request = total_average_time / NUM_ITERATIONS

            print("=" * 80)
            print("Final Results:")
            print(f"Total successful requests: {successful_read_requests} from {NUM_ITERATIONS*num_requests}")
            print(f"Average time per request across iterations: {average_time_per_request:.3f} seconds")
            print(f"Average iteration time: {average_iteration_time:.3f} seconds")
            print(f"Total time for all iterations: {total_time:.3f} seconds")
            print("=" * 80)
    finally:
        if reuse_session and shared_session:
            await shared_session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the read consistency checker.")
    parser.add_argument("--reuse-session", action="store_true", help="Reuse a single session for all requests")
    parser.add_argument("--num-requests", type=int, default=DEFAULT_NUM_REQUESTS, help="Number of requests to send in each iteration (default: 900)")
    args = parser.parse_args()

    asyncio.run(main(args.reuse_session, args.num_requests))
