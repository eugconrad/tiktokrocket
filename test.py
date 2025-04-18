"""
File: test.py
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
import time

from tiktokrocket import TikTokRocket, Browser

rocket = TikTokRocket()

browser = Browser(
    browser_executable_file=rocket.browser_executable_file,
    driver_executable_file=rocket.driver_executable_file
)

browser.create()

browser.open("https://ident.me")

time.sleep(60)

browser.quit()
