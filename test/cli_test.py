# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import unittest
import sys

#
# Third party libraries
#

from mock import MagicMock, patch

#
# Internal libraries
#

from krux_iam.cli import Application, NAME, main
from krux.stats import DummyStatsClient


class CLItest(unittest.TestCase):

    USERNAME = 'phan'
    USER_DATA = 'test_user_data'

    def setUp(self):
        self.app = Application()
        self.app.logger = MagicMock()

    @patch('krux_iam.cli.get_iam')
    def test_init(self, mock_get_iam):
        """
        IAM CLI Application is initialized properly
        """
        # Instantiating app again in this test to check if get_iam is being called in init
        app = Application()

        # There are not much we can test except all the objects are under the correct name
        self.assertEqual(NAME, app.name)
        self.assertEqual(NAME, app.parser.description)
        # The dummy stats client has no awareness of the name. Just check the class.
        self.assertIsInstance(app.stats, DummyStatsClient)
        self.assertEqual(NAME, app.logger.name)

        mock_get_iam.assert_called_once_with(app.args, app.logger, app.stats)

    @patch('krux_iam.cli.pprint')
    @patch('krux_iam.cli.IAM.get_user', return_value=USER_DATA)
    def test_run(self, mock_get_user, mock_pprint):
        """
        Test IAM CLI Application run
        """
        self.app.run()

        mock_get_user.assert_called_once_with(self.USERNAME)
        mock_pprint.assert_called_once_with(self.USER_DATA)

    def test_main(self):
        """
        IAM CLI Application is instantiated and run() is called in main()
        """
        app = MagicMock()
        app_class = MagicMock(return_value=app)

        with patch('krux_iam.cli.Application', app_class):
            main()

        app_class.assert_called_once_with()
        app.run.assert_called_once_with()
