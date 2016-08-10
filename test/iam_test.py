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
# Third party libraries
#

from mock import MagicMock, patch, call
import botocore

#
# Internal libraries
#

import krux_boto.boto
from krux_iam.iam import IAM, get_iam, NAME, add_iam_cli_arguments


class IAMtest(unittest.TestCase):
    TEST_REGION = 'us-west-2'
    TEST_USER = 'jdoe'
    TEST_GROUP = 'krux-test'
    ACCESS_KEY = '123'
    SECRET_KEY = 'ABC'
    KEY_DICT = {'AccessKeyId': ACCESS_KEY, 'SecretAccessKey': SECRET_KEY}
    CREATE_KEY_RESPONSE = {'AccessKey': KEY_DICT}
    GET_KEY_RESPONSE = {'AccessKeyMetadata': [KEY_DICT]}
    USER_RESPONSE = {'User': {'UserName': TEST_USER}}
    GROUPS_RESPONSE = {'Groups': [{'GroupName': 'group1'}, {'GroupName': 'group2'}, {'GroupName': 'group3'}]}
    KEY_LIST = [{'AccessKeyId': '123'}, {'AccessKeyId': '456'}, {'AccessKeyId': '789'}]
    ERROR_DICT = {'Error': {}}

    @patch('krux_iam.iam.get_stats')
    @patch('krux_iam.iam.get_logger')
    def setUp(self, mock_logger, mock_stats):
        self.logger = mock_logger()
        self.stats = mock_stats()
        self.boto = krux_boto.boto.Boto3(region=self.TEST_REGION)
        self.boto.client = MagicMock()
        self.iam = IAM(
            boto=self.boto,
            logger=self.logger,
            stats=self.stats
        )

    def test_init(self):
        """
        Tests IAM init with logger and stats passed in
        """
        self.assertIn(NAME, self.iam._name)
        self.assertEqual(self.logger, self.iam._logger)
        self.assertEqual(self.stats, self.iam._stats)
        self.assertEqual(self.boto.client.return_value, self.iam._client)

    @patch('krux_iam.iam.get_stats')
    @patch('krux_iam.iam.get_logger')
    def test_empty_init(self, mock_logger, mock_stats):
        """
        Test IAM init with no logger or stats passed in
        """
        boto = krux_boto.boto.Boto3(region=self.TEST_REGION)
        boto.client = MagicMock()
        iam = IAM(boto=boto)

        self.assertIn(NAME, iam._name)

        mock_logger.assert_called_once_with(NAME)
        mock_stats.assert_called_once_with(prefix=NAME)
        self.assertEqual(mock_logger.return_value, iam._logger)
        self.assertEqual(mock_stats.return_value, iam._stats)

        boto.client.assert_called_once_with(IAM._IAM_STR)
        self.assertEqual(boto.client.return_value, iam._client)

    @patch('krux_iam.iam.Boto3')
    @patch('krux_iam.iam.IAM')
    @patch('krux_iam.iam.add_iam_cli_arguments')
    @patch('krux_iam.iam.get_parser')
    @patch('krux_iam.iam.get_stats')
    @patch('krux_iam.iam.get_logger')
    def test_get_iam_none(self, mock_logger, mock_stats, mock_parser, mock_add_args, mock_iam, mock_boto):
        """
        Test get_iam when no arguments are passed in
        """
        parser = MagicMock()
        mock_parser.return_value = parser
        args = MagicMock()
        parser.parse_args.return_value = args

        iam = get_iam()

        mock_parser.assert_called_once_with(description=NAME)
        mock_add_args.assert_called_once_with(parser)
        parser.parse_args.assert_called_once_with()

        mock_logger.assert_called_once_with(name=NAME)
        mock_stats.assert_called_once_with(prefix=NAME)

        mock_boto.assert_called_once_with(
            log_level=args.boto_log_level,
            access_key=args.boto_access_key,
            secret_key=args.boto_secret_key,
            region=args.boto_region,
            logger=mock_logger.return_value,
            stats=mock_stats.return_value,
        )

        mock_iam.assert_called_once_with(
            boto=mock_boto.return_value,
            logger=mock_logger.return_value,
            stats=mock_stats.return_value
        )
        self.assertEquals(mock_iam.return_value, iam)

    @patch('krux_iam.iam.Boto3')
    @patch('krux_iam.iam.IAM')
    @patch('krux_iam.iam.add_iam_cli_arguments')
    @patch('krux_iam.iam.get_parser')
    @patch('krux_iam.iam.get_stats')
    @patch('krux_iam.iam.get_logger')
    def test_get_iam_all(self, mock_logger, mock_stats, mock_parser, mock_add_args, mock_iam, mock_boto):
        """
        Test get_iam when all arguments are passed in
        """
        parser = MagicMock()
        mock_parser.return_value = parser
        args = MagicMock()
        logger = MagicMock()
        stats = MagicMock()

        iam = get_iam(args=args, logger=logger, stats=stats)

        self.assertFalse(mock_parser.called)
        self.assertFalse(mock_add_args.called)
        self.assertFalse(parser.parse_args.called)

        self.assertFalse(mock_logger.called)
        self.assertFalse(mock_stats.called)

        mock_boto.assert_called_once_with(
            log_level=args.boto_log_level,
            access_key=args.boto_access_key,
            secret_key=args.boto_secret_key,
            region=args.boto_region,
            logger=logger,
            stats=stats,
        )

        mock_iam.assert_called_once_with(
            boto=mock_boto.return_value,
            logger=logger,
            stats=stats
        )

    @patch('krux_iam.iam.get_group')
    @patch('krux_iam.iam.add_boto_cli_arguments')
    def test_get_cli_arguments(self, mock_add_boto, mock_get_group):
        """
        Test add_iam_cli_arguments
        """
        parser = MagicMock()

        add_iam_cli_arguments(parser)

        mock_add_boto.assert_called_once_with(parser)
        mock_get_group.assert_called_once_with(parser, NAME)

    @patch('krux_iam.iam.get_group')
    @patch('krux_iam.iam.add_boto_cli_arguments')
    def test_get_cli_arguments_no_boto(self, mock_add_boto, mock_get_group):
        """
        Test add_iam_cli_arguments with include_boto_arguments = False
        """
        parser = MagicMock()

        add_iam_cli_arguments(parser, False)

        self.assertFalse(mock_add_boto.called)

    def test_create_access_keys(self):
        """
        Test that create_access_keys calls client.create_access_key and returns an access key and secret key
        """
        self.iam._client.create_access_key = MagicMock(return_value=self.CREATE_KEY_RESPONSE)

        access_key, secret_key = self.iam.create_access_keys(self.TEST_USER)

        self.iam._client.create_access_key.assert_called_once_with(UserName=self.TEST_USER)
        self.assertEquals(self.ACCESS_KEY, access_key)
        self.assertEquals(self.SECRET_KEY, secret_key)

    def test_get_access_keys(self):
        """
        Test that get_access_keys calls client.list_access_keys and returns a list of dicts with access keys
        """
        self.iam._client.list_access_keys = MagicMock(return_value=self.GET_KEY_RESPONSE)

        keys = self.iam.get_access_keys(self.TEST_USER)

        self.iam._client.list_access_keys.assert_called_once_with(UserName=self.TEST_USER)
        self.assertEquals(self.GET_KEY_RESPONSE['AccessKeyMetadata'], keys)

    def test_delete_access_key(self):
        """
        Test that checks if client.delete_access_key is called correctly
        """
        self.iam.delete_access_key(self.TEST_USER, self.ACCESS_KEY)

        self.iam._client.delete_access_key.assert_called_once_with(
            UserName=self.TEST_USER,
            AccessKeyId=self.ACCESS_KEY
        )

    def test_create_user(self):
        """
        Test that checks if client.create_user is called correctly and create_user returns a user dict
        """
        self.iam._client.create_user = MagicMock(return_value=self.USER_RESPONSE)

        user = self.iam.create_user(self.TEST_USER)

        self.iam._client.create_user.assert_called_once_with(UserName=self.TEST_USER)
        self.assertEquals(self.USER_RESPONSE['User'], user)

    @patch('krux_iam.iam.IAM.delete_access_key')
    @patch('krux_iam.iam.IAM.get_access_keys', return_value=KEY_LIST)
    @patch('krux_iam.iam.IAM.delete_user_from_group')
    @patch('krux_iam.iam.IAM.get_groups', return_value=GROUPS_RESPONSE['Groups'])
    def test_delete_user(self, mock_get_groups, mock_delete_from_group, mock_get_keys, mock_delete_keys):
        """
        Test that checks if user is deleted successfully.
        Checks if get groups, delete_user_from group, get_keys, delete_keys, and delete_user are called.
        """
        self.iam.delete_user(self.TEST_USER)

        mock_get_groups.assert_called_once_with(self.TEST_USER)
        groups = mock_get_groups.return_value
        calls = []
        for group in groups:
            calls.append(call(self.TEST_USER, group['GroupName']))

        mock_delete_from_group.assert_has_calls(calls)
        self.assertEquals(len(groups), mock_delete_from_group.call_count)

        mock_get_keys.assert_called_once_with(self.TEST_USER)
        keys = mock_get_keys.return_value
        calls = []
        for key in keys:
            calls.append(call(self.TEST_USER, key['AccessKeyId']))

        mock_delete_keys.assert_has_calls(calls)
        self.assertEquals(len(keys), mock_delete_keys.call_count)

        self.iam._client.delete_user.assert_called_once_with(UserName=self.TEST_USER)

    def test_get_user(self):
        """
        Test that checks if client.get_user is called correctly and get_user returns a user dict
        """
        self.iam._client.get_user = MagicMock(return_value=self.USER_RESPONSE)

        user = self.iam.get_user(self.TEST_USER)

        self.iam._client.get_user.assert_called_once_with(UserName=self.TEST_USER)
        self.assertEquals(self.USER_RESPONSE['User'], user)

    def test_get_user_error(self):
        """
        Test that checks when client.get_user throws an error, if it's handled properly
        """
        self.iam._client.get_user = MagicMock(side_effect=botocore.exceptions.ClientError(self.ERROR_DICT, 'error'))

        user = self.iam.get_user(self.TEST_USER)

        self.assertTrue(self.iam._client.get_user.called)
        self.assertEquals(None, user)

    def test_add_user_to_group(self):
        """
        Test that checks if client.add_user_to_group is called correctly
        """
        self.iam.add_user_to_group(self.TEST_USER, self.TEST_GROUP)

        self.iam._client.add_user_to_group.assert_called_once_with(GroupName=self.TEST_GROUP, UserName=self.TEST_USER)

    def test_delete_user_from_group(self):
        """
        Test that checks if client.remove_user_from_group is called correctly
        """
        self.iam.delete_user_from_group(self.TEST_USER, self.TEST_GROUP)

        self.iam._client.remove_user_from_group.assert_called_once_with(GroupName=self.TEST_GROUP, UserName=self.TEST_USER)

    def test_get_groups(self):
        """
        Test that checks if client.list_groups_for_user is called correctly and a list of dictionaries is returned
        """
        self.iam._client.list_groups_for_user = MagicMock(return_value=self.GROUPS_RESPONSE)

        groups = self.iam.get_groups(self.TEST_USER)

        self.iam._client.list_groups_for_user.assert_called_once_with(UserName=self.TEST_USER)
        self.assertEquals(self.GROUPS_RESPONSE['Groups'], groups)
