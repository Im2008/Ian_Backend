import jwt
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource  # used for REST API building
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
from model.group import Group

"""
This Blueprint object is used to define APIs for the Group model.
- Blueprint is used to modularize application files.
- This Blueprint is registered to the Flask app in main.py.
"""
group_api = Blueprint('group_api', __name__, url_prefix='/api')

"""
The Api object is connected to the Blueprint object to define the API endpoints.
- The API object is used to add resources to the API.
- The objects added are mapped to code that contains the actions for the API.
- For more information, refer to the API docs: https://flask-restful.readthedocs.io/en/latest/api.html
"""
api = Api(group_api)

class GroupAPI:
    """
    Define the API CRUD endpoints for the Group model.
    There are four operations that correspond to common HTTP methods:
    - post: create a new group
    - get: read groups
    - put: update a group
    - delete: delete a group
    """
    class _CRUD(Resource):
        @token_required()
        def post(self):
            """
            Create a new group.
            """
            # Obtain the current user from the token required setting in the global context
            current_user = g.current_user
            # Obtain the request data sent by the RESTful client API
            data = request.get_json()
            # Create a new group object using the data from the request
            group = Group(data['name'], data['section_id'], data.get('moderator_id', current_user.id))
            # Save the group object using the Object Relational Mapper (ORM) method defined in the model
            group.create()
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify(group.read())

        def get(self):
            """
            Retrieve all groups.
            """
            # Find all the groups
            groups = Group.query.all()
            # Prepare a JSON list of all the groups, using list comprehension
            json_ready = [group.read() for group in groups]
            # Return a JSON list, converting Python dictionaries to JSON format
            return jsonify(json_ready)

        @token_required()
        def put(self):
            """
            Update a group.
            """
            # Obtain the current user from the token required setting in the global context
            current_user = g.current_user
            # Obtain the request data sent by the RESTful client API
            data = request.get_json()
            # Find the group to update
            group = Group.query.get(data['id'])
            if group is None:
                return {'message': 'Group not found'}, 404
            # Update the group object using the data from the request
            group._name = data['name']
            group._section_id = data['section_id']
            group._moderator_id = data.get('moderator_id', current_user.id)
            # Save the group object using the Object Relational Mapper (ORM) method defined in the model
            group.update()
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify(group.read())

        @token_required()
        def delete(self):
            """
            Delete a group.
            """
            # Obtain the request data sent by the RESTful client API
            data = request.get_json()
            # Find the group to delete
            group = Group.query.get(data['id'])
            if group is None:
                return {'message': 'Group not found'}, 404
            # Delete the group object using the Object Relational Mapper (ORM) method defined in the model
            group.delete()
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify({'message': 'Group deleted'})

    """
    Map the _CRUD class to the API endpoints for /group.
    - The API resource class inherits from flask_restful.Resource.
    - The _CRUD class defines the HTTP methods for the API.
    """
    api.add_resource(_CRUD, '/group')