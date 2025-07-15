# MySql.py
#
# Copyright 2010 AL Haines (from original MyFunctions.php)
#
# This module provides a Pythonic class for interacting with a MySQL database,
# translating the functionality found in the original PHP MyFunctions.php.
# It adheres to modularity and securely retrieves database credentials from
# the user-provided 'config.py' file.

import pymysql
import pymysql.cursors
import sys

# Initialize credential variables as None
DB_HOST = None
DB_USER = None
DB_PASSWORD = None
DB_NAME = None

try:
    import config

    # Attempt to load from mysql_config dictionary first
    if hasattr(config, 'mysql_config') and isinstance(config.mysql_config, dict):
        # Use .get() with a default of None to avoid KeyError if a key is missing
        DB_HOST = config.mysql_config.get('host')
        DB_USER = config.mysql_config.get('user')
        DB_PASSWORD = config.mysql_config.get('password')
        DB_NAME = config.mysql_config.get('database')

    # If any credential is still None, try to load from individual variables as fallback
    if DB_HOST is None and hasattr(config, 'SERVER'):
        DB_HOST = config.SERVER
    if DB_USER is None and hasattr(config, 'USER'):
        DB_USER = config.USER
    if DB_PASSWORD is None and hasattr(config, 'PASSWORD'):
        DB_PASSWORD = config.PASSWORD
    if DB_NAME is None and hasattr(config, 'DATABASE'):
        DB_NAME = config.DATABASE

    # Final validation: Ensure all critical credentials are not None
    if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
        raise ValueError("One or more required database credentials (host, user, password, database) are missing or incomplete in config.py.")

except ImportError:
    print("Error: config.py module not found.", file=sys.stderr)
    print("Please create a config.py file with your MySQL credentials (mysql_config dictionary or SERVER, USER, PASSWORD, DATABASE variables).", file=sys.stderr)
    sys.exit(1)
except ValueError as e:
    # Catch the specific ValueError we raised for missing credentials
    print(f"Configuration Error: {e}", file=sys.stderr)
    print("Please check your config.py file to ensure all required database credentials are properly defined.", file=sys.stderr)
    sys.exit(1)
except Exception:
    # Catch any other unexpected errors during config loading, without printing the exception object
    print("An unexpected error occurred while loading database configuration from config.py.", file=sys.stderr)
    print("Please verify the syntax and content of your config.py file.", file=sys.stderr)
    sys.exit(1)


class MySQL:
    """
    A class to encapsulate MySQL database operations using PyMySQL,
    providing methods for connection, data retrieval, data insertion/update,
    and schema information (field names, number of fields).
    """

    def __init__(self, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME):
        """
        Initializes the MySQL connection parameters.
        Parameters are defaulted to values from config.py for convenience.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def _connect(self):
        """
        Establishes a connection to the MySQL database using PyMySQL.
        This is a private helper method, not intended for direct external use.
        Returns:
            pymysql.connections.Connection: The database connection object.
        Raises:
            pymysql.Error: If the connection fails.
        """
        if self.connection and self.connection.open: # Check if connection is open
            return self.connection
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=5 # CRITICAL FIX: Add a 5-second connection timeout
            )
            return self.connection
        except pymysql.Error as e:
            # Print to stderr for console apps
            print(f"Error connecting to MySQL database. Please check credentials and database status: {e}", file=sys.stderr)
            sys.exit(1) # Exit if critical connection fails

    def _close(self):
        """
        Closes the database connection if it is open.
        """
        if self.connection and self.connection.open:
            self.connection.close()
            self.connection = None

    def get_data(self, query_string, params=None):
        """
        Executes a SELECT query and fetches all results.
        Supports parameterized queries for security.

        Args:
            query_string (str): The SQL query string to execute (can contain %s placeholders).
            params (tuple, list, or dict, optional): Parameters to bind to the query. Defaults to None.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary represents a row
                        and keys are column names.
        """
        data = []
        conn = None
        try:
            conn = self._connect() # Use the robust _connect
            with conn.cursor() as cursor:
                cursor.execute(query_string, params)
                data = cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error executing query: {e}", file=sys.stderr)
        finally:
            if conn:
                self._close()
        return data

    def put_data(self, query_string, params=None):
        """
        Executes an INSERT, UPDATE, or DELETE query.
        Supports parameterized queries for security.

        Args:
            query_string (str): The SQL query string to execute (can contain %s placeholders).
            params (tuple, list, or dict, optional): Parameters to bind to the query. Defaults to None.

        Returns:
            bool: True if the query was successful, False otherwise.
        """
        success = False
        conn = None
        try:
            conn = self._connect() # Use the robust _connect
            with conn.cursor() as cursor:
                cursor.execute(query_string, params)
            conn.commit()
            success = True
        except pymysql.Error as e:
            print(f"Error executing update/insert/delete query: {e}", file=sys.stderr)
            if conn:
                conn.rollback()
        finally:
            if conn:
                self._close()
        return success

    def get_field_names(self, table):
        """
        Retrieves the names of all fields (columns) in a given table.
        """
        field_names = []
        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{table}' ORDER BY ORDINAL_POSITION")
                for row in cursor.fetchall():
                    field_names.append(row['COLUMN_NAME'])
        except pymysql.Error as e:
            print(f"Error getting field names for table '{table}': {e}", file=sys.stderr)
        finally:
            if conn:
                self._close()
        return field_names

    def get_num_fields(self, table):
        """
        Retrieves the number of fields (columns) in a given table.
        """
        num_fields = -1
        conn = None
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute(f"DESCRIBE {table}")
                num_fields = cursor.rowcount
        except pymysql.Error as e:
            print(f"Error getting number of fields for table '{table}': {e}", file=sys.stderr)
        finally:
            if conn:
                self._close()
        return num_fields

# Global helper functions (add_quotes_double, add_quotes_single)
# are now largely redundant due to parameterized queries, but kept for direct translation reference.

def add_quotes_double(text):
    """
    Adds double quotes around a string and escapes existing double/single quotes
    within the string for use in contexts like SQL.
    Note: For SQL queries, prefer parameterized queries over manual quoting.
    """
    text = str(text).replace('"', '`').replace("'", '%') # Ensure text is string
    return f'"{text}"'

def add_quotes_single(text):
    """
    Adds single quotes around a string and escapes existing double/single quotes
    within the string for use in contexts like SQL.
    Note: For SQL queries, prefer parameterized queries over manual quoting.
    """
    text = str(text).replace('"', '`').replace("'", '%') # Ensure text is string
    return f"'{text}'"
