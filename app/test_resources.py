import unittest
import os
import app

class RegistrationTest(unittest.TestCase):

    def setUp(self):
        self.app = app.create_app().test_client()

    def tearDown(self):
        pass
