#!/usr/bin/env python
##-------------------------------------------------------------------
## @copyright 2017 DennyZhang.com
## Licensed under MIT
##   https://www.dennyzhang.com/wp-content/mit_license.txt
##
## File: delete_closed_es_indices.py
## Author : Denny <https://www.dennyzhang.com/contact>
## Description :
## --
## Created : <2018-02-06>
## Updated: Time-stamp: <2018-02-06 18:01:45>
##-------------------------------------------------------------------
# pip install elasticsearch==2.3.0
import argparse
import sys, time
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import AuthorizationException
################################################################################
NOT_EXISTS="NOT_EXISTS"
IS_CLOSED="IS_CLOSED"
IS_OPEN="IS_OPEN"

def index_status(es_instance, index_name):
    if es_instance.indices.exists(index=index_name, expand_wildcards='all') is False:
        return NOT_EXISTS
    # TODO: better way to get index status
    try:
        es_instance.indices.stats(index=index_name)
    except AuthorizationException as e:
        if e.error == 'index_closed_exception':
            return IS_CLOSED
        print("ERROR: unexpected error when checking index(%s), error: %s" % (index_name, str(e)))
    return IS_OPEN

def wait_es_slowness(es_instance, max_wait_seconds, try_count=3):
    # TODO
    for i in range(0, try_count):
        print("Sleep %d seconds for ES slowness" % (max_wait_seconds))
        time.sleep(max_wait_seconds)
    return True

def get_list_from_string(string):
    res = []
    for entry in string.split('\n'):
        entry = entry.strip()
        if entry == "" or entry.startswith('#'): continue
        res.append(entry)
    return res
################################################################################
def delete_closed_index(es_ip, es_port, index_list, max_wait_seconds):
    es_instance = Elasticsearch(["%s:%s"%(es_ip, es_port)])
    # precheck
    for index_name in index_list:
        status = index_status(es_instance, index_name)
        if status != IS_CLOSED:
            print("ERROR: index(%s) should be closed. But its status is %s" % (index_name, status))
            sys.exit(1)

    # deal with each index
    for index_name in index_list:
        print("Deleting index: %s" % (index_name))
        status = index_status(es_instance, index_name)
        if status != IS_CLOSED:
            print("ERROR: index(%s) should be closed. But its status is %s" % (index_name, status))
            sys.exit(1)

        output = es_instance.indices.delete(index=index_name)
        if output != {'acknowledged': True}:
            print("ERROR: deleting index(%s) has failed. output: %s" % (index_name, str(output)))

        if wait_es_slowness(es_instance, max_wait_seconds) is False:
            print("ERROR: ES is slow after deleting index(%s)." % (index_name))
            sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--es_ip', required=True, help="Elasticsearch IP", type=str)
    parser.add_argument('--es_port', default='9200', help="Elasticsearch port", type=str)
    parser.add_argument('--index_list', required=True, type=str, \
                        help="Index list to be deleted. If any open index is detected, the whole process will be aborted.")
    parser.add_argument('--max_wait_seconds', dest='max_wait_seconds', type=int, default='5', \
                        help="Wait for ES slowness after index removal")

    l = parser.parse_args()
    delete_closed_index(l.es_ip, l.es_port, get_list_from_string(l.index_list), l.max_wait_seconds)
## File: delete_closed_es_indices.py ends
