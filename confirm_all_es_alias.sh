#!/usr/bin/env bash
##-------------------------------------------------------------------
## File: confirm_all_es_alias
## Author : Denny
## Description :
## --
## Created : <2018-01-29>
## Updated: Time-stamp: <2018-01-29 16:25:54>
##-------------------------------------------------------------------
function get_alias_from_index() {
    local index=${1?}
    alias="${index%-new*}"
    echo "${alias//-index/}"
}

function list_indices() {
    local es_ip=${1?}
    local es_port=${2?}
    curl -XGET "http://${es_ip}:${es_port}/_cat/indices?v"  | grep "\-index" | awk '{print $3}'
}

function shell_exit() {
    errcode=$?
    if [ $errcode -eq 0 ]; then
        echo "All es alias is OK"
    else
        echo "Some es alias has issues"
    fi
    exit $errcode
}

es_ip=${1?}
es_port=${2?}

trap shell_exit SIGHUP SIGINT SIGTERM 0

index_list=$(list_indices "$es_ip" "$es_port")
# echo $index_list
for index in $index_list; do
    alias_name=$(get_alias_from_index "$index")
    echo "index: $index. Get alias doc count. alias_name: $alias_name"
    curl "http://$es_ip:$es_port/${alias_name}/_count" | grep -v error
done    
