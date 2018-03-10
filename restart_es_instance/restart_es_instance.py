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
##
##  Example: Restart es in 172.17.0.5
##   python ./restart_es_instance.py --es_host_mgmt 172.17.0.6 --es_port 9200 --es_host 172.17.0.5
## --
## Created : <2018-03-09>
## Updated: Time-stamp: <2018-03-10 00:23:43>
##-------------------------------------------------------------------
import sys
import argparse, socket
import requests, json
import subprocess, time

# curl $es_ip:9200/_cluster/health?pretty
def get_es_health(es_host_mgmt, es_port):
    # make sure es is green. And response to the query fast
    url = "http://%s:%s/_cluster/health?pretty" % (es_host_mgmt, es_port)
    r = requests.get(url)
    if r.status_code != 200: raise Exception("Fail to run REST API: %s. Content: %s" % (url, r.content))
    content_json = json.loads(r.content)
    es_status = content_json["status"]
    # TODO: return false, if es cluster is too slow to response
    return es_status

# service elasticsearch stop/start/status
def manage_es_service(action, retries=2, sleep_seconds=5):
    if action not in ["start", "stop", "status"]:
        print("Error: unsupported action: %s" % (action))
        return False

    if action == "start":
        commands = ['service', 'elasticsearch', 'start']
    elif action == "stop":
        commands = ['service', 'elasticsearch', 'stop']
    else:
        commands = ['service', 'elasticsearch', 'status']

    print("Run command: %s" % ' '.join(commands))
    return_code = subprocess.call(commands)
    if return_code != 0:
        for i in range(retries):
            print("Warning: retry the command")
            time.sleep(sleep_seconds)
            print("Sleep %d seconds" % (sleep_seconds))
            return_code = subprocess.call(commands)
            if return_code == 0: break
        if return_code != 0:
            print("ERROR: fail to run the command")
            return False
    return True

# https://www.elastic.co/guide/en/elasticsearch/guide/current/_rolling_restarts.html
def update_es_allocation(es_host_mgmt, es_port, allocation_policy, retries=2, sleep_seconds=5):
    if allocation_policy not in ["all", "none"]:
        print("Error: unsupported allocation policy: %s" % (allocation_policy))
        return False

    url = "http://%s:%s/_cluster/settings" % (es_host_mgmt, es_port)
    payload = {}
    payload["transient"] = {}
    payload["transient"]["cluster.routing.allocation.enable"] = allocation_policy

    r = requests.put(url, data = json.dumps(payload))
    if r.status_code != 200: raise Exception("Fail to run REST API: %s. Content: %s" % (url, r.content))

    print(r.content)
    content_json = json.loads(r.content)
    acknowledged_status = content_json["acknowledged"]
    if acknowledged_status is False:
        for i in range(retries):
            print("Warning: retry the rest API call")
            time.sleep(sleep_seconds)
            print("Sleep %d seconds" % (sleep_seconds))
            r = requests.put(url, data = json.dumps(payload))
            if r.status == 200:
                content_json = json.loads(r.content)
                acknowledged_status = content_json["acknowledged"]
                if acknowledged_status is True: break

    if acknowledged_status is False:
        print("Failed to change shards allocations to %s. Error: %s" % (allocation_policy, str(content_json)))
        return False
    else:
        print("Changed ES shards allocation to %s" % (allocation_policy))
        return True

# https://www.elastic.co/guide/en/elasticsearch/guide/current/_rolling_restarts.html
def es_flushed_sync(es_host_mgmt, es_port, retries=2, sleep_seconds=5):
    url = "http://%s:%s/_flush/synced" % (es_host_mgmt, es_port)
    r = requests.post(url)
    if r.status_code != 200: raise Exception("Fail to run REST API: %s. Content: %s" % (url, r.content))
    content_json = json.loads(r.content)
    failed_shards_count = content_json["_shards"]["failed"]

    if failed_shards_count != 0:
        for i in range(retries):
            print("Warning: retry the rest API call")
            time.sleep(sleep_seconds)
            print("Sleep %d seconds" % (sleep_seconds))
            r = requests.put(url)
            if r.status_code == 200:
                content_json = json.loads(r.content)
                failed_shards_count = content_json["_shards"]["failed"]
                if failed_shards_count == 0: break
            
    if failed_shards_count != 0:
        print("ERROR: %d shards failed to finish flushed sync. Content: %s" % (failed_shards_count, str(content_json)))
        return False
    else:
        print("All shards have finished flushed sync correctly")
        return True

def restart_es_instance(es_host_mgmt, es_port, es_host):
    # TODO: better code skeleton?
    es_status = get_es_health(es_host_mgmt, es_port)
    if es_status != "green":
        print("ES status is %s, not green. Abort the following actions" % (es_status))
        return False

    if not update_es_allocation(es_host_mgmt, es_port, "none"): return False
    if not es_flushed_sync(es_host_mgmt, es_port): return False
    if not manage_es_service("stop"): return False
    if not manage_es_service("start"): return False
    # add sleep for es slow start
    sleep_seconds = 10
    print("Sleep %d seconds, for ES slow start" % (sleep_seconds))
    time.sleep(sleep_seconds)
    if not manage_es_service("status"): return False
    if not update_es_allocation(es_host_mgmt, es_port, "all"): return False
    return True

if __name__ == '__main__':
    # get parameters from users
    parser = argparse.ArgumentParser()
    parser.add_argument('--es_host_mgmt', required=False, \
                        help="Interact with another ES instance for management requests. Current node may stuck into full GC.", type=str)
    parser.add_argument('--es_port', default='9200', required=False, \
                        help="server port for elasticsearch instance", type=str)
    parser.add_argument('--es_host', required=False, \
                        help="Restart which ES instance. Default value is ip of eth0", type=str)
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

    try:
        if restart_es_instance(es_host_mgmt, es_port, es_host) is False:
            print("ERROR: restart es in %s." % (es_host))
            sys.exit(1)
        else:
            print("OK: restarted es in %s." % (es_host))
            es_status = get_es_health(es_host_mgmt, es_port)
            print("ES status is %s. ES cluster should be loading shards now" % (es_status))
    except Exception as e:
        print("Unexpected error:%s, %s" % (sys.exc_info()[0], e))
## File: restart_es_instance.py ends
