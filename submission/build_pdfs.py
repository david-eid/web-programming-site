from pathlib import Path
import sys
sys.path.insert(0, str(Path('.codex-tmp').resolve()))
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from xml.sax.saxutils import escape
import fitz
out = Path('output/pdf'); out.mkdir(parents=True, exist_ok=True)
styles = getSampleStyleSheet()
styles['Title'].textColor = HexColor('#67502d')
styles['Title'].fontSize = 23
styles['BodyText'].fontSize = 10.5
styles['BodyText'].leading = 16
styles['BodyText'].spaceAfter = 11

def footer(canvas, doc):
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(HexColor('#666666'))
    canvas.drawString(48, 30, 'GIN446 | David Eid | 30 September 2026')
    canvas.drawRightString(547, 30, str(doc.page))

def make(name, title, paragraphs):
    story = [Paragraph(escape(title), styles['Title']), Spacer(1, 15)]
    for p in paragraphs:
        story.append(Paragraph(escape(p), styles['BodyText']))
    dest = out / name
    SimpleDocTemplate(str(dest), leftMargin=48, rightMargin=48, topMargin=48, bottomMargin=48).build(story, onFirstPage=footer, onLaterPages=footer)
    doc = fitz.open(dest)
    for i, page in enumerate(doc):
        target = Path('tmp/pdfs'); target.mkdir(parents=True, exist_ok=True)
        page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(str(target / f'{dest.stem}-{i+1}.png'))
    print(name, len(doc), 'pages')

statement = Path('submission/AI_CONTRIBUTION.md').read_text(encoding='utf-8-sig').split('\n\n')[1:]
make('AI-contribution-statement.pdf', 'AI Contribution Statement', statement)
make('AI-session-summary.pdf', 'AI Session Summary', [
    'This document summarizes the current assistance session. It is not a verbatim conversation export and should not be submitted as though it were the complete AI conversation. Export the actual chat separately for the conversation-PDF requirement.',
    'User request (verbatim excerpt): "i need the ful work done to get a 100/100". The user supplied a profile-form brief, Week 5 quiz screenshots, quiz.js, quiz.css, quiz.html, app_week5.py, and a JavaScript lecture PDF.',
    'Scope: The existing repository already contained a profile form. The quiz starter had an empty questions array and unimplemented logic functions. The assistant asked whether the submission concerned Week 5, Week 4, or both. This work focused on the supplied Week 5 quiz while preserving the existing profile implementation.',
    'Design work: The assistant generated a dedicated quiz stylesheet using the existing charcoal backgrounds, gold accents, text colors, and border variables. Selectors are scoped to .quiz-app. The stylesheet includes selected-choice styling, visible keyboard focus, disabled navigation states, wrapping correction text, and a mobile two-column button layout.',
    'Implementation and debugging: AI authored ten question objects, saved-answer state handling, bounded navigation, scoring, percentage rounding, performance classification, and complete correction text. It kept the supplied rendering and result-display functions. It replaced a nested main element in the supplied template with a div and added quiz instructions, a radio-group name, a no-JavaScript notice, and explicit button types.',
    'Verification: Node tests passed for navigation, saved and changed answers, bounds, unanswered/wrong/correct scoring, percentage rounding, performance thresholds, and result wiring. Flask checks passed for the existing pages, quiz assets, and a profile submission with multiple selected values. Browser UI access was unavailable, so these checks do not establish visual or keyboard behavior in a real browser.',
    'Review still required: The student must read and understand every accepted rule and function, perform browser checks, verify the live Render deployment, and export the actual conversation. A CSS walkthrough and manual checklist are included in submission/REVIEW.md.',
    'Authorship: AI assistance included application logic and question data as well as styling and debugging. The accompanying contribution statement discloses this scope. The assistant cannot guarantee a grade or certify that this scope meets the instructor\'s AI-use rules.'
])
