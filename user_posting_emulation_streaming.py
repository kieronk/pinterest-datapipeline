import requests
import random
import os
import json
import base64
import logging
from sqlalchemy import text
from user_posting_emulation import AWSDBConnector
from datetime import datetime

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the URL from env file 
api_url = os.getenv('api_url')

new_connector = AWSDBConnector()

def send_data_to_kinesis(data_type, suffix):
    random_row = random.randint(0, 1000)
    engine = new_connector.create_db_connector()

    with engine.connect() as connection:
        query_string = text(f"SELECT * FROM {data_type} LIMIT {random_row}, 1")
        selected_row = connection.execute(query_string)

        for row in selected_row:
            result = dict(row._mapping)

            # Convert datetime objects to strings as otherwise they throw and error 
            for key, value in result.items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()  # Convert datetime to a string format

            # Log the data before sending
            logging.info(f'Retrieved row: {result}')
            # Prepare payload 
            payload = json.dumps({
                "StreamName": f"streaming-0ebb0073c95b{suffix}",
                "Data": result, 
                "PartitionKey": str(result.get('id', random.randint(1, 1000)))  # Use 'id' if available, else a random key
            })

            # Log the payload
            logging.info(f"Prepared payload: {payload}")    
            
            headers = {'Content-Type': 'application/json'}
            invoke_url = f"{api_url}/streams/streaming-0ebb0073c95b{suffix}/record"

            # Send request with a timeout to avoid hanging
            try:
                response = requests.put(invoke_url, headers=headers, data=payload, timeout=10)
                response.raise_for_status()  # Automatically raises an HTTPError for bad responses (4xx/5xx)
                logging.info(f"Data successfully sent: {response.text}")                
            except requests.exceptions.Timeout:
                logging.error("Request timed out")
            except requests.exceptions.HTTPError as http_err:
                logging.error(f"HTTP error {http_err} has occurred - status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    send_data_to_kinesis('pinterest_data', '-pin')
    send_data_to_kinesis('geolocation_data', '-geo')
    send_data_to_kinesis('user_data', '-user')
