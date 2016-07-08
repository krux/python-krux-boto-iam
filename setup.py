# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#

######################
# Standard Libraries #
######################
from __future__ import absolute_import
from setuptools import setup, find_packages

# We use the version to construct the DOWNLOAD_URL.
VERSION      = '0.0.1'

# URL to the repository on Github.
REPO_URL     = 'https://github.com/krux/python-krux-boto-iam'
# Github will generate a tarball as long as you tag your releases, so don't
# forget to tag!
DOWNLOAD_URL = ''.join((REPO_URL, '/tarball/release/', VERSION))


### XXX these all need to be in sub dirs, or it won't work :(
setup(
    name             = 'krux-boto-iam',
    version          = VERSION,
    author           = 'Kelsey Lam',
    author_email     = 'klam@krux.com',
    description      = 'Library for interacting with AWS IAM built on krux-boto',
    url              = REPO_URL,
    download_url     = DOWNLOAD_URL,
    license          = 'All Rights Reserved.',
    packages         = find_packages(),
    # dependencies are named in requirements.pip
    install_requires = [],
    entry_points     = {
        'console_scripts': [
            'krux-iam-test = krux_boto_iam.cli:main',
        ],
    },
)