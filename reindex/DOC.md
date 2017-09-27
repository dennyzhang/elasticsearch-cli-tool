Re-index elasticsearch index

- Whether to update alias
- Whether to create new index
- Allow people to customize the data structure change, after creating the new index

Entrypoint: reindex.sh

# How To Run
```
#!/bin/bash -ex
es_ip="YOUR_ELASTICSEARCH_IP"
es_port="9200"
avoid_update_alias="no" #yes/no
avoid_create_new_index="no" #yes/no
avoid_run_reindex="yes" #yes/no
avoid_close_index="no" #yes/no
new_es_index_suffix="new2"
es_index_list="index1
index2"

command_before_create="./update_schema_json_20170828.sh"
shard_count="10" # Reconfigure shard count

bash -ex ./reindex.sh "$es_ip" "$es_port" "$avoid_update_alias" \
        "$avoid_create_new_index" "$avoid_run_reindex" "$avoid_close_index" \
        "$new_es_index_suffix" "$es_index_list" "$command_before_create" "$shard_count"
```

Notice:
- After updating alias, we will close old indices. But won't delete them.

# Hook: before create index
Global envs:
