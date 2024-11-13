import requests
from time import sleep
import random
from multiprocessing import Process
import boto3
import os
import json
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

random.seed(100) # ensures that the random numbers are always the same when I run this script 

class AWSDBConnector:

    def __init__(self):
        
        try:
            # Load environment variables from .env file
            load_dotenv()

            # Access the environment variables
            self.db_host = os.getenv('DB_HOST')
            self.db_user = os.getenv('DB_USER')
            self.db_password = os.getenv('DB_PASSWORD')
            self.db_database = os.getenv('DB_DATABASE')
            self.db_port = os.getenv('DB_PORT') 

            # Check if any of the required variables are missing
            if not all([self.db_host, self.db_user, self.db_password, self.db_database, self.db_port]):
                raise ValueError("Missing one or more required database environment variables")

        except ValueError as ve:
            print(f"Error loading environment variables: {ve}")
            # You can also raise the exception again if you want to stop execution
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Handle any other exceptions 
            raise
 
    
    def create_db_connector(self):
        engine = sqlalchemy.create_engine(f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_database}?charset=utf8mb4")
        return engine

# get the api_url
api_url = os.getenv('api_url')

# Create a new instance of the AWSDBConnector class
new_connector = AWSDBConnector()

# attempting to make this a function 

def send_data_to_kafka(data_type, data_label):
    
    random_row = random.randint(0, 11000)
    engine = new_connector.create_db_connector() 
    #data_type = data_type

    with engine.connect() as connection:
        
        query_string = text(f"SELECT * FROM {data_type}")
        #query_string = text(f"SELECT * FROM {data_type} LIMIT {random_row}, 1")
        selected_row = connection.execute(query_string)

        for row in selected_row:
            result = dict(row._mapping)
            
            # Format for Kafka REST Proxy
            payload = json.dumps({
                "records": [
                    {
                        "value": result  # the actual row data as the "value" of the message
                    }
                ]
            }, default=str)

            # Headers for Kafka REST Proxy
            headers = {
                'Content-Type': 'application/vnd.kafka.json.v2+json',
                #'Accept': 'application/vnd.kafka.v2+json'
            }

            # Make the POST request to the Kafka REST Proxy
            response = requests.post(f"{api_url}/topics/0ebb0073c95b{data_label}", headers=headers, data=payload)

            # response = requests.post(f"{api_url}/{topic_url}", headers=headers, data=payload)
            # and have the topic_url
            # topics/0ebb0073c95b.pin
            # topics/0ebb0073c95b.geo
            # topics/0ebb0073c95b.user
            # that would be passed in when I called it? 

            # Print the status and response from Kafka REST Proxy
            print(f"Sent data, {response.status_code}, {response.text}")


if __name__ == "__main__":
    send_data_to_kafka('pinterest_data', '.pin') #and topic url
    send_data_to_kafka('geolocation_data', '.geo') #and topic url
    send_data_to_kafka('user_data', '.user') #and topic url


