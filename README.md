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
export TOKEN=your-token
python curl.py
```
