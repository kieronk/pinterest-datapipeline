## pinterest-datapipeline

This project attempts to replicate the Pinterest data pipeline. 

The project brings together several elements: 

#Data: 

Note: The data used in this project is synthetic and as such, contains no real user data. 

There are 3 different datasets used in this project. They replicate the type of data found in pinterest posts: 
- 'Pin' data. This is data about the 'pins' that users have created. Essentially the content of the pin they place on the site. For example: the title of the pin, or the content of the post. 
- 'Geo' data. This is geolocation data about the pin that has been created. Such as the country, latitude and longitude in which the pin was created.
- 'User' data. This is data about the user who posted the pin, such as their user name, and the name associated with the user account. 

The 3 datasets can used in 2 different process with the files contained in this repo: 
- Batch processing and cleaning using Kafka
- Streaming using AWS kinesis 

#Batch Processing

user_posting_emulation.py
This python file connects to an AWS RDS database, selects the data from the database for the 3 different datasets mentioned above, and sends them to Kafka via an API that was created in AWS API Gateway. 

pinterest_dataCleaning
This takes 3 differents datasets from 3 seperate S3 buckets and performs transformations ensuring they are clean and formatted correctly. 

#Streaming

user_posting_emulation_streaming.py 
This python connects to the same AWS RDS database mentioned above, selects the data from the database for the 3 different datasets, and posts them kinesis. This is with the aim of creating a data stream of the data. 

read_data_from_kinesis
This notebook reads data from 3 different kinesis streams, performs transformations to ensure they are clean and fomatted correctly, then writes them to a Delta Table in Spark. 


# Installation instructions

The infrastructure for this project was set up on AWS and Databricks. 

The requirements are: 
- An  EC2 instance running
  - Kafka ver: 2.12-2.8.1
  - IAM MSK authentication package
  - Java version 8 (in order to use Kafka)
- AWS S3
  - With a dedicated bucket to receive the batch data sent via Kafka
s-  

AWS M
3 kafka topics for each of the 3 datasets running on the EC2 instance. In the code they are called 0ebb0073c95b.pin, 0ebb0073c95b.geo, 0ebb0073c95b.user 

An S3 bucket set up with the Confluent.io Amazon S3 Connector in order that the S3 bucket can connect with Kafka 

An MSK cluster 

An API created via AWS APIT gateway that can send data to the 

Process: 
- Set up a EC2 instance and install Kafka ver: 2.12-2.8.1 and the IAM MSK authentication package
- Ensure you have the the necessary permissions to authenticate to the MSK cluster and configure your Kafka client to use AWS IAM authentication to the cluster
- Create a Kafka topic for each of the datasets you will batch process (i.e. 3 in total). In this repo the topics had a unique idenfier followed by .pin, .geo or .user
- Create a S3 bucket, with an IAM role that allows you to write to this bucket and a VPC Endpoint to S3
- On the EC2 client, download the Confluent.io Amazon S3 Connector and copy it to the S3 bucket 
- Create a custom plugin and connector in the MSK Connect console
- Create an API (using API Gateway) and create a Kafka REST proxy integration
- Set up the Kafka REST proxy on the EC@ client
  -  install the Confluent package for the Kafka REST Proxy on your EC2 client machine.
  -  Allow the REST proxy to perform IAM authentication to the MSK cluster
  -  Ensure the REST proxy on the EC2 client machine is started when you want to start sending dtaa
-  Modify user_posting_emulation.py with the specific details you have used to send data to your Kafka topics. The data will be sent to the S3 bucket across the 3 different topics
- Upload DAG to AWS MWAA environment
-   In this step, you will need to connect Databricks  create an API token in Databricks to connect to your AWS account, set up the MWAA-Databricks connection and create a requirements.txt file. 


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
