"""
File: grizzly.py
Created: 14.04.2025

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
import json
from abc import ABC
from typing import Optional

from .base import BaseAPI


class GrizzlySMS(BaseAPI, ABC):
    """
    GrizzlySMS is a concrete implementation of the BaseAPI for interacting with the Grizzly SMS provider.

    Methods:
        __init__(api_key: str) -> None: Initializes the GrizzlySMS instance with the provided API key.
        get_number(country: str, max_price: Optional[None], service: str) -> dict: Retrieves a phone number.
        _set_status(activation_id: int, status: int) -> str: Sets the status of a request.
        get_status(activation_id: int) -> dict: Retrieves the status of a request.
        get_balance() -> float: Retrieves the account balance.
        get_prices(country: str, service: str) -> float: Retrieves pricing information.
        confirm_activation(activation_id: int) -> str: Confirms the activation of a service.
        cancel_activation(activation_id: int) -> str: Cancels the activation of a service.
        get_code(activation_id: int) -> int | None: Retrieves a code from the service.
    """
    def __init__(self, api_key: str) -> None:
        """
        Initializes the GrizzlySMS instance with the provided API key and sets the
        provider-specific base URL and provider name.

        Args:
            api_key (str): The API key used for authentication with the Grizzly SMS provider.
        """
        super().__init__(api_key, "http://api.7grizzlysms.com/stubs/handler_api.php")
        self.provider = "Grizzly SMS"

    async def get_number(self, country: str, service: str = "lf") -> dict:
        """
        Asynchronously retrieves a phone number from the Grizzly SMS provider.

        Args:
            country (str): The country code for which to retrieve the phone number.
            service (str): The service identifier, defaults to "lf".

        Returns:
            dict: A dictionary containing the activation ID and the phone number.

        Raises:
            Exception: If the response from the API does not start with "ACCESS_NUMBER".
        """
        params = {
            "api_key": self.api_key,
            "action": "getNumber",
            "service": service,
            "country": country
        }
        response_text = await self._make_request(params=params)
        if response_text.startswith("ACCESS_NUMBER"):
            _, activation_id, number = response_text.split(":")
            return {"activation_id": int(activation_id), "number": int(number)}
        raise Exception(response_text)

    async def _set_status(self, activation_id: int, status: int) -> str:
        """
        Asynchronously sets the status of a request with the given activation ID and status.

        Args:
            activation_id (int): The ID of the activation to update.
            status (int): The new status to set for the activation.

        Returns:
            str: The response text from the API if it starts with "ACCESS_".

        Raises:
            Exception: If the response from the API does not start with "ACCESS_".
        """
        params = {
            "api_key": self.api_key,
            "action": "setStatus",
            "id": activation_id,
            "status": status
        }
        response_text = await self._make_request(params=params)
        if response_text.startswith("ACCESS_"):
            return response_text
        raise Exception(response_text)

    async def get_status(self, activation_id: int) -> dict:
        """
        Asynchronously retrieves the status of a request from the Grizzly SMS provider.

        Args:
            activation_id (int): The ID of the activation to check the status for.

        Returns:
            dict: A dictionary containing the status of the request. If the status is "success",
            the dictionary includes the code. If the status is "pending" or "error", it includes
            a message.

        Raises:
            Exception: If the response from the API is not recognized.
        """
        params = {
            "api_key": self.api_key,
            "action": "getStatus",
            "id": activation_id
        }
        response_text = await self._make_request(params=params)
        if response_text.startswith("STATUS_OK"):
            _, code = response_text.split(":")
            return {"status": "success", "code": code}
        return {"status": "pending" if response_text.startswith("STATUS_WAIT") else "error", "message": response_text}

    async def get_balance(self) -> float:
        """
        Asynchronously retrieves the account balance from the Grizzly SMS provider.

        Returns:
            float: The account balance as a floating-point number.

        Raises:
            Exception: If the response from the API does not start with "ACCESS_BALANCE".
        """
        params = {
            "api_key": self.api_key,
            "action": "getBalance"
        }
        response_text = await self._make_request(params=params)
        if response_text.startswith("ACCESS_BALANCE"):
            _, balance = response_text.split(":")
            return float(balance)
        raise Exception(response_text)

    async def get_prices(self, country: str, service: str = "lf") -> float:
        """
        Asynchronously retrieves the pricing information for a specified country and service
        from the Grizzly SMS provider.

        Args:
            country (str): The country code for which to retrieve pricing information.
            service (str): The service identifier, defaults to "lf".

        Returns:
            float: The price for the specified service in the given country.

        Raises:
            KeyError: If the response does not contain the expected country or service keys.
        """
        params = {
            "api_key": self.api_key,
            "action": "getPrices",
            "service": service,
            "country": country
        }
        response_text = await self._make_request(params=params)
        return json.loads(response_text)[country][service]

    async def confirm_activation(self, activation_id: int) -> str:
        """
        Asynchronously confirms the activation of a service by setting its status to 6.

        Args:
            activation_id (int): The ID of the activation to confirm.

        Returns:
            str: The response text from the API if the status is successfully set.
        """
        return await self._set_status(activation_id=activation_id, status=6)

    async def cancel_activation(self, activation_id: int) -> str:
        """
        Asynchronously cancels the activation of a service by setting its status to -1.

        Args:
            activation_id (int): The ID of the activation to cancel.

        Returns:
            str: The response text from the API if the status is successfully set.
        """
        return await self._set_status(activation_id=activation_id, status=-1)

    async def get_code(self, activation_id: int) -> int | None:
        """
        Asynchronously retrieves the code associated with a given activation ID from the
        Grizzly SMS provider.

        Args:
            activation_id (int): The ID of the activation to retrieve the code for.

        Returns:
            int | None: The code as an integer if available, otherwise None.
        """
        status = await self.get_status(activation_id=activation_id)
        if status.get("code", None):
            return int(status.get("code"))
        return None
