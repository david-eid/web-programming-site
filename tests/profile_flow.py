"""Browser integration check. Requires Selenium and Chrome (test tools only).
Run from the repository root: python tests/profile_flow.py
"""
import sys
import threading
from pathlib import Path
from urllib.parse import parse_qs
from io import BytesIO

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import make_server

requests = []
posts = []


def record(environ, start_response):
    requests.append((environ['REQUEST_METHOD'], environ['PATH_INFO']))
    if environ['REQUEST_METHOD'] == 'POST':
        body = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0)))
        posts.append(parse_qs(body.decode(), keep_blank_values=True))
        environ['wsgi.input'] = BytesIO(body)
    return app(environ, start_response)


server = make_server('127.0.0.1', 0, record)
threading.Thread(target=server.serve_forever, daemon=True).start()
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--window-size=1280,1000')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)


def js(script, *args):
    return driver.execute_script(script, *args)


def click(selector):
    element = driver.find_element(By.CSS_SELECTOR, selector)
    js('arguments[0].scrollIntoView({behavior: "instant", block: "center"});', element)
    element.click()


def review_visible():
    return driver.find_element(By.ID, 'profile-review').is_displayed()


def fill(values):
    js('for (const [key, value] of Object.entries(arguments[0])) '
       '{ document.getElementById(key).value = value; }', values)


def review_rows():
    return js('return Array.from(document.querySelectorAll("#review-values dt"), '
              'e => [e.textContent, e.nextElementSibling.textContent])')


def submitted_values():
    return js('return Array.from(new FormData(document.getElementById("profile-form")).entries())')


