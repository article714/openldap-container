from flask import Flask
from flask_restful import Api

from .database_mgmt import DatabaseMgmt
from .hello import HelloWorld
from .ldif import LdifEndpoint

app = Flask("ldapi")
api = Api(app)

# Routes
api.add_resource(HelloWorld, "/hlo")
api.add_resource(DatabaseMgmt, "/db")
api.add_resource(LdifEndpoint, "/ldif")
