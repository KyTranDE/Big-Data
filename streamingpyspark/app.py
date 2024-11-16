from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext

def main():
    # Khởi tạo SparkSession
    spark = SparkSession.builder \
        .appName("PySparkStreamingExample") \
        .getOrCreate()

    # Khởi tạo StreamingContext với khoảng thời gian batch là 5 giây
    ssc = StreamingContext(spark.sparkContext, 5)

    # Tạo DStream từ socket
    lines = ssc.socketTextStream("localhost", 9999)

    # Thực hiện thao tác đơn giản: đếm số từ
    counts = lines.flatMap(lambda line: line.split(" ")) \
                  .map(lambda word: (word, 1)) \
                  .reduceByKey(lambda a, b: a + b)

    # In kết quả ra console
    counts.pprint()

    # Bắt đầu StreamingContext
    ssc.start()
    ssc.awaitTermination()

if __name__ == "__main__":
    main()
