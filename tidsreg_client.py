"""
Tidsreg HTTP Client
Handles authentication and data retrieval from Tidsreg time registration system.
"""

import requests
from typing import Dict, Any, Optional


class TidsregClient:
    """Client for interacting with the Tidsreg API."""

    BASE_URL = "https://tidsreg.trifork.com"

    def __init__(self):
        """Initialize the client with a persistent session."""
        self.session = requests.Session()
        self._authenticated = False

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle HTTP response and return JSON or error dict.

        Args:
            response: The HTTP response object

        Returns:
            Parsed JSON response or error dictionary
        """
        if response.status_code != 200:
            return {
                "error": f"HTTP request failed: {response.reason}",
                "status": response.status_code
            }

        try:
            return response.json()
        except ValueError:
            # If response is not JSON, return success indicator
            return {"success": True, "text": response.text}

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate with Tidsreg.

        Args:
            username: Tidsreg username
            password: Tidsreg password

        Returns:
            Dictionary with ok=True on success or error on failure
        """
        try:
            url = f"{self.BASE_URL}/Login?ReturnUrl=/"
            data = {
                "userName": username,
                "password": password
            }

            response = self.session.post(url, data=data, allow_redirects=True)

            if response.status_code == 200:
                # Check if we got an AuthTicket cookie
                if 'AuthTicket' in self.session.cookies:
                    self._authenticated = True
                    return {"ok": True}
                else:
                    return {"error": "Authentication failed - no AuthTicket cookie received", "status": 401}
            else:
                return {"error": f"Login failed: {response.reason}", "status": response.status_code}

        except Exception as e:
            return {"error": f"Login exception: {str(e)}", "status": 0}

    def list_customers(self) -> Dict[str, Any]:
        """
        Retrieve list of available customers.

        Returns:
            List of customer objects or error dictionary
        """
        try:
            url = f"{self.BASE_URL}/Find/SelectCustomers"
            params = {"mode": "0"}

            response = self.session.get(url, params=params)
            return self._handle_response(response)

        except Exception as e:
            return {"error": f"Failed to fetch customers: {str(e)}", "status": 0}

    def list_projects(self, customerId: str, date: str) -> Dict[str, Any]:
        """
        Retrieve list of projects for a specific customer.

        Args:
            customerId: The customer ID
            date: Date in format YYYY-MM-DD

        Returns:
            List of project objects or error dictionary
        """
        try:
            url = f"{self.BASE_URL}/Find/SelectProjects"
            params = {
                "mode": "0",
                "date": date,
                "customerId": customerId
            }

            response = self.session.get(url, params=params)
            return self._handle_response(response)

        except Exception as e:
            return {"error": f"Failed to fetch projects: {str(e)}", "status": 0}

    def list_phases(self, projectId: str, date: str) -> Dict[str, Any]:
        """
        Retrieve list of phases for a specific project.

        Args:
            projectId: The project ID
            date: Date in format YYYY-MM-DD

        Returns:
            List of phase objects or error dictionary
        """
        try:
            url = f"{self.BASE_URL}/Find/SelectPhases"
            params = {
                "mode": "0",
                "date": date,
                "projectId": projectId
            }

            response = self.session.get(url, params=params)
            return self._handle_response(response)

        except Exception as e:
            return {"error": f"Failed to fetch phases: {str(e)}", "status": 0}

    def list_activities(self, phaseId: str, date: str) -> Dict[str, Any]:
        """
        Retrieve list of activities for a specific phase.

        Args:
            phaseId: The phase ID
            date: Date in format YYYY-MM-DD

        Returns:
            List of activity objects or error dictionary
        """
        try:
            url = f"{self.BASE_URL}/Find/SelectActivities"
            params = {
                "mode": "0",
                "date": date,
                "phaseId": phaseId
            }

            response = self.session.get(url, params=params)
            return self._handle_response(response)

        except Exception as e:
            return {"error": f"Failed to fetch activities: {str(e)}", "status": 0}

    def list_kinds(self, projectName: str, activityName: str) -> Dict[str, Any]:
        """
        Retrieve list of kinds for a specific project and activity.

        Args:
            projectName: The project name
            activityName: The activity name

        Returns:
            List of kind objects or error dictionary
        """
        try:
            url = f"{self.BASE_URL}/Find/SelectKinds"
            params = {
                "mode": "0",
                "projectName": projectName,
                "activityName": activityName
            }

            response = self.session.get(url, params=params)
            return self._handle_response(response)

        except Exception as e:
            return {"error": f"Failed to fetch kinds: {str(e)}", "status": 0}

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return self._authenticated
