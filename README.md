# CATALOG-RBAC-TESTS

## Using the tree graph builder

```bash
python tree.py -g 25 -u 2000 -r 250 -z 250
```

-g will be the number of groups

- For the total number of groups to be generated multiple -g by -r

-u the number of users

- This is independent to the number of groups

-r the number of root groups that you want
-z the number of roles that you will want

Search and replace `<YOUR_USER_NAME>` with your username

Add the following to your app-config

```YAML
catalog:
  # ... other configuration values ... #
  locations:
    # Local example template
    - type: file
      target: ../../catalog-entities/large-org/all.local.yaml
      rules:
        - allow: [User, Group]
```

An rbac policy file will be generated `rbac-policy.csv`

Also, a simple text file will be generated to show the hierarchy of the graph

Also included is `curl.py` which will allow you to make 10 groups of 15 calls to the catalog.

```bash
export token=your-token
python curl.py
```

### Newest updates

```bash
python hierarchy.py -r 10 -g 10 -u 4 -l 9
```

- `-r` or `--root` will determine the number of root groups to use
- `-g` or `--hierarchy` will determine the hierarchy level of your tree
- `-u` or `--users` will determine the number of users per the lowest level group
- `-l` or `--level` is the starting level in which we will begin defining roles

The above example will generate where roles will start at the ninth level or one level above the last group:

- Groups: 10230
- Users: 20480
- Roles: 2560
- Permissions: 10240

The following catalog entities, group hierarchy graph, and policy csv file will be found under the directory `catalog-entities/extreme-org`

Some more examples:

The following will set the roles at the lowest group level

```bash
python hierarchy.py -r 2 -g 2 -u 2 -l 2
```

- The number of groups: 6
- The number of users: 8
- The number of roles: 4
- The number of permissions: 16

```bash
python hierarchy.py -r 5 -g 5 -u 5 -l 5
```

- The number of groups: 155
- The number of users: 400
- The number of roles: 80
- The number of permissions: 320

```bash
python hierarchy.py -r 10 -g 5 -u 10 -l 5
```

- The number of groups: 310
- The number of users: 1600
- The number of roles: 160
- The number of permissions: 640
