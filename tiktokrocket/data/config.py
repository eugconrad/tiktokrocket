"""
File: config.py
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


class ApiConfig:
    """
    Configuration class for API settings.

    Attributes:
        BASE_URL (str): The base URL for the API endpoint.
        REQUEST_TIMEOUT (int): The timeout duration for API requests in seconds.
        AUTH_HEADER (str): The header key used for authorization in API requests.
    """
    BASE_URL: str = "https://tiktok.eugconrad.com/"  # Замените на реальный URL
    REQUEST_TIMEOUT: int = 10
    AUTH_HEADER: str = "Authorization"

    def __str__(self):
        pass

    def __del__(self):
        pass
