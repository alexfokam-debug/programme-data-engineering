from pyspark import pipelines as dp
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    LongType,
    StringType,
    DoubleType,
)


event_schema = StructType([
    StructField("event_id", LongType(), True),
    StructField("event_time", StringType(), True),
    StructField("category", StringType(), True),
    StructField("amount", DoubleType(), True),
])


@dp.table(
    name="workspace.study_s06.bronze_json_events",
    comment="Evenements JSON synthetiques ingeres incrementalement",
)
def bronze_json_events():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .schema(event_schema)
        .load("/Volumes/workspace/study_s06/lakeflow_files/events")
    )


@dp.table(
    name="workspace.study_s06.silver_json_events",
    comment="Evenements JSON valides et types",
)
@dp.expect_or_drop("reasonable_event_id", "event_id < 1000")
@dp.expect_or_drop("positive_amount", "amount > 0")
@dp.expect_or_drop("valid_event_id", "event_id IS NOT NULL")
@dp.expect_or_drop("valid_category", "category IS NOT NULL")
def silver_json_events():
    return (
        spark.readStream
        .table("workspace.study_s06.bronze_json_events")
        .withColumn("event_time", F.to_timestamp("event_time"))
    )


@dp.table(
    name="workspace.study_s06.quarantine_json_events",
    comment="Evenements invalides conserves pour diagnostic",
)
def quarantine_json_events():
    return (
        spark.readStream
        .table("workspace.study_s06.bronze_json_events")
        .filter(
            "event_id IS NULL "
            "OR event_id >= 1000 "
            "OR category IS NULL "
            "OR amount <= 0"
        )
        .withColumn(
            "quarantine_reason",
            F.concat_ws(
                ", ",
                F.when(
                    F.col("event_id").isNull(),
                    F.lit("event_id_null"),
                ),
                F.when(
                    F.col("event_id") >= 1000,
                    F.lit("event_id_out_of_range"),
                ),
                F.when(
                    F.col("category").isNull(),
                    F.lit("category_null"),
                ),
                F.when(
                    F.col("amount") <= 0,
                    F.lit("amount_not_positive"),
                ),
            ),
        )
    )


@dp.materialized_view(
    name="workspace.study_s06.gold_json_daily_metrics",
    comment="Indicateurs quotidiens par categorie",
)
def gold_json_daily_metrics():
    return (
        spark.read.table(
            "workspace.study_s06.silver_json_events"
        )
        .withColumn("event_date", F.to_date("event_time"))
        .groupBy("event_date", "category")
        .agg(
            F.sum("amount").alias("total_amount"),
            F.count("*").alias("event_count"),
        )
    )