try:
    driver.get(f'http://127.0.0.1:{server.server_port}/submit-profile')
    js('document.documentElement.style.scrollBehavior = "auto";')
    js('window.originalDocument = true; window.originalForm = document.getElementById("profile-form");')
    assert js('return document.getElementById("profile-form").method') == 'post'
    assert js('return new URL(document.getElementById("profile-form").action).pathname') == '/submit-profile'
    click('button[type=submit]')
    assert not review_visible() and not posts
    fill({'student_id': '001234567', 'fullname': '<img src=x onerror=alert(1)>',
          'email': 'student@example.com', 'major': 'computer', 'gpa': '85'})
    click('#graduation-spring')
    click('#confirmation')
    for field, invalid, valid in [
        ('student_id', '123', '001234567'), ('fullname', '', 'Test Student'),
        ('student_id', '12345678a', '001234567'),
        ('email', 'invalid', 'student@example.com'), ('major', '', 'computer'),
        ('gpa', '39', '85'), ('gpa', '101', '85'),
        ('credits', '-1', '0'), ('credits', '149', '0'),
        ('team_size', '0', '2'), ('team_size', '7', '2'),
        ('team_size', '1.5', '2'), ('portfolio', 'bad-url', '')
    ]:
        fill({field: invalid})
        click('button[type=submit]')
        assert not review_visible() and not posts, field
        assert js('return document.getElementById(arguments[0]).validationMessage.length > 0', field)
        fill({field: valid})
    click('#confirmation')
    click('button[type=submit]')
    assert not review_visible() and not posts
    click('#confirmation')
    js('document.getElementById("graduation-spring").checked = false;')
    click('button[type=submit]')
    assert not review_visible() and not posts
    click('#graduation-spring')
    fill({'credits': '', 'team_size': ''})
    empty_expected = submitted_values()
    before = len(requests)
    click('button[type=submit]')
    assert review_visible()
    assert js('return document.activeElement.id') == 'review-heading'
    assert len(driver.find_elements(By.CSS_SELECTOR, '#review-values dt')) == 25
    empty_rows = dict(review_rows())
    for label in ['Mobile number', 'Date of birth', 'Portfolio / GitHub URL',
                  'GIN446 website URL', 'Credits completed / 148',
                  'Expected graduation month and year', 'Internship completed',
                  'Technical skills', 'Primary programming language', 'Engineering software used',
                  'Proposed project title', 'Preferred project area', 'Brief project description',
                  'Preferred team size', 'Preferred meeting date', 'Preferred meeting time']:
        assert empty_rows[label] == 'Not provided / none selected', label
    assert 'Not provided / none selected' in driver.find_element(By.ID, 'review-values').text
    assert not driver.find_elements(By.CSS_SELECTOR, '#profile-review input, #profile-review select, #profile-review textarea')
    click('#edit-profile')
    assert js('return window.originalForm === document.getElementById("profile-form")')
    assert submitted_values() == empty_expected
    assert js('return document.activeElement.id') == 'student_id'
    fill({'fullname': '<img src=x onerror=alert(1)>', 'phone': '+961123456',
          'birthdate': '2003-01-02', 'portfolio': 'https://example.com/me',
          'gin446': 'https://example.com/course', 'graduation_month': '2027-06',
          'language': 'C++', 'project_title': 'A & B', 'project_area': 'web-applications',
          'description': 'First line\nSecond <b>line</b>', 'project_color': '#123456',
          'meeting_date': '2026-11-01', 'meeting_time': '14:30', 'credits': '0', 'team_size': '2'})
    click('#internship-no')
    click('#skill-programming')
    click('#skill-ai')
    js('for (const o of document.getElementById("software").options) o.selected = ["MATLAB", "Vivado"].includes(o.value);')
    expected = submitted_values()
    click('button[type=submit]')
    rows = js('return Array.from(document.querySelectorAll("#review-values dd"), e => e.textContent)')
    grouped = {}
    for key, value in expected:
        grouped.setdefault(key, []).append(value)
    assert len(rows) == len(grouped) == 25
    for values in grouped.values():
        assert ', '.join(values) in rows, values
    # Independently read names from HTML to ensure every control has a review row.
    names = js('return Array.from(new Set(Array.from(document.querySelectorAll("#profile-form [name]"), e => e.name)))')
    assert set(names) == set(grouped)
    # Check order too: identical values in unrelated fields must not mask an omission.
    assert rows == [', '.join(grouped[name]) for name in names if name != 'form_version'] + [grouped['form_version'][0]]
    assert not driver.find_elements(By.CSS_SELECTOR, '#review-values img, #review-values b')
    click('#edit-profile')
    assert expected == js('return Array.from(new FormData(document.getElementById("profile-form")).entries())')
    fill({'project_title': 'Edited project'})
    driver.find_element(By.ID, 'project_title').send_keys(Keys.ENTER)
    wait.until(lambda d: review_visible())
    assert 'Edited project' in driver.find_element(By.ID, 'review-values').text
    assert len(requests) == before and js('return window.originalDocument')
    # Recheck on confirmation must reject a value changed after review.
    fill({'gpa': '101'})
    click('#confirm-profile')
    assert not review_visible() and not posts
    fill({'gpa': '85'})
    click('button[type=submit]')
    grouped['project_title'] = ['Edited project']
    Path('tmp').mkdir(exist_ok=True)
    driver.save_screenshot('tmp/week6-review-desktop.png')
    # Chrome's desktop window has a minimum width; emulate the actual mobile viewport.
    driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
        'width': 390, 'height': 844, 'deviceScaleFactor': 1, 'mobile': True
    })
    assert js('return window.innerWidth') == 390
    assert js('return document.documentElement.scrollWidth <= window.innerWidth')
    js('document.getElementById("review-heading").scrollIntoView({behavior: "instant"});')
    driver.save_screenshot('tmp/week6-review-mobile.png')
    js('document.getElementById("confirm-profile").scrollIntoView({behavior: "instant", block: "center"});')
    driver.save_screenshot('tmp/week6-review-mobile-controls.png')
    click('#confirm-profile')
    wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, 'article.profile'))
    # Native URL-encoded submission normalizes textarea newlines to CRLF.
    # Compare the exact wire payload with that browser serialization accounted for.
    wire_expected = {name: [value.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')
                            for value in values] for name, values in grouped.items()}
    assert len(posts) == 1 and posts[0] == wire_expected, posts
    assert not js('return Boolean(window.originalDocument)')
    assert 'Edited project' in driver.find_element(By.CSS_SELECTOR, 'article.profile').text
    result = driver.find_element(By.CSS_SELECTOR, 'article.profile').text
    assert all(value in result for value in ['001234567', 'Programming', 'Matlab', 'Vivado', '2026-2027'])
    print('PASS: native validation, 25 review rows, all values, multi-select, empty options, safe text,')
    print('Edit/state retention, refreshed review, no early requests/reloads, confirmation revalidation,')
    print('mobile overflow, one genuine POST with exact payload, and original Flask result page.')
finally:
    driver.quit()
    server.shutdown()
