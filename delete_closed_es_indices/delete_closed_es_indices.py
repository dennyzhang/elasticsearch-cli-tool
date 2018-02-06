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
## Updated: Time-stamp: <2018-02-06 15:26:02>
##-------------------------------------------------------------------
import sys
def is_index_open(es_ip, es_port, index_name):
    # TODO
    return False

def delete_index(es_ip, es_port, index_name):
    # TODO
    return False

def wait_es_slowness(es_ip, es_port, max_wait_seconds, try_count=3):
    # TODO
    return True

def delete_closed_index(es_ip, es_port, index_list, max_wait_seconds):
    for index_name in index_list:
        print("Delete index: %s" % (index_name))
        if is_index_open(es_ip, es_port):
            print("ERROR: index(%s) is open. Abort the whole process." % (index_name))
            sys.exit(1)
        if delete_index(es_ip, es_port, index_name) is False:
            print("ERROR: deleting index(%s) has failed" % (index_name))
        if wait_es_slowness(es_ip, es_port, max_wait_seconds) is False:
            print("ERROR: ES is slow after deleting index(%s)." % (index_name))
            sys.exit(1)

if __name__ == '__main__':
    max_wait_seconds = 5
    delete_closed_index(es_ip, es_port, index_list, max_wait_seconds)
## File: delete_closed_es_indices.py ends
