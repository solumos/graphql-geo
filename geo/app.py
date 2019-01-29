import os

from flask import Flask
from flask_graphql import GraphQLView

from geo.models.base import Session, init_db
from geo.api.schema import schema

app = Flask(__name__)
app.debug = True

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql", schema=schema, graphiql=True  # for having the GraphiQL interface
    ),
)


@app.teardown_appcontext
def shutdown_session(exception=None):
    Session.remove()


def main():
    init_db(os.getenv("POSTGRES_URL"))
    app.run(host="0.0.0.0")
