# mkpipe-extractor-postgres

PostgreSQL extractor plugin for [MkPipe](https://github.com/mkpipe-etl/mkpipe). Reads PostgreSQL tables via JDBC.

## Documentation

For more detailed documentation, please visit the [GitHub repository](https://github.com/mkpipe-etl/mkpipe).

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

---

## Connection Configuration

```yaml
connections:
  pg_source:
    variant: postgresql
    host: localhost
    port: 5432
    database: mydb
    schema: public
    user: myuser
    password: mypassword
```

---

## Table Configuration

```yaml
pipelines:
  - name: pg_to_pg
    source: pg_source
    destination: pg_target
    tables:
      - name: public.users
        target_name: stg_users
        replication_method: full
        fetchsize: 100000
```

### Incremental Replication

```yaml
      - name: public.users
        target_name: stg_users
        replication_method: incremental
        iterate_column: updated_at
        iterate_column_type: datetime
        partitions_column: id
        partitions_count: 4
        fetchsize: 50000
```

### Custom SQL

```yaml
      - name: public.orders
        target_name: stg_orders
        replication_method: incremental
        iterate_column: created_at
        iterate_column_type: datetime
        custom_query: "SELECT id, user_id, amount FROM public.orders WHERE {query_filter}"
```

Use `{query_filter}` as a placeholder — replaced with the incremental `WHERE` clause, or `WHERE 1=1` on full runs. Can also reference a SQL file:

```yaml
        custom_query_file: orders.sql   # looks in sql/ directory
```

---

## Read Parallelism

For large tables, set `partitions_column` and `partitions_count` to read in parallel using multiple JDBC connections:

```yaml
      - name: public.events
        target_name: stg_events
        replication_method: incremental
        iterate_column: created_at
        iterate_column_type: datetime
        partitions_column: id       # numeric column to split on
        partitions_count: 8         # number of parallel JDBC partitions
        fetchsize: 50000
```

### How it works

- Spark queries min/max of `partitions_column` within the time window and divides into `partitions_count` equal slices
- Each slice is fetched by a separate Spark task via a separate JDBC connection
- `fetchsize` controls rows per JDBC round-trip

### Performance Notes

- **Full replication:** partitioning is not applied (only incremental).
- `partitions_column` should be a numeric column with good distribution (e.g. primary key).
- PostgreSQL default `fetchsize` in JDBC is 0 (loads all rows at once). Setting `fetchsize: 50000–200000` avoids out-of-memory on large tables.

---

## All Table Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | string | required | PostgreSQL table name (include schema: `public.users`) |
| `target_name` | string | required | Destination table name |
| `replication_method` | `full` / `incremental` | `full` | Replication strategy |
| `iterate_column` | string | — | Column used for incremental watermark |
| `iterate_column_type` | `int` / `datetime` | — | Type of `iterate_column` |
| `partitions_column` | string | same as `iterate_column` | Column to split JDBC reads on |
| `partitions_count` | int | `10` | Number of parallel JDBC partitions |
| `fetchsize` | int | `100000` | Rows per JDBC fetch |
| `custom_query` | string | — | Override SQL with `{query_filter}` placeholder |
| `custom_query_file` | string | — | Path to SQL file (relative to `sql/` dir) |
| `write_partitions` | int | — | Coalesce to N partitions before writing |
| `tags` | list | `[]` | Tags for selective pipeline execution |
| `pass_on_error` | bool | `false` | Skip table on error instead of failing |