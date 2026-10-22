"""Local API/browser regression checks. Run: python tests/live_quiz_flow.py.
Requires application dependencies plus Selenium and Chrome. Uses a temporary SQLite DB.
"""
import ast
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TEMP = tempfile.TemporaryDirectory()
os.environ['DATABASE_URL'] = 'sqlite:///' + str(Path(TEMP.name) / 'test.db').replace('\\', '/')
from app import app
from quiz_api import database_uri, db
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import make_server, WSGIRequestHandler

# Read fixture without importing the seeder (importing it writes the database).
module = ast.parse((ROOT / 'seed_db.py').read_text(encoding='utf-8'))
questions = next(ast.literal_eval(n.value) for n in module.body
                 if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'QUESTIONS' for t in n.targets))
for expected in ['Seeded 10 questions.', 'Already seeded: 10 questions.']:
    result = subprocess.run([sys.executable, 'seed_db.py'], cwd=ROOT, capture_output=True, text=True, check=True)
    assert expected in result.stdout and 'sqlite:' not in result.stdout
client = app.test_client()
for route in ['/', '/internet-history', '/web-history', '/internet-history-ai', '/web-history-ai', '/research', '/submit-profile', '/quiz', '/live-quiz']:
    assert client.get(route).status_code == 200, route
assert client.post('/quiz').status_code == 200
assert client.post('/submit-profile', data={'fullname': 'Test', 'skills': ['Programming'], 'software': ['MATLAB']}).status_code == 200
assert 'Live Quiz with Fetch' in client.get('/').text
assert client.get('/api/questions/count').json == {'count': 10}
for i, q in enumerate(questions):
    assert client.get(f'/api/question/{i}').json == dict(index=i, **q)
for index in [-1, 10, 999, 'abc', '1.5']:
    assert client.get(f'/api/question/{index}').status_code == 404
for prefix in ['postgres://', 'postgresql://', 'postgresql+psycopg2://']:
    with patch.dict(os.environ, {'DATABASE_URL': prefix + 'example.invalid/quiz'}):
        assert database_uri() == 'postgresql+psycopg2://example.invalid/quiz'
with patch.dict(os.environ, {}, clear=True):
    assert database_uri().startswith('sqlite:///')
print('PASS: all existing routes, profile POST, all 10 question payloads, invalid indices, idempotent seeding, URI normalization.')

requests = Counter()
mode = {'delay': 0, 'path': None, 'failure': None}
def record(environ, start_response):
    path = environ['PATH_INFO']
    requests[path] += 1
    if path.startswith('/api/'):
        time.sleep(mode['delay'])
        if mode['path'] == path:
            failure = mode['failure']
            if failure == 'http':
                start_response('503 Service Unavailable', [('Content-Type', 'application/json')])
                return [b'{}']
            if failure in ['json', 'empty', 'shape']:
                start_response('200 OK', [('Content-Type', 'application/json')])
                return [{'json': b'not json', 'empty': b'{"count":0}', 'shape': b'{"count":"ten"}'}[failure]]
    return app(environ, start_response)
class Quiet(WSGIRequestHandler):
    def log_request(self, *args, **kwargs): pass
server = make_server('127.0.0.1', 0, record, request_handler=Quiet, threaded=True)
threading.Thread(target=server.serve_forever, daemon=True).start()
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--window-size=1280,1000')
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)
base = f'http://127.0.0.1:{server.server_port}'
def js(script, *args): return driver.execute_script(script, *args)
def el(id): return driver.find_element(By.ID, id)
def ready(): wait.until(lambda d: js('return !busy'))
def click(selector):
    target = driver.find_element(By.CSS_SELECTOR, selector)
    js('arguments[0].scrollIntoView({behavior:"instant",block:"center"})', target)
    target.click()
def open_quiz():
    driver.get(base + '/live-quiz')
    js('document.documentElement.style.scrollBehavior="auto"; window.sameDocument=true;')
    ready()
