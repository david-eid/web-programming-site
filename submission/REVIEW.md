# Week 5 review and submission checklist

## Implementation
- `app.py` uses the supplied Week 5 server, adding `/quiz` and the home-page link.
- `templates/quiz.html` extends `base.html` and loads `quiz.css` after `style.css`.
- `static/quiz.js` contains 10 question objects, zero-based answer indexes, state, all required functions, and the supplied interface code.
- `static/quiz.css` uses the existing dark-and-gold design variables and scopes every selector to `.quiz-app`.

## Explain the JavaScript
`currentQuestion` stores an array index. `userAnswers` stores each selected choice index at the same question index. An empty slot is `undefined`; index 0 is a real answer. Navigation changes only the current index and rerenders, so previous answers are retained. Boundary conditions prevent indexes outside the array. Scoring adds one only for strict equality with the correct index. Percentage is rounded with `Math.round`. Performance tests run from highest to lowest: 80+, 60+, 50+, below 50. Correction loops over every question, including unanswered ones. The provided UI uses `textContent` for correction text, so answer text is not interpreted as HTML.

## Explain every CSS group
1. `.quiz-app`: limits reading width and centers the quiz within the site's main area.
2. `.quiz-eyebrow`, `.quiz-intro`: establish hierarchy, letter spacing, readable line length, and spacing.
3. Panel selectors: responsive padding with `clamp`.
4. `#progress`: a compact gold outlined pill for question position.
5. `#questionText`: readable responsive question size and line height.
6. `.choice`: flex alignment, spacing, dark background, clickable label, wrapping.
7. Choice hover, `:has(input:checked)`, and `:focus-within`: separate hover, selected, and keyboard-focus states.
8. Radio input: native control with consistent size and gold accent; flex shrinking is disabled.
9. `.navigation`: wrapping buttons, spacing, and a divider.
10. Buttons: inherited typography, minimum 44px height, borders, padding, and pointer cursor.
11. Button states: hover is limited to enabled controls, focus has a visible outline, disabled controls are dimmed.
12. Submit button: gold background with dark text, separate spacing, lighter hover.
13. `#resultsPanel`: initially hidden; the provided JS sets inline display to show it after submission.
14. Result text: larger score, compact percentage spacing, outlined performance label.
15. `#correction`: keeps newlines while wrapping long text and inheriting readable typography.
16. Small-screen media query: two-column navigation and full-width submit button.

## Verification performed
Run `node tests/quiz.test.cjs`. The checks cover navigation and bounds, saved/changed answers, unanswered/wrong/correct scoring, zero/full/mixed results, rounding with 11 questions, all performance thresholds, correction counts, and result-panel wiring using a minimal DOM test double. This is not a real-browser test.
Flask test-client checks passed for the home page, quiz, profile form, four history pages, quiz assets, and a profile POST with multiple skill/software values.

## Manual checks still required
- Open `/quiz` on desktop and phone. Check legibility, wrapping, focus outlines, and no horizontal overflow.
- Select the first option, navigate away and return; confirm it remains selected.
- Use Tab/arrow keys to select options and activate all four navigation buttons.
- Submit once with unanswered questions and once with all correct answers.
- Verify the live Render `/quiz` page after deployment.
- Read the CSS and JS in VS Code and explain each accepted rule/function.

## Submission and authorship
The screenshot brief permits AI-assisted styling. In this session AI also implemented the application logic, question data, and integration. Do not describe those as independently student-written. Review the course rules with the instructor if AI implementation of Part 1 is not permitted.
The generated session-summary PDF is explicitly a summary, not a full chat transcript. Export this actual conversation to PDF for the requested conversation deliverable; do not replace it with invented prompts.
A 100/100 grade cannot be guaranteed. The student audit, real-browser checks, live deployment verification, and instructor assessment remain necessary.

## Existing work preserved
The profile form already existed as `templates/profile-form.html`; it was not rewritten. The supplied Week 5 server expects that filename. The separate pasted Week 4 brief requests `profile_form.html` and references a detailed field spec that was not supplied here. Exact Week 4 compliance is therefore not certified. Existing uncommitted changes to shared styles/templates were preserved.
