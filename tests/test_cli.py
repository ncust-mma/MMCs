# -*- coding: utf-8 -*-

from tests.base import BaseTestCase

from MMCs.extensions import db
from MMCs.models import Competition, Solution, User


class CLITestCase(BaseTestCase):

    def setUp(self, *args, **kwargs):
        super(CLITestCase, self).setUp(*args, **kwargs)
        db.drop_all()

    def test_init_command(self):
        result = self.runner.invoke(args=['init'])
        self.assertIn('Initializing the database...', result.output)
        self.assertIn('Done.', result.output)

    def test_init_command_with_drop(self):
        result = self.runner.invoke(args=['init', '--drop'], input='y\n')
        self.assertIn(
            'This operation will delete the database, do you want to continue?', result.output)
        self.assertIn('Drop tables.', result.output)

    def test_forge(self):
        pass

    def test_forge_command_with_count(self):
        result = self.runner.invoke(
            args=['forge', '--teacher', '2', '--solution', '3'])

        self.assertIn(
            'Generating the default root administrator...', result.output)
        self.assertIn(
            'Generating the default administrator...', result.output)
        self.assertIn('Generating the default teacher...', result.output)
        self.assertIn('Generating 2 teacher...', result.output)

        self.assertEqual(User.query.count(), 5)

        self.assertIn('Generating the competition...', result.output)
        self.assertEqual(Competition.query.count(), 1)

        self.assertIn('Generating 3 solution...', result.output)
        self.assertEqual(Solution.query.count(), 3)

        self.assertIn('Generating the task...', result.output)

        self.assertIn('Done.', result.output)

    def test_gen_root(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['gen-root'])
        self.assertIn(
            'Generating the default root administrator...', result.output)
        self.assertIn('Done.', result.output)

    def test_translate(self):
        self.runner.invoke(args=['translate'])

    def test_translate_compile(self):
        self.runner.invoke(args=['translate', 'compile'])
