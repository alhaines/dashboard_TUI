#!/home/al/miniconda3/envs/py/bin/python3
# -*- coding: utf-8 -*-
#
# filename:   check_imports.py
#
# Copyright 2025 AL Haines (Python Module for On-Demand Package Installation)
# with assist from Google Gemini AI
#
# This module provides a utility function to check for the availability of
# Python packages and, if they are missing, attempts to install them
# using pip. This helps to ensure that application dependencies are met
# at runtime, making applications more robust against missing libraries
# in the environment where they are executed.
#
# The primary function is `ensure_module`, which can be imported and called
# by other scripts to verify and install their required external dependencies.
#
# Usage Example in another script (e.g., `my_app.py`):
#
#   import sys
#   from check_imports import ensure_module
#
#   # Call ensure_module for each required package at the very beginning of your app,
#   # before attempting to import them.
#   if not ensure_module('requests'):
#       sys.exit("Error: 'requests' package could not be installed. Exiting.")
#   if not ensure_module('google-generativeai', 'google.generativeai'):
#       sys.exit("Error: 'google-generativeai' package could not be installed. Exiting.")
#
#   # Now you can safely import the modules
#   import requests
#   import google.generativeai as genai
#
#   # ... rest of your application code ...

import sys
import subprocess
import importlib # Added for cleaner re-importing

def ensure_module(package_name, import_name=None):
    """
    Ensures a Python module is available. If not, it attempts to install it
    using pip. This function is designed to be called at the beginning of
    scripts that rely on external packages.

    Args:
        package_name (str): The name of the package to install via pip
                            (e.g., 'requests', 'google-generativeai').
        import_name (str, optional): The name to use in the 'import' statement.
                                     If different from package_name (e.g., 'bs4'
                                     for 'beautifulsoup4', or 'google.generativeai'
                                     for 'google-generativeai').
                                     Defaults to package_name if not provided.
    Returns:
        bool: True if the module is successfully imported/installed, False otherwise.
    """
    if import_name is None:
        import_name = package_name

    try:
        # Attempt to import the module to check if it's already available.
        # importlib.util.find_spec is a robust way to check for module existence
        # without actually loading it fully, which can prevent some side effects.
        if importlib.util.find_spec(import_name):
            print(f"INFO: '{import_name}' module already installed.", file=sys.stderr)
            return True
        else:
            raise ImportError # Force installation attempt if not found by spec
    except ImportError:
        print(f"INFO: '{import_name}' module not found. Attempting to install '{package_name}'...", file=sys.stderr)
        try:
            # Use sys.executable to ensure pip is run with the current Python interpreter.
            # This is critical for working correctly within virtual environments like Conda.
            # The '--disable-pip-version-check' argument is added to suppress annoying
            # pip upgrade notifications in automated scripts.
            subprocess.check_call([
                sys.executable,
                "-m", "pip", "install",
                "--disable-pip-version-check", # Suppress pip update notifications
                package_name
            ])
            print(f"SUCCESS: '{package_name}' installed successfully.", file=sys.stderr)

            # After successful installation, try to import the module again.
            # This ensures it's usable immediately by the calling script.
            importlib.import_module(import_name)
            print(f"INFO: '{import_name}' imported successfully after installation.", file=sys.stderr)
            return True
        except subprocess.CalledProcessError as e:
            # Catch errors specifically from the pip installation command.
            print(f"ERROR: Failed to install '{package_name}': {e}", file=sys.stderr)
            print("Please check pip output above for details (e.g., permissions, network issues).", file=sys.stderr)
            return False
        except ImportError:
            # This rare case means installation succeeded, but import still failed.
            # Could indicate complex package structure or environmental issues.
            print(f"ERROR: '{package_name}' installed, but '{import_name}' could not be imported.", file=sys.stderr)
            print("This might happen if the package name and import name are truly different, or if there's a deeper environment issue.", file=sys.stderr)
            return False
        except Exception as e:
            # Catch any other unexpected errors during the process.
            print(f"ERROR: An unexpected error occurred during installation or re-import of '{package_name}': {e}", file=sys.stderr)
            return False

# This module is primarily for import. No direct execution block unless for testing.
if __name__ == '__main__':
    # Simple test cases for the module
    print("\n--- Testing check_imports.py ---", file=sys.stderr)

    # Test case 1: Module that should exist (e.g., 'json')
    print("\nTesting 'json' module...", file=sys.stderr)
    if ensure_module('json'):
        print("'json' test passed.", file=sys.stderr)
    else:
        print("'json' test failed.", file=sys.stderr)

    # Test case 2: Module that might not exist, but is easy to install (e.g., 'requests')
    print("\nTesting 'requests' module...", file=sys.stderr)
    if ensure_module('requests'):
        print("'requests' test passed.", file=sys.stderr)
    else:
        print("'requests' test failed. (This might indicate a real installation issue)", file=sys.stderr)

    # Test case 3: A dummy module name to test failure case
    print("\nTesting a non-existent module ('nonexistent-module')...", file=sys.stderr)
    if ensure_module('nonexistent-module'):
        print("'nonexistent-module' test failed (unexpected success!).", file=sys.stderr)
    else:
        print("'nonexistent-module' test passed (expected failure).", file=sys.stderr)

    print("\n--- check_imports.py tests complete ---", file=sys.stderr)
