import os
import random
import yaml
import argparse
import csv

FRUITS = [
  "apple", "apricot",
  "banana", "blackberry", "blueberry", "breadfruit",
  "cantaloupe", "cherry",
  "date",
  "elderberry",
  "fig",
  "grape", "grapefruit", "guava",
  "kiwi",
  "lemon", "lime",
  "mango", "melon",
  "orange",
  "papaya", "peach", "pear", "pineapple", "plum", "pomegranate",
  "raspberry",
  "starfruit", "strawberry",
  "watermelon",
  "starfruit",
]

VEGETABLES = [
  "artichoke", "asparagus", "avocado",
  "beet", "broccoli", "broccolini",
  "cabbage", "carrots", "cauliflower", "celeriac", "celery", "chard", "chicory", "corn", "cress", "cucumbers",
  "daikon",
  "garlic", "greens", "gourds",
  "jicama",
  "kale", "kohlrabi",
  "leeks", "lettuce",
  "mushrooms",
  "okra", "onions",
  "parsnips", "peas", "peppers", "potatoes", "pumpkin",
  "radicchio", "radish", "rhubarb", "rutabaga",
  "shallots", "spinach", "squash",
  "tomatillo", "tomatoes", "turnips",
  "yam",
  "zucchini",
]

GROUP_FOLDER_STRUCTURE = "catalog-entities/extreme-org/groups"
USER_FOLDER_STRUCTURE = "catalog-entities/extreme-org/users"
LOCATION_FOLDER_STRUCTURE = "catalog-entities/extreme-org/"
BASE_USER_FOLDER_STRUCTURE = "catalog-entities/extreme-org/"

GROUP_CHOICES = []
USER_CHOICES = []
LOCATIONS = ["users", "groups"]
LOCATIONS_CHOICES = [USER_CHOICES, GROUP_CHOICES]

global NODE_COUNTER

GUARANTEED_PERMISSION = [
  [" catalog-entity", " read", " allow"],
  [" catalog-entity", " read", " deny"]
]

PERMISSIONS = [
  [" catalog-entity", " update", " allow"],
  [" catalog-entity", " update", " deny"],
  [" catalog-entity", " delete", " allow"],
  [" catalog-entity", " delete", " deny"],
  [" catalog.entity.create", " create", " allow"],
  [" catalog.entity.create", " create", " deny"],
  [" scaffolder.action.execute", " use", " allow"],
  [" scaffolder.action.execute", " use", " deny"],
  [" scaffolder.template.parameter.read", " read", " allow"],
  [" scaffolder.template.parameter.read", " read", " deny"],
  [" scaffolder.template.step.read", " read", " allow"],
  [" scaffolder.template.step.read", " read", " deny"],
]

NUM_OF_USERS = 0
NUM_OF_GROUPS = 0
NUM_OF_ROLES = 0
NUM_OF_PERMISSIONS = 0

def generate_user_yaml_content(name, number, group, group_number):
  memberOf = group
  if number > -1:
    username = f"{name.lower()}_{number}_{group_number}"
    email = f"{name.lower()}-{number}-{group_number}@example.com"
    displayName = f"{name.capitalize()} {number} {group_number}"
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
        "memberOf": [memberOf]
    }
  }
  return yaml.dump(content)

