from mkpipe.functions_spark.base_extractor import BaseExtractor

class PostgresExtractor(BaseExtractor):
    def __init__(self, config, settings):
        super().__init__(
            config,
            settings,
            driver_name='clickhouse',
            driver_jdbc='com.clickhouse.jdbc.ClickHouseDriver',
        )
