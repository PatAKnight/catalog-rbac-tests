# 
# This script generates users and groups in Keycloak for testing purposes.
# It creates a specified number of groups and users within a realm.
# The script can be configured to create subgroups under each group.
# Additionally, it can create a cyclic group structure within the realm.
#
# Author: Patrick Knight
# Co-author: Oleksandr Andriienko
#
# Usage: testing @backstage-community/plugin-catalog-backend-module-keycloak
#
from keycloak import KeycloakAdmin

import warnings
from urllib3.exceptions import InsecureRequestWarning
from typing import List
import asyncio
import os

# Suppress only InsecureRequestWarnings
warnings.simplefilter('ignore', InsecureRequestWarning)

# Keycloak Admin setup
admin_url = os.getenv("ADMIN_URL", "http://localhost:8080/").strip()
admin_username = os.getenv("ADMIN_USERNAME", "admin").strip()
admin_password = os.getenv("ADMIN_PASSWORD", "admin").strip()

# Realms
realms = [
    # "realm-a",
    "realm-b",
    # "realm-c",
    # "realm-d"
]

group_count_str = os.getenv("GROUP_COUNT", "1000").strip()
# Try to convert to an integer
try:
    group_count = int(group_count_str)
except ValueError:
    # If the conversion fails, set a default value
    print(f"Invalid value for GROUP_COUNT: {group_count_str}. Using default value '1000'.")
    group_count = 1000

user_count_str = os.getenv("USER_COUNT", "500000").strip()
# Try to convert to an integer
try:
    user_count = int(user_count_str)
except ValueError:
    # If the conversion fails, set a default value
    print(f"Invalid value for USER_COUNT: {user_count_str}. Using default value '500000'.")
    user_count = 500000

# Get the environment variable, default to '100' if not set
concurrency_tasks_str = os.getenv("CONCURRENCY_TASKS", "100").strip()
# Try to convert to an integer
try:
    concurrency_tasks = int(concurrency_tasks_str)
except ValueError:
    # If the conversion fails, set a default value
    print(f"Invalid value for CONCURRENCY_TASKS: {concurrency_tasks_str}. Using default value '100'.")
    concurrency_tasks = 100

sub_group_depth = 2  # Define depth of sub-groups
sub_groups_per_group = 3  # Number of sub-groups per group
cyclic_group_count = 5  # Number of groups to include in the cyclic structure for RealmD

# Client settings
client_spec = {
    "clientId": "backstage",
    "clientAuthenticatorType": "client-secret",
    "defaultClientScopes": ["profile", "email", "roles"],
    "directAccessGrantsEnabled": True,
    "implicitFlowEnabled": False,
    "publicClient": False,
    "redirectUris": ["http://localhost:7007/api/auth/oidc/handler/frame"],
    "serviceAccountsEnabled": True,
    "standardFlowEnabled": True,
    "roles": {
        "realm-management": ["query-groups", "query-users", "view-users"]
    }
}

def init_keycloak_admin(realm) -> KeycloakAdmin: #, client_spec
    # Initialize Keycloak Admin client
    return KeycloakAdmin(
        server_url=admin_url,
        username=admin_username,
        password=admin_password,
        realm_name=realm,  # realm
        verify=False, # skip tls verification
        user_realm_name='master'
    )

# Helper functions
def create_realm(keycloak_admin: KeycloakAdmin, realm_name: str):
    """Create a Keycloak realm."""
    try:
        keycloak_admin.create_realm({"realm": realm_name, "enabled": True})
        print(f"Realm {realm_name} created.")
    except Exception as e:
        print(f"Realm {realm_name} creation failed: {e}")

def create_client(realm_admin: KeycloakAdmin, realm_name: str, spec):
    """Create a client for a realm."""
    try:
        # Create client
        client_id = realm_admin.create_client({
            "clientId": spec["clientId"],
            "clientAuthenticatorType": spec["clientAuthenticatorType"],
            "defaultClientScopes": spec["defaultClientScopes"],
            "directAccessGrantsEnabled": spec["directAccessGrantsEnabled"],
            "implicitFlowEnabled": spec["implicitFlowEnabled"],
            "publicClient": spec["publicClient"],
            "redirectUris": spec["redirectUris"],
            "serviceAccountsEnabled": spec["serviceAccountsEnabled"],
            "standardFlowEnabled": spec["standardFlowEnabled"]
        })
        print(f"Client '{spec['clientId']}' created in {realm_name}.")

        # Assinge client roles to service account user
        # Under the hood it works like role mapping: POST /{realm}/users/{id}/role-mappings/clients/{client}
        service_account_user = realm_admin.get_client_service_account_user(client_id)
        realm_management_client_id = realm_admin.get_client_id("realm-management")
        view_users_role = realm_admin.get_client_role(realm_management_client_id, "view-users")
        query_users_role = realm_admin.get_client_role(realm_management_client_id, "query-users")
        query_groups_role = realm_admin.get_client_role(realm_management_client_id, "query-groups")
        realm_admin.assign_client_role(service_account_user['id'], realm_management_client_id, [view_users_role, query_users_role, query_groups_role])

        # Assinge realm roles to service account user
        roles = realm_admin.get_realm_default_roles()
        realm_admin.assign_realm_roles(service_account_user['id'], roles)

        print(f"Roles assigned to service account for client '{spec['clientId']}'.")
    except Exception as e:
        print(f"Client creation failed for {realm_name}: {e}")

# Group assignment strategies
def assign_all_groups(user_id: str, group_ids: List[str], user_index: int):
    """Assign all groups to a user."""
    return group_ids

def assign_three_groups_evenly(user_id: str, group_ids: List[str], user_index: int):
    """Assign exactly three groups to a user evenly."""
    start = (user_index * 3) % len(group_ids)
    return group_ids[start:start+3]

