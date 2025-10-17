# Tidsreg MCP Server

Model Context Protocol (MCP) server for interacting with the Tidsreg time registration system at https://tidsreg.trifork.com.

## Overview

This MCP server allows LLMs to authenticate and retrieve hierarchical data from Tidsreg:
- Customers
- Projects (per customer)
- Phases (per project)
- Activities (per phase)
- Kinds (per project/activity combination)

## Installation

1. Clone or download this directory
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### With Claude Desktop

Add the server to your Claude Desktop configuration:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "tidsreg": {
      "command": "python3",
      "args": ["/absolute/path/to/tidsreg_mcp/server.py"]
    }
  }
}
```

Replace `/absolute/path/to/tidsreg_mcp/` with the actual path to this directory.

### With Other MCP Clients

Any MCP-compatible client can connect to this server by running:

```bash
python3 server.py
```

The server communicates via stdin/stdout using JSON-RPC 2.0.

### With ChatGPT Online (Custom GPT Actions)

For using this API with ChatGPT Online via custom GPT Actions, see the complete guide in **[CHATGPT_GUIDE.md](CHATGPT_GUIDE.md)**. This includes:
- Multiple deployment options (localtunnel, ngrok, cloud)
- OpenAPI schema configuration
- Step-by-step GPT creation instructions
- Troubleshooting tips

Quick files reference:
- `openapi.yaml` - OpenAPI schema for GPT Actions
- `gpt_instructions.txt` - Ready-to-paste GPT instructions
- `CHATGPT_GUIDE.md` - Complete setup guide

### With ChatGPT Desktop or HTTP Clients (via Localtunnel)

For clients that don't support stdin/stdout MCP protocol (like ChatGPT Desktop), use the HTTP server:

1. Start the HTTP server:

```bash
python3 http_server.py
```

The server will run on **port 8000**.

2. Expose it via localtunnel:

```bash
npm install -g localtunnel
lt --port 8000
```

You'll get a public URL like `https://xyz.loca.lt` that you can use with ChatGPT Desktop or any HTTP client.

3. Use the API endpoints:

```bash
# Login first
curl -X POST https://xyz.loca.lt/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Then call other endpoints
curl https://xyz.loca.lt/api/customers
curl "https://xyz.loca.lt/api/projects?customerId=11166&date=2025-10-13"
```

Available HTTP endpoints:
- `POST /api/login` - Authenticate
- `GET /api/customers` - List customers
- `GET /api/projects?customerId={id}&date={date}` - List projects
- `GET /api/phases?projectId={id}&date={date}` - List phases
- `GET /api/activities?phaseId={id}&date={date}` - List activities
- `GET /api/kinds?projectName={name}&activityName={name}` - List kinds
- `GET /api/tools` - List all available endpoints
- `GET /health` - Health check

## Available Tools

### 1. login

Authenticate with Tidsreg. **Must be called before using any other tools.**

Parameters:
- `username` (string, required): Your Tidsreg username
- `password` (string, required): Your Tidsreg password

Example:
```json
{
  "name": "login",
  "arguments": {
    "username": "your_username",
    "password": "your_password"
  }
}
```

Response:
```json
{
  "ok": true
}
```

### 2. list_customers

Retrieve all available customers.

Parameters: None

Response example:
```json
[
  {
    "id": 11166,
    "name": "&Money ApS"
  },
  ...
]
```

### 3. list_projects

Retrieve projects for a specific customer.

Parameters:
- `customerId` (string, required): The customer ID
- `date` (string, required): Date in format YYYY-MM-DD

Example:
```json
{
  "name": "list_projects",
  "arguments": {
    "customerId": "11166",
    "date": "2025-10-13"
  }
}
```

### 4. list_phases

Retrieve phases for a specific project.

Parameters:
- `projectId` (string, required): The project ID
- `date` (string, required): Date in format YYYY-MM-DD

Example:
```json
{
  "name": "list_phases",
  "arguments": {
    "projectId": "12345",
    "date": "2025-10-13"
  }
}
```

### 5. list_activities

Retrieve activities for a specific phase.

Parameters:
- `phaseId` (string, required): The phase ID
- `date` (string, required): Date in format YYYY-MM-DD

Example:
```json
{
  "name": "list_activities",
  "arguments": {
    "phaseId": "67890",
    "date": "2025-10-13"
  }
}
```

### 6. list_kinds

Retrieve kinds for a specific project and activity combination.

Parameters:
- `projectName` (string, required): The project name
- `activityName` (string, required): The activity name

Example:
```json
{
  "name": "list_kinds",
  "arguments": {
    "projectName": "My Project",
    "activityName": "Development"
  }
}
```

## Usage Flow

1. **Authenticate first**: Always call `login` before any other tool
2. **Navigate hierarchically**:
   - Get customers with `list_customers`
   - Get projects for a customer with `list_projects`
   - Get phases for a project with `list_phases`
   - Get activities for a phase with `list_activities`
   - Get kinds with `list_kinds`

## Error Handling

If a request fails, the response will contain an error object:

```json
{
  "error": "Description of the error",
  "status": 401
}
```

Common status codes:
- `401`: Authentication failed or required
- `404`: Resource not found
- `500`: Server error
- `0`: Network or connection error

## Session Management

The server maintains a single session across all requests. Once you authenticate with `login`, the session cookies (AuthTicket) are automatically preserved for subsequent requests.

## Development

### Project Structure

```
tidsreg/
├── server.py              # MCP server (JSON-RPC 2.0 stdin/stdout)
├── http_server.py         # HTTP/REST API server (port 8000)
├── tidsreg_client.py      # HTTP client for Tidsreg
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── CHATGPT_GUIDE.md      # Guide for ChatGPT Online integration
├── openapi.yaml          # OpenAPI schema for GPT Actions
└── gpt_instructions.txt  # GPT configuration instructions
```

### Testing

You can test the server manually by sending JSON-RPC requests via stdin:

```bash
python3 server.py
```

Then type (or pipe) JSON-RPC requests:

```json
{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}, "id": 1}
{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}
{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "login", "arguments": {"username": "test", "password": "test"}}, "id": 3}
```

### Logging

The server logs to stderr (stdout is reserved for JSON-RPC communication). You can monitor the logs while running:

```bash
python3 server.py 2> server.log
```

## Requirements

- Python 3.11+
- requests >= 2.31.0
- flask >= 3.0.0 (for HTTP server)
- flask-cors >= 4.0.0 (for HTTP server)

## License

This is a custom integration tool for Tidsreg. Use in accordance with Trifork's terms of service.

## Support

For issues or questions, please contact the maintainer or refer to the Tidsreg documentation.
