# Spending Balancer

Spending Balancer is a tool for managing spending between a group of people. For example, roommates could use the tool
to keep track of shared purchases and balance the amount of money spent.

## Environment Variables

```bash
SB_SECRET_KEY=my-secret-key-here
SB_ALLOWED_HOSTS='["my-domain.local"]'
```

## Bind Mounts

* `path/to/db.sqlite3:/app/db.sqlite3`
* `path/to/static:/app/static` <-- needs to be served externally via static file server
