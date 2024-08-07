# Spending Balancer

Spending Balancer is a tool for managing spending between a group of people. For example, roommates could use the tool
to keep track of shared purchases and balance the amount of money spent.

This is an old project mostly developed from 2016-2018 for balancing roommate expenses.

## Environment Variables

```bash
SB_SECRET_KEY=my-secret-key-here
SB_ALLOWED_HOSTS='["example.org"]'
SB_CSRF_TRUSTED_ORIGINS='["https://example.org"]'
```

## Bind Mounts

* `path/to/db.sqlite3:/app/db.sqlite3`
* `path/to/static:/app/static` <-- needs to be served externally via static file server

## Developing Locally

First, install [Poetry](https://python-poetry.org/docs/) for Python dependency management.

Then, install the dependencies:

```bash
poetry install
```

Next, you can start the development server to start working on the application (or execute any other Django `manage.py` 
command):

```bash
poetry run manage.py runserver
```
