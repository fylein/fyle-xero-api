# Fyle Xero API
Django Rest Framework API for Fyle Xero Integration

### Setup

* Rename docker-compose.yml.template to docker-compose.yml

    ```
    $ mv docker-compose.yml.template docker-compose.yml
    ```
  
* Setup environment variables in setup.sh

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
    docker-compose up db api qcluster
    ```

* The database will be available on port 5432 and can be accessed by this command

    ```
    PGPASSWORD=postgres psql -h localhost -U postgres xero_db
    ```

* To tail the logs a service you can do
    
    ```
    docker-compose logs -f <api / qcluster>
    ```