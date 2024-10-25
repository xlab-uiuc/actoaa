# Notes for mariadb

## Ignored fields

Fields marked as removed or deprecated are ignored.

`shared_memory` is Windows-only, so ignored

## Boolean

Boolean fields can be `Yes`/`No`, `ON`/`OFF` or `1`/`0`. `1`/`0` is used.

## Aliases

- `max_insert_delayed_threads` and `max_delayed_threads`
- `identity` and `last_insert_id`
- `tmp_memory_table_size` and `tmp_table_size`

## Misc

`lower_case_table_names` is a guaranteed bug just by looking.
