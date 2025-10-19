"""
Tidsreg HTTP Client
Handles authentication and data retrieval from Tidsreg time registration system.
"""

import requests
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class TidsregClient:
    """Client for interacting with the Tidsreg API."""

    BASE_URL = "https://tidsreg.trifork.com"

    def __init__(self):
        """Initialize the client with a persistent session."""
        self.session = requests.Session()
        self._authenticated = False

    @staticmethod
    def _convert_date_to_hours_format(date_str: str) -> str:
        """
        Convert date from YYYY-MM-DD to DD-MM-YYYY format for Hours endpoint.

        Args:
            date_str: Date in YYYY-MM-DD format

        Returns:
            Date in DD-MM-YYYY format
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d-%m-%Y")
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD, got {date_str}") from e

    @staticmethod
    def _convert_date_to_api_format(date_str: str) -> str:
        """
        Convert date from DD-MM-YYYY to YYYY-MM-DD format for API endpoints.

        Args:
            date_str: Date in DD-MM-YYYY format

        Returns:
            Date in YYYY-MM-DD format
        """
        try:
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected DD-MM-YYYY, got {date_str}") from e

    @staticmethod
    def get_week_dates(year: Optional[int] = None, week: Optional[int] = None) -> Dict[str, Any]:
        """
        Get start and end dates for a specific week.

        Args:
            year: Year (defaults to current year)
            week: ISO week number (defaults to current week)

        Returns:
            Dictionary with start_date, end_date, year, and week
        """
        try:
            if year is None or week is None:
                now = datetime.now()
                year = year or now.isocalendar()[0]
                week = week or now.isocalendar()[1]

            # Get first day of the week (Monday) using ISO week format
            # ISO 8601: %G=year, %V=week, %u=day (1=Monday)
            first_day = datetime.strptime(f"{year}-W{week:02d}-1", "%G-W%V-%u")
            # Get last day of the week (Sunday)
            last_day = first_day + timedelta(days=6)

            return {
                "year": year,
                "week": week,
                "start_date": first_day.strftime("%Y-%m-%d"),
                "end_date": last_day.strftime("%Y-%m-%d"),
                "start_date_formatted": first_day.strftime("%d-%m-%Y"),
                "end_date_formatted": last_day.strftime("%d-%m-%Y")
            }
        except Exception as e:
            return {"error": f"Failed to calculate week dates: {str(e)}"}

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

    def navigate_to_date(self, date: str) -> Dict[str, Any]:
        """
        Navigate to a specific date in Tidsreg.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            Dictionary with success status and date information
        """
        try:
            # Convert to Hours endpoint format (DD-MM-YYYY)
            hours_date = self._convert_date_to_hours_format(date)
            url = f"{self.BASE_URL}/Hours/{hours_date}"

            response = self.session.get(url, allow_redirects=True)

            if response.status_code == 200:
                return {
                    "ok": True,
                    "date": date,
                    "date_formatted": hours_date,
                    "message": f"Successfully navigated to {date}"
                }
            else:
                return {
                    "error": f"Navigation failed: {response.reason}",
                    "status": response.status_code
                }

        except ValueError as e:
            return {"error": str(e), "status": 0}
        except Exception as e:
            return {"error": f"Navigation exception: {str(e)}", "status": 0}

    def navigate_to_week(self, year: Optional[int] = None, week: Optional[int] = None) -> Dict[str, Any]:
        """
        Navigate to a specific week in Tidsreg.

        Args:
            year: Year (defaults to current year)
            week: ISO week number (defaults to current week)

        Returns:
            Dictionary with success status and week information
        """
        try:
            week_info = self.get_week_dates(year, week)

            if "error" in week_info:
                return week_info

            # Navigate to the start of the week
            nav_result = self.navigate_to_date(week_info["start_date"])

            if "error" in nav_result:
                return nav_result

            return {
                "ok": True,
                "week_info": week_info,
                "message": f"Successfully navigated to week {week_info['week']} of {week_info['year']}"
            }

        except Exception as e:
            return {"error": f"Week navigation exception: {str(e)}", "status": 0}

    def list_customers(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve list of available customers.

        Args:
            date: Optional date in YYYY-MM-DD format. If provided, retrieves customers for that specific date.

        Returns:
            List of customer objects or error dictionary
        """
        try:
            url = f"{self.BASE_URL}/Find/SelectCustomers"
            params = {"mode": "0"}

            # Add date parameter if provided (matches navigation behavior)
            if date:
                params["date"] = date

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

    def _get_day_index_for_date(self, date: str, week_start_date: str) -> int:
        """
        Get the index (0-6) for a specific date within a week.

        Args:
            date: Date in YYYY-MM-DD format
            week_start_date: Week start date in YYYY-MM-DD format

        Returns:
            Day index (0=Monday, 6=Sunday)
        """
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            week_start_obj = datetime.strptime(week_start_date, "%Y-%m-%d")
            delta = (date_obj - week_start_obj).days
            return delta if 0 <= delta <= 6 else 0
        except:
            return 0

    def get_registered_hours(self, date: str) -> Dict[str, Any]:
        """
        Retrieve registered hours for a specific date/week.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            Dictionary with registered hours data including:
            - registrations: List of time entries
            - totals: Summary of hours
            - week_info: Week information
        """
        try:
            # Convert to Hours endpoint format (DD-MM-YYYY)
            hours_date = self._convert_date_to_hours_format(date)
            url = f"{self.BASE_URL}/Hours/{hours_date}"

            response = self.session.get(url, allow_redirects=True)

            if response.status_code != 200:
                return {
                    "error": f"Failed to fetch hours: {response.reason}",
                    "status": response.status_code
                }

            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # Extract registrations data
            registrations = self._parse_registrations(soup)

            # Extract totals
            totals = self._parse_totals(soup)

            # Get week information
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            year, week, _ = date_obj.isocalendar()
            week_info = self.get_week_dates(year, week)

            # Get day index for the requested date
            day_index = self._get_day_index_for_date(date, week_info["start_date"])

            # Extract hours for the specific day
            day_entries = []
            day_names = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

            for reg in registrations:
                if reg.get('level') == 'groupLevel4' and 'hours' in reg and 'data' in reg:
                    hours_list = reg['hours']
                    if len(hours_list) > day_index and hours_list[day_index]:
                        # Extract activity name (first element in data)
                        activity_name = reg['data'][0] if reg['data'] else "Unknown"
                        # Clean up the name
                        activity_name = activity_name.split('(')[0].strip()

                        day_entries.append({
                            "activity": activity_name,
                            "hours": hours_list[day_index],
                            "billable": "(Billable)" in reg['data'][0] if reg['data'] else False,
                            "week_total": reg['data'][8] if len(reg['data']) > 8 else "0",
                            "hours_all_days": hours_list
                        })

            # Calculate total hours for the day and check if suspicious
            total_hours = 0.0
            for entry in day_entries:
                try:
                    # Convert European format (4,50) to float
                    hours_str = entry['hours'].replace(',', '.')
                    total_hours += float(hours_str)
                except (ValueError, AttributeError):
                    pass

            # Check if day is suspicious (weekday with < 7.5 hours)
            warnings = []
            is_weekday = day_index < 5  # Monday=0 to Friday=4
            if is_weekday and total_hours < 7.5 and total_hours > 0:
                warnings.append({
                    "type": "suspicious_hours",
                    "message": f"⚠️ Seulement {total_hours:.2f}h enregistrées pour un jour de semaine ({day_names[day_index]})",
                    "suggestion": "Vérifier si toutes les heures ont bien été enregistrées"
                })

            return {
                "ok": True,
                "date": date,
                "date_formatted": hours_date,
                "day_name": day_names[day_index] if day_index < 7 else "Unknown",
                "day_index": day_index,
                "week_info": week_info,
                "hours_for_day": day_entries,
                "total_hours_for_day": total_hours,
                "warnings": warnings,
                "registrations": registrations,
                "totals": totals,
                "raw_html_size": len(response.text)
            }

        except ValueError as e:
            return {"error": str(e), "status": 0}
        except Exception as e:
            return {"error": f"Failed to retrieve hours: {str(e)}", "status": 0}

    def _parse_registrations(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parse time registrations from HTML.

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            List of registration dictionaries
        """
        registrations = []

        try:
            # Look for registration tables - typically have classes like 'groupLevel*'
            # Find all input fields for hours (typically named like 'registration-hours')
            hour_inputs = soup.find_all('input', {'class': lambda x: x and 'registration-hours' in x})

            # Find all registration rows
            for input_field in hour_inputs:
                # Try to extract registration info from the row
                row = input_field.find_parent('tr')
                if not row:
                    continue

                # Get the customer/project/phase/activity info from the hierarchy
                registration = {
                    'value': input_field.get('value', ''),
                    'id': input_field.get('id', ''),
                    'name': input_field.get('name', ''),
                    'disabled': input_field.has_attr('disabled')
                }

                # Try to find associated labels or headers
                parent_table = input_field.find_parent('table')
                if parent_table:
                    # Look for group headers (customer, project, phase, activity)
                    headers = parent_table.find_all('td', {'class': lambda x: x and any(h in str(x) for h in ['customer-header', 'project-header', 'phase-header', 'activity'])})
                    registration['context'] = [h.get_text(strip=True) for h in headers]

                if registration['value']:  # Only include if there's a value
                    registrations.append(registration)

            # Also look for existing registrations in a more structured way
            time_registrations = soup.find(id='TimeRegistrations')
            if time_registrations:
                # Find all tables with registration data
                for table in time_registrations.find_all('table'):
                    # Extract customer/project/phase/activity hierarchy
                    for level_class in ['groupLevel1', 'groupLevel2', 'groupLevel3', 'groupLevel4']:
                        level_rows = table.find_all('tr', {'class': lambda x: x and level_class in str(x)})
                        for row in level_rows:
                            # Extract text content and hours
                            cells = row.find_all('td')
                            if cells:
                                row_data = {
                                    'level': level_class,
                                    'data': [cell.get_text(strip=True) for cell in cells]
                                }
                                # Look for input fields in this row
                                inputs = row.find_all('input', {'class': 'registration-hours'})
                                if inputs:
                                    row_data['hours'] = [inp.get('value', '') for inp in inputs]

                                if row_data['data']:  # Only add if there's content
                                    registrations.append(row_data)

        except Exception as e:
            registrations.append({"error": f"Error parsing registrations: {str(e)}"})

        return registrations

    def _parse_totals(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Parse totals from HTML.

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            Dictionary with totals information
        """
        totals = {}

        try:
            # Look for total fields - typically have classes containing 'total' or 'sum'
            total_elements = soup.find_all(class_=lambda x: x and any(t in str(x) for t in ['total', 'sum', 'Sum']))

            for element in total_elements:
                # Extract the total value
                value = element.get_text(strip=True)
                class_name = ' '.join(element.get('class', []))

                if value and value.replace('.', '').replace(',', '').replace('-', '').isdigit():
                    totals[class_name] = value

            # Also look for specific total containers
            for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                day_total = soup.find(id=f'totalHours{day.capitalize()}')
                if day_total:
                    totals[f'{day}_total'] = day_total.get_text(strip=True)

        except Exception as e:
            totals['error'] = f"Error parsing totals: {str(e)}"

        return totals

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return self._authenticated
