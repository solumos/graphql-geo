# GraphQL-Geo

GraphQL Geo provides two simple geocoding api's:

   - `nearby`
   - `reverseGeolocate`

The application is written in Python 3/Flask, and exposes these API's via GraphQL. The underlying datastore is PostgreSQL
w/ PostGIS extensions enabled. Alembic is also used for database migrations.

# Installation

## Requirements

GraphQL Geo relies on a dockerized development environment. This requires a recent version of the docker engine,
docker machine and docker compose. This project was built on Docker Desktop CE, which corresponds to the
following versions:
    
   - Docker Desktop CE Version 2.0.0.2 (30215)
        - Engine: 18.09.1
        - Compose: 1.23.2
        - Machine: 0.16.1

## Running the local dev environment

Convenience targets that handle Compose file inheritance are provided in the `Makefile`. To run the development
server, simply run `make up`. This builds the development image, creates the docker networking layer, and runs the
`graphql-geo` and `postgis` services. Once these services are up and running, apply the alembic migration by running
`make alembic-upgrade`. Once the schema migration has been applied, run `make restart-app` to restart the application.

## Example queries

See the provided [integration test](geo/api/test/integration.py) for example GraphQL queries. The GraphiQL query builder
is also available by navigating to `localhost:5000/graphql` in the browser when the app service is running.