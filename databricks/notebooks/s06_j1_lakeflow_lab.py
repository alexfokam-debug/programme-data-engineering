from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.table(
    name="bronze_events",
    comment="Evenements synthetiques bruts du lab S06"
)
def bronze_events():
    return spark.readStream.table("s06_synthetic_events_source")


@dp.materialized_view(
    name="silver_events",
    comment="Evenements nettoyes et dedupliques du lab S06"
)
@dp.expect_or_drop("valid_event_id", "event_id IS NOT NULL")
@dp.expect_or_drop("valid_category", "category IS NOT NULL")
@dp.expect_or_drop("positive_amount", "amount > 0")
def silver_events():
    return (
        spark.read.table("bronze_events")
        .withColumn(
            "event_time",
            F.to_timestamp("event_time")
        )
        .dropDuplicates(["event_id"])
    )


@dp.table(
    name="quarantine_events",
    comment="Evenements invalides conserves pour investigation"
)
def quarantine_events():
    return (
        spark.readStream.table("bronze_events")
        .filter(
            "event_id IS NULL "
            "OR category IS NULL "
            "OR amount <= 0"
        )
        .withColumn(
            "quarantine_reason",
            F.concat_ws(
                ", ",
                F.when(
                    F.col("event_id").isNull(),
                    F.lit("event_id_null")
                ),
                F.when(
                    F.col("category").isNull(),
                    F.lit("category_null")
                ),
                F.when(
                    F.col("amount") <= 0,
                    F.lit("amount_not_positive")
                )
            )
        )
    )


@dp.materialized_view(
    name="gold_daily_sales",
    comment="Ventes agregees par date et categorie"
)
def gold_daily_sales():
    return (
        spark.read.table("silver_events")
        .withColumn(
            "event_date",
            F.to_date("event_time")
        )
        .groupBy("event_date", "category")
        .agg(
            F.sum("amount").alias("total_amount"),
            F.count("*").alias("event_count")
        )
    )