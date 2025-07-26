#!/home/al/miniconda3/envs/py/bin/python3
# -*- coding: utf-8 -*-
#
# filename:   /home/al/py/dashboard.py
#
# Copyright 2025 AL Haines

import sys
import shlex
import subprocess

try:
    from MySql import MySQL
    from check_imports import ensure_module
    from runner import stream_command
except ImportError as e:
    print(f"ERROR: Critical modules not found: {e}", file=sys.stderr)
    sys.exit(1)

if not ensure_module('textual'):
    sys.exit("Error: 'textual' library is required but could not be installed. Exiting.")

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Log, Input

def get_dashboard_commands():
    db_manager = MySQL()
    query = "SELECT `key`, `name`, `command_type`, `command_string`, `requires_input`, `quote_input` FROM `dashboard_commands` ORDER BY `sort_order` ASC"
    try:
        return db_manager.get_data(query)
    except Exception:
        return None

class DashboardApp(App):
    CSS_PATH = "dashboard.css"
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.raw_commands = get_dashboard_commands()
        if self.raw_commands is None:
            sys.exit("CRITICAL: Failed to load commands from database.")
        self.command_map = {cmd['key']: cmd for cmd in self.raw_commands}
        self.active_command = None

    def compose(self) -> ComposeResult:
        yield Header(name="Haines Homelab Dashboard")
        yield Footer()
        with Container(id="app-grid"):
            with Container(id="sidebar-container"):
                yield Static("MENU", id="sidebar-title")
                if self.raw_commands:
                    for command_data in self.raw_commands:
                        yield Static(f" ({command_data.get('key')}) {command_data.get('name')}")
                else:
                    yield Static("No commands found in database.")
            with Vertical(id="main-container"):
                yield Log(id="output-log", highlight=True)
                yield Input(placeholder="Enter your input here...", id="command-input", classes="hidden")

    def on_mount(self) -> None:
        log = self.query_one(Log)
        log.wrap = True
        log.write_line("Welcome to your Homelab Dashboard.")
        log.write_line("Press a key from the menu to run a command.")
        log.write_line("Press tab to return to the menu.")
        self.query_one("#sidebar-container").focus()

    def on_key(self, event) -> None:
        if event.key in self.command_map:
            command_data = self.command_map[event.key]
            if command_data.get('requires_input'):
                self.active_command = command_data
                inp = self.query_one("#command-input")
                self.query_one(Log).clear()
                inp.placeholder = f"Enter text for '{command_data['name']}'..."
                inp.remove_class("hidden")
                inp.focus()
            else:
                self.run_command_directly(command_data)

    def run_command_directly(self, command_data: dict, user_input: str = "") -> None:
        log = self.query_one(Log)
        log.clear()
        log.write_line(f"Running '{command_data['name']}'...")
        final_command = command_data['command_string']
        if user_input:
            final_command += " " + (shlex.quote(user_input) if command_data.get('quote_input') else user_input)
        
        log_width = self.query_one(Log).content_size.width
        self.run_worker(self.execute_command_and_update_log(final_command, command_data['command_type'], log_width), exclusive=True)
        self.call_next(self.query_one("#sidebar-container").focus)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.active_command:
            self.run_command_directly(self.active_command, event.value)
            self.active_command = None
            event.input.value = ""
            self.query_one("#command-input").add_class("hidden")

    async def execute_command_and_update_log(self, command_string: str, command_type: str, width: int) -> None:
        log = self.query_one(Log)
        log.clear()
        try:
            for line in stream_command(command_string, command_type, width=width):
                log.write_line(line)
        except Exception as e:
            log.write_line(f"An error occurred in the worker: {e}")

if __name__ == "__main__":
    app = DashboardApp()
    app.run()
