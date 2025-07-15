#!/home/al/miniconda3/envs/py/bin/python3
# -*- coding: utf-8 -*-
#
# filename:   runner.py
#
# Copyright 2025 AL Haines
#
# DEFINITIVE FIX: This version correctly passes the user's full environment,
# including SUDO_ASKPASS, to the subprocess to make graphical sudo prompts work.

import subprocess
import sys
import shlex
import os

def stream_command(command_string: str, command_type: str):
    """
    Executes a command and yields its output line-by-line.
    """
    if command_type not in ["shell", "python"]:
        yield f"Command type '{command_type}' is not yet implemented."
        return

    cmd_to_run = command_string
    # --- Create a copy of the current environment ---
    # This is the critical step. It ensures that variables like
    # SUDO_ASKPASS and PATH are available to the command we run.
    command_env = os.environ.copy()

    if cmd_to_run.strip().startswith('sudo'):
        if 'SUDO_ASKPASS' not in command_env:
            yield "FATAL ERROR: This command requires sudo."
            yield "The SUDO_ASKPASS environment variable is not set."
            yield "Please run this in your terminal before starting the dashboard:"
            yield "export SUDO_ASKPASS=~/scripts/askpass.sh"
            return

        # Rebuild the command string to use 'sudo -A'
        parts = cmd_to_run.split()
        parts[0] = 'sudo'
        parts.insert(1, '-A')
        cmd_to_run = ' '.join(parts)
        yield f"INFO: Rerunning with graphical password prompt: {cmd_to_run}"

    try:
        # --- THE CORRECTED SUBPROCESS CALL ---
        # We now pass the 'env=command_env' argument.
        process = subprocess.Popen(
            cmd_to_run,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=command_env # This passes the environment to the subprocess
        )

        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                yield line.strip()
            process.stdout.close()

        return_code = process.wait()
        if return_code != 0:
            yield f"\n--- PROCESS EXITED WITH ERROR CODE: {return_code} ---"

    except Exception as e:
        yield f"An unexpected error occurred: {e}"
