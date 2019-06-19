# -*- coding: utf-8 -*-

from flask import current_app, abort

from tests.base import BaseTestCase


class BasicTestCase(BaseTestCase):

    def test_app_exist(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_400_error(self):

        @current_app.route('/400')
        def error_page():
            abort(400)

        response = self.client.get('/400')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn('400 Error', data)
        self.assertIn('Bad Request', data)

    def test_401_error(self):

        @current_app.route('/401')
        def error_page():
            abort(401)

        response = self.client.get('/401')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 401)
        self.assertIn('401 Error', data)
        self.assertIn('Unauthorized', data)

    def test_403_error(self):

        @current_app.route('/403')
        def error_page():
            abort(403)

        response = self.client.get('/403')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 403)
        self.assertIn('403 Error', data)
        self.assertIn('Forbidden', data)

    def test_404_error(self):

        @current_app.route('/404')
        def error_page():
            abort(404)

        response = self.client.get('/404')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn('404 Error', data)
        self.assertIn('Page Not Found', data)

    def test_405_error(self):

        @current_app.route('/405')
        def error_page():
            abort(405)

        response = self.client.get('/405')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 405)
        self.assertIn('405 Error', data)
        self.assertIn('Method not allowed', data)

    def test_413_error(self):

        @current_app.route('/413')
        def error_page():
            abort(413)

        response = self.client.get('/413')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 413)
        self.assertIn('413 Error', data)
        self.assertIn('Upload too large', data)

    def test_500_error(self):

        @current_app.route('/500')
        def error_page():
            abort(500)

        response = self.client.get('/500')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn('500 Error', data)
        self.assertIn('Internal Server Error Explained', data)
