# This script check latency for permission evaluation for user assigned to a lot of roles.
# This script creates a number of roles and permissions, checks the latency of permission evaluation,
# and then deletes the roles and permissions. It can reuse a single aiohttp session for all requests
# or create a new session for each request based on the command line argument.
import asyncio
import json
import ssl
import aiohttp # type: ignore
import time
import argparse
import sys

USER="user:default/cyber-stalker-bit"
BASE_URL = "<base_url_here>"  # Replace with your actual base URL
DEFAULT_NUM_REQUESTS = 1000
NUM_ROLES = 50

ADMIN_TOKEN = "<your_admin_token_here>"  # Replace with your actual admin token
USER_TOKEN= "<your_user_token_here>"  # Replace with your actual user token

# Set up an SSL context that disables certificate verification
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

successful_read_requests = 0
counter_lock = asyncio.Lock()

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

async def deleteRole(role, session):
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

async def deletePermission(role, permission, session):
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

async def fetch_permission(session, auth_token):
    """Make a single async POST request to the Permission API."""
    start_time_inner = time.time()
    payload = {
    "items": [
            {
                "id": "9c43936f-4bc1-44e5-9ff0-9b9139cce546",
                "permission": {
                    "attributes": {
                        "action": "read"
                    },
                    "name": "catalog.entity.read",
                    "type": "resource",
                    "resourceType": "catalog-entity",
                },
                "resourceRef": USER
            }
        ]
    }

    authorizeEndpoint = f"{BASE_URL}/api/permission/authorize"

    async with session.post(
        authorizeEndpoint,
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    ) as response:
        end_time_inner = time.time()

        if response.status == 401:
            print(await response.json())
            print(f"ERROR: Update token for user")
            sys.exit(1)
        if response.status != 200:
            print(f"Unexpected error. Status code is {response.status}.")
            sys.exit(1)

        result = (await response.json())['items'][0]['result']
        if (result != 'ALLOW'):
          print(f"Expected result: 'ALLOW' does not match result: ${result}")

        return end_time_inner - start_time_inner
    
async def createRoleAndPermissionForUser(reuse_session, shared_session):
    for iteration in range(NUM_ROLES):
        session = shared_session or aiohttp.ClientSession()
        role = f"role:default/test-role-{iteration}"
        roleMembers = f"[\"{USER}\"]"
        roleRaw = '{ "memberReferences":  ' + str(roleMembers) + ', "name": "' + role + '" }'
        permission = '[{"entityReference": "' + role + '", "permission": "catalog.entity.read", "policy": "read", "effect":"allow"}]'
        try:
            await createRole(role, roleRaw, session)
            await createPermission(permission, session)
        finally:
            if not reuse_session:
                await session.close()

async def deleteRoleAndPermissionForUser(reuse_session, shared_session):
    for iteration in range(NUM_ROLES):
        try:
            session = shared_session or aiohttp.ClientSession()
            role = f"role:default/test-role-{iteration}"
            permission = '[{"entityReference": "' + role + '", "permission": "catalog.entity.read", "policy": "read", "effect":"allow"}]'
            await deleteRole(role, session)
            await deletePermission(role, permission, session)
        finally:
            if not reuse_session:
                await session.close()
    print(f"All roles and permissions deleted for {USER}")

async def checkPermissionEvaluationLatency(reuse_session, shared_session):
    minLatency = sys.float_info.max
    maxLatency = 0.0
    total_time = 0.0
    for iteration in range(DEFAULT_NUM_REQUESTS):
        try:
            session = shared_session or aiohttp.ClientSession()
            latency = await fetch_permission(shared_session or session, USER_TOKEN)
            total_time += latency

            if latency < minLatency:
                minLatency = latency

            if latency > maxLatency:
                maxLatency = latency
            await session.close()
            print(f"Latency for permission fetch: {latency:.3f} seconds. Iteration: {iteration + 1}")
        finally:
            if not reuse_session:
                await session.close()

    average_iteration_time = total_time / DEFAULT_NUM_REQUESTS
    print(f"Max latency value is {maxLatency:.3f} seconds")
    print(f"Min latency value is {minLatency:.3f} seconds")
    print(f"Average request duration is time: {average_iteration_time:.3f} seconds")

async def main(reuse_session):
    if reuse_session:
        shared_session = aiohttp.ClientSession()
    else:
        shared_session = None
    try:
        await createRoleAndPermissionForUser(reuse_session, shared_session)
        await checkPermissionEvaluationLatency(reuse_session, shared_session)
    finally:
        await deleteRoleAndPermissionForUser(reuse_session, shared_session)
        if reuse_session and shared_session:
            await shared_session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the fetch permission evaluation latency checker.")
    parser.add_argument("--reuse-session", action="store_true", help="Reuse a single session for all requests")
    args = parser.parse_args()

    asyncio.run(main(args.reuse_session))
