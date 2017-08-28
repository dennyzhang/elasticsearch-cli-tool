Re-index elasticsearch index

- Whether to update alias
- Whether to create new index
- Allow people to customize the data structure change, after creating the new index

Entrypoint: reindex.sh


Notice:
- After updating alias, we will close old indices. But won't delete them.

# Hook: before create index
Global envs:
