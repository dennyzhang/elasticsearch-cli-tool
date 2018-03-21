#!/usr/bin/env python3
##-------------------------------------------------------------------
## File: check_es_gc_count.py
## Author : Denny
## Description :
## --
## Created : <2018-03-20>
## Updated: Time-stamp: <2018-03-20 21:23:40>
##-------------------------------------------------------------------
import sys
import argparse, socket
import requests, json

# curl "http://$es_ip:9200/_nodes/stats" \
# | jq '[ .nodes | to_entries | sort_by(.value.jvm.gc.collectors.old.collection_count) | .[] | { node: .value.name, full_gc_count: .value.jvm.gc.collectors.old.collection_count } ]'

def get_es_gc_count(es_host, es_port):
    url = "http://%s:%s/_nodes/stats" % (es_host, es_port)
    r = requests.get(url)
    if r.status_code != 200: raise Exception("Fail to run REST API: %s. Content: %s" % (url, r.content))
    content_json = json.loads(r.content)
    nodes_dict = content_json["nodes"]
    res = []
    for key in nodes_dict:
        res.append([nodes_dict[key]["name"], nodes_dict[key]["jvm"]["gc"]["collectors"]["old"]["collection_count"]])
    return sorted(res, key=lambda item: item[1], reverse=True)

def check_es_gc_count(es_host, es_port):
    l = get_es_gc_count(es_host, es_port)
    print("ES nodes full gc, sorted in a reverse order")
    for [node_name, gc_count] in l:
        print("%s\t%s" % (node_name, gc_count))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--es_host', required=False, \
                        help="server ip or hostname for elasticsearch instance. Default value is ip of eth0", type=str)
    parser.add_argument('--es_port', default='9200', required=False, \
                        help="server port for elasticsearch instance", type=str)
    l = parser.parse_args()
    es_host = l.es_host
    es_port = l.es_port
    # get ip of eth0, if es_host is not given
    if es_host is None:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        es_host = s.getsockname()[0]

    try:
        check_es_gc_count(es_host, es_port)
    except Exception as e:
        print("Unexpected error:%s, %s" % (sys.exc_info()[0], e))
        sys.exit(1)
## File: check_es_gc_count.py ends
