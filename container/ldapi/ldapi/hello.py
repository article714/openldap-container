from flask import Flask, request
from flask_restful import Api, Resource

from .database_mgmt import DatabaseMgmt
from .utils import _connect

app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    """
    Simple connection test
    """

    def put(self):
        json_data = request.get_json(force=True)
        ldap_o = _connect(json_data)
        if ldap_o is not None:
            return {"status": "ok"}
        ldap_o.unbind()
        return {"status": "failed", "reason": "Wrong credentials"}


# Routes
api.add_resource(HelloWorld, "/hlo")
api.add_resource(DatabaseMgmt, "/db")
