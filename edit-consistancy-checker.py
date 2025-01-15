
import asyncio
import json
import ssl
import sys
import time
from typing import List
import aiohttp

class BackstageClient:
    def __init__(self, base_url, admin_token):
        self.base_url = base_url
        self.admin_token = admin_token
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.successful_read_requests = 0
        self.counter_lock = asyncio.Lock()
        self.timeout = aiohttp.ClientTimeout(total=60)

    async def create_permission(self, permission):
        endpoint = f"{self.base_url}/api/permission/policies"
        print(f"Create permission: {permission}")
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.post(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {self.admin_token}",
                        "Content-Type": "application/json",
                    },
                    data=permission,
                    ssl=self.ssl_context,
                ) as response:
                    if response.status == 401:
                        print("ERROR: Update token for user!")
                        sys.exit(1)
                    if response.status != 201:
                        print(await response.json())
                        raise ValueError(f"Unexpected error. Status code is {response.status}.")
                    print(f"Permission was created: {permission}")
            except asyncio.TimeoutError:
                print(f"Request timed out while creating permission: {permission}")
    
    async def update_permissions(self, role, old_permissions: List, new_permissions: List):
        endpoint = f"{self.base_url}/api/permission/policies/{role.replace(':', '/')}"
        print(f"Update permissions: {new_permissions}")
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.put(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {self.admin_token}",
                        "Content-Type": "application/json",
                    },
                    data=json.dumps({"oldPolicy": old_permissions, "newPolicy": new_permissions}),
                    ssl=self.ssl_context,
                ) as response:
                    if response.status == 401:
                        print("ERROR: Update token for user!")
                        sys.exit(1)
                    if response.status != 200:
                        print(await response.json())
                        raise ValueError(f"Unexpected error. Status code is {response.status}.")
                    print(f"Permission was updated. Old permissions: {old_permissions} to {new_permissions}")
            except asyncio.TimeoutError:
                print(f"Request timed out while updating permission from old permissions: {old_permissions} to new permissions: {new_permissions}")

    async def delete_permission(self, role, permission):
        endpoint = f"{self.base_url}/api/permission/policies/{role.replace(':', '/')}"
        print(f"Delete permission: {permission}")
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.delete(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {self.admin_token}",
                        "Content-Type": "application/json",
                    },
                    data=permission,
                    ssl=self.ssl_context,
                ) as response:
                    if response.status == 401:
                        print("ERROR: Update token for user!")
                        sys.exit(1)
                    if response.status != 204:
                        raise ValueError(f"Unexpected error. Status code is {response.status}.")
                    print(f"Permission was deleted: {permission}")
            except asyncio.TimeoutError:
                print(f"Request timed out while deleting permission: {permission}")

    async def create_role(self, role, role_content):
        endpoint = f"{self.base_url}/api/permission/roles"
        print(f"Create role: {role}")
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.post(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {self.admin_token}",
                        "Content-Type": "application/json",
                    },
                    data=role_content,
                    ssl=self.ssl_context,
                ) as response:
                    if response.status == 401:
                        print("ERROR: Update token for user!")
                        sys.exit(1)
                    if response.status != 201:
                        raise ValueError(f"Unexpected error. Role: {role}. Status code is {response.status}. Message {response}.")
                    print(f"Role was created: {role}")
            except asyncio.TimeoutError:
                print(f"Request timed out while creating role: {role}")

    async def update_role(self, role, oldRole, newRole):
        endpoint = f"{self.base_url}/api/permission/roles/{role.replace(':', '/')}"
        print(f"Update role: {role}")
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.put(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {self.admin_token}",
                        "Content-Type": "application/json",
                    },
                    data=json.dumps({"oldRole": oldRole, "newRole": newRole}),
                    ssl=self.ssl_context,
                ) as response:
                    if response.status == 401:
                        print("ERROR: Update token for user!")
                        sys.exit(1)
                    if response.status != 200:
                        raise ValueError(f"Unexpected error. Role: {role}. Status code is {response.status}. Message {response}.")
                    print(f"Role was updated from: {oldRole} to {newRole}")
            except asyncio.TimeoutError:
                print(f"Request timed out while updating role from: {oldRole} to {newRole}")

    async def delete_role(self, role):
        endpoint = f"{self.base_url}/api/permission/roles/{role.replace(':', '/')}"
        print(f"Delete role: {role}")
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.delete(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {self.admin_token}",
                        "Content-Type": "application/json",
                    },
                    ssl=self.ssl_context,
                ) as response:
                    if response.status == 401:
                        print("ERROR: Update token for user!")
                        sys.exit(1)
                    if response.status != 204:
                        raise ValueError(f"Unexpected error. Role: {role}, Status code is {response.status}. Message {response}.")
                    print(f"Role was deleted: {role}")
            except asyncio.TimeoutError:
                print(f"Request timed out while deleting role: {role}")

    async def get_role(self, role, iteration=None):
        endpoint = f"{self.base_url}/api/permission/roles/{role.replace(':', '/')}"
        iteration_info = f"Iteration number was {iteration}" if iteration is not None else ""
        print(f"{endpoint} {iteration_info}")
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                start_time = time.time()
                async with session.get(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {self.admin_token}",
                        "Content-Type": "application/json",
                    },
                    ssl=self.ssl_context,
                ) as response:
                    end_time = time.time()
                    if iteration is not None:
                        print(f"Request iteration: {iteration}")
                    if response.status == 401:
                        print("ERROR: Update token for user!")
                        sys.exit(1)
                    if response.status == 200:
                        response_body = (await response.json())[0]
                        print(f"Response body: {response_body}")
                        async with self.counter_lock:
                            self.successful_read_requests += 1
                        return end_time - start_time
                    else:
                        print(f"Failed to get role {role}. Status code is: {response.status}.")
                        return 0
            except asyncio.TimeoutError:
                print(f"Request timed out while getting role: {role}")
                return 0