# Updated helper functions
def create_groups_with_subgroups(realm_admin: KeycloakAdmin, count: int, group_ids: List[str], create_subgroups=False, depth=1):
    """Create groups in a realm, optionally with sub-groups."""
    for i in range(count):
        group_name = f"group-{i+1}"
        try:
            group_id = realm_admin.create_group({"name": group_name})
            group_ids.append(group_id)
            print(f"Created group: {group_name}")
            
            # Create sub-groups if enabled
            if create_subgroups and depth > 0:
                create_sub_groups(realm_admin, group_name, group_id, depth)
        except Exception as e:
            print(f"Group creation failed for {group_name}: {e}")

def create_sub_groups(realm_admin: KeycloakAdmin, parent_group_name: str, parent_group_id: str, depth: int):
    """Recursively create sub-groups under a parent group."""
    for j in range(sub_groups_per_group):
        sub_group_name = f"{parent_group_name}-sub-{j+1}"
        try:
            sub_group_id = realm_admin.create_group({"name": sub_group_name}, parent_group_id)

            print(f"Created sub-group: {sub_group_name} under {parent_group_name}")
            
            # Recurse if depth > 1
            if depth > 1:
                create_sub_groups(realm_admin, sub_group_name, sub_group_id, depth - 1)
        except Exception as e:
            print(f"Sub-group creation failed for {sub_group_name}: {e}")

# Helper function for cyclic groups
def create_cyclic_groups(realm_admin: KeycloakAdmin, count: int):
    """Create a cyclic group structure."""
    cyclic_group_ids = []
    for i in range(count):
        group_name = f"cyclic-group-{chr(97 + i)}"  # cyclic-group-a, cyclic-group-b, etc.
        try:
            if i == 0:
                print('this is the first group')
                group_id = realm_admin.create_group({"name": group_name})
                print(f'here is the first group that was created {group_id}')
                first_group = realm_admin.get_group(group_id)
                print(first_group)
            else:
                previous_group_id = cyclic_group_ids[i - 1]
                group_id = realm_admin.create_group({"name": group_name}, previous_group_id)
            cyclic_group_ids.append(group_id)
            print(f"Created cyclic group: {group_name}")
            if i == 4:
                print(f'here is the first group that was created {cyclic_group_ids[0]}')
                first_group_id = cyclic_group_ids[0]
                first_group = realm_admin.get_group(first_group_id)
                print(first_group)
                print(f'here is the last group to be created {group_id}')
        except Exception as e:
            print(f"Cyclic group creation failed for {group_name}: {e}")

async def create_user_task(realm_admin: KeycloakAdmin, username: str, group_ids, group_assignment, user_index):
    """Asynchronous user creation and group assignment."""
    try:
        await asyncio.to_thread(realm_admin.create_user, {"username": username, "enabled": True})
        user_id = await asyncio.to_thread(realm_admin.get_user_id, username)

        # Assign groups
        groups = group_assignment(user_id, group_ids, user_index)
        for group_id in groups:
            await asyncio.to_thread(realm_admin.group_user_add, user_id, group_id)

        return f"User {username} created and assigned to groups."
    except Exception as e:
        return f"User creation failed for {username}: {e}"

async def create_users_async(realm_admin: KeycloakAdmin, count: int, group_assignment, group_ids, max_concurrent_tasks=10):
    """Asynchronous user creation."""
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def sem_task(i):
        username = f"user-{i+1}"
        async with semaphore:
            return await create_user_task(realm_admin, username, group_ids, group_assignment, i)

    tasks = [sem_task(i) for i in range(count)]
    for result in await asyncio.gather(*tasks):
        print(result)

async def create_group_task(realm_admin: KeycloakAdmin, group_name: str):
    """Asynchronous group creation."""
    try:
        group_id = await asyncio.to_thread(realm_admin.create_group, {"name": group_name})
        return group_id, f"Group {group_name} created."
    except Exception as e:
        return None, f"Group creation failed for {group_name}: {e}"

async def create_groups_async(realm_admin: KeycloakAdmin, count: int, group_ids, max_concurrent_tasks=10):
    """Asynchronous group creation."""
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def sem_task(i):
        group_name = f"group-{i+1}"
        async with semaphore:
            return await create_group_task(realm_admin, group_name)

    tasks = [sem_task(i) for i in range(count)]
    for group_id, result in await asyncio.gather(*tasks):
        if group_id:
            group_ids.append(group_id)
        print(result)
    
async def main():
    group_ids = []
    for realm in realms:
        keycloak_admin = init_keycloak_admin('master')

        # Create realm
        create_realm(keycloak_admin, realm)
        realm_admin = init_keycloak_admin(realm)

        # Create client
        create_client(realm_admin, realm, client_spec)

        # Create groups and users
        if realm == "realm-a":
            await create_groups_async(realm_admin, group_count, group_ids, concurrency_tasks)
            await create_users_async(realm_admin, user_count, assign_all_groups, group_ids, concurrency_tasks)
        elif realm == "realm-b":
            await create_groups_async(realm_admin, group_count, group_ids, concurrency_tasks)
            await create_users_async(realm_admin, user_count, assign_three_groups_evenly, group_ids, concurrency_tasks)
        # elif realm == "realm-c":
        #     create_groups_with_subgroups(
        #         realm_admin, group_count, group_ids, create_subgroups=True, depth=sub_group_depth
        #     )
        # elif realm == "realm-d":
        #     # Create cyclic groups
        #     create_cyclic_groups(realm_admin, cyclic_group_count)
        #     # Create the remaining normal groups
        #     await create_groups_async(realm_admin, group_count - cyclic_group_count, group_ids)

# Execution
if __name__ == "__main__":
    asyncio.run(main())
