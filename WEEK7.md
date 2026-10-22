# Week 7 handoff — David Eid

Implementation and local testing: 22 October 2026. No Git staging, commit, push,
remote repository changes, Render changes, or production database connections
were performed.

## Files

Modified:
- `app.py`: registers the supplied quiz Blueprint through `init_quiz(app)` and
  adds the Week 7 homepage card. Every original route remains unchanged.
- `requirements.txt`: adds Flask-SQLAlchemy and psycopg2-binary using the supplied
  requirements. Flask and Gunicorn remain.
- `.gitignore`: excludes SQLite databases, sidecar files, environment variants,
  and Flask instance data in addition to the existing exclusions.
- `README.md`: adds local seeding, testing, and a link to this handoff.

Created:
- `quiz_api.py`: exact copy of the provided backend, unchanged.
- `seed_db.py`: supplied seeding logic with the ten original Week 5 questions;
  removes credential-bearing comments and connection-URL logging.
- `templates/live_quiz.html`: copied Week 5 interface with the new script,
  accessible loading/error messages, retry control, and initially disabled buttons.
- `static/live_quiz.js`: asynchronous fetch, cache, navigation, answer storage,
  scoring, correction, input validation, and recoverable error handling.
- `static/live_quiz.css`: scoped feedback/focus styles and small-screen spacing;
  uses the existing `quiz.css` and site colors.
- `tests/live_quiz_flow.py`: isolated SQLite API tests and real Chrome integration tests.
- `WEEK7.md`: this handoff, rubric, walkthrough, and deployment instructions.

Local-only generated items: `quiz.db` (ten seeded questions), Python cache files,
`tmp/` (baseline hashes/copies, extracted reference text, screenshots), and
`.codex-tmp/` (test dependencies). These are ignored and must not be staged.
Existing Week 5 files, Week 6 form code, shared templates/styles, other assignment
pages, `Procfile`, and the original test files were preserved.

## How it works / professor walkthrough

1. In `app.py`, `init_quiz(app)` configures SQLAlchemy, creates the question table
   if absent, and registers `/live-quiz`, `/api/questions/count`, and
   `/api/question/<index>`. Without `DATABASE_URL`, the provided helper uses
   `quiz.db` in the current working directory. With the environment variable,
   it uses PostgreSQL and normalizes `postgres://` / `postgresql://` to the
   psycopg2 driver. Always run local commands from the project root.
2. `seed_db.py` converts my existing Week 5 questions into Python dictionaries.
   Choices are stored as JSON text. It inserts only when the table is empty;
   running it twice does not duplicate data. It does not overwrite an existing
   nonempty database or synchronize later content changes.
3. On page load, `init()` fetches the count before rendering question zero.
   `getQuestion(index)` uses a relative URL, checks `response.ok`, then awaits
   `response.json()` to read and parse the body. The browser gets the questions
   from Flask, not a hardcoded question array in the live JavaScript.
4. `async` makes a function return a Promise. `await` pauses that function while
   its asynchronous operation completes; the browser can still process events.
   Rendering, scoring, correction, and submission await their required data.
5. `cache[index]` remembers successful question responses for this page visit.
   `pending[index]` also shares a request that is still in progress. Failed
   requests are removed so retry can send a fresh request.
6. HTTP 404/500 responses do not reject `fetch` automatically, so `response.ok`
   must be checked. Network, HTTP, invalid JSON, and malformed question failures
   propagate to a `try/catch` around rendering or submission. `finally` always
   hides loading and restores controls. Retry keeps the selected answers.
7. `userAnswers[index]` stores a choice index, including zero. Rendering restores
   the checked radio button. Answers last until leaving/reloading the page.
   Buttons are disabled at the boundaries and while requests are running;
   handlers also guard invalid indices and concurrent actions. The displayed
   index changes only after a question loads successfully.
8. Scoring adds one point for each strict match between the stored choice and
   the API's correct answer. Undefined answers earn zero. Percentage is
   `Math.round(score / total * 100)`. Messages are Excellent (80+), Good (60+),
   Pass (50+), and Needs improvement. Correction includes every question,
   selected/correct answer, result, and explanation; missing answers say
   `Not answered`. Results appear only after scoring and correction succeed.
