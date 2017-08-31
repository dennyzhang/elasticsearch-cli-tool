#!/bin/bash -e
##-------------------------------------------------------------------
## File : reindex.sh
## Description : Re-index existing giant index to create more shards.
## Then create alias to handle the requests properly
## Check more: https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-reindex.html
##
## --
## Created : <2017-08-27>
## Updated: Time-stamp: <2017-08-31 14:34:46>
##-------------------------------------------------------------------
es_ip=${1?}
es_port=${2?}
avoid_update_alias=${3?} # yes/no
avoid_create_new_index=${4?} # yes/no
avoid_skip_reindex=${5?} # yes/no
avoid_close_index=${6?}
new_es_index_suffix=${7?}
es_index_list=${8?}
command_before_create=${9:-""}
shard_count=${10:-""}

wait_seconds=30

for old_index_name in $es_index_list; do
    # From master-index-799e458055c611e6bb000401f8d88101 to master-index-799e458055c611e6bb000401f8d88101-new3
    # From master-index-799e458055c611e6bb000401f8d88101-new2 to master-index-799e458055c611e6bb000401f8d88101-new3
    new_index_name="${old_index_name%%-new*}-${new_es_index_suffix}"
    # From master-index-799e458055c611e6bb000401f8d88101-new3 to master-799e458055c611e6bb000401f8d88101
    index_alias_name=$(echo "${new_index_name%%-new*}" | sed "s/-index//g")
    if [ "$avoid_create_new_index" = "no" ]; then
        bash -ex ./create_index_from_old.sh "$old_index_name" "$new_index_name" "$es_port" "$es_ip" \
             "$command_before_create" "$shard_count"

        echo "sleep $wait_seconds seconds for new ES index($new_index_name) to be up and running"
        sleep "$wait_seconds"
    fi

    bash -ex ./run_reindex.sh "$old_index_name" "$new_index_name" "$index_alias_name" \
         "$es_port" "$es_ip" "$avoid_update_alias" "$avoid_skip_reindex" "$avoid_close_index"
done
## File : reindex.sh ends
