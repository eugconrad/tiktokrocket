"""
File: env.py
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
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv, set_key, unset_key


class Env:
    """
    A class to manage environment variables using a .env file.

    The Env class provides methods to load, set, remove, and retrieve
    environment variables from a specified .env file. It utilizes the
    dotenv library to interact with the environment variables, allowing
    for easy management of application configurations.

    Attributes:
        env_file (Path): The path to the .env file.
        env: The loaded environment variables from the .env file.

    Methods:
        __init__(env_file): Initializes the Env instance and loads the
            environment variables from the specified .env file.
        set(key, value): Sets an environment variable in the .env
            file and the current environment.
        remove(key): Removes an environment variable from the .env
            file and the current environment.
        get(key, default): Retrieves the value of an environment
            variable, returning a default value if the variable is not found.
    """

    def __init__(self, env_file: Path) -> None:
        """
        Initialize the Env instance by loading environment variables from a .env file.

        Args:
            env_file (Path): The path to the .env file to load.
        """
        self.env_file = env_file
        self.env = load_dotenv(self.env_file)

    def set(self, key: str, value: str) -> None:
        """
        Set an environment variable in the .env file and the current
        environment.

        Args:
            key (str): The name of the environment variable to set.
            value (str): The value to assign to the environment variable.
        """
        set_key(dotenv_path=self.env_file, key_to_set=key, value_to_set=value)
        os.environ[key] = value

    def remove(self, key: str) -> None:
        """
        Remove an environment variable from the .env file and the current
        environment.

        Args:
            key (str): The name of the environment variable to remove.
        """
        unset_key(dotenv_path=self.env_file, key_to_unset=key)
        if key in os.environ:
            del os.environ[key]

    @staticmethod
    def get(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve the value of an environment variable.

        Args:
            key (str): The name of the environment variable to retrieve.
            default (optional): The default value to return if the environment
                variable is not found. Defaults to None.

        Returns:
            The value of the environment variable if it exists, otherwise the
            specified default value.
        """
        return os.getenv(key, default)