9. API text is inserted with text nodes / `textContent`, not interpolated HTML.
   As required by the assignment, the answer is in the public API and scoring
   is in the browser. This is a practice quiz, not a secure examination system.

Short demonstration: open the Week 7 homepage card; select an answer; press Next,
Last, then First to show that it is remembered. In browser Network tools, revisit
questions to show the cache. Leave questions blank and submit to show the score
and complete correction. Explain the fetch/check/JSON/await/catch sequence above.

## Executed local checks

- Seeded local SQLite: `Seeded 10 questions.`; second run:
  `Already seeded: 10 questions.` No connection URL printed.
- `node --check static/live_quiz.js`: passed.
- `node tests/quiz.test.cjs`: passed the existing Week 5 navigation, scores,
  percentage rounding, all performance boundaries, correction, and results tests.
- `python tests/live_quiz_flow.py`: passed API/startup and Chrome tests:
  - All nine page routes return 200; original quiz POST and profile POST work.
  - Count is 10; every question payload matches the seeded data.
  - Negative, out-of-range, nonnumeric, and decimal indices return 404.
  - Seeder rerun is safe; SQLite fallback and PostgreSQL URI normalization work.
  - First/Previous/Next/Last, boundaries, saved selections, keyboard selection,
    cache hits, in-flight request sharing, rapid-action locking, and no reload.
  - Zero, partial, full scores; all performance thresholds; every explanation;
    correct/incorrect markers and unanswered items.
  - HTTP errors, network rejection, malformed JSON, malformed count, empty
    database response, initial question failure, navigation failure, scoring
    failure, and correction failure show feedback and support retry.
  - Loading appears during startup/navigation and disappears on completion.
  - No uncaught JavaScript errors during tested flows. Injected HTTP failures
    intentionally produce failed-request network messages in the browser.
  - Quiz and results have no horizontal overflow/clipped controls or overlapping
    navigation buttons at 320, 375, 390, 430, 768, and 1280 CSS pixels.
  - Original Week 5 browser navigation/submission and the Week 7 home link work.
- `python tests/profile_flow.py`: existing Week 6 Chrome test passed native
  validation, email rules, all 25 review values, Edit/state retention, safe text,
  final revalidation, mobile overflow, and exactly one correct POST.
- Screenshots of quiz and results saved in `tmp/`; representative desktop and
  mobile views visually inspected.

Tests used Python 3.13, Node 24, Selenium/Chrome, Flask 3.1.3,
Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.1.6, and psycopg2-binary 2.9.13.
Database packages were installed in ignored `.codex-tmp/deps` for the test session;
commands used that directory through `PYTHONPATH`. Normal setup uses the virtual
environment instructions in README.

Not executed: real PostgreSQL connection/seeding, Linux Gunicorn runtime,
Render build/deployment/live URL tests, or Git history/status/diff verification.
This supplied folder has no `.git` directory. Baseline file hashes and local
file comparisons substitute for a Git diff, but cannot verify remote/history
state. No production credentials were used. These deployment checks remain
David's responsibility after review.

## Grading rubric checklist (100 possible points)

This is an evidence checklist, not an awarded grade.

| Criterion | Points | Evidence/status |
|---|---:|---|
| Duplicate template, live script, loading/error elements | 10 | Implemented; rendered and tested |
| No hardcoded live questions; fetch count and individual questions | 25 | Implemented; API/request-count tests passed |
| async/await and response.json() | 15 | Implemented and reviewed; browser flows passed |
| response.ok and try/catch | 15 | Implemented; injected errors/retries passed |
| Loading and error states | 10 | Startup, navigation, submission, and failures tested |
| Navigation, disabled boundaries, remembered answers | 15 | Browser and keyboard tests passed |
| Score, percentage, message, full correction, unanswered | 5 | Zero/partial/full scores and corrections passed |
| Week 7 home link, relative URLs, live Render, explain changes | 5 | Local link/URLs passed; walkthrough above; live deployment and David's explanation remain to verify |

Part A: supplied backend registered, dependencies added, ten personal questions,
SQLite seeded twice, API checked, and PostgreSQL environment configuration
prepared. The production database and deployment portions are intentionally
left for David. Part B is implemented and locally tested.

## Security review

The downloaded seeder contained two credential-bearing database URL comments
and printed the full connection URL on success. Neither is present in the
project's seeder. No database password or credential-bearing URL was found in
the project source review. Secrets are read from the environment. SQLite files,
`.env`/`.env.*`, dependencies, and temporary evidence are ignored.

