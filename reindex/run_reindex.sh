#!/bin/bash -e
##-------------------------------------------------------------------
## File : run_reindex.sh
## Description : Re-index existing giant index to create more shards.
## Then create alias to handle the requests properly
## Check more: https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-reindex.html
##
## --
## Created : <2017-08-27>
## Updated: Time-stamp: <2017-08-31 17:28:33>
##-------------------------------------------------------------------
. library.sh

old_index_name=${1?}
new_index_name=${2?}
index_alias_name=${3?}
es_port=${4?}
es_ip=${5:-""}
avoid_update_alias=${6:-"yes"}
avoid_skip_reindex=${7:-"no"}
avoid_close_index=${8:-"yes"}

log "=============== Run re-index"
log "old_index_name: $old_index_name, new_index_name: $new_index_name, index_alias_name: $index_alias_name"
log "avoid_update_alias: $avoid_update_alias, avoid_skip_reindex: $avoid_skip_reindex, avoid_close_index: $avoid_close_index"

################################################################################
# Set default values
log_file="/var/log/run_reindex_sh_${BUILD_ID}.log"

if [ -z "$REINDEX_BATCH_SIZE" ]; then
    # By default _reindex uses scroll batches of 100. Here we change it to 500
    # https://www.elastic.co/guide/en/elasticsearch/reference/2.3/docs-reindex.html
    REINDEX_BATCH_SIZE="500"
fi

# if $es_ip is not given, use ip of eth0 as default
if [ -z "$es_ip" ]; then
    es_ip=$(/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')
fi

################################################################################
# Precheck
assert_alias_name "$old_index_name" "$index_alias_name"

# TODO: quit when alias and index doesn't match
assert_es_not_red "$es_ip" "$es_port"
assert_index_not_exists "$es_ip" "$es_port" "$old_index_name"
################################################################################

assert_index_not_exists "$es_ip" "$es_port" "$new_index_name"

list_indices "$es_ip" "$es_port"

# TODO: better way to make sure all shards(primary/replica) for this new index are good.
assert_index_status "$es_ip" "$es_port" "$new_index_name"
################################################################################

if [ "$avoid_skip_reindex" = "no" ]; then
    log "Reindex index. Attention: this will take a very long time, if the index is big"
    time curl -XPOST "http://${es_ip}:${es_port}/_reindex?pretty" -d "
     {
       \"conflicts\": \"proceed\",
       \"source\": {
       \"index\": \"${old_index_name}\",
       \"size\": \"${REINDEX_BATCH_SIZE}\"
    },
       \"dest\": {
       \"index\": \"${new_index_name}\",
       \"op_type\": \"create\"
    }
 }" | tee -a "$log_file"

    # confirm status, before proceed
    if tail -n 5 "$log_file" | grep "\"failures\" : \[ \]"; then
        log "keep going with the following process"
    else
        log "ERROR to run previous curl command"
        tail -n 5 "$log_file"
        exit 1
    fi
fi

# # We can start a new terminal and check reindex status
# log "Get all re-index tasks"
# time curl -XGET "http://${es_ip}:${es_port}/_tasks?detailed=true&actions=*reindex&pretty"

# # Check status
# time curl -XGET "http://${es_ip}:${es_port}/_cat/indices?v"

if [ "$avoid_update_alias" = "no" ]; then
    log "Add index to existing alias and remove old index from that alias. alias: $index_alias_name"
    time curl -XPOST "http://${es_ip}:${es_port}/_aliases" -d "
{
 \"actions\": [
 { \"remove\": {
 \"alias\": \"${index_alias_name}\",
 \"index\": \"${old_index_name}\"
 }},
 { \"add\": {
 \"alias\": \"${index_alias_name}\",
 \"index\": \"${new_index_name}\"
 }}
 ]
}" | tee -a "$log_file"

    echo >> "$log_file"

    if tail -n 1 "$log_file" | grep "\"acknowledged\"*:*true"; then
        log "keep going with the following process"
    else
        log "ERROR to update alias"
        tail -n 5 "$log_file"
        exit 1
    fi

    if [ "$avoid_close_index" = "no" ]; then
        # Close index: only after no requests access old index, we can close it
        curl -XPOST "http://${es_ip}:${es_port}/${old_index_name}/_close" | tee -a "$log_file"
    fi
fi

check_alias_by_index_name "$es_ip" "$es_port" "$index_alias_name"
list_indices "$es_ip" "$es_port"

# TODO: Delete index
# curl -XDELETE "http://${es_ip}:${es_port}/${old_index_name}?pretty" | tee -a "$log_file"
## File : run_reindex.sh ends
