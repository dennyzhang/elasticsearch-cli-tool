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
## Updated: Time-stamp: <2018-02-06 15:37:43>
##-------------------------------------------------------------------
# pip install elasticsearch
import argparse
import elasticsearch
import sys
################################################################################
def detect_open_index(es_ip, es_port, index_name_list):
    # TODO
    return (False, [])

def delete_index(es_ip, es_port, index_name):
    # TODO
    return False

def wait_es_slowness(es_ip, es_port, max_wait_seconds, try_count=3):
    # TODO
    return True

################################################################################
def delete_closed_index(es_ip, es_port, index_list, max_wait_seconds):
    # precheck
    (status, l) = detect_open_index(es_ip, es_port, index_name_list) is False:
    if status:
        print("ERROR: problematic input. Detected some open index: %s") % (','.join(l))
        sys.exit(1)

    # deal with each index
    for index_name in index_list:
        print("Delete index: %s" % (index_name))
        (status, l) = detect_open_index(es_ip, es_port, [index_name]):
        if status:
            print("ERROR: index(%s) is open. Abort the whole process." % (index_name))
            sys.exit(1)
        if delete_index(es_ip, es_port, index_name) is False:
            print("ERROR: deleting index(%s) has failed" % (index_name))
        if wait_es_slowness(es_ip, es_port, max_wait_seconds) is False:
            print("ERROR: ES is slow after deleting index(%s)." % (index_name))
            sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--es_ip', required=True, help="Elasticsearch IP", type=str)
    parser.add_argument('--es_port', default='9200', help="Elasticsearch port", type=str)
    parser.add_argument('--max_wait_seconds', dest='max_wait_seconds', default='5', \
                        help="Wait for ES slowness after index removal")
    # TODO
    parser.add_argument('--index_list', required=True, default='mdm-master,mdm-staging',
                        help="Index list to be deleted. If open index is detected, the whole process will abort", type=str)

    l = parser.parse_args()
    examine_only = l.examine_only
    print "bucket_list: " + l.bucket_list
    delete_closed_index(es_ip, es_port, index_list, l.max_wait_seconds)
## File: delete_closed_es_indices.py ends
