We created this package to test a high-availability scenario: the rbac-backend plugin has multiple instances connected to the same database. In this case, the REST API and permission policy evaluation should remain consistent.

To test these scenarios, we have two tests:

edit-consistency-checker.py – tests parallel edit operations
read-consistency-checker.py – tests parallel read operations

To emulate two pod replicas, you can run two localhost instances configured on ports 7007 and 7008 for the backends.

The API instance on port 7007 uses the default configuration. For the API instance on port 7008, apply the following configuration to app-config.local.yaml:

```
backend:
  baseUrl: http://localhost:7008
  listen:
    port: 7008
  csp:
    connect-src: ["'self'", 'http:', 'https:']
  cors:
    origin: http://localhost:3001
    methods: [GET, HEAD, PATCH, POST, PUT, DELETE]
    credentials: true

app:
  title: RBAC Backstage App
  baseUrl: http://localhost:3001
```

Then, use Docker Compose with HAProxy in the localhost-compose folder:

```
$ cd localhost-compose
$ docker compose up
```

This proxy will run on port 8080 and distribute traffic between localhost:7007 and localhost:7008. Requests should work with an API token retrieved from either instance.