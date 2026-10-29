"""Week 8 validation and route checks. Run: python -m unittest discover -s tests."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Initialize the app against a test database without leaking the environment change.
with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///:memory:'}):
    from app import app
from validators import validate_profile
from werkzeug.datastructures import MultiDict

VALID = dict(student_id='001234567', fullname='Test Student', email='test@net.usek.edu.lb',
             major='computer', gpa='85', graduation='spring', confirmation='yes')


class ProfileValidationTests(unittest.TestCase):
    def test_valid_and_normalization(self):
        form = MultiDict({**VALID, 'email': ' TEST@NET.USEK.EDU.LB ', 'fullname': ' Test Student ',
                          'phone': '+961 70 123456', 'birthdate': '2003-02-28',
                          'portfolio': 'https://github.com/student/project', 'gin446': 'https://example.com',
                          'credits': '148', 'graduation_month': '2027-06', 'internship_completed': 'no',
                          'language': 'Python', 'project_title': 'My project', 'project_area': 'web-applications',
                          'description': 'A web application.', 'team_size': '4', 'project_color': '#abcdef',
                          'meeting_date': '2027-01-01', 'meeting_time': '18:00',
                          'skills': ['programming', 'electronics'], 'software': ['MATLAB', 'Vivado']})
        errors, cleaned = validate_profile(form)
        self.assertEqual(errors, {})
        self.assertEqual(cleaned['email'], 'test@net.usek.edu.lb')
        self.assertEqual(cleaned['fullname'], 'Test Student')
        response = app.test_client().post('/profile-validated', data=form)
        self.assertIn(b'<article class="profile">', response.data)
        self.assertIn(b'My project', response.data)

    def test_invalid_fields(self):
        cases = {
            'student_id': ['abc', '12345678', '1234567890', '123456789\nX'],
            'fullname': ['A', 'Name123', 'x' * 81],
            'email': ['test@gmail.com', 'test@@net.usek.edu.lb', 'x@net.usek.edu.lb.evil', '.x@net.usek.edu.lb'],
            'phone': ['70123456', '+962 70 123456', '+961 70 12345'],
            'birthdate': ['2026-02-30', '2999-01-01', '1900-01-01', '2020-01-01', '20030101'],
            'portfolio': ['https://github.com.evil/user', 'https://example.com', 'javascript:alert(1)'],
            'gin446': ['http://example.com', 'https://', 'https://[bad', 'https://example.com:bad'],
            'major': ['hacker'], 'gpa': ['39', '101', 'NaN', 'inf', '-inf', 'abc'],
            'credits': ['-1', '149', '1.5'], 'graduation': ['winter'],
            'graduation_month': ['2027-13', '0000-01', '2027-1'],
            'internship_completed': ['maybe'], 'language': ['x' * 40],
            'skills': [['programming', 'hacker']], 'software': [['MATLAB', 'hacker']],
            'project_title': ['x' * 121], 'project_area': ['hacker'], 'description': ['x' * 1001],
            'team_size': ['0', '5', '1.5'], 'project_color': ['red', '#123', '#123456; color:red'],
            'meeting_date': ['2027-02-30', 'not a date'],
            'meeting_time': ['07:59', '18:01', '24:00', '8:00', '12:60'],
            'confirmation': ['', 'no']}
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    form = MultiDict({**VALID, field: value})
                    self.assertIn(field, validate_profile(form)[0])
                    response = app.test_client().post('/profile-validated', data=form)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(f'id="{field}-error"'.encode(), response.data)
                    self.assertNotIn(b'<article class="profile">', response.data)

    def test_required_and_boundaries(self):
        for field in VALID:
            with self.subTest(field=field):
                self.assertIn(field, validate_profile(MultiDict({**VALID, field: ' '}))[0])
        for field, values in {'gpa': ['40', '100'], 'credits': ['0', '148'],
                              'team_size': ['1', '4'], 'meeting_time': ['08:00', '18:00'],
                              'language': ['x' * 39], 'project_title': ['x' * 120],
                              'description': ['x' * 1000]}.items():
            for value in values:
                self.assertEqual(validate_profile(MultiDict({**VALID, field: value}))[0], {})

    def test_errors_retention_and_escaping(self):
        form = MultiDict({**VALID, 'student_id': 'abc', 'gpa': '999', 'credits': 'oops',
                          'description': '<script>alert(1)</script>', 'skills': ['programming', 'electronics'],
                          'software': ['MATLAB', 'Vivado'], 'internship_completed': 'no'})
        html = app.test_client().post('/profile-validated', data=form).text
        self.assertIn('id="student_id-error"', html)
        self.assertIn('id="gpa-error"', html)
        self.assertIn('value="abc"', html)
        self.assertIn('value="oops"', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>alert(1)</script>', html)
        for value in ['programming', 'electronics', 'no', 'spring', 'yes']:
            self.assertRegex(html, 'value="' + value + '"[^>]*checked')
        for value in ['MATLAB', 'Vivado', 'computer']:
            self.assertRegex(html, 'value="' + value + '"[^>]*selected')

    def test_existing_routes(self):
        for route in ['/', '/research', '/submit-profile', '/quiz', '/live-quiz',
                      '/internet-history', '/web-history', '/internet-history-ai', '/web-history-ai',
                      '/profile-validated']:
            self.assertEqual(app.test_client().get(route).status_code, 200, route)
        html = app.test_client().get('/profile-validated').text
        self.assertIn('novalidate', html)
        self.assertNotIn('profile-validation.js', html)
        self.assertIn('profile-validation.js', app.test_client().get('/submit-profile').text)
        self.assertIn('Server-Side Validation', app.test_client().get('/').text)


if __name__ == '__main__':
    unittest.main()
