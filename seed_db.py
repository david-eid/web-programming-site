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
from flask import Flask
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


# A minimal app just for seeding (separate from your web app).
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    if Question.query.count() == 0:
        for q in QUESTIONS:
            db.session.add(
                Question(
                    question=q["question"],
                    choices=json.dumps(q["choices"]),
                    answer=q["answer"],
                    explanation=q["explanation"],
                )
            )
        db.session.commit()
        print("Seeded", len(QUESTIONS), "questions.")
    else:
        print("Already seeded:", Question.query.count(), "questions.")
