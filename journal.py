#!/home/al/miniconda3/envs/py/bin/python3
# -*- coding: utf-8 -*-
#
# filename:  /home/al/system_files/projects/py/journal.py
#
# Copyright 2026 AL Haines <alfredhaines@gmail.com>
#
# Description: Main CLI entry point for the personal journal application,
#              integrating JournalApp logic, MySQL connectivity, and Rich formatting.

import sys
import argparse
import json
import os

sys.path.insert(0, '/home/al/system_files/projects')
sys.path.insert(0, '/home/al/system_files/projects/py')

try:
    from logic import JournalApp
    from MySql import MySQL
    from rich.console import Console
except ImportError as e:
    print(f"ERROR: Missing critical module: {e}", file=sys.stderr)
    sys.exit(1)

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Personal Journal CLI application.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to execute")

    # list command
    subparsers.add_parser("list", help="List recent journal entries")

    # display command
    p_display = subparsers.add_parser("display", help="Display full entry by ID")
    p_display.add_argument("id", help="Entry ID")

    # search command
    p_search = subparsers.add_parser("search", help="Search journal entries")
    p_search.add_argument("phrase", help="Search phrase")

    # update command
    p_update = subparsers.add_parser("update", help="Add or update a journal entry")
    p_update.add_argument("note", help="Note content")

    # dump command
    p_dump = subparsers.add_parser("dump", help="Dump all entries to a text file")
    p_dump.add_argument("filename", help="Output text filename")

    # json command
    p_json = subparsers.add_parser("json", help="Export entries to a JSON file")
    p_json.add_argument("filename", help="Output JSON filename")

    # import command
    p_import = subparsers.add_parser("import", help="Import entries from a JSON file")
    p_import.add_argument("filename", help="Input JSON filename")

    args = parser.parse_args()
    app = JournalApp()
    db = MySQL(database='als')

    if args.command == "list":
        app.list_entries()
    elif args.command == "display":
        app.display_entry(args.id)
    elif args.command == "search":
        app.search_entries(args.phrase)
    elif args.command == "update":
        app.add_entry(args.note)
    elif args.command == "dump":
        app.dump_to_text(args.filename)
    elif args.command == "json":
        entries = db.get_data("SELECT id, title, note FROM journal ORDER BY id ASC")
        if not entries:
            console.print("[yellow]Journal is empty. No JSON created.[/yellow]")
            return
        try:
            with open(args.filename, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=4, ensure_ascii=False)
            console.print(f"[bold green]SUCCESS: Journal exported to JSON '{args.filename}'.[/bold green]")
        except IOError as e:
            console.print(f"[bold red]ERROR: Failed to write JSON file: {e}[/bold red]", file=sys.stderr)
    elif args.command == "import":
        if not os.path.exists(args.filename):
            console.print(f"[bold red]ERROR: File '{args.filename}' not found.[/bold red]", file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            count = 0
            for item in data:
                title = item.get('title')
                note = item.get('note')
                if title and note:
                    query = "INSERT INTO journal (title, note) VALUES (%s, %s) ON DUPLICATE KEY UPDATE note = %s"
                    db.put_data(query, (title, note, note))
                    count += 1
            console.print(f"[bold green]SUCCESS: Imported {count} entries from '{args.filename}'.[/bold green]")
        except Exception as e:
            console.print(f"[bold red]ERROR: Failed to import JSON file: {e}[/bold red]", file=sys.stderr)

if __name__ == "__main__":
    main()
#============= end of code      ================#