def split_workload(num_roles, num_connections):
    roles_per_connection = num_roles // num_connections
    remainder = num_roles % num_connections
    workloads = []
    start = 1
    for i in range(num_connections):
        end = start + roles_per_connection - 1
        if remainder > 0:
            end += 1
            remainder -= 1
        workloads.append((start, end))
        start = end + 1
    return workloads

async def create_roles(client: BackstageClient, start, end):
    tasks = []
    for i in range(start, end + 1):
        role_name = f"role:default/test-{i}"
        role_content = f"{{\"name\": \"{role_name}\", \"description\": \"Role {i}\", \"memberReferences\": [ \"user:default/test-user\"]}}"
        tasks.append(client.create_role(role_name, role_content))
    await asyncio.gather(*tasks)

async def update_role(client: BackstageClient, start, end):
    tasks = []
    for i in range(start, end + 1):
        role_name = f"role:default/test-{i}"
        old_role = {"name": role_name, "description": "Role {i}", "memberReferences": [ "user:default/test-user" ]}
        new_role = {"name": role_name, "description": "Role {i} updated", "memberReferences": [ "user:default/test-user", "user:default/test-user-2" ]}
        tasks.append(client.update_role(role_name, old_role, new_role))
    await asyncio.gather(*tasks)

async def create_permissions(client: BackstageClient, start, end):
    tasks = []
    for i in range(start, end + 1):
        role_name = f"role:default/test-{i}"
        permission = '[{"entityReference": "' + role_name + '", "permission": "catalog-entity", "policy": "read", "effect":"deny"}]'
        tasks.append(client.create_permission(permission))
    await asyncio.gather(*tasks)

async def update_permissions(client: BackstageClient, start, end):
    tasks = []
    for i in range(start, end + 1):
        role_name = f"role:default/test-{i}"
        old_permission = [{"entityReference": role_name, "permission": "catalog-entity", "policy": "read", "effect":"deny"}]
        permission = [{"entityReference": role_name, "permission": "catalog-entity", "policy": "read", "effect":"allow"}]
        tasks.append(client.update_permissions(role_name, old_permission, permission))
    await asyncio.gather(*tasks)

def main():
    base_url = ">rhdh-with-few-replicas-uri<"
    admin_token = ">admin-token<"

    client = BackstageClient(base_url, admin_token)

    num_roles = 50
    num_connections = 10

    workloads = split_workload(num_roles, num_connections)

    async def run():
        tasks = []
        for start, end in workloads:
            tasks.append(create_roles(client, start, end))
        await asyncio.gather(*tasks)

        tasks.clear()
        for start, end in workloads:
            tasks.append(create_permissions(client, start, end))
        await asyncio.gather(*tasks)

        tasks.clear()
        for start, end in workloads:
            tasks.append(update_role(client, start, end))
            tasks.append(update_permissions(client, start, end))
        await asyncio.gather(*tasks)

        tasks.clear()
        for i in range(num_roles):
            role_name = f"role:default/test-{i+1}"
            permission = '[{"entityReference": "' + role_name + '", "permission": "catalog-entity", "policy": "read", "effect":"allow"}]'
            tasks.append(client.delete_role(role_name))
            tasks.append(client.delete_permission(role_name, permission))

        await asyncio.gather(*tasks)

    asyncio.run(run())

if __name__ == "__main__":
    main()
