"""
Week 7 — Database seeder (provided). Run this ONCE to fill the database with
the quiz questions. Adapted with David Eid's Week 5 questions; credentials and URL logging removed.

RUN IT:
  - Locally (fills the local SQLite file quiz.db):
        python seed_db.py
  - Against your Render database (fills the PostgreSQL database):
        set the DATABASE_URL environment variable to your database's EXTERNAL URL,
        then run:  python seed_db.py

It creates the table if needed and inserts the questions only if the table is empty,
so it is safe to run more than once.
"""

import json
import sys
from flask import Flask
from sqlalchemy import select, func, text
from quiz_api import db, Question, database_uri

QUESTIONS = [
    {
        "question": "Which keyword declares a block-scoped variable that can later be reassigned?",
        "choices": [
            "var",
            "let",
            "const",
            "static"
        ],
        "answer": 1,
        "explanation": "let declares a block-scoped variable whose value may later be reassigned."
    },
    {
        "question": "Which JavaScript operator tests strict equality?",
        "choices": [
            "=",
            "==",
            "===",
            "!="
        ],
        "answer": 2,
        "explanation": "The === operator compares both value and type."
    },
    {
        "question": "Which property gives the number of elements in an array?",
        "choices": [
            "size",
            "count",
            "length",
            "total"
        ],
        "answer": 2,
        "explanation": "An array's length property gives its number of elements."
    },
    {
        "question": "What is the index of the first element in an array?",
        "choices": [
            "0",
            "1",
            "-1",
            "It depends on the array"
        ],
        "answer": 0,
        "explanation": "JavaScript arrays use zero-based indexes, so the first element is at index 0."
    },
    {
        "question": "What does a function's return statement do?",
        "choices": [
            "Repeats the function",
            "Displays a message",
            "Declares a variable",
            "Ends the function and sends back a value"
        ],
        "answer": 3,
        "explanation": "return ends the function call and optionally provides a value to its caller."
    },
    {
        "question": "What is the result of 7 % 3?",
        "choices": [
            "2",
            "1",
            "3",
            "0"
        ],
        "answer": 1,
        "explanation": "The remainder operator % returns 1 because 7 divided by 3 leaves a remainder of 1."
    },
    {
        "question": "Which loop is commonly used when the number of repetitions is known?",
        "choices": [
            "if",
            "switch",
            "for",
            "return"
        ],
        "answer": 2,
        "explanation": "A for loop combines initialization, a condition, and an update to control repetitions."
    },
    {
        "question": "Given const student = {name: 'Maya'}, how do you read the name?",
        "choices": [
            "student.name",
            "student( name )",
            "student->name",
            "name.student"
        ],
        "answer": 0,
        "explanation": "Dot notation reads a named property of an object: student.name."
    },
    {
        "question": "What does 'JavaScript'.toUpperCase() return?",
        "choices": [
            "javascript",
            "JavaScript",
            "JAVASCRIPT",
            "Java Script"
        ],
        "answer": 2,
        "explanation": "toUpperCase() returns a new string with its letters converted to uppercase."
    },
    {
        "question": "What is the value of true && false?",
        "choices": [
            "true",
            "false"
        ],
        "answer": 1,
        "explanation": "Logical AND is true only when both Boolean operands are true."
    }
]


def seed_database(require_postgres=False):
    """Insert the assignment once, atomically; never modify existing rows."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"hide_parameters": True}
    db.init_app(app)
    with app.app_context():
        try:
            if require_postgres and db.engine.dialect.name != "postgresql":
                raise RuntimeError("Render startup requires PostgreSQL in DATABASE_URL.")
            with db.engine.begin() as connection:
                if connection.dialect.name == "postgresql":
                    # Serializes overlapping deployments, including table creation.
                    connection.execute(text("SET LOCAL lock_timeout = '60s'"))
                    connection.execute(text("SELECT pg_advisory_xact_lock(446, 7)"))
                elif connection.dialect.name == "sqlite":
                    connection.exec_driver_sql("BEGIN IMMEDIATE")
                db.metadata.create_all(connection)
                table = Question.__table__
                count = connection.scalar(select(func.count()).select_from(table))
                if count:
                    print("Already seeded:", count, "questions.")
                    if count != len(QUESTIONS):
                        print("NOTICE: existing question count differs from 10; all rows preserved.")
                    return count
                connection.execute(table.insert(), [
                    dict(q, choices=json.dumps(q["choices"])) for q in QUESTIONS
                ])
            print("Seeded", len(QUESTIONS), "questions.")
            return len(QUESTIONS)
        finally:
            db.session.remove()
            db.engine.dispose()


def main(require_postgres=False):
    try:
        seed_database(require_postgres=require_postgres)
    except Exception:
        # Driver exceptions can contain credentials or connection strings.
        print("Database initialization failed; no partial seed was committed. "
              "Check DATABASE_URL and database availability in Render.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
