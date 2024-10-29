import jwt
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource  # used for REST API building
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
from model.section import Section

"""
This Blueprint object is used to define APIs for the Post model.
- Blueprint is used to modularize application files.
- This Blueprint is registered to the Flask app in main.py.
"""
section_api = Blueprint('section_api', __name__, url_prefix='/api')

"""
The Api object is connected to the Blueprint object to define the API endpoints.
- The API object is used to add resources to the API.
- The objects added are mapped to code that contains the actions for the API.
- For more information, refer to the API docs: https://flask-restful.readthedocs.io/en/latest/api.html
"""
api = Api(section_api)

class SectionAPI:
    """
    Define the API CRUD endpoints for the Section model.
    There are four operations that correspond to common HTTP methods:
    - post: create a new section 
    - get: read sections
    - put: update a section
    - delete: delete a section 
    """
    class _CRUD(Resource):
        @token_required()
        def post(self):
            # Obtain the current user from the token required setting in the global context
            current_user = g.current_user
            # Obtain the request data sent by the RESTful client API
            data = request.get_json()
            # Create a new section object using the data from the request
            section = Section(data['name'], data['theme'])
            # Save the section object using the Object Relational Mapper (ORM) method defined in the model
            section.create()
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify(section.read())

        def get(self):
            # Find all the posts by the current user
            sections = Section.query.all()
            # Prepare a JSON list of all the ectionsi, uses for loop shortcut called list comprehension
            json_ready = [section.read() for section in sections]
            # Return a JSON list, converting Python dictionaries to JSON format
            return jsonify(json_ready)

    """
    Map the _CRUD class to the API endpoints for /section
    - The API resource class inherits from flask_restful.Resource.
    - The _CRUD class defines the HTTP methods for the API.
    """
    api.add_resource(_CRUD, '/section')