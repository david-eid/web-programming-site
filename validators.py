"""Server-side checks for the Week 8 student profile."""
import math
import re
from datetime import date
from urllib.parse import urlsplit

STUDENT_ID = re.compile(r"[0-9]{9}")
FULLNAME = re.compile(r"[A-Za-z][A-Za-z .'\-]{1,79}")
EMAIL = re.compile(r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@net\.usek\.edu\.lb")
PHONE = re.compile(r"\+961 ?[1-9][0-9]? ?[0-9]{3} ?[0-9]{3}")
GITHUB = re.compile(r"https://github\.com/[A-Za-z0-9-]+(?:/[^\s]*)?")
HTTPS_URL = re.compile(r"https://[^\s<>\"\\]+")
MONTH = re.compile(r"[0-9]{4}-(?:0[1-9]|1[0-2])")
TIME = re.compile(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]")
HEXCOLOR = re.compile(r"#[0-9a-fA-F]{6}")

MAJORS = {"computer", "electrical", "biomedical", "telecommunications"}
GRADUATION = {"spring", "summer", "fall"}
YESNO = {"yes", "no"}
SKILLS = {"programming", "embedded-systems", "electronics", "computer-networks",
          "telecommunications", "biomedical-instrumentation",
          "artificial-intelligence / machine-learning", "signal-processing"}
SOFTWARE = {"MATLAB", "Simulink", "LabVIEW", "LTspice", "Vivado", "SolidWorks"}
PROJECT_AREAS = {"artificial-intelligence", "web-applications", "cybersecurity",
                 "internet-of-things", "power-systems", "renewable-energy",
                 "control-systems", "medical-imaging", "biosensors", "medical-devices",
                 "wireless-communications", "5g / 6g-networks"}
REQUIRED = {"student_id", "fullname", "email", "major", "gpa", "graduation"}


def parse_date(text):
    # Require the HTML date format before checking the calendar date.
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text):
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def to_number(text):
    try:
        number = float(text)
        # float() also accepts NaN and infinity; neither is a valid GPA.
        return number if math.isfinite(number) else None
    except ValueError:
        return None


def to_int(text):
    if not re.fullmatch(r"[+-]?[0-9]+", text):
        return None
    try:
        return int(text)
    except ValueError:
        return None


def validate_profile(form):
    """Return field errors and normalized values; use cleaned only if errors is empty."""
    errors = {}
    fields = ("student_id fullname email phone birthdate portfolio gin446 major gpa credits "
              "graduation graduation_month internship_completed language project_title "
              "project_area description team_size project_color meeting_date meeting_time confirmation").split()
    cleaned = {field: form.get(field, "").strip() for field in fields}
    cleaned["email"] = cleaned["email"].lower()
    cleaned["major"] = cleaned["major"].lower()
    for field in REQUIRED:
        if not cleaned[field]:
            errors[field] = "This field is required."

    patterns = {
        "student_id": (STUDENT_ID, "Student ID must be exactly 9 digits."),
        "fullname": (FULLNAME, "Use letters, spaces, periods, hyphens or apostrophes (2-80 characters)."),
        "email": (EMAIL, "Use your USEK email (...@net.usek.edu.lb)."),
        "phone": (PHONE, "Enter a valid Lebanese number, e.g. +961 70 123456."),
        "portfolio": (GITHUB, "Use a GitHub URL: https://github.com/username"),
        "graduation_month": (MONTH, "Use the month picker (YYYY-MM)."),
        "project_color": (HEXCOLOR, "Use a colour like #336699."),
        "meeting_time": (TIME, "Use HH:MM."),
    }
    for field, (pattern, message) in patterns.items():
        if cleaned[field] and not pattern.fullmatch(cleaned[field]):
            errors[field] = message

    link = cleaned["gin446"]
    if link:
        try:
            parts = urlsplit(link)
            valid = (HTTPS_URL.fullmatch(link) and parts.hostname and
                     not parts.username and not parts.password)
            parts.port  # Reject malformed ports too.
        except ValueError:
            valid = False
        if not valid:
            errors["gin446"] = "Enter a valid https:// link."

    for field, allowed in {"major": MAJORS, "graduation": GRADUATION,
                           "internship_completed": YESNO, "project_area": PROJECT_AREAS}.items():
        if cleaned[field] and cleaned[field] not in allowed:
            errors[field] = "Choose a valid " + field.replace("_", " ") + "."

    for field, low, high, parser in [("gpa", 40, 100, to_number),
                                     ("credits", 0, 148, to_int), ("team_size", 1, 4, to_int)]:
        if cleaned[field]:
            number = parser(cleaned[field])
            if number is None or not low <= number <= high:
                kind = "a whole number" if parser == to_int else "a number"
                errors[field] = f"{field.replace('_', ' ').capitalize()} must be {kind} between {low} and {high}."

    for field in ("birthdate", "meeting_date"):
        if cleaned[field]:
            day = parse_date(cleaned[field])
            if day is None:
                errors[field] = "Not a valid date."
            elif field == "birthdate":
                today = date.today()
                # Subtract a year if this year's birthday has not happened yet.
                age = today.year - day.year - ((today.month, today.day) < (day.month, day.day))
                if day > today:
                    errors[field] = "Date of birth cannot be in the future."
                elif not 15 <= age <= 100:
                    errors[field] = "Age must be between 15 and 100."
    month = cleaned["graduation_month"]
    if month and "graduation_month" not in errors and parse_date(month + "-01") is None:
        errors["graduation_month"] = "Use a valid month (YYYY-MM)."
    # Zero-padded HH:MM values sort in time order after the format check.
    meeting_time = cleaned["meeting_time"]
    if meeting_time and "meeting_time" not in errors and not "08:00" <= meeting_time <= "18:00":
        errors["meeting_time"] = "Pick a time between 08:00 and 18:00."

    for field, limit in [("language", 39), ("project_title", 120), ("description", 1000)]:
        if len(cleaned[field]) > limit:
            errors[field] = f"Use {limit} characters or fewer."
    for field, allowed in [("skills", SKILLS), ("software", SOFTWARE)]:
        values = form.getlist(field)
        cleaned[field] = [value for value in values if value in allowed]
        if len(cleaned[field]) != len(values):
            errors[field] = "Choose only the listed " + field + "."
    if cleaned["confirmation"] != "yes":
        errors["confirmation"] = "You must confirm the information is accurate."
    cleaned["project_color"] = cleaned["project_color"] or "#336699"
    cleaned["form_version"] = "2026-2027"
    return errors, cleaned
