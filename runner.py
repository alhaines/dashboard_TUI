#!/home/al/miniconda3/envs/py/bin/python3
# -*- coding: utf-8 -*-
#
# filename:   runner.py
#
# v3.0: This version forces 'rich' to render full colors for a
#       beautiful display inside the dashboard log.

import subprocess
import sys
import os

def stream_command(command_string: str, command_type: str):
    """
    Executes a command and yields its output line-by-line.
    """
    if command_type not in ["shell", "python"]:
        yield f"Command type '{command_type}' is not yet implemented."
        return

    cmd_to_run = command_string
    command_env = os.environ.copy()

    # --- THE CRITICAL COLOR FIX ---
    # This environment variable tells 'rich' (and other modern tools)
    # to output its full 24-bit color ANSI escape codes, even though
    # it's in a pipe. Textual can render these correctly.
    command_env["FORCE_COLOR"] = "1"

    if cmd_to_run.strip().startswith('sudo'):
        if 'SUDO_ASKPASS' not in command_env:
            yield "FATAL ERROR: This command requires sudo."
            yield "Please set the SUDO_ASKPASS environment variable first."
            return

        parts = cmd_to_run.split()
        parts[0] = 'sudo'
        parts.insert(1, '-A')
        cmd_to_run = ' '.join(parts)
        yield f"INFO: Rerunning with graphical password prompt: {cmd_to_run}"

    try:
        process = subprocess.Popen(
            cmd_to_run,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=command_env
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
