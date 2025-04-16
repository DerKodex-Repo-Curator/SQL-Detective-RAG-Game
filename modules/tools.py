import json
import re


def model_answer_regex(response, field_name):
    """Extract field value from JSON-like text response."""
    FIELD = rf'"{field_name}"'  # Field name in quotes
    SEPARATOR = r"\s*:\s*"  # Colon : with optional spaces
    QUOTE = r'"'  # Opening quote '
    CONTENT = r'([^"]*)'  # Capture group for field content
    END = r'(?:"|$)'  # Closing quote ' or end of string

    regex = f"{FIELD}{SEPARATOR}{QUOTE}{CONTENT}{END}"
    match = re.search(pattern=regex, string=response, flags=re.VERBOSE)

    if match:
        return match.group(1)
    return None


def manually_parse_response(response):
    """Manually parse string response to extract fields from JSON-like response."""
    fields = ["sql_query", "answer", "next_step", "thinking", "rules_followed", "user_input"]
    parsed_response = {}

    for field in fields:
        value = model_answer_regex(response, field)
        if value:
            parsed_response[field] = value

    return parsed_response


def convert_list_to_string(results, columns):
    """Convert list of tuples to string with column names"""
    results_str = f"{', '.join(columns)}\n"
    for row in results:
        results_str += str(row) + "\n"
    return results_str
