from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import jsonify, render_template, Blueprint, current_app
from flask_swagger_ui import get_swaggerui_blueprint
from marshmallow import Schema, fields

# Create ApiSpec
spec = APISpec(
    title="Gift List API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[MarshmallowPlugin()],
)

# Define schemas for API documentation
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)
    post_count = fields.Int(dump_only=True)

class PostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(required=True)
    author = fields.Str(dump_only=True)

# Register schemas with spec
spec.components.schema("User", schema=UserSchema)
spec.components.schema("Post", schema=PostSchema)

# Define paths/routes
def add_api_specs():
    # Users endpoints
    spec.path(
        path="/api/users",
        operations={
            "get": {
                "tags": ["Users"],
                "summary": "Get all users",
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Users"],
                "summary": "Create a new user",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/User"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "User created",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    }
                }
            }
        }
    )

    spec.path(
        path="/api/users/{id}",
        operations={
            "get": {
                "tags": ["Users"],
                "summary": "Get a specific user",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "404": {
                        "description": "User not found"
                    }
                }
            },
            "put": {
                "tags": ["Users"],
                "summary": "Update a user",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/User"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "User updated",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    },
                    "404": {
                        "description": "User not found"
                    }
                }
            },
            "delete": {
                "tags": ["Users"],
                "summary": "Delete a user",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "User deleted",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "properties": {"result": {"type": "boolean"}}}
                            }
                        }
                    },
                    "404": {
                        "description": "User not found"
                    }
                }
            }
        }
    )
    
    # Posts endpoints
    spec.path(
        path="/api/posts",
        operations={
            "get": {
                "tags": ["Posts"],
                "summary": "Get all posts",
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {"type": "array", "items": {"$ref": "#/components/schemas/Post"}}
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Posts"],
                "summary": "Create a new post",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Post"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Post created",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Post"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    }
                }
            }
        }
    )

    spec.path(
        path="/api/posts/{id}",
        operations={
            "get": {
                "tags": ["Posts"],
                "summary": "Get a specific post",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Post"}
                            }
                        }
                    },
                    "404": {
                        "description": "Post not found"
                    }
                }
            },
            "put": {
                "tags": ["Posts"],
                "summary": "Update a post",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Post"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Post updated",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Post"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    },
                    "404": {
                        "description": "Post not found"
                    }
                }
            },
            "delete": {
                "tags": ["Posts"],
                "summary": "Delete a post",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Post deleted",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "properties": {"result": {"type": "boolean"}}}
                            }
                        }
                    },
                    "404": {
                        "description": "Post not found"
                    }
                }
            }
        }
    )

    spec.path(
        path="/api/users/{id}/posts",
        operations={
            "get": {
                "tags": ["Users", "Posts"],
                "summary": "Get posts by a specific user",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {"type": "array", "items": {"$ref": "#/components/schemas/Post"}}
                            }
                        }
                    },
                    "404": {
                        "description": "User not found"
                    }
                }
            }
        }
    )

def create_swagger_blueprint(app):
    # Add swagger specs
    add_api_specs()
    
    # Create a blueprint to serve the swagger specification as JSON
    swagger_bp = Blueprint('swagger', __name__)
    
    @swagger_bp.route('/swagger.json')
    def get_swagger():
        return jsonify(spec.to_dict())
    
    # Set up swagger-ui
    SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI
    API_URL = '/swagger.json'  # Our API url (can be a local file or url)
    
    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Flask SQLAlchemy API"
        }
    )
    
    # Register blueprints
    app.register_blueprint(swagger_bp)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    return swagger_bp