#!/usr/bin/env python3
"""
Tidsreg HTTP Server
HTTP/REST API wrapper for the Tidsreg MCP tools.
Can be exposed via localtunnel for use with ChatGPT Desktop or other HTTP clients.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from tidsreg_client import TidsregClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global Tidsreg client instance to maintain session
client = TidsregClient()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "authenticated": client.is_authenticated()
    })


@app.route('/api/login', methods=['POST'])
def login():
    """
    Authenticate with Tidsreg.

    Request body:
    {
        "username": "your_username",
        "password": "your_password"
    }
    """
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"error": "Missing username or password"}), 400

        result = client.login(
            username=data['username'],
            password=data['password']
        )

        if 'error' in result:
            return jsonify(result), 401

        return jsonify(result)

    except Exception as e:
        logger.exception("Login error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/customers', methods=['GET'])
def list_customers():
    """
    List all available customers.

    No parameters required.
    """
    try:
        result = client.list_customers()

        if 'error' in result:
            status_code = result.get('status', 500)
            return jsonify(result), status_code

        return jsonify(result)

    except Exception as e:
        logger.exception("List customers error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/projects', methods=['GET'])
def list_projects():
    """
    List projects for a customer.

    Query parameters:
    - customerId: Customer ID (required)
    - date: Date in format YYYY-MM-DD (required)
    """
    try:
        customer_id = request.args.get('customerId')
        date = request.args.get('date')

        if not customer_id or not date:
            return jsonify({"error": "Missing customerId or date parameter"}), 400

        result = client.list_projects(
            customerId=customer_id,
            date=date
        )

        if 'error' in result:
            status_code = result.get('status', 500)
            return jsonify(result), status_code

        return jsonify(result)

    except Exception as e:
        logger.exception("List projects error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/phases', methods=['GET'])
def list_phases():
    """
    List phases for a project.

    Query parameters:
    - projectId: Project ID (required)
    - date: Date in format YYYY-MM-DD (required)
    """
    try:
        project_id = request.args.get('projectId')
        date = request.args.get('date')

        if not project_id or not date:
            return jsonify({"error": "Missing projectId or date parameter"}), 400

        result = client.list_phases(
            projectId=project_id,
            date=date
        )

        if 'error' in result:
            status_code = result.get('status', 500)
            return jsonify(result), status_code

        return jsonify(result)

    except Exception as e:
        logger.exception("List phases error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/activities', methods=['GET'])
def list_activities():
    """
    List activities for a phase.

    Query parameters:
    - phaseId: Phase ID (required)
    - date: Date in format YYYY-MM-DD (required)
    """
    try:
        phase_id = request.args.get('phaseId')
        date = request.args.get('date')

        if not phase_id or not date:
            return jsonify({"error": "Missing phaseId or date parameter"}), 400

        result = client.list_activities(
            phaseId=phase_id,
            date=date
        )

        if 'error' in result:
            status_code = result.get('status', 500)
            return jsonify(result), status_code

        return jsonify(result)

    except Exception as e:
        logger.exception("List activities error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/kinds', methods=['GET'])
def list_kinds():
    """
    List kinds for a project and activity.

    Query parameters:
    - projectName: Project name (required)
    - activityName: Activity name (required)
    """
    try:
        project_name = request.args.get('projectName')
        activity_name = request.args.get('activityName')

        if not project_name or not activity_name:
            return jsonify({"error": "Missing projectName or activityName parameter"}), 400

        result = client.list_kinds(
            projectName=project_name,
            activityName=activity_name
        )

        if 'error' in result:
            status_code = result.get('status', 500)
            return jsonify(result), status_code

        return jsonify(result)

    except Exception as e:
        logger.exception("List kinds error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/tools', methods=['GET'])
def list_tools():
    """
    List all available API endpoints/tools.
    """
    tools = [
        {
            "name": "login",
            "method": "POST",
            "endpoint": "/api/login",
            "description": "Authenticate with Tidsreg",
            "body": {
                "username": "string",
                "password": "string"
            }
        },
        {
            "name": "list_customers",
            "method": "GET",
            "endpoint": "/api/customers",
            "description": "List all available customers"
        },
        {
            "name": "list_projects",
            "method": "GET",
            "endpoint": "/api/projects",
            "description": "List projects for a customer",
            "params": {
                "customerId": "string",
                "date": "YYYY-MM-DD"
            }
        },
        {
            "name": "list_phases",
            "method": "GET",
            "endpoint": "/api/phases",
            "description": "List phases for a project",
            "params": {
                "projectId": "string",
                "date": "YYYY-MM-DD"
            }
        },
        {
            "name": "list_activities",
            "method": "GET",
            "endpoint": "/api/activities",
            "description": "List activities for a phase",
            "params": {
                "phaseId": "string",
                "date": "YYYY-MM-DD"
            }
        },
        {
            "name": "list_kinds",
            "method": "GET",
            "endpoint": "/api/kinds",
            "description": "List kinds for a project and activity",
            "params": {
                "projectName": "string",
                "activityName": "string"
            }
        }
    ]

    return jsonify({"tools": tools})


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    port = 8000
    logger.info(f"Starting Tidsreg HTTP Server on port {port}")
    logger.info("Available endpoints:")
    logger.info("  POST /api/login")
    logger.info("  GET  /api/customers")
    logger.info("  GET  /api/projects")
    logger.info("  GET  /api/phases")
    logger.info("  GET  /api/activities")
    logger.info("  GET  /api/kinds")
    logger.info("  GET  /api/tools")
    logger.info("  GET  /health")
    logger.info("")
    logger.info(f"To expose via localtunnel: lt --port {port}")

    app.run(host='0.0.0.0', port=port, debug=False)
