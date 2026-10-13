# Week 6 implementation and handoff

## What changed

The existing `templates/profile-form.html` now loads `static/profile-validation.js` with `defer`, which waits until HTML parsing finishes. The form has an ID so JavaScript can find it. A separate review section contains a definition list (`dl`, with `dt` labels and `dd` answers) and two explicitly non-submitting buttons. Its heading can receive keyboard focus because of `tabindex="-1"`.

The added CSS hides elements with `is-hidden`, styles the review using the existing site colors, wraps long text, preserves description line breaks, and lets the buttons wrap on narrow screens. The form is hidden, never deleted, reset, copied, or disabled. Its original controls remain the source of the final submission.

`app.py`, `templates/profile.html`, `Procfile`, and `requirements.txt` are unchanged. The form still uses POST to `/submit-profile`. All original control names, values, validation attributes, and hidden form version are preserved. No application dependency was added. Review displays exact submitted values (for example, `computer` and `web-applications`) so it does not silently transform answers.

## Every line of the application JavaScript

Line numbers refer to `static/profile-validation.js`. `const` names a reference that is not reassigned; it does not freeze the referenced HTML element. Blank lines only separate related code.

| Line | Beginner explanation |
| --- | --- |
| 1 | Find the original form by its HTML ID and remember it as `form`. |
| 2 | Find the review section and remember it as `review`. |
| 3 | Find the empty list that will hold review labels and answers. |
| 4 | Find the form's section navigation links by their CSS class. |
| 5 | Start an array: an ordered list of field-name/label pairs. |
| 6 | Pair `student_id` with the Student ID label. |
| 7 | Pair `fullname` with Full name. |
| 8 | Pair `email` with USEK email. |
| 9 | Pair `phone` with Mobile number. |
| 10 | Pair `birthdate` with Date of birth. |
| 11 | Pair `portfolio` with Portfolio / GitHub URL. |
| 12 | Pair `gin446` with GIN446 website URL. |
| 13 | Pair `major` with Engineering major. |
| 14 | Pair `gpa` with Current GPA / 100. |
| 15 | Pair `credits` with Credits completed / 148. |
| 16 | Pair `graduation_month` with the month/year label. |
| 17 | Pair the graduation radio group with Expected graduation. |
| 18 | Pair the optional internship radio group with Internship completed. |
| 19 | Pair the repeated skills checkboxes with Technical skills. |
| 20 | Pair `language` with Primary programming language. |
| 21 | Pair the multiple-selection software control with its label. |
| 22 | Pair `project_title` with Proposed project title. |
| 23 | Pair `project_area` with Preferred project area. |
| 24 | Pair the description textarea with its label. |
| 25 | Pair `team_size` with Preferred team size. |
| 26 | Pair `project_color` with Project dashboard color. |
| 27 | Pair `meeting_date` with Preferred meeting date. |
| 28 | Pair `meeting_time` with Preferred meeting time. |
| 29 | Pair the consent checkbox with its full statement. |
| 30 | Include the existing hidden form version for completeness. |
| 31 | Finish the field list. |
| 33 | Define a reusable function called `editProfile`. Defining it does not run it yet. |
| 34 | Add the CSS class that hides the review. |
| 35 | Remove that class from the original form so it becomes visible. |
| 36 | Show the form's section links again. |
| 37 | Move keyboard focus to Student ID. This does not change its answer. |
| 38 | End the Edit function. |
| 40 | Listen for form submission, including submission using the keyboard; receive its event object. |
| 41 | Cancel the event's default server submission and navigation. |
| 42 | Ask the browser to validate the original HTML rules and show warnings. `!` means 'not', so the block runs if invalid. |
| 43 | Stop this event handler immediately when invalid. |
| 44 | End the invalid-data block. |
| 45 | Create a built-in `FormData` snapshot of the original form's submitted values. This alone sends no network request. |
| 46 | Clear only the old review list, safely, so another review has no stale rows. |
| 47 | Run the following function once for every pair in `fields`. |
| 48 | Create a definition-term element for the field label. |
| 49 | Create a definition-description element for its answer. |
| 50 | Set the label as plain text. Array position 1 is the readable label. |
| 51 | Get every value for this field name. Position 0 is the original control name. `getAll` preserves multiple skills and software selections. |
| 52 | Join the values with commas; if the resulting string is empty, show the explicit empty marker. `textContent` treats typed HTML as text, not executable markup. |
| 53 | Add the label to the review list. |
| 54 | Add its answer immediately after the label. |
| 55 | End the per-field function and its `forEach` call. |
| 56 | Hide the original form without removing its controls or answers. |
| 57 | Hide links to the now-hidden form sections. |
| 58 | Show the completed review. |
| 59 | Focus the review heading, helping keyboard and assistive-technology users locate the new content. |
| 60 | End the submit handler and register it. |
| 62 | Run the existing Edit function whenever the Edit button is clicked. |
| 64 | Register a click handler on Confirm & Submit. |
| 65 | Check validity again before final submission. This also catches a value changed programmatically while the review was open. |
| 66 | If invalid, reveal the original form so its invalid control can receive focus. |
| 67 | Show the browser's validation warning on that visible form. |
| 68 | Stop; do not submit invalid data. |
| 69 | End the final validation failure block. |
| 70 | Perform the genuine native form submission using its existing action and method. `submit()` does not fire another submit event, so there is no interception loop. It also skips automatic validation, which is why lines 65-69 check first. |
| 71 | End the confirmation handler and register it. |

Native browser validation normally blocks invalid submission before the `submit` event fires. The explicit `reportValidity()` also guards the handler itself. Unchecked checkboxes and radios are omitted by `FormData`; `getAll` then gives an empty list and the review shows the empty marker. Empty text controls yield an empty string. Defaults such as team size and color display their actual values. Hiding a control with CSS does not remove it from submission.

