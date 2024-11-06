## pinterest-datapipeline

This project attempts to replicate the Pinterest data pipeline. 

The project brings together several elements: 

#Data: 

Note: The data used in this project is synthetic and as such, contains no real user data. 

There are 3 different datasets used in this project. They replicate the type of data found in pinterest posts: 
- 'Pin' data. This is data about the 'pins' that users have created. Essentially the content of the pin they place on the site. For example: the title of the pin, content of the post and so on. 
- 'Geo' data. This is geolocation data about the pin that has been created. Such as the country in which the pin and it's latitude and longitude.
- 'User' data. This is data about the user who posted the pin, such as their user name, and the name associated with the user account. 

The 3 datasets used in 2 different process: 
- Batch processing and cleaning using Kafka
- Streaming using AWS kinesis 

#Batch Processing

user_posting_emulation.py
This python file connects to an AWS RDS database, selects the data from the database for the 3 different datasets mentioned above, and sends them to Kafka via an API that was created in AWS API Gateway. 

pinterest_dataCleaning
This takes 3 differents datasets from 3 seperate S3 buckets, performs transformations ensuring they are clean and formatted correctly. 

#Streaming
user_posting_emulation_streaming.py 
This python connects to the same AWS RDS database mentioned above, selects the data from the database for the 3 different datasets, and posts them kinesis. This is with the aim of creating a data stream of the data. 

read_data_from_kinesis
This notebook reads data from 3 different kinesis streams, performs transformations to ensure they are clean and fomatted correctly, then writes them to a Delta Table in Spark. 


# Installation instructions

An EC2 instance running 
- Kafka ver: 2.12-2.8.1
- IAM MSK authentication package
- Java version 8 (in order to use Kafka) 

3 kafka topics for each of the 3 datasets running on the EC2 instance. In the code they are called 0ebb0073c95b.pin, 0ebb0073c95b.geo, 0ebb0073c95b.user 

An S3 bucket set up with the Confluent.io Amazon S3 Connector in order that the S3 bucket can connect with Kafka 

An MSK cluster 

An API created via AWS APIT gateway that can send data to the 

The project requires these packages: 
pyspark.sql 
urllib
functools
requests
random
os
json
base64
logging
sqlalchemy
datetime 
requests
time 
multiprocessing 
boto3
dotenv


# Usage instructions


File structure of the project

#License information
