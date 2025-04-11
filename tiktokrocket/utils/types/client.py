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
    """Класс для взаимодействия с API TikTokRocket."""

    def __init__(
            self,
            access_token: str,
            base_url: str = ApiConfig.BASE_URL,
            timeout: int = ApiConfig.REQUEST_TIMEOUT
    ):
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
        """Выполняет HTTP-запрос к API."""
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
            logger.error(f"API request failed: {e}")
            return None

    def login(self, login: str, password: str) -> Optional[str]:
        data = self._make_request(
            method="POST",
            endpoint="api/auth/login",
            json={"login": login, "password": password},
        )
        if data:
            self._access_token = data.get("access_token")
            return self._access_token
        else:
            return None

    def get_me(self) -> Optional[Dict[str, Any]]:
        return self._make_request(
            method="GET",
            endpoint="api/user/get_me",
            headers={
                ApiConfig.AUTH_HEADER: self._access_token,
                "Content-Type": "application/json; charset=utf-8",
            },
        )
