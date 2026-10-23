"""Render start command: initialize PostgreSQL before starting web workers."""
import os
import sys

from seed_db import main


if __name__ == "__main__":
    if not os.environ.get("DATABASE_URL"):
        sys.exit("DATABASE_URL is required; web server was not started.")
    if main(require_postgres=True):
        sys.exit(1)
    os.execvp("gunicorn", ["gunicorn", "--bind", "0.0.0.0:" + os.environ.get("PORT", "10000"), "app:app"])