def generate_group_yaml_content(name, number, parent_group=None):
  groupName = f"{name.lower()}_{number}"
  title = f"{name.capitalize()} {number}"
  content = {
    "apiVersion": "backstage.io/v1alpha1",
    "kind": "Group",
    "metadata": {
      "name": groupName,
      "title": title,
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
      children[i] = f"./{children[i]}{ex}"
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

class Node:
    def __init__(self, name, value, node_id):
        self.name = name
        self.value = value
        self.left = None
        self.right = None
        self.id = node_id

def create_balanced_binary_tree(root_choice, root_value, root_group_name, height, users, node_counter, hierarchy_counter):
    global NUM_OF_USERS
    global NUM_OF_GROUPS
    # We will use root number for the users
    name = f"{root_choice.lower()}_{node_counter + hierarchy_counter}"
    if height == 0:
        for user_number in range(users):
            user_choice = random.choice(FRUITS)
            user_content = generate_user_yaml_content(user_choice, user_number, name, node_counter + hierarchy_counter)
            NUM_OF_USERS += 1
            save_user_yaml_file_for_group(name, user_content, USER_FOLDER_STRUCTURE)
        USER_CHOICES.append(name)
        return None
    root = Node(name, root_value, node_counter + hierarchy_counter)

    # Left
    left_node_number = node_counter * 2
    left_choice = f"{random.choice(VEGETABLES)}"
    left_content = generate_group_yaml_content(left_choice, left_node_number + hierarchy_counter, root.name)
    NUM_OF_GROUPS += 1
    save_yaml_file_for_group(root_group_name, left_content, GROUP_FOLDER_STRUCTURE)
    if height - 1 == 0:
        left_name = f"{left_choice.lower()}_{left_node_number + hierarchy_counter}"
        root.left = Node(left_name, left_content, left_node_number + hierarchy_counter)
        create_balanced_binary_tree(left_choice, left_content, root_group_name, height - 1, users, left_node_number, hierarchy_counter)
    else:
        root.left = create_balanced_binary_tree(left_choice, left_content, root_group_name, height - 1, users, left_node_number, hierarchy_counter)

    # Right
    right_node_number = node_counter * 2 + 1
    right_choice = f"{random.choice(VEGETABLES)}"
    right_content = generate_group_yaml_content(right_choice, right_node_number + hierarchy_counter, root.name)
    NUM_OF_GROUPS += 1
    save_yaml_file_for_group(root_group_name, right_content, GROUP_FOLDER_STRUCTURE)
    if height - 1 == 0:
        right_name = f"{right_choice.lower()}_{right_node_number + hierarchy_counter}"
        root.right = Node(right_name, right_content, right_node_number + hierarchy_counter)
        create_balanced_binary_tree(right_choice, right_content, root_group_name, height - 1, users, right_node_number, hierarchy_counter)
    else:
        root.right = create_balanced_binary_tree(right_choice, right_content, root_group_name, height - 1, users, right_node_number, hierarchy_counter)
    return root

def print_tree(root, level=0, file=None):
    if root is not None:
        line = "| " * level + "|- group:default/" + str(root.name)
        print(line)
        file.write(line + "\n")
        print_tree(root.left, level + 1, file)
        print_tree(root.right, level + 1, file)

def draw_hierarchy_tree(root):
  with open("catalog-entities/extreme-org/hierarchy_tree.txt", "a") as file:
    if root is not None:
      print_tree(root, 0, file)
      line = "---------------------------"
      print(line)
      file.write(line + "\n")

def create_content(args):
    global NUM_OF_GROUPS
    for root_number in range(args.root):
        if root_number == 0:
            number = 0
        else:
            number = (2 ** (args.hierarchy) - 1) * root_number
        
        NODE_COUNTER = 1
        root_choice = random.choice(VEGETABLES)
        root_content = generate_group_yaml_content(root_choice, number + NODE_COUNTER)
        NUM_OF_GROUPS += 1
        root_group_name = f"{root_choice.lower()}_{number + NODE_COUNTER}"
        save_yaml_file_for_group(root_group_name, root_content, GROUP_FOLDER_STRUCTURE)
        GROUP_CHOICES.append(root_group_name)

        # Create the balanced binary tree for this root
        tree_root = create_balanced_binary_tree(root_choice, root_content, root_group_name, args.hierarchy - 1, args.users, NODE_COUNTER, number)
        draw_hierarchy_tree(tree_root)

        write_to_csv(tree_root, args.level)
    
    for i in range(len(LOCATIONS)):
        location_yaml_content = generate_location_yaml_content(LOCATIONS[i], LOCATIONS_CHOICES[i])
        save_location_yaml_file(LOCATIONS[i], location_yaml_content, 1, f"{LOCATION_FOLDER_STRUCTURE}/{LOCATIONS[i]}")

    all_location_target = ['base-user', 'groups/groups', 'users/users']
    location_yaml_content = generate_location_yaml_content('entities', all_location_target)
    save_location_yaml_file('all', location_yaml_content, 1, f"{LOCATION_FOLDER_STRUCTURE}")


    base_user_yaml_content = generate_user_yaml_content('<YOUR_USER_NAME>', -1, '<YOUR_GROUP>', -1)
    save_location_yaml_file('base-user', base_user_yaml_content, 1, f"{LOCATION_FOLDER_STRUCTURE}")

def save_yaml_file_for_group(parent_group_name, content, folder_structure):
    filename = f"{folder_structure}/{parent_group_name}.local.yaml"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "a") as file:
        file.write(content)
        file.write("---\n")

def save_user_yaml_file_for_group(group_name, content, folder_structure):
    filename = f"{folder_structure}/{group_name}.local.yaml"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "a") as file:
        file.write(content)
        file.write("---\n")

def save_location_yaml_file(name, content, number, folder_structure):
    filename = f"{folder_structure}/{name.lower()}.local.yaml"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as file:
        file.write(content)

def write_to_csv(root, level):
    with open("catalog-entities/extreme-org/rbac-policy.csv", mode="a", newline='') as file:
        writer = csv.writer(file)
        write_tree_to_csv(root, writer, 1, level)

def write_tree_to_csv(root, writer, current_level, level):
    global NUM_OF_ROLES
    global NUM_OF_PERMISSIONS
    if root is not None:
        if current_level == level:
            # Write the current node to CSV
            writer.writerow(["g", " group:default/" + root.name, " role:default/" + root.name])
            NUM_OF_ROLES += 1
            aOd = random.randint(0,1)
            writer.writerow(["p", " role:default/" + root.name, *GUARANTEED_PERMISSION[aOd]])
            NUM_OF_PERMISSIONS += 1
            
            ranges = [(0, 3), (4, 7), (8, 11)]

            for start, end in ranges:
                random_permission = random.randint(start, end)
                writer.writerow(["p", " role:default/" + root.name, *PERMISSIONS[random_permission]])
                NUM_OF_PERMISSIONS += 1
            writer.writerow([])
        # Recursively traverse left and right subtrees
        write_tree_to_csv(root.left, writer, current_level + 1, level)
        write_tree_to_csv(root.right, writer, current_level + 1, level)

def main():
  parser = argparse.ArgumentParser(description="Your script description")
  parser.add_argument("-r", "--root", type=int, default=2, help="Number of Root Groups")
  parser.add_argument("-g", "--hierarchy", type=int, default=3, help="Hierarchy level for your true")
  parser.add_argument("-u", "--users", type=int, default=2, help="Number of users at the base of the tree")
  parser.add_argument("-l", "--level", type=int, default=3, help="Start writing roles from this hierarchy level")

  args = parser.parse_args()

  root = create_content(args)

  print(f"- The number of groups: {NUM_OF_GROUPS}")
  print(f"- The number of users: {NUM_OF_USERS}")
  print(f"- The number of roles: {NUM_OF_ROLES}")
  print(f"- The number of permissions: {NUM_OF_PERMISSIONS}")

if __name__ == "__main__":
  main()
