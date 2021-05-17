import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_extract, to_timestamp
from pyspark.sql.types import DoubleType

def main(argv):
    input_uri = argv[0]
    equipment_sensors_uri = argv[1]
    equipment_uri = argv[2]
    output_project_dataset_table = argv[3]
    staging_bucket = argv[4]

    spark = SparkSession.builder \
    .master("yarn") \
    .appName("parse-sensor-logs") \
    .getOrCreate()
    spark.conf.set("temporaryGcsBucket", staging_bucket)
    sc = spark.sparkContext
    sc.setLogLevel("WARN")

    timestamp_group = r"([0-9]{1,4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})"
    level_group = r"([A-Z]+)"
    sensor_group = r"sensor\[(\d+)\]"
    temperature_group = r"temperature\s(-?\d+.\d+)"
    vibration_group = r"vibration\s(-?\d+.\d+)"

    logs = spark.read.text(input_uri)
    parsed_logs = logs.select(
        regexp_extract('value', timestamp_group, 1).alias("event_timestamp"),
        regexp_extract('value', level_group, 1).alias("level"),
        regexp_extract('value', sensor_group, 1).alias("sensor_id"),
        regexp_extract('value', temperature_group, 1).alias("temperature"),
        regexp_extract('value', vibration_group, 1).alias("vibration")
    )

    parsed_logs \
        .withColumn("event_timestamp", to_timestamp("event_timestamp")) \
        .withColumn("temperature", parsed_logs.temperature.cast(DoubleType())) \
        .withColumn("vibration", parsed_logs.vibration.cast(DoubleType())) \
        .createTempView("cleaned_logs")

    spark.read.load(
        equipment_sensors_uri, 
        format="csv", sep=";", 
        inferSchema="true", 
        header="true") \
        .createTempView("equipment_sensors")

    spark.read.option("multiline", "true") \
        .json(equipment_uri) \
        .createTempView("equipment")

    equipment_log_query = r"""
    SELECT 
        eq.*,
        eq_s.sensor_id,
        logs.*
    FROM
        equipment eq
        JOIN
        equipment_sensors eq_s
            USING (equipment_id)
        JOIN
        cleaned_logs logs
            USING(sensor_id)    
    """
    equipment_log = spark.sql(equipment_log_query)

    equipment_log.write.format("bigquery") \
        .mode("append") \
        .option("partitionType", "DAY") \
        .option("partitionField", "event_timestamp") \
        .save(output_project_dataset_table)

if __name__ == "__main__":
    main(sys.argv[1:])