def layout(width, panel):
    driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {'width': width, 'height': 900, 'deviceScaleFactor': 1, 'mobile': width < 600})
    assert js('return innerWidth') == width
    assert js('return document.documentElement.scrollWidth <= innerWidth'), width
    # Check actual controls as well; body overflow:hidden must not conceal clipped content.
    assert js('''return [...document.querySelectorAll('#quizPanel button, #choices label, #resultsPanel, .main-nav a')]
      .filter(e=>e.getClientRects().length).every(e=>{const r=e.getBoundingClientRect(); return r.left>=0 && r.right<=innerWidth+1 && e.scrollWidth<=e.clientWidth+1;})'''), width
    assert js('''const r=[...document.querySelectorAll('.navigation button')].map(e=>e.getBoundingClientRect());
      return r.every((a,i)=>r.every((b,j)=>i===j || a.right<=b.left || b.right<=a.left || a.bottom<=b.top || b.bottom<=a.top));'''), width
    js('arguments[0].scrollIntoView({behavior:"instant",block:"start"})', el(panel))
    driver.save_screenshot(str(ROOT / 'tmp' / f'week7-{panel}-{width}.png'))

try:
    mode['delay'] = .6
    driver.get(base + '/live-quiz')
    assert el('loading').is_displayed() and not el('submitBtn').is_enabled()
    ready()
    mode['delay'] = 0
    requests.clear()
    open_quiz()
    assert el('progress').text == 'Question 1 of 10'
    assert not el('firstBtn').is_enabled() and not el('previousBtn').is_enabled()
    click('#choices input[value="1"]')
    click('#nextBtn'); ready()
    assert el('progress').text == 'Question 2 of 10'
    click('#choices input[value="2"]')
    click('#previousBtn'); ready()
    assert driver.find_element(By.CSS_SELECTOR, '#choices input[value="1"]').is_selected()
    assert requests['/api/question/0'] == 1
    click('#lastBtn'); ready()
    assert el('progress').text == 'Question 10 of 10'
    assert not el('lastBtn').is_enabled() and not el('nextBtn').is_enabled()
    click('#firstBtn'); ready()
    for width in [1280, 768, 430, 390, 375, 320]: layout(width, 'quizPanel')
    # Keyboard radio selection and visible focus styling.
    radio = driver.find_element(By.CSS_SELECTOR, '#choices input[value="1"]')
    radio.send_keys(Keys.ARROW_RIGHT)
    assert driver.find_element(By.CSS_SELECTOR, '#choices input[value="2"]').is_selected()
    assert js('return getComputedStyle(document.activeElement.parentElement).outlineStyle') != 'none'
    radio.send_keys(Keys.SPACE)
    click('#submitBtn'); ready()
    assert el('scoreText').text == 'Score: 2 / 10'
    assert el('percentageText').text == 'Percentage: 20%'
    assert el('performanceText').text == 'Needs improvement'
    text = el('correction').text
    assert text.count('Not answered') == 8 and text.count('Explanation:') == 10
    assert text.count('Result: Correct') == 2 and text.count('Result: Incorrect') == 8
    assert all(requests[f'/api/question/{i}'] == 1 for i in range(10))
    assert requests['/live-quiz'] == 1 and js('return window.sameDocument')
    for width in [1280, 768, 430, 390, 375, 320]: layout(width, 'resultsPanel')
    assert not [e for e in driver.get_log('browser') if e['source'] == 'javascript' and e['level'] == 'SEVERE']
    print('PASS: real fetch, cache, navigation, boundaries, keyboard answers, persistence, 2/10 score, full correction, no reload/errors; layouts at 1280/768/430/390/375/320.')

    # Full, zero, partial scoring and every message threshold.
    for count, message in [(0,'Needs improvement'), (5,'Pass'), (6,'Good'), (8,'Excellent'), (10,'Excellent')]:
        open_quiz()
        for i in range(count):
            click(f'#choices input[value="{questions[i]["answer"]}"]')
            if i < count-1: click('#nextBtn'); ready()
        click('#submitBtn'); ready()
        assert el('scoreText').text == f'Score: {count} / 10'
        assert el('percentageText').text == f'Percentage: {count*10}%'
        assert el('performanceText').text == message
    assert js('return [49,50,59,60,79,80,100].map(getPerformanceMessage)') == ['Needs improvement','Pass','Pass','Good','Good','Excellent','Excellent']
    print('PASS: zero/full/partial scores and all performance boundaries.')

    # Count errors, malformed data, empty database; retry without reload.
    for failure in ['http', 'json', 'empty', 'shape']:
        mode.update(path='/api/questions/count', failure=failure)
        open_quiz()
        assert el('error').is_displayed() and not el('loading').is_displayed()
        assert not el('submitBtn').is_enabled()
        mode.update(path=None, failure=None)
        click('#retryBtn'); ready()
        assert el('progress').text == 'Question 1 of 10' and not el('error').is_displayed()
    # HTTP failure during navigation retains current question and answer.
    open_quiz(); click('#choices input[value="1"]')
    mode.update(path='/api/question/1', failure='http')
    click('#nextBtn'); ready()
    assert el('progress').text == 'Question 1 of 10' and el('error').is_displayed()
    assert driver.find_element(By.CSS_SELECTOR, '#choices input[value="1"]').is_selected()
    mode.update(path=None)
    click('#retryBtn'); ready()
    assert el('progress').text == 'Question 2 of 10'
    # Submit must fail gracefully if an unseen question cannot be fetched.
    mode.update(path='/api/question/2', failure='http')
    click('#submitBtn'); ready()
    assert el('error').is_displayed() and not el('resultsPanel').is_displayed()
    assert not el('loading').is_displayed()
    mode.update(path=None)
    click('#retryBtn'); ready()
    assert el('scoreText').text == 'Score: 1 / 10'
    # A correction failure must not reveal incomplete results.
    open_quiz()
    js('window.originalCorrection=buildCorrection; buildCorrection=async()=>{throw new Error("test failure")};')
    click('#submitBtn'); ready()
    assert el('error').is_displayed() and not el('resultsPanel').is_displayed()
    js('buildCorrection=window.originalCorrection;')
    click('#retryBtn'); ready()
    assert el('scoreText').text == 'Score: 0 / 10'
    # First-question failure also has a working retry.
    mode.update(path='/api/question/0', failure='http')
    open_quiz()
    assert el('error').is_displayed() and not el('submitBtn').is_enabled()
    mode.update(path=None)
    click('#retryBtn'); ready()
    assert el('progress').text == 'Question 1 of 10'
    # Network rejection and malformed question JSON are also caught.
    for failure in ['network', 'json']:
        open_quiz()
        if failure == 'network':
            js('window.realFetch=window.fetch; window.fetch=()=>Promise.reject(new TypeError("offline"));')
        else: mode.update(path='/api/question/1', failure='json')
        click('#nextBtn'); ready()
        assert el('error').is_displayed() and not el('loading').is_displayed()
        if failure == 'network': js('window.fetch=window.realFetch;')
        mode.update(path=None)
        click('#retryBtn'); ready()
        assert el('progress').text == 'Question 2 of 10'
    print('PASS: HTTP/network/invalid JSON/count/empty data errors, navigation and submission retries, retained answers.')

    open_quiz()
    mode['delay'] = .6
    js('goNext(); goLast(); submitQuiz();')
    assert el('loading').is_displayed()
    assert all(not el(id).is_enabled() for id in ['firstBtn','previousBtn','nextBtn','lastBtn','submitBtn'])
    ready()
    assert el('progress').text == 'Question 2 of 10'
    before = requests['/api/question/4']
    result = driver.execute_async_script('const done=arguments[0]; Promise.all([getQuestion(4),getQuestion(4)]).then(q=>done(q[0].index===q[1].index));')
    assert result and requests['/api/question/4'] == before+1
    mode['delay'] = 0
    # Bounds do nothing, even if handlers are called directly.
    js('goFirst()'); ready(); js('goPrevious()'); ready()
    assert el('progress').text == 'Question 1 of 10'
    js('goLast()'); ready(); js('goNext()'); ready()
    assert el('progress').text == 'Question 10 of 10'
    assert not [e for e in driver.get_log('browser') if e['source'] == 'javascript' and e['level'] == 'SEVERE']
    print('PASS: loading visibility, rapid action lock, shared in-flight fetch, direct-handler bounds, no uncaught JS errors.')
    # Week 5 still renders, navigates, and submits in the browser.
    driver.get(base+'/quiz')
    click('#choices input[value="1"]'); click('#nextBtn'); click('#previousBtn')
    assert driver.find_element(By.CSS_SELECTOR, '#choices input[value="1"]').is_selected()
    click('.submit')
    assert el('scoreText').text == 'Score: 1 / 10'
    driver.get(base+'/')
    click('a[href="/live-quiz"]'); ready()
    assert el('progress').text == 'Question 1 of 10'
    print('PASS: original Week 5 browser flow and homepage Week 7 link.')
finally:
    driver.quit()
    server.shutdown()
    with app.app_context(): db.engine.dispose()
    TEMP.cleanup()
