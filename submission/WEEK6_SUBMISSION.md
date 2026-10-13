# Week 6: final submission steps

Local implementation and browser testing are complete. No commit, push, or deployment was performed. The full testing record and JavaScript explanation are in `WEEK6.md`.

## 1. Push when you are ready

Run these commands yourself from the project folder. Review the diff first. Include only the intended Week 6 files; the screenshots under `tmp/` are ignored and are not needed for deployment.

```powershell
git status --short
git diff -- templates/profile-form.html static/form_style.css
git add templates/profile-form.html static/form_style.css static/profile-validation.js tests/profile_flow.py submission/WEEK6.md submission/WEEK6_AI_CONTRIBUTION.md submission/WEEK6_SUBMISSION.md
git diff --cached --stat
git diff --cached
git commit -m "Add Week 6 profile review and confirmation"
git push origin main
git rev-parse HEAD
```

Inspect GitHub at `https://github.com/david-eid/web-programming-site`: verify that `main` shows the same commit ID, including `static/profile-validation.js`. If pushing is rejected because GitHub has newer commits, fetch and inspect the differences before integrating them; do not force-push. The contribution PDF is an e-learning artifact and does not need to be committed. Keep the actual conversation PDF out of the public repository unless you intentionally want to publish the conversation.

## 2. Deploy the existing Render service

1. Open the existing service in the Render dashboard. Verify repository `david-eid/web-programming-site` and branch `main`. Use the existing Python Web Service, not a Static Site.
2. Verify the root directory is the repository root; build command is `pip install -r requirements.txt`; start command is `gunicorn app:app`. Keep the existing working Python runtime configuration. Do not use the local Flask debug server as the production command.
3. If automatic deployment is enabled, a push can start deployment immediately. If you want pushing and deployment to be separate, disable automatic deployment in your service settings before pushing. Otherwise wait for that build, or select the dashboard's manual option to deploy the latest commit.
4. Check the deployment logs and successful live status. Match the deployed commit ID to `git rev-parse HEAD`. Do not count the previous deployment remaining online as proof the new build succeeded.
5. Open your real Render domain and `/submit-profile`. Hard-refresh once if needed to load the updated JavaScript.

These commands and deploy behavior are documented in [Render's Flask guide](https://render.com/docs/deploy-flask) and [deployment guide](https://render.com/docs/deploys). The account settings and live URL were not accessed or verified in this task.

## 3. Check the live website

Use synthetic details, such as student ID `001234567`, a test name, and `student@example.com`.

- Try missing required fields, a short ID, GPA below 40 or above 100, and unchecked consent. A browser warning must appear; review must stay closed.
- Fill required fields and leave optional fields empty. Review must show explicit empty markers and all fields, including consent and form version.
- Select at least two skills and two software options; add a multiline description and other optional values. Every value must appear as read-only text. `<b>hello</b>` should stay literal text.
- Click Edit, check that every answer remains, change an answer, and submit again. Try pressing Enter in a text input. The updated review should appear without a reload.
- Open DevTools Network and enable Preserve log. No POST should occur before confirmation. Confirm & Submit should make exactly one POST to `/submit-profile` and display the original profile result page. Check the leading-zero ID and both sets of multiple selections.
- Repeat on a narrow screen; check that the review text wraps and both buttons work. Check the browser console for JavaScript errors and Network for missing Week 6 assets.

## 4. Export the actual AI conversation to a readable PDF

The actual conversation PDF must be exported manually from the chat you can see. No conversation PDF was generated in this task, and a generated summary is not a substitute. I could not verify a direct PDF-export control for this exact app surface in the official documentation I checked. Use the following method, which does not depend on such a control:

1. Wait until this task's final reply is present. Start at the first Week 6 request and include the entire Week 6 exchange, including follow-up requests, answers, visible progress messages, and test-failure/test-success information. Expand relevant visible tool/code sections where available. If an earlier part of this same Week 6 work is in another chat, include it as a clearly labeled continuation.
2. Copy the messages verbatim into Word, LibreOffice Writer, or Google Docs in chronological order. Use each message's Copy control where available, or select and copy its visible text. Label the speakers **User** and **Assistant**; label copied visible tool output separately. Preserve code blocks and error messages. Do not replace the dialogue with a summary or claim that omitted material is included.
3. Add a title such as **GIN446 Week 6 - AI Conversation**, your name, and the date. Use A4 or Letter pages, approximately 11-point body text, normal margins, and page numbers. Use a monospaced font for code and wrap long lines so they do not disappear off the page. This is a formatting step, not permission to rewrite the conversation.
4. Use your document editor's PDF export or Print command, choosing **Microsoft Print to PDF** or **Save as PDF** as available. Save as `GIN446_Week6_AI_Conversation.pdf`.
5. Open the resulting PDF. Check the first and last messages, message order, code readability, page breaks, and that no pages or long lines are clipped. Search for the original request and the final successful browser-test report. Add any missing visible messages before submitting.

If this exact chat can be opened in a browser, printing it directly may be quicker: load the whole conversation, expand relevant sections, press Ctrl+P, and choose Save as PDF. Inspect the preview carefully; long or virtualized chat views can omit earlier content, so use the document-copy method if anything is missing.

## 5. Upload to e-learning

Required assignment artifacts:

1. `GIN446_Week6_AI_Conversation.pdf` - the actual conversation exported by you using the steps above; still to be created.
2. `output/pdf/Week6-AI-contribution-statement.pdf` - the updated Week 6 disclosure, after your review. Its editable source is `submission/WEEK6_AI_CONTRIBUTION.md`.

Supply your GitHub repository and live Render URL wherever the e-learning activity asks for links. The assignment reference lists the conversation PDF and contribution statement as uploads; only upload a source ZIP or extra report if your instructor's submission form asks for it.

Do not upload the pre-existing `AI-session-summary.pdf` as the actual conversation: it explicitly describes an earlier session and is only a summary. Do not use the older `AI-contribution-statement.pdf` for Week 6. `WEEK6.md` and the browser screenshots are supporting evidence, not replacements for the two required artifacts.
