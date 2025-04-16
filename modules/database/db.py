import sqlite3

from langchain_community.utilities import SQLDatabase

from modules.settings import DB_FILE


def execute_sql_query(extracted_query):
    """Connect to database and execute SQL query"""
    if not extracted_query:
        return None
    with sqlite3.connect(DB_FILE) as db_connection:
        cursor = db_connection.cursor()
        try:
            cursor.execute(extracted_query)
        except Exception as e:
            print(f"Error executing SQL query: {e}")
            print(f"Query: {extracted_query}")
            return None
        results = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]

        return convert_results_to_dict(results, column_names)


def convert_results_to_dict(records, column_names):
    """Convert list of tuples to a list of dictionaries."""
    return [dict(zip(column_names, row)) for row in records]


def get_db_schema():
    db = db_without_solution()
    return db.get_table_info()


def database_connect():
    """Establishes a connection to the SQL database using the provided URI."""
    db = SQLDatabase.from_uri(f"sqlite:///{DB_FILE}")
    return db


def db_without_solution():
    """Connects to SQL database. Solution table is excluded."""
    return SQLDatabase.from_uri(f"sqlite:///{DB_FILE}", ignore_tables=["solution"])
