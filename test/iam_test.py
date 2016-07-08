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
import krux_boto_iam.iam


class IAMtest(unittest.TestCase):
    TEST_REGION = 'us-west-2'
    TEST_QUEUE_NAME = 'klam-test'

    def setUp(self):
        self._iam = krux_boto_iam.iam.IAM(
            boto=krux_boto.boto.Boto3(
                region=self.TEST_REGION
            )
        )

    def test_create_user(self):
        """
        AWS user with given username is created correctly
        """
        # TODO: This test needs to be improved using mock and stuff. But for the interest of time,
        # let's leave it at this minimal state.
        user = self._iam.create_user('hworld')

        self.assertIsNotNone(user)
        self.assertEqual('hworld', user['UserName'])

        user = self._iam.get_user('hworld')

        self.assertIsNotNone(user)
        self.assertEqual('hworld', user['UserName'])

    def test_delete_user(self):
        """
        AWS user can be deleted.
        """
        # TODO: This test needs to be improved using mock and stuff. But for the interest of time,
        # let's leave it at this minimal state.
        self._iam.delete_user('hworld')
        user = self._iam.get_user('hworld')

        self.assertIsNone(user)
