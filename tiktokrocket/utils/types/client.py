"""
File: client.py
Created: 09.04.2025

This source code constitutes confidential information and is the 
exclusive property of the Author. You are granted a non-exclusive, 
non-transferable license to use this code for personal, non-commercial 
purposes only.

STRICTLY PROHIBITED:
- Any form of reproduction, distribution, or modification for commercial purposes
- Selling, licensing, sublicensing or otherwise monetizing this code
- Removing or altering this proprietary notice

Violations will be prosecuted to the maximum extent permitted by law.
For commercial licensing inquiries, contact author.

Author: me@eugconrad.com
Contacts:
  • Telegram: @eugconrad

Website: https://eugconrad.com
Copyright © 2025 All Rights Reserved
"""
from typing import Optional, Dict, Any

import requests
from loguru import logger

from tiktokrocket.data.config import ApiConfig


class Client:
    """
    A client class for interacting with the TikTokRocket API, providing methods
    for authentication and user information retrieval.

    Attributes:
        _access_token (str): The access token for API authentication.
        _base_url (str): The base URL of the API.
        _timeout (int): The request timeout in seconds.
        _session (requests.Session): The session object for making HTTP requests.

    Methods:
        __init__(access_token, base_url, timeout): Initializes the client with
        authentication details and configuration.

        _make_request(method, endpoint, headers, json): Sends an HTTP request to
        the specified API endpoint and returns the JSON response.

        login(login, password): Authenticates the user and retrieves an access
        token.

        get_me(): Retrieves the current user's information from the API.
    """

    def __init__(
            self,
            access_token: str,
            base_url: str = ApiConfig.BASE_URL,
            timeout: int = ApiConfig.REQUEST_TIMEOUT
    ) -> None:
        """
        Initializes a new instance of the Client class for interacting with the TikTokRocket API.

        Args:
            access_token (str): The access token for authenticating API requests.
            base_url (str, optional): The base URL of the API. Defaults to ApiConfig.BASE_URL.
            timeout (int, optional): The request timeout in seconds. Defaults to
            ApiConfig.REQUEST_TIMEOUT.
        """
        self._access_token = access_token
        self._base_url = base_url
        self._timeout = timeout
        self._session = requests.Session()
        self._session.timeout = timeout

    def _make_request(
            self,
            method: str,
            endpoint: str,
            headers: Optional[Dict[str, str]] = None,
            json: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Sends an HTTP request to the specified API endpoint.

        Args:
            method (str): The HTTP method to use (e.g., 'GET', 'POST').
            endpoint (str): The API endpoint to send the request to.
            headers (Optional[Dict[str, str]]): Optional HTTP headers to include in the request.
            json (Optional[Dict[str, Any]]): Optional JSON payload to include in the request.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API if the request is successful,
            otherwise None.
        """
        url = self._base_url + endpoint.lstrip("/")
        try:
            response = self._session.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"[API] Ошбка запроса: {e}")
            return None

    def login(self, login: str, password: str) -> Optional[str]:
        """
        Authenticates the user by sending login credentials to the API.

        Args:
            login (str): The user's login identifier.
            password (str): The user's password.

        Returns:
            Optional[str]: The access token if authentication is successful,
            otherwise None.
        """
        data = self._make_request(
            method="POST",
            endpoint="api/auth/login",
            json={"login": login, "password": password},
        )
        if data:
            self._access_token = data.get("access_token")
            return self._access_token
        return None

    def get_me(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves the current user's information from the API.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing user information
            if the request is successful, otherwise None.
        """
        return self._make_request(
            method="GET",
            endpoint="api/user/get_me",
            headers={
                ApiConfig.AUTH_HEADER: self._access_token,
                "Content-Type": "application/json; charset=utf-8",
            },
        )
