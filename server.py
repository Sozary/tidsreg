#!/usr/bin/env python3
"""
Tidsreg MCP Server
Implements the Model Context Protocol (JSON-RPC 2.0) for Tidsreg integration.
"""

import sys
import json
import logging
from typing import Dict, Any, Optional
from tidsreg_client import TidsregClient

# Configure logging to stderr (stdout is reserved for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Global Tidsreg client instance to maintain session across requests
client = TidsregClient()


def get_tool_definitions() -> list:
    """Return the list of available tools in MCP format."""
    return [
        {
            "name": "login",
            "description": "Authenticate with Tidsreg using username and password. Must be called before using other tools.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Tidsreg username"
                    },
                    "password": {
                        "type": "string",
                        "description": "Tidsreg password"
                    }
                },
                "required": ["username", "password"]
            }
        },
        {
            "name": "list_customers",
            "description": "Retrieve the list of all available customers from Tidsreg",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "list_projects",
            "description": "Retrieve the list of projects for a specific customer",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "customerId": {
                        "type": "string",
                        "description": "The customer ID"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in format YYYY-MM-DD"
                    }
                },
                "required": ["customerId", "date"]
            }
        },
        {
            "name": "list_phases",
            "description": "Retrieve the list of phases for a specific project",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "projectId": {
                        "type": "string",
                        "description": "The project ID"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in format YYYY-MM-DD"
                    }
                },
                "required": ["projectId", "date"]
            }
        },
        {
            "name": "list_activities",
            "description": "Retrieve the list of activities for a specific phase",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "phaseId": {
                        "type": "string",
                        "description": "The phase ID"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in format YYYY-MM-DD"
                    }
                },
                "required": ["phaseId", "date"]
            }
        },
        {
            "name": "list_kinds",
            "description": "Retrieve the list of kinds for a specific project and activity combination",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "projectName": {
                        "type": "string",
                        "description": "The project name"
                    },
                    "activityName": {
                        "type": "string",
                        "description": "The activity name"
                    }
                },
                "required": ["projectName", "activityName"]
            }
        }
    ]


def handle_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the initialize request.

    Args:
        params: Initialize parameters from the client

    Returns:
        Server capabilities and info
    """
    logger.info("Initializing MCP server")
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "tidsreg-mcp",
            "version": "1.0.0"
        }
    }


def handle_tools_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the tools/list request.

    Args:
        params: Request parameters (unused)

    Returns:
        List of available tools
    """
    logger.info("Listing available tools")
    return {
        "tools": get_tool_definitions()
    }


def handle_tools_call(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the tools/call request.

    Args:
        params: Tool call parameters including name and arguments

    Returns:
        Tool execution result
    """
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")

    # Route to appropriate client method
    try:
        if tool_name == "login":
            result = client.login(
                username=arguments["username"],
                password=arguments["password"]
            )
        elif tool_name == "list_customers":
            result = client.list_customers()
        elif tool_name == "list_projects":
            result = client.list_projects(
                customerId=arguments["customerId"],
                date=arguments["date"]
            )
        elif tool_name == "list_phases":
            result = client.list_phases(
                projectId=arguments["projectId"],
                date=arguments["date"]
            )
        elif tool_name == "list_activities":
            result = client.list_activities(
                phaseId=arguments["phaseId"],
                date=arguments["date"]
            )
        elif tool_name == "list_kinds":
            result = client.list_kinds(
                projectName=arguments["projectName"],
                activityName=arguments["activityName"]
            )
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({"error": f"Unknown tool: {tool_name}"})
                    }
                ],
                "isError": True
            }

        # Format result as MCP tool response
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False)
                }
            ]
        }

    except KeyError as e:
        error_msg = f"Missing required argument: {str(e)}"
        logger.error(error_msg)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"error": error_msg})
                }
            ],
            "isError": True
        }
    except Exception as e:
        error_msg = f"Tool execution failed: {str(e)}"
        logger.error(error_msg)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"error": error_msg})
                }
            ],
            "isError": True
        }


def handle_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Route JSON-RPC request to appropriate handler.

    Args:
        request: JSON-RPC request object

    Returns:
        JSON-RPC response object, or None for notifications
    """
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")

    # Handle notifications (no id = no response needed)
    if request_id is None:
        logger.debug(f"Received notification: {method}")
        # Notifications don't get a response
        if method == "notifications/initialized":
            logger.info("Client initialized")
        return None

    try:
        if method == "initialize":
            result = handle_initialize(params)
        elif method == "tools/list":
            result = handle_tools_list(params)
        elif method == "tools/call":
            result = handle_tools_call(params)
        else:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                },
                "id": request_id
            }

        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }

    except Exception as e:
        logger.exception(f"Error handling request: {e}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            },
            "id": request_id
        }


def main():
    """Main server loop - read from stdin, write to stdout."""
    logger.info("Tidsreg MCP Server starting...")

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                logger.debug(f"Received request: {request}")

                response = handle_request(request)

                # Only send response if it's not a notification (response is not None)
                if response is not None:
                    logger.debug(f"Sending response: {response}")
                    print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    },
                    "id": None
                }
                print(json.dumps(error_response), flush=True)

    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.exception(f"Unexpected error in main loop: {e}")
    finally:
        logger.info("Tidsreg MCP Server shutting down")


if __name__ == "__main__":
    main()
