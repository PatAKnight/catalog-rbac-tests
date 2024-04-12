# CATALOG-RBAC-TESTS

Search and replace `<YOUR_USER_NAME>` with your username

Edit `./catalog-entities/all.local.yaml` to select the number of users and groups that you wish to load into your backstage instance

Each user file has 13 users

Each group file has 13 groups

Add the following to your app-config

```YAML
catalog:
  # ... other configuration values ... #
  locations:
    # Local example template
    - type: file
      target: ../../catalog-entities/all.local.yaml
      rules:
        - allow: [User, Group]
```

Update the `rbac-policy.csv` to include the permissions and roles that you wish to load. Best to make a copy and then only add the permissions and roles that match the users and groups that you added above.

It is setup in groups of four. So, the first four set of roles and permissions correspond to the first four user files and group files in `./catalog-entities/all.local.yaml`.

Also included is `curl.py` which will allow you to make 10 groups of 15 calls to the catalog.

```bash
export TOKEN=your-token
python curl.py
```
