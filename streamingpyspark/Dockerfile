# Sử dụng hình ảnh cơ bản của Python với Java (cần cho Spark)
FROM openjdk:8-jdk-alpine

# Cài đặt Python và các gói cần thiết
RUN apk add --no-cache python3 py3-pip

# Cài đặt PySpark
RUN pip3 install pyspark

# Sao chép mã nguồn vào container
COPY app.py /app/app.py

# Đặt thư mục làm việc
WORKDIR /app

# Expose cổng cho Spark UI (4040)
EXPOSE 4040

# Chạy ứng dụng
CMD ["python3", "app.py"]
