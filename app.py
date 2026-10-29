"""Portfolio pages, quizzes, and student profile forms.

Week 6 keeps its browser validation and review flow at /submit-profile.
Week 8 validates submissions on the server at /profile-validated.
"""

from flask import Flask, render_template, request
from quiz_api import init_quiz
from validators import validate_profile

app = Flask(__name__)
init_quiz(app)


@app.route("/")
def home():
    """Serve the portfolio home page."""
    weekly_work = [
        {"week": 2, "title": "History of the Internet", "url": "/internet-history"},
        {"week": 2, "title": "History of the Web", "url": "/web-history"},
        {"week": 2, "title": "History of the Internet (AI)", "url": "/internet-history-ai"},
        {"week": 2, "title": "History of the Web (AI)", "url": "/web-history-ai"},
        {"week": 3, "title": "Research", "url": "/research"},
        {"week": 4, "title": "Engineering Student Profile", "url": "/submit-profile"},
        {"week": 5, "title": "JavaScript app", "url": "/quiz"},
        {"week": 6, "title": "JavaScript Form Validation", "url": "/submit-profile"},
        {"week": 7, "title": "Live Quiz with Fetch", "url": "/live-quiz"},
        {"week": 8, "title": "Server-Side Validation", "url": "/profile-validated"},
    ]
    return render_template("index.html", weekly_work=weekly_work)


@app.route("/internet-history")
def internet_history():
    return render_template("internet-history.html")


@app.route("/web-history")
def web_history():
    return render_template("web-history.html")


@app.route("/internet-history-ai")
def internet_history_ai():
    return render_template("internet-history-ai.html")


@app.route("/web-history-ai")
def web_history_ai():
    return render_template("web-history-ai.html")


@app.route("/research")
def research():
    return render_template("research.html")


@app.route("/submit-profile", methods=["GET", "POST"])
def submit_profile():
    """Show the Week 6 form or display its submitted profile."""
    if request.method == "POST":
        data = request.form.to_dict()                   # all single-value fields
        skills = request.form.getlist("skills")         # checkboxes -> list
        software = request.form.getlist("software")     # multiple <select> -> list
        return render_template(
            "profile.html", data=data, skills=skills, software=software
        )

    return render_template("profile-form.html")


@app.route("/profile-validated", methods=["GET", "POST"])
def profile_validated():
    """Show the form, return field errors, or display a validated profile."""
    if request.method == "POST":
        errors, cleaned = validate_profile(request.form)
        if not errors:
            return render_template(
                "profile.html", data=cleaned,
                skills=cleaned["skills"], software=cleaned["software"]
            )
        # Keep the original input so users can correct it without retyping.
        return render_template(
            "profile-form-validated.html", errors=errors, data=request.form,
            sel_skills=request.form.getlist("skills"),
            sel_software=request.form.getlist("software")
        )
    return render_template(
        "profile-form-validated.html", errors={}, data={},
        sel_skills=[], sel_software=[]
    )


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    return render_template("quiz.html")


if __name__ == "__main__":
    app.run(debug=True)
