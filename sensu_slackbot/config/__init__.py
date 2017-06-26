#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

import yaml

LOG = logging.getLogger(__name__)


def get_config():
    """
    Just looks in current dir for config.yml
    :return:
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(current_dir, 'config.yml')
    if os.path.isfile(config_file):
        with open(config_file, 'r') as f:
            config_dict = yaml.load(f)
        return config_dict
    else:
        LOG.error("Can't find config file, looked here: {}".format(config_file))
        raise IOError


if __name__ == '__main__':
    print(get_config())
