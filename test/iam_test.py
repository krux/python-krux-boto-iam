# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import unittest

#
# Internal libraries
#

import krux_boto.boto
from krux_boto_iam.iam import IAM, get_iam, NAME


class IAMtest(unittest.TestCase):
    TEST_REGION = 'us-west-2'
    TEST_QUEUE_NAME = 'klam-test'

    @patch('krux_boto_iam.iam.get_stats')
    @patch('krux_boto_iam.iam.get_logger')
    def setUp(self, mock_logger, mock_stats):
        self.logger = mock_logger
        self.stats = mock_stats
        self.iam = krux_boto_iam.iam.IAM(
            boto=krux_boto.boto.Boto3(
                region=self.TEST_REGION
            ),
            logger=self.logger,
            stats=self.stats
        )

    def test_init(self):
        self.assertIn(NAME, iam._name)
        self.assertEqual(self.mock_logger, self.iam._logger)
        self.assertEqual(self.mock_stats, self.iam._stats)

    def test_empty_init(self):
        """
        Kafka Manager API Test: Checks if KafkaManagerAPI initialized property if all user
        inputs provided.
        """
        iam = IAM(KafkaManagerTest._HOSTNAME, self.mock_logger, self.mock_stats)
        self.assertIn(NAME, iam._name)
        self.assertEqual(self.mock_logger, iam._logger)
        self.assertEqual(self.mock_stats, iam._stats)

    def test_create_user(self):
        """
        AWS user with given username is created correctly
        """
        # TODO: This test needs to be improved using mock and stuff. But for the interest of time,
        # let's leave it at this minimal state.
        user = self.iam.create_user('hworld')

        self.assertIsNotNone(user)
        self.assertEqual('hworld', user['UserName'])

        user = self.iam.get_user('hworld')

        self.assertIsNotNone(user)
        self.assertEqual('hworld', user['UserName'])

    def test_delete_user(self):
        """
        AWS user can be deleted.
        """
        # TODO: This test needs to be improved using mock and stuff. But for the interest of time,
        # let's leave it at this minimal state.
        self.iam.delete_user('hworld')
        user = self.iam.get_user('hworld')

        self.assertIsNone(user)
