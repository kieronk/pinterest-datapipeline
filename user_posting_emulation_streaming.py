import requests
import random
import os
import json
import base64
import logging
from sqlalchemy import text
from user_posting_emulation import AWSDBConnector
from datetime import datetime
from dotenv import load_dotenv

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Get the URL from env file 
api_url = os.getenv('api_url')
if not api_url:
    raise ValueError("API URL not found in environment variables")

new_connector = AWSDBConnector()

def send_data_to_kinesis(table_name, suffix, user_id):
    """
    Retrieves a random row from a specified database table and sends it to an AWS Kinesis stream.

    This function connects to the specified database table (based on `table_name`), retrieves a random row,
    formats it as JSON compatible with Kinesis, and sends it to a Kinesis stream using the REST API.

    Args:
        table_name (str): The name of the database table to retrieve data from.
        suffix (str): A suffix to add to the Kinesis stream name for unique identification.

    Returns:
        None

    Raises:
        requests.exceptions.Timeout: If the request to Kinesis times out.
        requests.exceptions.HTTPError: If there is an HTTP error when sending data.
        requests.exceptions.RequestException: For other types of request-related errors.

    Logs:
        - Retrieved row from the database.
        - Prepared JSON payload for Kinesis.
        - Success or error messages for the data transmission.

    Note:
        - Converts datetime fields in the data to ISO 8601 format strings to avoid errors in JSON serialization.
        - Uses the 'id' field as the Kinesis `PartitionKey` if present; otherwise, generates a random key.
    """
    
    
    random_row = random.randint(0, 1000)
    engine = new_connector.create_db_connector()

    with engine.connect() as connection:
        query_string = text(f"SELECT * FROM {table_name} LIMIT {random_row}, 1")
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
                "StreamName": f"streaming-{user_id}{suffix}",
                "Data": result, 
                "PartitionKey": str(result.get('id', random.randint(1, 3)))  # Use 'id' if available, else a random key
            })

            # Log the payload
            logging.info(f"Prepared payload: {payload}")    
            
            headers = {'Content-Type': 'application/json'}
            invoke_url = f"{api_url}/streams/streaming-{user_id}{suffix}/record"

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
    # note 'user_id' should be replaced with the actual user_id, but that is not included in this public repo
    send_data_to_kinesis('pinterest_data', '-pin', 'user_id') 
    send_data_to_kinesis('geolocation_data', '-geo', 'user_id') 
    send_data_to_kinesis('user_data', '-user', 'user_id') 