## Verification record (13 October 2026)

- Passed: JavaScript syntax check (`node --check static/profile-validation.js`), existing quiz regression tests (`node tests/quiz.test.cjs`), and Git whitespace checks.
- Passed: Flask test-client GET of the form and POST to the original endpoint, including repeated skills and software; the original result template returned HTTP 200 and displayed those submitted values.
- Passed: Git comparison confirmed no changes to `app.py`, `templates/profile.html`, `Procfile`, or `requirements.txt`.
- Resolved test failures: the initial sandbox could not launch Chrome; approved runs outside it worked. The original first-click failure was caused by smooth scrolling, so the test now scrolls instantly. A later run reached the result page but its payload assertion expected LF-only textarea line breaks. Native form submission correctly sends CRLF, so the test expectation now accounts for that standard serialization. Neither issue required changing application code.
- Passed: `python tests/profile_flow.py` in local headless Chrome. Invalid required fields, a short/non-numeric ID, malformed email/URL, missing graduation/consent, numeric min/max violations, and fractional team size stayed out of review. Browser validation messages were nonempty for the individually tested invalid controls.
- Passed: all 25 review rows (24 user-facing groups plus form version), values and order, explicit markers for each empty optional field/group, repeated skills/software, literal HTML-like text, and absence of editable form controls in review.
- Passed: Edit preserves the same form node and all values/selections, focus moves to the review heading and returns to Student ID, keyboard Enter refreshes review after an edit, and no extra network request or document reload occurs during review/Edit. Confirmation revalidation rejects an invalid value introduced while reviewing.
- Passed: exactly one real browser POST to `/submit-profile`, with the full expected payload (including leading zeros, repeated values, consent, form version, and native CRLF line breaks), followed by the original `article.profile` result and HTTP 200.
- Passed: an emulated 390-pixel viewport has no horizontal overflow; screenshots of desktop review, mobile review, and mobile buttons were visually inspected. Evidence is in ignored local files `tmp/week6-review-desktop.png`, `tmp/week6-review-mobile.png`, and `tmp/week6-review-mobile-controls.png`.
- Passed: every existing page route and both Week 6 static assets return HTTP 200; the imported WSGI application has debug disabled. A missing favicon returns 404 and is unrelated to form behavior.
- Not checked: Firefox/Safari, a physical phone, the live Render service, and a Linux/Gunicorn production process. Local testing used the real Flask app through Werkzeug on Windows. Native warning text was checked programmatically; browser warning-bubble appearance was not separately photographed.

### Checklist for the live site

1. Submit an empty form: a native warning appears, review stays closed, and the page does not reload. Repeat with a short ID, invalid email/URL, GPA outside 40-100, credits outside 0-148, team size outside 1-6, missing graduation, and unchecked consent.
2. Complete required fields; leave optional fields blank and groups unselected. Submit and check explicit empty markers, consent, defaults, and all 25 review rows.
3. Select several skills and software options; fill every optional field, including dates, time, color, and a multiline description. Confirm that every answer appears. Text such as `<b>hello</b>` must appear literally.
4. Click Edit. Confirm all answers and selections remain. Change an answer and submit again; check that review updates without duplicate rows or a reload. Try keyboard submission too.
5. In browser Network tools, confirm no POST occurs during review or Edit. Click Confirm & Submit: exactly one POST to `/submit-profile` should produce the original profile result page with the submitted values.
6. Repeat on the deployed site and a narrow/mobile screen. Review buttons must be usable, long values must wrap, and keyboard focus must reach the review heading and return to the form.

## GitHub and Render preparation

Inspected configuration: Git branch `main`; origin `https://github.com/david-eid/web-programming-site.git`; `requirements.txt` contains Flask and Gunicorn; `Procfile` contains `web: gunicorn app:app`. README already specifies build `pip install -r requirements.txt` and start `gunicorn app:app`. No Render URL or dashboard configuration was established in this task.

The local project is ready for the existing Render Python Web Service configuration. The WSGI entry point imports successfully, all templates/assets are present, and no database, secret, or new environment variable is required by this update. No `render.yaml` is needed when the existing service is configured in the dashboard. The repository's commands match [Render's Flask deployment guide](https://render.com/docs/deploy-flask). Actual account settings and production startup still need verification by the owners.

Remaining steps:

1. Review the changes and this disclosure. Run `python tests/profile_flow.py` (Selenium plus Chrome are test-only prerequisites) and `node tests/quiz.test.cjs`.
2. Stage `templates/profile-form.html`, `static/form_style.css`, `static/profile-validation.js`, `tests/profile_flow.py`, `submission/WEEK6.md`, and `submission/WEEK6_AI_CONTRIBUTION.md`. Commit with a message such as `Add Week 6 profile review and confirmation`, then push `main` to `origin`. Check GitHub displays that exact commit and all changed files.
3. In the existing Render service, verify the linked repository/branch, build command, and start command above. Allow its automatic deploy or use Deploy latest commit. Check logs, successful service status, and the deployed commit ID.
4. Open the actual Render `/submit-profile` URL and repeat the checklist, including final submission. A local test is not proof of a successful Render deployment.
5. Export the complete actual AI conversation as PDF and upload it with the accurate contribution statement to e-learning. The pre-existing PDFs in `output/pdf` and earlier contribution files were not rewritten; they do not document this Week 6 session. This handoff is not a conversation transcript.

Exact commands, deployment checks, and conversation-export steps are in `submission/WEEK6_SUBMISSION.md`. The new Week 6 contribution statement is available as Markdown and a separate PDF; the old Week 5 PDFs remain unchanged.

No commit, push, or deployment is claimed by this document.
