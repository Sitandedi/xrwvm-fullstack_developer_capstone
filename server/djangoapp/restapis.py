# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")

# Add code for get requests to back end
def get_request(endpoint, **kwargs):
    params = ""
    if(kwargs):
        for key,value in kwargs.items():
            params=params+key+"="+value+"&"

    request_url = backend_url+endpoint+"?"+params

    print("GET from {} ".format(request_url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except:
        # If any error occurs
        print("Network exception occurred")


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url+"analyze/"+text
    # Add code for retrieving sentiments
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")

# Add code for posting review
def post_review(data_dict):
    """
    Posts a review to the backend endpoint /insert_review
    and returns the response JSON (or None on failure).
    """
    request_url = backend_url + "/insert_review"

    try:
        response = requests.post(request_url, json=data_dict, timeout=10)

        # Log status
        logger.info(f"Backend /insert_review response: {response.status_code}")

        # Try to parse the response
        try:
            response_json = response.json()
        except ValueError:
            logger.error("Backend did not return valid JSON.")
            return None

        # Check if backend confirmed success
        if response.status_code in [200, 201]:
            return response_json
        else:
            return None

    except requests.exceptions.RequestException as e:
        return None
