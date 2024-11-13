# pinterest-datapipeline

This project attempts to replicate the Pinterest data pipeline. 

The project brings together several elements: 

## Data: 

Note: The data used in this project is synthetic and as such, contains no real user data. 

There are 3 different datasets used in this project. They replicate the type of data found in Pinterest posts: 
- 'Pin' data. This is data about the 'Pins' that users have created. Essentially the content of the Pin they place on the site. For example: the title of the Pin, or the content of the Pin. 
- 'Geo' data. This is geolocation data about the Pin that has been created. Such as the country, latitude and longitude in which the pin was created.
- 'User' data. This is data about the user who posted the Pin, such as their user name, and the name associated with the user account. 

The 3 datasets can used in 2 different process with the files contained in this repo: 
- Batch processing and data transformation using Kafka
- Streaming using AWS kinesis 

## File structure 

### Batch Processing

user_posting_emulation.py
This python file connects to an AWS RDS database, selects the data from the database for the 3 different datasets mentioned above, and sends them to Kafka via an API that was created in AWS API Gateway. The data is stored in topics in an S3 bucket. 

pinterest_dataCleaning_DAG_job
This takes the 3 differents datasets stored in the S3 bucket and performs transformations ensuring they are clean and formatted correctly. 

dag_job_clean.py 
This python file triggers a DAG on AWS MWAA to run pinterest_dataCleaning_DAG_job notebook daily.

### Streaming

user_posting_emulation_streaming.py 
This python file connects to the same AWS RDS database mentioned above, selects the data from the database for the 3 different datasets, and posts them kinesis.  

read_data_from_kinesis
This notebook reads data from 3 different kinesis streams, performs transformations to ensure they are clean and fomatted correctly, then writes them to a Delta Table in Spark. 


## Installation instructions

The infrastructure for this project was set up on AWS and Databricks. 

The elements are: 
- An  EC2 instance running
  - Kafka ver: 2.12-2.8.1
  - IAM MSK authentication package
  - Java version 8 (in order to use Kafka)
- AWS S3
  - With a dedicated bucket to receive the batch data sent via Kafka and store it in Kafka topics.  
  - With the Confluent.io Amazon S3 Connector downloaded to connect to Kafka 
- AWS MSK
  - With a custom plugin and connector   
- AWS MWAA
  - With a DAG to run the databricks notebook which gathers the latest data    
- AWS API Gateway
  - To create the Kafka REST proxy integration
- AWS Kinesis Data Streams
-   With three data streams, one for each Pinterest table

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

## Usage instructions

### Setup Process: 
- Set up a EC2 instance and install Kafka ver: 2.12-2.8.1 and the IAM MSK authentication package
- Ensure you have the the necessary permissions to authenticate to the MSK cluster and configure your Kafka client to use AWS IAM authentication to the cluster
- Create a Kafka topic for each of the datasets you will batch process (i.e. 3 in total). In user_posting_emulation.py the topics had a unique idenfier followed by .pin, .geo or .user
- Create a S3 bucket, with an IAM role that allows you to write to the bucket and a VPC Endpoint to S3
- On the EC2 client, download the Confluent.io Amazon S3 Connector and copy it to the S3 bucket 
- Create a custom plugin and connector in the MSK Connect console
- Create an API (using API Gateway) and create a Kafka REST proxy integration
- Set up the Kafka REST proxy on the EC2 client
  -  Install the Confluent package for the Kafka REST Proxy on your EC2 client machine
  -  Allow the REST proxy to perform IAM authentication to the MSK cluster
  -  Ensure the REST proxy on the EC2 client machine is started when you want to start sending dtaa
-  Modify user_posting_emulation.py with the specific details you have used to send data to your Kafka topics. The data will be sent to the S3 bucket across the 3 different topics
- Upload DAG to AWS MWAA environment
  - Here you will need to connect Databricks to the AWS account, including creating  an API token in Databricks, set up the MWAA-Databricks connection and create a requirements.txt file. 

Extra process steps for datastreaming with Kinesis:  
- Using Kinesis Data Streams create three data streams, one for each Pinterest table. In user_posting_emulation_streaming.py these have this format: streaming-<unique_id>-pin
- Configure the previously created REST API to allow it to invoke Kinesis actions
  - The API should be able to:
    - List streams in Kinesis
    - Create, describe and delete streams in Kinesis
    - Add records to streams in Kinesis
- Use user_posting_emulation_streaming.py to send data to Kinesis

## Note 
This project was created for personal educational purposes, based on coursework from [AI-Core](https://www.theaicore.com/). It is not intended for production use.
