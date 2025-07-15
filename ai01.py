#!/home/al/miniconda3/envs/py/bin/python3
# -*- coding: utf-8 -*-
#
# filename:   ai01.py
#
# Copyright 2025 AL Haines (Console CLI for Gemini API & MySQL)
# with assist from Google Gemini AI
#
# This version is simplified to ALWAYS save Q&A results to the database
# when using the 'ask' command. The --save flag has been removed.

import argparse
import sys
import os
import requests
import json

# --- Import Dependency Checker Module FIRST ---
try:
    from check_imports import ensure_module
except ImportError:
    print("CRITICAL ERROR: 'check_imports.py' module not found.", file=sys.stderr)
    print("Please ensure check_imports.py is in your Python path (e.g., /home/al/py/ or symlinked).", file=sys.stderr)
    sys.exit(1)

# --- Ensure core external libraries are installed ---
if not ensure_module('requests'):
    sys.exit("Error: 'requests' library missing and could not be installed. Exiting.")
if not ensure_module('rich'):
    sys.exit("Error: 'rich' library missing and could not be installed. Exiting.")

# --- Now, safely import external and custom modules ---
try:
    from MySql import MySQL      # Database interaction module
    import config                # Configuration module for API key and MySQL credentials
    from rich.console import Console # For rich text output
    from rich.markdown import Markdown # For Markdown parsing
    from rich.panel import Panel     # For styled boxes
except ImportError as e:
    print(f"ERROR: Could not import required modules: {e}", file=sys.stderr)
    sys.exit(1)

# Initialize console for rich printing
console = Console()

# Initialize MySQL database manager instance
db_manager = MySQL()

# --- Global Configuration for Gemini API ---
GEMINI_API_KEY = config.APIKEY
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
    console.print("[bold red]ERROR: Gemini API key is missing or not correctly configured in config.py.[/bold red]")
    sys.exit(1)

GEMINI_MODEL_NAME = 'gemini-1.5-flash-latest'


# --- Console Output Formatting Helpers (using rich) ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_formatted_qa(qa_dict):
    entry_id = qa_dict.get('id', 'N/A')
    question = qa_dict.get('question', 'N/A')
    answer_markdown = qa_dict.get('text', 'No answer text found.')
    comment = qa_dict.get('comment', None)
    console.print(Panel(f"[bold cyan]{question}[/bold cyan]", title=f"[yellow]ID: {entry_id}[/yellow]", title_align="left", border_style="green"))
    console.print("\n--- [bold]Answer[/bold] ---\n")
    console.print(Markdown(answer_markdown))
    if comment:
        console.print("\n--- [bold]Comment[/bold] ---\n")
        console.print(Markdown(comment))
    console.print("\n" + "~" * 80 + "\n")


# --- Gemini API Interaction ---
def get_gemini_response(question):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": question}]}]}
    console.print(f"\n[yellow]Querying Gemini API with model '{GEMINI_MODEL_NAME}'...[/yellow]")
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        if 'candidates' in result and result['candidates']:
            generated_text = result['candidates'][0]['content']['parts'][0]['text']
            print_formatted_qa({'question': question, 'text': generated_text})
            return generated_text
        else:
            console.print("[bold red]No response candidates found from Gemini API.[/bold red]")
            console.print(result)
            return "ERROR: No response from Gemini API."
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]ERROR: Error connecting to Gemini API: {e}[/bold red]")
        return "ERROR: Could not connect to Gemini API."
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        console.print(f"[bold red]ERROR: Error parsing Gemini API response: {e}[/bold red]")
        if 'response' in locals():
            console.print("[bold]Raw API response:[/bold]", response.text)
        return "ERROR: Could not parse Gemini API response."


# --- Database Operations ---
def create_past_results_table_if_not_exists():
    query = "CREATE TABLE IF NOT EXISTS past_results (id INT AUTO_INCREMENT PRIMARY KEY, question TEXT, text MEDIUMTEXT, comment MEDIUMTEXT);"
    if not db_manager.put_data(query):
        console.print("[bold red]CRITICAL ERROR: Failed to ensure 'past_results' table exists.[/bold red]")
        sys.exit(1)

def insert_qa_to_db(question, answer, comment=None):
    query = "INSERT INTO past_results (question, text, comment) VALUES (%s, %s, %s)"
    if db_manager.put_data(query, (question, answer, comment)):
        console.print("\n[bold green]SUCCESS: Q&A saved to database.[/bold green]")
    else:
        console.print("\n[bold red]ERROR: Failed to save Q&A to database.[/bold red]")

def search_qa_in_db(search_term):
    clear_screen()
    console.print(f"[bold]Searching Database for: '{search_term}'[/bold]\n")
    query = "SELECT id, question, text, comment FROM past_results WHERE question LIKE CONCAT('%%', %s, '%%') OR text LIKE CONCAT('%%', %s, '%%') ORDER BY id DESC"
    results = db_manager.get_data(query, (search_term, search_term))
    if results:
        console.print(f"Found {len(results)} results:")
        for qa in results:
            print_formatted_qa(qa)
    else:
        console.print("[yellow]No results found for your search term.[/yellow]")

def dump_all_qa():
    clear_screen()
    console.print("[bold]Dumping All Past Results[/bold]\n")
    query = "SELECT id, question, text, comment FROM past_results ORDER BY id DESC"
    results = db_manager.get_data(query)
    if results:
        console.print(f"Found {len(results)} total entries:")
        for qa in results:
            print_formatted_qa(qa)
    else:
        console.print("[yellow]No entries found in the 'past_results' table.[/yellow]")


# --- Main CLI Application Logic ---
def main():
    parser = argparse.ArgumentParser(description="CLI tool to interact with Gemini API and manage a Q&A database.", formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

    # MODIFICATION: The --save argument has been removed from the 'ask' command parser.
    ask_parser = subparsers.add_parser('ask', help='Ask Gemini a question and save it to the database.')
    ask_parser.add_argument('question', type=str, nargs='+', help='The question to ask Gemini.')

    search_parser = subparsers.add_parser('search', help='Search past Q&A results in the database.')
    search_parser.add_argument('search_term', type=str, nargs='+', help='The term to search for.')

    dump_parser = subparsers.add_parser('dump', help='Dump all Q&A entries from the database.')

    args = parser.parse_args()

    create_past_results_table_if_not_exists()

    if args.command == 'ask':
        if isinstance(args.question, list):
            question_text = " ".join(args.question)
        else:
            question_text = args.question

        clear_screen()
        answer_text = get_gemini_response(question_text)

        # MODIFICATION: We now check for a valid answer and then save it automatically.
        if answer_text and not answer_text.startswith("ERROR:"):
            insert_qa_to_db(question_text, answer_text)
        else:
            console.print("\n[bold red]Did not get a valid answer from Gemini. Not saving.[/bold red]")

    elif args.command == 'search':
        search_term = " ".join(args.search_term)
        search_qa_in_db(search_term)

    elif args.command == 'dump':
        dump_all_qa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user. Exiting.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]An unhandled error occurred: {e}[/bold red]")
        sys.exit(1)
