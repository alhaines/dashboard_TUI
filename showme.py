#!/home/al/miniconda3/envs/py/bin/python3
# -*- coding: utf-8 -*-
#
# filename:   showme.py
#
# Copyright 2025 AL Haines
#
# A smart, read-only CLI for viewing MySQL databases.
# v4.0: Complete rewrite to use the 'rich' library exclusively for all
# console output, removing the 'textwrap' dependency entirely.

import sys
import argparse
# NOTE: import textwrap has been REMOVED.

# --- Import Required Libraries ---
try:
    from MySql import MySQL
except ImportError:
    # Rich might not be available for this very first error, so use standard print.
    print("FATAL: Could not import MySql.py. Ensure it is in the Python path.", file=sys.stderr)
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:
    print("FATAL: The 'rich' library is not installed.", file=sys.stderr)
    print("Please run: pip install rich", file=sys.stderr)
    sys.exit(1)

# --- Rich Console Initialization ---
# A single console object to handle all printing.
console = Console()

# --- Helper Function (The "Nice" Rich Version) ---
def print_formatted_record(record: dict):
    """
    Prints a single database record using rich.Panel and rich.Table
    for a beautiful, bordered, and consistent display.
    """
    if not record:
        console.print("[bold red]Record not found.[/bold red]")
        return

    # A Rich Table provides clean, aligned key-value layout automatically.
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(style="cyan", justify="right", width=15) # Column for keys
    table.add_column()  # Column for values

    # Get the title and ID for the Panel header.
    record_id = record.get('id', 'N/A')
    record_title = record.get('title', 'N/A')
    panel_title = f"[bold yellow]ID: {record_id} | {record_title}[/bold yellow]"

    # Populate the table with the record's data. Rich handles wrapping.
    for key, value in record.items():
        value_str = str(value).strip() if value is not None else "[italic dim]NULL[/italic dim]"
        table.add_row(f"[bold cyan]{key.upper()}:[/bold cyan]", value_str)

    # Print the table inside a Panel for the bordered effect.
    console.print(Panel(table, title=panel_title, border_style="blue", expand=True))

# --- Main Application Class ---
class ShowMeApp:
    def __init__(self, db_name):
        self.db = MySQL(database=db_name)
        self.db_name = db_name

    def get_last_record(self, table):
        console.print(f"Fetching last record from '[bold]{self.db_name}.{table}[/bold]'...")
        query = f"SELECT * FROM `{table}` ORDER BY id DESC LIMIT 1"
        results = self.db.get_data(query)
        if results:
            print_formatted_record(results[0])
        else:
            console.print(f"[red]No records found in table '{table}'.[/red]")

    def dump_table(self, table):
        console.print(f"Fetching all records from '[bold]{self.db_name}.{table}[/bold]'...")
        query = f"SELECT id, title, note FROM `{table}` ORDER BY id DESC"
        records = self.db.get_data(query)

        if not records:
            console.print(f"[red]No records found in table '{table}'.[/red]")
            return

        summary_table = Table(title="Select a Record", border_style="green", show_lines=True)
        summary_table.add_column("ID", style="magenta", justify="right")
        summary_table.add_column("Title / Note Preview", overflow="fold") # Let Rich handle wrapping

        for record in records:
            preview_text = record.get('title') or record.get('note', '')
            summary_table.add_row(str(record.get('id')), preview_text.replace('\n', ' '))

        console.print(summary_table)

        while True:
            try:
                choice = console.input("\nEnter ID to display (or '[bold]q[/bold]' to quit): ")
                if choice.lower() == 'q':
                    break
                record_id = int(choice)
                query = f"SELECT * FROM `{table}` WHERE id = %s"
                results = self.db.get_data(query, (record_id,))
                if results:
                    print_formatted_record(results[0])
                else:
                    console.print(f"[yellow]No record found with ID: {record_id}[/yellow]")
            except (ValueError, TypeError):
                console.print("[red]Invalid input. Please enter a number or 'q'.[/red]")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold]Exiting.[/bold]")
                break

    def list_tables(self):
        console.print(f"Fetching all tables from database '[bold]{self.db_name}[/bold]'...")
        tables = self.db.get_data("SHOW TABLES")
        if tables:
            table_list = [list(t.values())[0] for t in tables]
            console.print(Panel("    " + "\n    ".join(f"- {name}" for name in table_list),
                                title="[bold yellow]Tables Found[/bold yellow]", border_style="blue"))
        else:
            console.print("[red]No tables found in this database.[/red]")

    def search_all_titles(self, phrase):
        console.print(f"Searching for '[bold]{phrase}[/bold]' in all 'title' columns...")
        info_schema_query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND COLUMN_NAME = 'title'"
        tables_with_title = self.db.get_data(info_schema_query, (self.db_name,))
        if not tables_with_title:
            console.print("[red]No tables with a 'title' column found.[/red]")
            return

        union_parts, search_params, search_pattern = [], [], f"%{phrase}%"
        for table_dict in tables_with_title:
            table_name = table_dict['TABLE_NAME']
            union_parts.append(f"(SELECT id, title, '{table_name}' as source_table FROM `{table_name}` WHERE title LIKE %s)")
            search_params.append(search_pattern)

        full_query = " UNION ALL ".join(union_parts) + " ORDER BY source_table, id"
        results = self.db.get_data(full_query, tuple(search_params))
        if not results:
            console.print(f"[yellow]No results found for '{phrase}'.[/yellow]")
            return

        search_results_table = Table(title=f"Found {len(results)} match(es) for '[bold]{phrase}[/bold]'", border_style="green")
        search_results_table.add_column("ID", style="magenta", justify="right")
        search_results_table.add_column("Source Table", style="yellow")
        search_results_table.add_column("Matching Title", overflow="fold")
        for record in results:
            search_results_table.add_row(str(record.get('id')), record.get('source_table'), record.get('title', ''))
        console.print(search_results_table)
        console.print(f"\nUse '[bold]showme {self.db_name} dump <Source Table>[/bold]' and enter an ID to see the full record.")

def main():
    parser = argparse.ArgumentParser(description="A CLI for viewing MySQL databases, with rich formatting.")
    parser.add_argument("database", help="The name of the database to connect to (e.g., 'als', 'media').")
    subparsers = parser.add_subparsers(dest='action', required=True, help="The action to perform.")
    parser_last = subparsers.add_parser('last', help="Show the most recent record from a table.")
    parser_last.add_argument("table", help="The name of the table.")
    parser_dump = subparsers.add_parser('dump', help="List records in a table and view one by ID.")
    parser_dump.add_argument("table", help="The name of the table.")
    parser_list = subparsers.add_parser('list', help="List all tables in the database.")
    parser_search = subparsers.add_parser('search', help="Search for a phrase in 'title' columns of all tables.")
    parser_search.add_argument("phrase", help="The text to search for.")
    args = parser.parse_args()
    app = ShowMeApp(args.database)
    if args.action == 'last':
        app.get_last_record(args.table)
    elif args.action == 'dump':
        app.dump_table(args.table)
    elif args.action == 'list':
        app.list_tables()
    elif args.action == 'search':
        app.search_all_titles(args.phrase)

if __name__ == "__main__":
    main()
