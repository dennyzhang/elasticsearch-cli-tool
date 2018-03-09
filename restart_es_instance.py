#!/usr/bin/env python3
##-------------------------------------------------------------------
## File: restart_es_instance.py
## Author : Denny
## Description : Restart one ES instance in a safe way
##
##   0. Run current script in the es instance we want to restart
##   1. If ES is not green, refuse to do that
##   2. If ES is too slow, refuse to do that
##   3. Add 2 retries for changing allocation setting and flush
##   4. If retire still doesn't work, abort with errors
## --
## Created : <2018-03-09>
## Updated: Time-stamp: <2018-03-09 15:10:07>
##-------------------------------------------------------------------
import sys
import argparse, socket

def check_es_health(es_host, es_port):
    # make sure es is green. And response to the query fast
    print("hello, world")

def update_es_allocation(es_host, es_port, allocation_policy):
    print("hello, world")

def es_flushed_sync(es_host, es_port):
    print("hello, world")

def restart_es_instance(es_host, es_port, es_host_mgmt):
    if not check_es_health(es_host_mgmt, es_port): return False

if __name__ == '__main__':
    # get parameters from users
    parser = argparse.ArgumentParser()
    parser.add_argument('--es_host', required=False, \
                        help="Restart which ES instance. Default value is ip of eth0", type=str)
    parser.add_argument('--es_host_mgmt', required=False, \
                        help="Interact with another ES instance for management requests. Current node may stuck into full GC.", type=str)
    parser.add_argument('--es_port', default='9200', required=False, \
                        help="server port for elasticsearch instance", type=str)
    l = parser.parse_args()

    es_host = l.es_host
    es_port = l.es_port
    es_host_mgmt = l.es_host
    # get ip of eth0, if es_host is not given
    if es_host is None or es_host_mgmt is None:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host = s.getsockname()[0]
        if es_host is None: es_host = host
        if es_host_mgmt is None: es_host_mgmt = host

    if restart_es_instance(es_host, es_port, es_host_mgmt) is False:
        print("ERROR: restart es in %s" % (es_host))
        sys.exit(1)
    else:
        print("OK: restarted es in %s" % (es_host))
## File: restart_es_instance.py ends
