#!/bin/bash -e
es_node_list="es-01 es-02 es-03"

shard_list_file="/Users/mac/shard_file.txt"

es_index="master-index-abae8b30ac9b11e692000401f8d88101"

for es_node in $es_node_list; do
    count=$(grep $es_node $shard_list_file | wc -l)
    bematech_shard_count=$(grep $es_node $shard_list_file | grep $es_index | wc -l)
    primary_count=$(grep $es_node $shard_list_file | grep $es_index | grep " | p | " | wc -l)
    replica_count=$(grep $es_node $shard_list_file | grep $es_index | grep " | r | " | wc -l)

    primary_count=$(echo "${primary_count}" | sed -e 's/^[ \t]*//')
    replica_count=$(echo "${replica_count}" | sed -e 's/^[ \t]*//')
    echo "In $es_node, shard count: $count, bematech_shard_count shard count: $bematech_shard_count, $primary_count(p), $replica_count(r)"
done
