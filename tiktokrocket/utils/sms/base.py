"""
File: base.py
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
from abc import ABC, abstractmethod

import aiohttp
from loguru import logger


class BaseAPI(ABC):
    """
    BaseAPI is an abstract base class that defines the interface for interacting with an SMS
    provider API.

    Attributes:
        api_key (str): The API key used for authentication.
        base_url (str): The base URL of the API.
        provider (str): The name of the provider, default is "Base Provider".

    Methods:
        _make_request(params: dict) -> str: Asynchronously makes a GET request to the API with the
        given parameters.
        get_number(*args, **kwargs): Abstract method to retrieve a phone number.
        _set_status(*args, **kwargs): Abstract method to set the status of a request.
        get_status(*args, **kwargs): Abstract method to retrieve the status of a request.
        get_balance(): Abstract method to retrieve the account balance.
        get_prices(*args, **kwargs): Abstract method to retrieve pricing information.
        confirm_activation(*args, **kwargs): Abstract method to confirm activation of a service.
        cancel_activation(*args, **kwargs): Abstract method to cancel activation of a service.
        get_code(*args, **kwargs): Abstract method to retrieve a code from the service.
    """

    def __init__(self, api_key: str, base_url: str) -> None:
        """
        Initializes the BaseAPI instance with the provided API key and base URL.

        Args:
            api_key (str): The API key used for authentication with the SMS provider.
            base_url (str): The base URL of the SMS provider's API.
        """
        self.api_key: str = api_key
        self.base_url: str = base_url
        self.provider: str = "Base Provider"

    async def _make_request(self, params: dict) -> str:
        """
        Asynchronously makes a GET request to the API using the provided parameters.

        Args:
            params (dict): A dictionary of parameters to include in the GET request.

        Returns:
            str: The response text from the API.

        Logs:
            The response object for debugging purposes.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                _ = await response.text()
                logger.debug(response)
                return _

    @abstractmethod
    async def get_number(self, *args, **kwargs):
        """
        Abstract method to asynchronously retrieve a phone number from the SMS provider.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    async def _set_status(self, *args, **kwargs):
        """
        Abstract method to asynchronously set the status of a request.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_status(self, *args, **kwargs):
        """
        Abstract method to asynchronously retrieve the status of a request from the SMS provider.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_balance(self):
        """
        Abstract method to asynchronously retrieve the account balance from the SMS provider.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_prices(self, *args, **kwargs):
        """
        Abstract method to asynchronously retrieve pricing information from the SMS provider.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    async def confirm_activation(self, *args, **kwargs):
        """
        Abstract method to asynchronously confirm the activation of a service.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    async def cancel_activation(self, *args, **kwargs):
        """
        Abstract method to asynchronously cancel the activation of a service.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_code(self, *args, **kwargs):
        """
        Abstract method to asynchronously retrieve a code from the SMS provider.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError
