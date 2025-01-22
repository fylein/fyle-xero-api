# Fyle Xero API
Django Rest Framework API for Fyle Xero Integration

### Setup

* Add and update the `fyle_integrations_imports` and `fyle-integrations-db-migrations` submodule
    ```bash
    $ git submodule init
    $ git submodule update
    ```

* ### Adding a New View, Function, or Trigger:
    Follow these steps to ensure your changes are applied correctly:

    1. **Make changes** in the `fyle-integrations-db-migrations` repository.
    2. **Update the submodule** in the Xero API:
        ```bash
        git submodule init
        git submodule update
        ```
    3. **Enter the Xero API container**:
        ```bash
        enter xero-api
        ```
    4. **Generate a migration file** using the provided convenient command:
        ```bash
        python3 manage.py create_sql_migration <file-path1> <file-path2> ... --app=<app_name>
        ```
        - Replace `<file-path1>`, `<file-path2>`, etc., with the paths to your SQL files. You can add as many files as needed, separated by spaces.
        - Replace `<app_name>` with the name of your Django app where the migration should be created. If omitted, the migration will be created in the `internal` app by default.

    **Example:**
    ```bash
    python3 manage.py create_sql_migration fyle-integrations-db-migrations/xero/functions/re_export_expenses_xero.sql fyle-integrations-db-migrations/xero/functions/delete_workspace.sql
    ```


* Download and install Docker desktop for Mac from [here.](https://www.docker.com/products/docker-desktop)

* If you're using a linux machine, please download docker according to the distrubution you're on.

* Rename docker-compose.yml.template to docker-compose.yml

    ```
    $ mv docker-compose.yml.template docker-compose.yml
    ```

* Setup environment variables in docker_compose.yml

    ```yaml
    environment:
      SECRET_KEY: thisisthedjangosecretkey
      ALLOWED_HOSTS: "*"
      DEBUG: "False"
      APP_URL: http://localhost:4200
      API_URL: http://localhost:8000/api
      DATABASE_URL: postgres://postgres:postgres@db:5432/xero_db
      FYLE_BASE_URL:
      FYLE_CLIENT_ID:
      FYLE_CLIENT_SECRET:
      FYLE_TOKEN_URI:
      XERO_BASE_URL: https://api.xero.com
      XERO_CLIENT_ID:
      XERO_CLIENT_SECRET:
      XERO_REDIRECT_URI: http://localhost:4200/workspaces/xero/callback
      XERO_TOKEN_URI: https://identity.xero.com/connect/token
   ```

* Build docker images

    ```
    docker-compose build api qcluster
    ```

* Run docker containers

    ```
    docker-compose up -d db api qcluster
    ```

* The database can be accessed by this command, on password prompt type `postgres`

    ```
    docker-compose run db psql -h db -U postgres xero_db
    ```

* To tail the logs a service you can do

    ```
    docker-compose logs -f <api / qcluster>
    ```

* To stop the containers

    ```
    docker-compose stop api qcluster
    ```

* To restart any containers - `would usually be needed with qcluster after you make any code changes`

    ```
    docker-compose restart qcluster
    ```

* To run bash inside any container for purpose of debugging do

    ```
    docker-compose exec api /bin/bash
    ```
