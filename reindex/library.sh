#!/bin/bash -e
##-------------------------------------------------------------------
## File : library.sh
## Description :
## --
## Created : <2017-06-13>
## Updated: Time-stamp: <2017-08-31 16:31:46>
##-------------------------------------------------------------------
function is_es_red() {
    local es_ip=${1?}
    local es_port=${2?}
    if curl "$es_ip:$es_port/_cluster/health?pretty" | grep red 1>/dev/null 2>&1; then
        # add a sleep and try again. Sleep for 5 minutes
        sleep 300
        if curl "$es_ip:$es_port/_cluster/health?pretty" | grep red 1>/dev/null 2>&1; then
            echo "yes"
        else
            echo "no"
        fi
    else
        echo "no"
    fi
}

function is_es_index_exists() {
    local es_ip=${1?}
    local es_port=${2?}
    local index_name=${3?}
    if curl -I "$es_ip:$es_port/$index_name" \
            | grep "200 OK" 1>/dev/null 2>&1; then
        echo "yes"
    else
        echo "no"
    fi
}

function is_es_alias_exists() {
    local es_ip=${1?}
    local es_port=${2?}
    local alias_name=${3?}
    if curl -I "$es_ip:$es_port/_alias/$alias_name" \
            | grep "200 OK" 1>/dev/null 2>&1; then
        echo "yes"
    else
        echo "no"
    fi
}

function get_index_shard_count() {
    local es_ip=${1?}
    local es_port=${2?}
    local index_name=${3?}
    value=$(curl "$es_ip:$es_port/$index_name/_settings?pretty" | grep number_of_shards | awk -F':' '{print $2}')
    value=${value# \"}
    value=${value%\",}
    echo "$value"
}

function get_index_replica_count() {
    local es_ip=${1?}
    local es_port=${2?}
    local index_name=${3?}
    value=$(curl "$es_ip:$es_port/$index_name/_settings?pretty" | grep number_of_replicas | awk -F':' '{print $2}')
    value=${value# \"}
    value=${value%\",}
    echo "$value"
}

function log() {
    local msg=$*
    date_timestamp=$(date +['%Y-%m-%d %H:%M:%S'])
    echo -ne "$date_timestamp $msg\n"

    if [ -n "$LOG_FILE" ]; then
        echo -ne "$date_timestamp $msg\n" >> "$LOG_FILE"
    fi
}
################################################################################
function list_indices() {
    local es_ip=${1?}
    local es_port=${2?}
    echo "List all indices"
    curl -XGET "http://${es_ip}:${es_port}/_cat/indices?v"
}

function check_alias_by_index_name() {
    local es_ip=${1?}
    local es_port=${2?}
    local index_alias_name=${3?}
    echo "List all alias for $index_alias_name"
    curl -XGET "http://${es_ip}:${es_port}/_alias/$index_alias_name"
}
################################################################################
# Precheck and Assertions
function assert_alias_name() {
    local old_index_name=${1?}
    local index_alias_name=${2?}

    if [ "$index_alias_name" = "$old_index_name" ]; then
        echo "ERROR: wrong parameter. old_index_name and index_alias_name can't be the same"
        exit 1
    fi
}

function assert_es_not_red() {
    local es_ip=${1?}
    local es_port=${2?}
    if [ "$(is_es_red "$es_ip" "$es_port")" = "yes" ]; then
        echo "ERROR: ES cluster is red"
        exit 1
    fi
}

function assert_index_not_exists() {
    local es_ip=${1?}
    local es_port=${2?}
    local index_name=${3?}
    if [ "$(is_es_index_exists "$es_ip" "$es_port" "$index_name")" = "no" ]; then
        echo "ERROR: index($index_name) doesn't exist."
        exit 1
    fi
}

function assert_index_exists() {
    local es_ip=${1?}
    local es_port=${2?}
    local index_name=${2?}
    if [ "$(is_es_index_exists "$es_ip" "$es_port" "$index_name")" = "yes" ]; then
        echo "ERROR: index($index_name) already exist."
        exit 1
    fi
}

function assert_index_status() {
    local es_ip=${1?}
    local es_port=${2?}
    local index_name=${3?}

    if [ "$(curl "$es_ip:$es_port/_cat/shards?v" | grep "${index_name}" | grep -c -v STARTED)" = "0" ]; then
        echo "index(${index_name}) is up and running"
    else
        echo "index(${index_name}) is not up and running"
        exit 1
    fi
}

function assert_jq_installed() {
    if ! which jq 1>/dev/null 2>&1; then
        echo "ERROR: jq is not installed"
        exit 1
    else
        if ! jq --version | grep "jq-1.5"; then
            echo "ERROR: Only jq-1.5 has been verified. Please make sure you have the right version installed"
            exit 1
        fi
    fi
}
################################################################################
## File : library.sh ends
