#!/bin/bash -e
##-------------------------------------------------------------------
## File : create_index_from_old.sh
## Description : Re-index existing giant index to create more shards.
## Then create alias to handle the requests properly
## Check more: https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-reindex.html
##
## --
## Created : <2017-03-27>
## Updated: Time-stamp: <2017-08-28 18:01:05>
##-------------------------------------------------------------------
. library.sh

old_index_name=${1?}
new_index_name=${2?}
es_port=${3?}
es_ip=${4:-""}
command_before_create=${5:-""}
shard_count=${6:-""}
replica_count=${7:-""}

################################################################################
# Set default values
log_file="/var/log/create_index_from_old_${BUILD_ID}.log"
# if $es_ip is not given, use ip of eth0 as default
if [ -z "$es_ip" ]; then
    es_ip=$(/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')
fi

if [ -z "$shard_count" ]; then
    shard_count=$(get_index_shard_count "$es_ip" "$es_port" "$old_index_name")
fi

if [ -z "$replica_count" ]; then
    replica_count=$(get_index_replica_count "$es_ip" "$es_port" "$old_index_name")
fi

################################################################################
# Precheck
if [ "$index_alias_name" = "$old_index_name" ]; then
    echo "ERROR: wrong parameter. old_index_name and index_alias_name can't be the same"
    exit 1
fi
assert_jq_installed

# TODO: quit when alias and index doesn't match
assert_es_not_red "$es_ip" "$es_port"
assert_index_not_exists "$es_ip" "$es_port" "$old_index_name"
assert_index_exists "$es_ip" "$es_port" "$new_index_name"

################################################################################
log "=============== Create new index. old_index_name: $old_index_name, new_index_name: $new_index_name"

list_indices "$es_ip" "$es_port"

tmp_dir="/tmp/${old_index_name}"
[ -d "$tmp_dir" ] || mkdir -p "$tmp_dir"

create_json_file="${tmp_dir}/combined.json"

log "Get setting and mappings of old index to ${create_json_file}"
cd "${tmp_dir}"
curl "http://${es_ip}:${es_port}/${old_index_name}/_settings" | \
    jq ".[] | .settings.index.number_of_shards=\"${shard_count}\" | .settings.index.number_of_replicas=\"${replica_count}\"" \
       > "${tmp_dir}/settings.json"

curl "http://${es_ip}:${es_port}/${old_index_name}/_mapping" \
    | jq '.[]' > "${tmp_dir}/mapping.json"

cat mapping.json | jq --sort-keys '.' > mapping_sorted.json

cat "mapping_sorted.json" "settings.json" \
    | jq --slurp '.[0] * .[1]' > "${create_json_file}"

################################################################################
# run the hook
if [ -n "$command_before_create" ]; then
    export OLD_INDEX_NAME="$old_index_name"
    export MAPPING_JSON_FILE="${tmp_dir}/mapping_sorted.json"
    export SETTINGS_JSON_FILE="${tmp_dir}/settings.json"
    export COMBINED_JSON_FILE="$create_json_file"

    eval "$command_before_create" | tee -a "$log_file"
    # java -jar /root/fix-mappings-reindex-2.0.jar "$index_type" "${old_index_name}" ./mapping_sorted.json ./settings.json | tee -a "$log_file"

    if tail -n 10 "$log_file" | grep -i "ERROR"; then
        log "error is found when running command: $command_before_create"
        exit 1
    fi
fi

################################################################################
create_timeout="30m"
log "create new index with settings and mappings"
time curl -XPOST "http://${es_ip}:${es_port}/${new_index_name}?timeout=${create_timeout}&wait_for_active_shards=all" \
     -d @"${create_json_file}" | tee -a "$log_file"
echo >> "$log_file"

if tail -n 1 "$log_file" | grep "\"acknowledged\"*:*true"; then
    log "keep going with the following process"
else
    log "ERROR to run previous curl command"
    tail -n 5 "$log_file"
    exit 1
fi

log "Get the setting of the new index"
curl -XGET "http://${es_ip}:${es_port}/${new_index_name}/_settings?pretty"
## File : create_index_from_old.sh ends
