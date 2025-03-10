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

# Load environment variables from .env file
load_dotenv()

class AWSDBConnector:

    """
    A class used to establish a connection to an AWS-hosted MySQL database using SQLAlchemy.

    This class loads necessary database credentials from environment variables and provides a method 
    to create an SQLAlchemy engine for database connectivity. 

    Attributes:
        db_host (str): The hostname of the database server.
        db_user (str): The username to connect to the database.
        db_password (str): The password for the specified database user.
        db_database (str): The name of the target database.
        db_port (str): The port number on which the database server is listening.

    Methods:
        create_db_connector():
            Creates and returns an SQLAlchemy engine using the loaded database credentials.
    """

    def __init__(self):
        
        try:

            # Access the environment variables
            self.db_prefix = os.getenv('DB_PREFIX')
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
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise
 
    
    def create_db_connector(self):
        engine = sqlalchemy.create_engine(f"{self.db_prefix}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_database}?charset=utf8mb4")
        return engine

# get the api_url
api_url = os.getenv('api_url')
if not api_url:
    raise ValueError("API URL not found in environment variables")


# Create a new instance of the AWSDBConnector class
new_connector = AWSDBConnector()

def send_data_to_kafka(table_name, data_label, user_id):
    """
    Retrieves a random row from a specified database table and sends it to a Kafka topic using the Kafka REST Proxy.

    This function connects to a database table (specified by `table_name`), retrieves a random row,
    formats it as a JSON payload compatible with Kafka, and sends it to a Kafka topic named 
    using the specified `data_label`.

    Args:
        table_name (str): The name of the database table to retrieve data from.
        data_label (str): A label to uniquely identify the Kafka topic.
        user_id (str): The id of the user on AWS

    Returns:
        None

    Raises:
        requests.exceptions.RequestException: If there's an error in sending the data to Kafka REST Proxy.
    """

    random_row = random.randint(0, 11000)
    engine = new_connector.create_db_connector() 

    with engine.connect() as connection:
        
        query_string = text(f"SELECT * FROM {table_name}")
        #query_string = text(f"SELECT * FROM {table_name} LIMIT {random_row}, 1")
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
            }

            # Make the POST request to the Kafka REST Proxy
            response = requests.post(f"{api_url}/topics/{user_id}{data_label}", headers=headers, data=payload)

            # Print the status and response from Kafka REST Proxy
            print(f"Sent data, {response.status_code}, {response.text}")


if __name__ == "__main__":
    # note 'user_id' should be replaced with the actual user_id, but that is not included in this public repo
    send_data_to_kafka('pinterest_data', '.pin', 'user_id')  
    send_data_to_kafka('geolocation_data', '.geo', 'user_id') 
    send_data_to_kafka('user_data', '.user', 'user_id') 


