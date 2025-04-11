import json


def described_db_schema():
    """Returns the database schema as a list of dictionaries."""
    schema = [
        {
            "table_name": "crime_scene_report",
            "description": "Contains police records of reported crimes including the date, type, description, and the city where the incident occurred.",
            "columns": [
                {
                    "name": "date",
                    "type": "INTEGER",
                    "format": "YYYYMMDD (integer format)",
                    "description": "Date of the crime",
                    "foreign_key": None,
                },
                {
                    "name": "type",
                    "type": "TEXT",
                    "description": "Type of the reported crime",
                    "foreign_key": None,
                },
                {
                    "name": "description",
                    "type": "TEXT",
                    "description": "Narrative description of the crime scene",
                    "foreign_key": None,
                },
                {
                    "name": "city",
                    "type": "TEXT",
                    "description": "Location - city where the crime occurred",
                    "foreign_key": None,
                },
            ],
            "relationships": [],
        },
        {
            "table_name": "drivers_license",
            "description": "Information from driving licenses, including personal attributes and vehicle data.",
            "columns": [
                {"name": "id", "type": "INTEGER", "description": "Unique driver license ID", "foreign_key": None},
                {"name": "age", "type": "INTEGER", "description": "Age of the license holder", "foreign_key": None},
                {
                    "name": "height",
                    "type": "INTEGER",
                    "description": "License holder's height in inches",
                    "foreign_key": None,
                },
                {
                    "name": "eye_color",
                    "type": "TEXT",
                    "description": "License holder's eye color",
                    "foreign_key": None,
                },
                {
                    "name": "hair_color",
                    "type": "TEXT",
                    "description": "License holder's hair color",
                    "foreign_key": None,
                },
                {"name": "gender", "type": "TEXT", "description": "Gender of the license holder", "foreign_key": None},
                {
                    "name": "plate_number",
                    "type": "TEXT",
                    "description": "License holder's car license plate number",
                    "foreign_key": None,
                },
                {
                    "name": "car_make",
                    "type": "TEXT",
                    "description": "Make of License holder's car",
                    "foreign_key": None,
                },
                {
                    "name": "car_model",
                    "type": "TEXT",
                    "description": "Model of License holder's car",
                    "foreign_key": None,
                },
            ],
            "relationships": [
                {
                    "type": "referenced_by",
                    "source_table": "person",
                    "source_column": "license_id",
                    "target_column": "id",
                }
            ],
        },
        {
            "table_name": "facebook_event_checkin",
            "description": "Tracks when a person checked into a Facebook event.",
            "columns": [
                {
                    "name": "person_id",
                    "type": "INTEGER",
                    "description": "ID of the person who checked in",
                    "foreign_key": "person.id",
                },
                {"name": "event_id", "type": "INTEGER", "description": "ID of the event", "foreign_key": None},
                {"name": "event_name", "type": "TEXT", "description": "Name of the event", "foreign_key": None},
                {
                    "name": "date",
                    "type": "INTEGER",
                    "format": "YYYYMMDD  (integer format)",
                    "description": "Date of check-in",
                    "foreign_key": None,
                },
            ],
            "relationships": [
                {"type": "foreign_key", "source_column": "person_id", "target_table": "person", "target_column": "id"}
            ],
        },
        {
            "table_name": "get_fit_now_check_in",
            "description": "Logs each time a gym member checked in and out.",
            "columns": [
                {
                    "name": "membership_id",
                    "type": "TEXT",
                    "description": "Membership ID",
                    "foreign_key": "get_fit_now_member.id",
                },
                {
                    "name": "check_in_date",
                    "type": "INTEGER",
                    "format": "YYYYMMDD  (integer format)",
                    "description": "Date of check-in",
                    "foreign_key": None,
                },
                {
                    "name": "check_in_time",
                    "type": "INTEGER",
                    "format": "minutes passed since midnight",
                    "description": "Time of check-in",
                    "foreign_key": None,
                },
                {
                    "name": "check_out_time",
                    "type": "INTEGER",
                    "format": "minutes passed since midnight",
                    "description": "Time of check-out",
                    "foreign_key": None,
                },
            ],
            "relationships": [
                {
                    "type": "foreign_key",
                    "source_column": "membership_id",
                    "target_table": "get_fit_now_member",
                    "target_column": "id",
                }
            ],
        },
        {
            "table_name": "get_fit_now_member",
            "description": "Information about gym members, including their name, start date, and status.",
            "columns": [
                {"name": "id", "type": "TEXT", "description": "Unique gym membership ID", "foreign_key": None},
                {
                    "name": "person_id",
                    "type": "INTEGER",
                    "description": "Person ID associated with the member",
                    "foreign_key": "person.id",
                },
                {"name": "name", "type": "TEXT", "description": "Name of the gym member", "foreign_key": None},
                {
                    "name": "membership_start_date",
                    "type": "INTEGER",
                    "description": "Start date of the membership",
                    "foreign_key": None,
                },
                {
                    "name": "membership_status",
                    "type": "TEXT",
                    "description": "Membership tier (gold, regular, silver)",
                    "foreign_key": None,
                },
            ],
            "relationships": [
                {"type": "foreign_key", "source_column": "person_id", "target_table": "person", "target_column": "id"},
                {
                    "type": "referenced_by",
                    "source_table": "get_fit_now_check_in",
                    "source_column": "membership_id",
                    "target_column": "id",
                },
            ],
        },
        {
            "table_name": "income",
            "description": "Annual income data matched by social security number.",
            "columns": [
                {
                    "name": "ssn",
                    "type": "INTEGER",
                    "description": "Social Security Number (unique)",
                    "foreign_key": None,
                },
                {
                    "name": "annual_income",
                    "type": "INTEGER",
                    "description": "Annual income in USD",
                    "foreign_key": None,
                },
            ],
            "relationships": [
                {"type": "logical_link", "source_column": "ssn", "target_table": "person", "target_column": "ssn"}
            ],
        },
        {
            "table_name": "interview",
            "description": "Interview transcripts linked to individuals by person ID.",
            "columns": [
                {
                    "name": "person_id",
                    "type": "INTEGER",
                    "description": "ID of the person interviewed",
                    "foreign_key": "person.id",
                },
                {
                    "name": "transcript",
                    "type": "TEXT",
                    "description": "Transcript of the interview",
                    "foreign_key": None,
                },
            ],
            "relationships": [
                {"type": "foreign_key", "source_column": "person_id", "target_table": "person", "target_column": "id"}
            ],
        },
        {
            "table_name": "person",
            "description": "Core table of individuals connected to the case, including identifiers and personal data.",
            "columns": [
                {"name": "id", "type": "INTEGER", "description": "Unique person ID (identifier)", "foreign_key": None},
                {"name": "name", "type": "TEXT", "description": "Full name of the person", "foreign_key": None},
                {
                    "name": "license_id",
                    "type": "INTEGER",
                    "description": "Driver's license ID (linked to drivers_license)",
                    "foreign_key": "drivers_license.id",
                },
                {
                    "name": "address_number",
                    "type": "INTEGER",
                    "description": "Person's street house address number",
                    "foreign_key": None,
                },
                {
                    "name": "address_street_name",
                    "type": "TEXT",
                    "description": "Name of the street person's house is located on",
                    "foreign_key": None,
                },
                {
                    "name": "ssn",
                    "type": "INTEGER",
                    "description": "Social Security Number (used to match with income)",
                    "foreign_key": None,
                },
            ],
            "relationships": [
                {
                    "type": "foreign_key",
                    "source_column": "license_id",
                    "target_table": "drivers_license",
                    "target_column": "id",
                },
                {
                    "type": "referenced_by",
                    "source_table": "facebook_event_checkin",
                    "source_column": "person_id",
                    "target_column": "id",
                },
                {
                    "type": "referenced_by",
                    "source_table": "get_fit_now_member",
                    "source_column": "person_id",
                    "target_column": "id",
                },
                {
                    "type": "referenced_by",
                    "source_table": "interview",
                    "source_column": "person_id",
                    "target_column": "id",
                },
                {"type": "logical_link", "source_column": "ssn", "target_table": "income", "target_column": "ssn"},
            ],
        },
    ]
    return json.dumps(schema, indent=2)
