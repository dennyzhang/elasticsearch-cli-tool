#!/usr/bin/python
##-------------------------------------------------------------------
## @copyright 2017 DennyZhang.com
## Licensed under MIT
##   https://www.dennyzhang.com/wp-content/mit_license.txt
##
## File : detect_elasticsearch_gc.py
## Author : Denny <contact@dennyzhang.com>
## Description :
##    When ES runs into full GC, the whole cluster will freeze. It's bad!
##    By default, ES doesn't enable gc logging. Enable it by "-Xloggc:/var/log/elasticsearch/gc.log"
##    Then we can detect full GC occurrence from scanning ES gc logfile.
## --
## Created : <2017-02-24>
## Updated: Time-stamp: <2017-09-12 11:03:46>
##-------------------------------------------------------------------
import argparse
import requests
import sys
import socket
import re

NAGIOS_OK_ERROR=0
NAGIOS_EXIT_ERROR=2

# Sample:
# python ./detect_elasticsearch_gc.py --gc_logfile "/var/log/elasticsearch/gc.log"

if __name__ == '__main__':
    # get parameters from users
    parser = argparse.ArgumentParser()
    parser.add_argument('--gc_logfile', required=True, default='', \
                        help="ES GC Log file", type=str)
    l = parser.parse_args()

## File : detect_elasticsearch_gc.py ends
