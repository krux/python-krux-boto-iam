# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import

#
# Third party libraries
#

import botocore

#
# Internal libraries
#

from krux.logging import get_logger
from krux.stats import get_stats
from krux.cli import get_parser, get_group
from krux_boto.boto import Boto3, add_boto_cli_arguments


NAME = 'krux-iam'


def get_iam(args=None, logger=None, stats=None):
    """
    Return a usable IAM object without creating a class around it.
    In the context of a krux.cli (or similar) interface the 'args', 'logger'
    and 'stats' objects should already be present. If you don't have them,
    however, we'll attempt to provide usable ones.
    (If you omit the add_iam_cli_arguments() call during other cli setup,
    the Boto object will still work, but its cli options won't show up in
    --help output)
    (This also handles instantiating a Boto3 object on its own.)
    """
    if not args:
        parser = get_parser(description=NAME)
        add_iam_cli_arguments(parser)
        args = parser.parse_args()

    if not logger:
        logger = get_logger(name=NAME)

    if not stats:
        stats = get_stats(prefix=NAME)

    boto = Boto3(
        log_level=args.boto_log_level,
        access_key=args.boto_access_key,
        secret_key=args.boto_secret_key,
        region=args.boto_region,
        logger=logger,
        stats=stats,
    )
    return IAM(
        boto=boto,
        logger=logger,
        stats=stats,
    )


def add_iam_cli_arguments(parser, include_boto_arguments=True):
    """
    Utility function for adding IAM specific CLI arguments.
    """
    if include_boto_arguments:
        # GOTCHA: Since many modules use krux_boto, the krux_boto's CLI arguments can be included twice,
        # causing an error. This creates a way to circumvent that.

        # Add all the boto arguments
        add_boto_cli_arguments(parser)

    # Add those specific to the application
    group = get_group(parser, NAME)


class IAM(object):
    """
    A manager to handle all IAM related functions.
    """

    def __init__(
        self,
        boto,
        logger=None,
        stats=None,
    ):
        # Private variables, not to be used outside this module
        self._name = NAME
        self._logger = logger or get_logger(self._name)
        self._stats = stats or get_stats(prefix=self._name)

        # Private client representing IAM
        self._client = boto.client('iam')

    def create_access_keys(self, username):
        """
        Creates and returns an AWS access key and secret key for the given user.
        """
        response = self._client.create_access_key(
            UserName=username
        )
        key = response['AccessKey']

        return key['AccessKeyId'], key['SecretAccessKey']

    def get_access_keys(self, username):
        """
        Gets all access keys for a given user. Returns a list of dicts representing access keys.
        """
        response = self._client.list_access_keys(
            UserName=username
        )

        return response['AccessKeyMetadata']

    def delete_access_key(self, username, key_id):
        """
        Deletes the access key associated with the given user.
        """
        self._client.delete_access_key(
            UserName=username,
            AccessKeyId=key_id
        )

    def create_user(self, username):
        """
        Creates user and returns the user as a dict of their attributes.
        """
        response = self._client.create_user(
            UserName=username
        )

        return response['User']

    def delete_user(self, username):
        """
        Deletes user and removes user from any groups they belong to and deletes
        all their access keys.
        """
        for group in self.get_groups(username):
            self.delete_user_from_group(username, group)

        for key in self.get_access_keys(username):
            self.delete_access_key(username, key['AccessKeyId'])

        self._client.delete_user(
            UserName=username
        )

    def get_user(self, username):
        """
        Gets the given user and upon failure returns None.
        """
        try:
            response = self._client.get_user(
                UserName=username
            )
            return response
        except botocore.exceptions.ClientError:
            return None

    def add_user_to_group(self, username, group):
        """
        Adds given user to the given group.
        """
        self._client.add_user_to_group(
            GroupName=group,
            UserName=username
        )

    def delete_user_from_group(self, username, group):
        """
        Deletes the user from the given group.
        """
        self._client.remove_user_from_group(
            GroupName=group['GroupName'],
            UserName=username
        )

    def get_groups(self, username):
        """
        Gets all the groups the current user belongs to.
        Returns a list of dicts representing each group.
        """
        response = self._client.list_groups_for_user(
            UserName=username
        )

        return response['Groups']
