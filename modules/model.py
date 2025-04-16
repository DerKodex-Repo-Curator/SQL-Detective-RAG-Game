import json

from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama

from modules.database.custom_db_schema import described_db_schema
from modules.database.db import db_without_solution
from modules.settings import DETECTIVE_MODEL, TRANSLATOR_MODEL
from modules.tools import manually_parse_response, model_answer_regex


class Model:
    """Base class for all models."""

    def __init__(self, user_input, context=None):
        self.user_input = user_input
        self.context = context
        self.model = self.select_model()
        self.full_response = self.get_model_response()
        self.sql_query = self.get_field("sql_query")
        self.answer = self.get_field("answer")
        self.next_step = self.get_field("next_step")
        self.thinking = self.get_field("thinking")
        self.rules = self.get_field("rules_followed")

    def get_model_response(self):
        """Get response using instance attributes."""
        try:
            langchain = self.build_langchain()
            response_str = langchain.invoke(self.model_input())
            try:
                parsed_response = json.loads(response_str)
                return parsed_response
            except Exception as e:
                print(f"Error parsing JSON: {e}\nParsing manually...")
                parsed_response = manually_parse_response(response_str)
                return parsed_response
        except Exception as e:
            return f"Model Connection error. Make sure Ollama is running and {self.model} is installed.\n{e}"

    def get_field(self, field=None):
        """Get SQL query from parsed_response."""
        if isinstance(self.full_response, dict):
            return self.full_response.get(field)

        if isinstance(self.full_response, str):
            return model_answer_regex(self.full_response, field)
        return None

    def get_thinking_process(self):
        """Get thinking process from parsed_response."""
        return self.response_json.get("thinking")


class Translator(Model):
    """SQL Translator model class."""

    def select_model(self):
        """Choose the model for translation."""
        return TRANSLATOR_MODEL

    def model_input(self):
        return {
            "input": self.user_input,
            "question": self.user_input,
            "top_k": 1,
            "top_p": 0.80,
        }

    def prompt(self) -> str:
        """Prompt template to translate text instructions into SQL query"""
        translator = """
        **ROLE:** You are a SQL Analyst. Your task is to translate the following question into a valid SQL query. Use {dialect} dialect.

        **Rules:**
        0. All dates use format YYYYMMDD.
        1. Output must contain a valid, properly constructed SQL Query.
        2. The query must strictly follow the provided database schema and use only the available tables and columns.
        3. Database schema contains "description" and "format" of the tables and columns contents. Make sure to follow it carefully.
        4. Keep the thinking process brief, ensuring it logically aligns with the user input.
        5. Fetch all columns by default using 'SELECT *', unless a specific column is mentioned in the input.
        6. Be flexible in interpreting imprecise or incomplete user input while providing a valid SQL query.
        7. Do not use your own knowledge or external sources.
        8. Do not assume anything that is not explicitly present in the schema.
        9. ONLY return the SQL query, no additional explanations or text.
        10. If the user is asking about the order of items (first, last etc.), use an ORDER BY clause based on the relevant column.
        11. While using columns from multiple tables, ensure you call proper tables.

        **Database Schema:**
        {table_info}

        **Examples:**
    
        User: "find all theft cases from SQL City"
        SQL Query: "SELECT * FROM crime_scene_report WHERE type = 'theft' AND city = 'SQL City';"
        
        User: "Find who lives in the first house in Northwestern Dr"
        SQL Query: "SELECT * FROM person WHERE address_street_name = 'Northwestern Dr' ORDER BY address_number ASC LIMIT 1;"
        
        User: "find all people with blue eyes"
        SQL Query: "SELECT * FROM person JOIN drivers_license ON person.license_id = drivers_license.id WHERE drivers_license.eye_color = 'blue';"
    
        **Input:** {input}

        **Output:**
        ```json
        {{
            "user_input": "{input}",
            "sql_query": "SELECT * FROM table_name WHERE condition;"
        }}
        top_k: {top_k}
        top_p: {top_p}
        ```
        """
        return PromptTemplate(
            template=translator,
            input_variables=["input"],
            partial_variables={
                "dialect": "sqlite",
                "table_info": described_db_schema(),
            },
        )

    def build_langchain(self):
        """Builds and returns a language chain with database and Ollama connections."""
        db = db_without_solution()
        llm = ChatOllama(
            temperature=0,
            seed=1,
            model=self.model,
            num_predict=1024,  # Output tokens limit
            format="json",
            mirostat=2,
            mirostat_eta=2,
            mirostat_tau=1,
            tfs_z=50,  # reduce the impact of less probable tokens
            repeat_penalty=1.5,
            top_k=2,
        )
        prompt = self.prompt()
        return create_sql_query_chain(llm, db, prompt)


class Detective(Model):
    """Detective model for analyzing case data and providing conclusions."""

    def select_model(self):
        """Choose the model for detective."""
        return DETECTIVE_MODEL

    def model_input(self):
        return {
            "user_input": self.user_input,
            "context": self.context,
        }

    def prompt(self) -> str:
        """Prompt template to translate text instructions into SQL query"""
        detective = """
        **ROLE:** You are a detective solving a case. Analyze the provided information in reference to the user's question. Your response must be concise, fact-based, and logically structured.

        **Rules:**
        1. Provide an "answer" based only on the given context.
        2. Suggest a "next_step" that logically follows from the answer.
        3. Keep "thinking" brief but clear, explaining how the answer was derived.
        4. Use only the received data—do not assume or use external knowledge.
        5. Use exact column names from the query results in responses.
        6. For **last, highest, or largest values**, return the maximum in the relevant column.
        7. For **first, lowest, or smallest values**, return the minimum in the relevant column.
        8. For **specific persons, objects, or events**, find an exact match in the data.
        9. For **patterns, summaries, or trends**, analyze and summarize the provided data.
        10. Dates are stored in the database as integers in the format YYYYMMDD. Make sure you read them properly.
        11. If query results contain relevant data, extract and summarize key information.
        12. If multiple records match, summarize them concisely.
        13. If no relevant data is found, return `"answer": "No relevant data available."`
        14. If the user input is ambiguous, provide a response based on the most likely interpretation.
        15. Ensure the answer is correct—scan the received context carefully.

        **User_input:** {{user_input}}

        **Context:** {{context}}

        **Output:**
        ```json
        {{
            "answer": "Your conclusion here.",
            "next_step": "Logical next step based on the answer.",
            "thinking": "Reasoning behind the answer and next step.",
            "user_input": "{user_input}",
            "rules_followed": "[List rules followed while generating answer.]"
        }}
        ```
        """
        return PromptTemplate(
            template=detective,
            input_variables=["user_input", "context"],
            partial_variables={
                "top_k": 1,
            },
        )

    def build_langchain(self):
        """Builds and returns a language chain with database and Ollama connections."""
        llm = ChatOllama(
            temperature=0,
            seed=1,
            model=self.model,
            num_predict=1024,  # Output tokens limit
            top_p=0.95,
            format="json",
            mirostat=2,
            mirostat_eta=2,
            mirostat_tau=1,
            tfs_z=50,  # reduce the impact of less probable tokens
            repeat_penalty=1.5,
        )
        prompt = self.prompt()

        return (
            {"user_input": RunnablePassthrough(), "context": lambda x: self.context} | prompt | llm | StrOutputParser()
        )
