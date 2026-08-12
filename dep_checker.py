#!/home/al/miniconda3/envs/py/bin/python3
# -*- coding: utf-8 -*-
#
# filename:   /home/al/projects/py/dep_checker.py
#
# Copyright 2025 AL Haines
#
# Description: Disk usage report grouped by internal/external/shares with
import importlib.util
import subprocess
import sys

class DepChecker:
    def __call__(self, package_name, import_name=None):
        """
        Checks if a module is installed. Prompts to install via pip if missing.

        Args:
            package_name (str): The pip name of the package (e.g., 'google-generativeai').
            import_name (str, optional): The name used in your Python code (e.g., 'google.generativeai').
                                         Defaults to package_name if not provided.
        """
        if import_name is None:
            import_name = package_name

        # Check if the module is available in the current environment path
        spec = importlib.util.find_spec(import_name)

        if spec is not None:
            # Module exists, it is safe to import
            return True

        # Module is missing, alert and prompt the user
        print(f"\n[!] CRITICAL: Required module '{import_name}' is missing.", file=sys.stderr)
        choice = input(f"[?] Would you like to try installing '{package_name}' via pip? [y/N]: ").strip().lower()

        if choice in ['y', 'yes']:
            print(f"[*] Attempting to install '{package_name}' into {sys.executable}...\n", file=sys.stderr)
            try:
                # sys.executable ensures it uses the active Python (Miniconda), not the OS default
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print(f"\n[+] Successfully installed '{package_name}'.", file=sys.stderr)
                return True
            except subprocess.CalledProcessError:
                print(f"\n[-] ERROR: Failed to install '{package_name}'.", file=sys.stderr)
                return False
        else:
            print(f"[-] Skipping installation of '{package_name}'.", file=sys.stderr)
            return False