Ask the owner of the credentials in the supplied seeder to rotate/revoke them;
if they belong to your database, rotate them before deployment and update the
Render environment variable. Removing comments does not revoke a password.
If those credentials were ever committed elsewhere, rotate first, then review
that repository's history separately. This folder has no Git history to inspect.
Do not copy the original downloaded seeder back over the sanitized version.

## Your Git steps

This directory is not currently a Git checkout. First copy the eleven deliverable
files listed above into your existing local checkout, preserving their paths,
or restore the intended Git metadata yourself. Do not blindly initialize a new
unrelated repository. In the correct checkout, review the remote and branch:

```powershell
git status --short
git remote -v
git branch --show-current
git diff --check
git diff
```

Then stage only these explicit files:

```powershell
git add -- .gitignore app.py requirements.txt README.md quiz_api.py seed_db.py templates/live_quiz.html static/live_quiz.js static/live_quiz.css tests/live_quiz_flow.py WEEK7.md
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "Complete Week 7 database-backed live quiz with Fetch and regression tests"
git push origin HEAD
```

`HEAD` pushes the current branch to the matching branch on origin. Confirm this
is the branch used by your existing Render service before pushing. If Render
auto-deploy is enabled, your push can trigger deployment; configure the database
first or control auto-deploy yourself. None of these Git mutation commands was run.

## Render configuration and seeding — performed by David

Use the existing Render web service. Keep these settings:

- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app` (already in `Procfile`)
- Runtime: Python 3; no Selenium or Node runtime is required for the website.

Create/select a Render PostgreSQL database in the same workspace/region as your
web service. Set the web service's `DATABASE_URL` environment variable to its
**Internal Database URL**. Store the URL only in Render's environment settings.
Do not put it in Python, Git, screenshots, or this document. Without this variable,
the provided helper falls back to SQLite; that is intended for local use.

After you deploy your reviewed code, run `python seed_db.py` once in the service's
Render Shell if your plan provides it. That uses the configured internal URL.
Alternatively, from your local project virtual environment, securely enter the
**External Database URL** without putting it in command history:

```powershell
$quizUrlSecure = Read-Host "Render External Database URL" -AsSecureString
$quizUrlPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($quizUrlSecure)
try {
    $env:DATABASE_URL = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($quizUrlPointer)
    python seed_db.py
} finally {
    Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($quizUrlPointer)
    Remove-Variable quizUrlSecure, quizUrlPointer
}
```

Use the external URL's TLS settings; for a URL without query parameters, append
`?sslmode=require` when entering it. Allow your client IP in the database's
external access settings if required. Do not weaken database access controls to
run the seeder. Expected output is `Seeded 10 questions.` A rerun should report
`Already seeded: 10 questions.` Run one seeder at a time. If it reports a different
existing count, inspect that database first: the supplied logic intentionally
does not delete or replace a nonempty question table.

Verify your deployed `/api/questions/count` returns `{"count":10}`, check
`/api/question/0` and `/api/question/1`, confirm `/api/question/10` returns 404,
then test `/live-quiz`, the home link, old pages, and the profile form.
Never use `python app.py` or Flask debug mode as the production start command.

Official references checked for these settings:
- [Render Flask deployment](https://render.com/docs/deploy-flask)
- [Render PostgreSQL connection URLs](https://render.com/docs/postgresql-creating-connecting)

## Truthful AI contribution statement

Suggested statement for David to review and adapt:

> I used OpenAI Codex to inspect my existing GIN446 Flask project and the supplied
> Week 7 materials; integrate the provided database API; adapt my Week 5 questions
> into the seeder; implement the asynchronous live quiz; remove embedded database
> credentials and URL logging; and create and run local regression/browser tests.
> Codex also prepared deployment instructions and this explanation. The Week 7
> frontend implementation and test code were substantially AI-assisted. The
> original course backend and existing website provided the starting point.
> GitHub operations, Render configuration, and deployment are my responsibility
> and were not performed by Codex.

Do not claim you independently authored this implementation. Review and understand
it before submission. The materials request an AI conversation PDF as well as the
contribution statement; export the actual conversation yourself from the chat UI
for that deliverable. This handoff is not a substitute for the conversation export.
