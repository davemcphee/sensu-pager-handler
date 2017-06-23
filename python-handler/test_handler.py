#!/usr/bin/env python
# -*- coding: utf-8 -*-
# run this on sensu server to check what kind of output we get fed from main proc


import logging
logging.basicConfig(level=logging.DEBUG)
import os
import sys

LOG = logging.getLogger(__name__)
what_i_got = sys.argv

LOG.debug("argsv\t\t{}".format(str(what_i_got)))
LOG.debug("join\t\t{}".format(' '.join(what_i_got)))
