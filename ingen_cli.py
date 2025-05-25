#!/usr/bin/env python3
"""
Entry point script for running the Insight Ingenious CLI commands.
"""

import os
import sys

from ingenious.cli import app

if __name__ == "__main__":
    print("Insight Ingenious CLI")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Command arguments: {sys.argv[1:]}")
    try:
        sys.exit(app())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
