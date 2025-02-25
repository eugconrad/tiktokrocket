#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: config.py
Date: 25.02.2025
License: Non-Commercial License

Author: me@eugconrad.com
Social: @eugconrad – Telegram, Lolzteam

      https://eugconrad.com
        © Copyright 2024
"""
import json


class Config:
    """
    A class to manage configuration settings loaded from a JSON file.

    The Config class provides methods to load configuration data from a specified
    JSON file and retrieve specific configuration settings such as API endpoints,
    timeout values, and maximum retry attempts. It handles file not found and JSON
    decoding errors gracefully by returning default values or empty data structures.
    """

    def __init__(self, config_file='data/config.json'):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        """
        Loads the configuration data from a JSON file specified by `self.config_file`.

        Returns:
            dict: The configuration data as a dictionary. Returns an empty dictionary
            if the file is not found or if there is a JSON decoding error.
        """
        try:
            with open(self.config_file, 'r', encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Конфигурационный файл {self.config_file} не найден.")
            return {}
        except json.JSONDecodeError:
            print(f"Ошибка при чтении файла {self.config_file}. Некорректный формат JSON.")
            return {}

    def get_api_endpoint(self, endpoint_name: str):
        """
        Retrieves the API endpoint URL for the specified endpoint name.

        Args:
            endpoint_name (str): The name of the API endpoint to retrieve.

        Returns:
            str or None: The URL of the API endpoint if found, otherwise None.
        """
        return self.config_data.get('api_endpoints', {}).get(endpoint_name)

    def get_timeout(self):
        """
        Retrieves the timeout value from the configuration data.

        Returns:
            int: The timeout value in seconds. Defaults to 30 if not specified
            in the configuration.
        """
        return self.config_data.get('timeout', 30)

    def get_max_retries(self):
        """
        Retrieves the maximum number of retry attempts from the configuration data.

        Returns:
            int: The maximum number of retries. Defaults to 3 if not specified
            in the configuration.
        """
        return self.config_data.get('max_retries', 3)
