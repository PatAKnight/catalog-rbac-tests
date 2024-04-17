import os
import random
import yaml
import argparse
import csv

FRUITS = ["apple", "banana", "cherry", "grapefruit", "strawberry", "plum", "raspberry", "mango", "pineapple", "papaya", "blueberry", "pomegranate", "guava", "orange", "apricot", "watermelon", "peach", "pear", "blackberry", "lime", "date", "elderberry", "fig", "grape", "kiwi", "lemon", "cantaloupe", "melon", "breadfruit", "starfruit"]

VEGETABLES = ["carrots", "peas", "tomatoes", "onions", "peppers", "mushrooms", "cucumbers", "gourds", "leeks", "parsnips", "potatoes", "pumpkins", "shallots", "zucchinis", "turnips"]

GROUP_FOLDER_STRUCTURE = "catalog-entities/large-org/groups"
USER_FOLDER_STRUCTURE = "catalog-entities/large-org/users"
LOCATION_FOLDER_STRUCTURE = "catalog-entities/large-org/"
BASE_USER_FOLDER_STRUCTURE = "catalog-entities/large-org/"

GROUP_CHOICES = []
USER_CHOICES = []
LOCATIONS = ["users", "groups"]
LOCATIONS_CHOICES = [USER_CHOICES, GROUP_CHOICES]

PERMISSIONS = [
    [" catalog-entity", " read", " allow"],
    [" catalog-entity", " update", " allow"],
    [" catalog-entity", " delete", " allow"],
    [" catalog.entity.create", " create", " allow"],
]

def generate_random_name(items):
    return random.choice(items)

def generate_user_yaml_content(name, number, group):
    memberOf = group
    if number:
        username = f"{name.lower()}_{number}"
        email = f"{name.lower()}-{number}@example.com"
        displayName = f"{name.capitalize()} {number}"
    else:
        username = name
        email = f"{name}@example.com"
        displayName = f"{name}"
    content = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "User",
        "metadata": {
            "name": username
        },
        "spec": {
            "profile": {
                "email": email,
                "displayName": displayName,
            },
            "memberOf": memberOf
        }
    }
    return yaml.dump(content)

def generate_group_yaml_content(name, number, root_number, parent_group=None):
    content = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Group",
        "metadata": {
            "name": f"{name.lower()}_{number}_{root_number}",
            "title": f"{name.capitalize()} {number} {root_number}"
        },
        "spec": {
            "type": "team",
            "children": []
        }
    }
    if parent_group:
        content["spec"]["parent"] = parent_group.lower()
    return yaml.dump(content)

def generate_location_yaml_content(name, children):
    folder = f"/{name}/"
    ex = ".local.yaml"
    for i in range(len(children)):
      children[i] = f".{folder}{children[i]}{ex}"
    content = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Location",
        "metadata": {
            "name": f"{name.lower()}",
            "description": f"A collection of all {name.lower()}"
        },
        "spec": {
            "targets": children
        }
    }
    return yaml.dump(content)

def draw_hierarchy_tree(group_hierarchy, node, indent=0, file=None):
    if node not in group_hierarchy:
        return

    current_node = group_hierarchy[node]
    node_type = current_node["kind"]
    if node_type == "Group":
        line = "|  " * indent + "|- group:default/" + current_node["metadata"]["name"]
        print(line)
        file.write(line + "\n")
        children = current_node["spec"]["children"]
        for child in children:
            draw_hierarchy_tree(group_hierarchy, child, indent + 1, file)
        # Print associated users for this group
        for user_node in group_hierarchy.values():
            if user_node["kind"] == "User" and current_node["metadata"]["name"] in user_node["spec"]["memberOf"]:
                line = "|  " * (indent + 1) + "|- user:default/" + user_node["metadata"]["name"]
                print(line)
                file.write(line + "\n")
    elif node_type == "User":
        # User nodes are already handled when printing associated groups, so no need to print here
        pass


def draw_hierarchy_ascii(group_hierarchy):
    with open("hierarchy_graph.txt", "w") as file:
        root_nodes = [node for node, data in group_hierarchy.items() if "parent" not in data["spec"] and "User" not in data["kind"]]
        for root_node in root_nodes:
            draw_hierarchy_tree(group_hierarchy, root_node, file=file)
            line = "-------------------------------------------------------------------"
            print(line)
            file.write(line + "\n")

def save_yaml_file_for_group(parent_group_name, content, folder_structure, location):
    if location:
        filename = f"{folder_structure}/{parent_group_name}.local.yaml"
    else:
        filename = f"{folder_structure}/{parent_group_name}.local.yaml"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "a") as file:
        file.write(content)
        file.write("---\n")

def save_user_yaml_file(name, content, number, folder_structure, location):
    if location:
        filename = f"{folder_structure}/{name.lower()}.local.yaml"
    else:
        filename = f"{folder_structure}/{name.lower()}_{number}.local.yaml"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as file:
        file.write(content)

def save_user_yaml_file_for_group(group_name, content, folder_structure, location):
    if location:
        filename = f"{folder_structure}/{group_name}.local.yaml"
    else:
        filename = f"{folder_structure}/{group_name}.local.yaml"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "a") as file:
        file.write(content)
        file.write("---\n")

def create_resources(args):
    group_hierarchy = {}
    user_choices = []
    root_choices = []
    for root_number in range(args.root):
      root_hierarchy = {}
      root_group = ""
      for group_number in range(args.groups):
          vegetable_name = generate_random_name(VEGETABLES)
          parent_group = random.choice(list(root_hierarchy.keys())) if root_hierarchy else None
          group_yaml_content = generate_group_yaml_content(vegetable_name, group_number, root_number, parent_group)
          if parent_group == None:
              root_group = vegetable_name + "_" + str(group_number) + "_" + str(root_number)
          save_yaml_file_for_group(root_group, group_yaml_content, GROUP_FOLDER_STRUCTURE, False)
          if parent_group:
              root_hierarchy[parent_group]["spec"]["children"].append(vegetable_name.lower() + "_" + str(group_number) + "_" + str(root_number))
              group_hierarchy[parent_group]["spec"]["children"].append(vegetable_name.lower() + "_" + str(group_number) + "_" + str(root_number))
          group_hierarchy[vegetable_name.lower() + "_" + str(group_number) + "_" + str(root_number)] = yaml.safe_load(group_yaml_content)
          root_hierarchy[vegetable_name.lower() + "_" + str(group_number) + "_" + str(root_number)] = yaml.safe_load(group_yaml_content)
          if root_group not in GROUP_CHOICES:
              GROUP_CHOICES.append(f"{root_group}")
          root_choices.append(f"{vegetable_name}_{group_number}_{root_number}")

    for user_number in range(args.users):
        fruit_name = generate_random_name(FRUITS)
        group_choice = random.choice(root_choices)
        user_yaml_content = generate_user_yaml_content(fruit_name, user_number, [group_choice])
        save_user_yaml_file_for_group(group_choice, user_yaml_content, USER_FOLDER_STRUCTURE, False)
        user_choices.append(f"{fruit_name.lower()}_{user_number}")
        group_hierarchy[fruit_name.lower() + "_" + str(user_number)] = yaml.safe_load(user_yaml_content)
        if group_choice not in USER_CHOICES:
            USER_CHOICES.append(f"{group_choice}")

    for i in range(len(LOCATIONS)):
        location_yaml_content = generate_location_yaml_content(LOCATIONS[i], LOCATIONS_CHOICES[i])
        save_user_yaml_file(LOCATIONS[i], location_yaml_content, 1, LOCATION_FOLDER_STRUCTURE, True)
    
    return group_hierarchy

def save_to_csv(group_hierarchy):
    with open("rbac-policy.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        root_nodes = [node for node, data in group_hierarchy.items() if "parent" not in data["spec"] and "User" not in data["kind"]]
        for root_node in root_nodes:
            levels_encountered = [False] * 4
            csv_hierarchy_tree(group_hierarchy, root_node, writer, 0, levels_encountered)
            writer.writerow([])

def csv_hierarchy_tree(group_hierarchy, node, writer, current_level, levels_encountered):
    if current_level > 3 or levels_encountered[current_level]:
        return
    
    permission = PERMISSIONS[current_level]

    if node not in group_hierarchy:
        return

    current_node = group_hierarchy[node]
    node_type = current_node["kind"]
    if node_type == "Group":
        writer.writerow(["g", " group:default/" + current_node["metadata"]["name"], " role:default/" + current_node["metadata"]["name"]])
        writer.writerow(["p", " role:default/" + current_node["metadata"]["name"], *permission])
        levels_encountered[current_level] = True
        children = current_node["spec"]["children"]
        for child in children:
            csv_hierarchy_tree(group_hierarchy, child, writer, current_level + 1, levels_encountered)
    elif node_type == "User":
        pass

def add_user_to_last_group_first_branch(group_hierarchy, number_of_attached_groups):
    current_level = number_of_attached_groups
    last_group_list = []
    root_nodes = [node for node, data in group_hierarchy.items() if "parent" not in data["spec"] and "User" not in data["kind"]]
    for root_node in root_nodes:
        if current_level == 0:
            return
        current_level -= 1
        last_group = find_last_group_first_branch(group_hierarchy, root_node)
        last_group_name = last_group["metadata"]["name"]
        last_group_list.append(last_group_name)
        user_yaml_content = generate_user_yaml_content(f"<YOUR_USERNAME_{current_level}>", None, last_group_name)
        group_hierarchy[f"<YOUR_USERNAME_{current_level}>"] = yaml.safe_load(user_yaml_content)
    user_yaml_content = generate_user_yaml_content(f"<YOUR_USERNAME_{current_level}>", None, last_group_list)
    save_user_yaml_file_for_group("base-user", user_yaml_content, BASE_USER_FOLDER_STRUCTURE, True)

def find_last_group_first_branch(group_hierarchy, node):
    if node not in group_hierarchy:
        return None
    
    current_node = group_hierarchy[node]
    node_type = current_node["kind"]
    if node_type == "Group":
        children = current_node["spec"]["children"]
        if children:
            # Recursively traverse the first child
            return find_last_group_first_branch(group_hierarchy, children[0])
        else:
            # No children, this is a leaf node this should be the group
            return current_node
    elif node_type == "User":
        # Leaf node (User)
        return None


def main():
    parser = argparse.ArgumentParser(description="Your script description")
    parser.add_argument("-g", "--groups", type=int, default=15, help="Number of Groups")
    parser.add_argument("-u", "--users", type=int, default=2, help="Number of Users")
    parser.add_argument("-r", "--root", type=int, default=2, help="Number of Root Groups")
    parser.add_argument("-z", "--roles", type=int, default=1, help="Number of roles the base user is attached to")

    args = parser.parse_args()
    group_hierarchy = create_resources(args)

    add_user_to_last_group_first_branch(group_hierarchy, args.roles)

    draw_hierarchy_ascii(group_hierarchy)
    save_to_csv(group_hierarchy)

if __name__ == "__main__":
    main()
