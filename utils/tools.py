import requests
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv
import os
from utils.logger import logger

class GetInfo(BaseModel):
    name: str = Field(..., title="Name", description="Name of the travel destination or landmark")

def get_headers():
    load_dotenv(find_dotenv())  # read local .env file
    return {
        'accept': 'application/json',
        'Authorization': 'Bearer ' +  os.getenv('TRIPADVISOR_API_TOKEN')
    }

class TravelInfo:
    def __init__(self, api_token: str) -> None:
        self.api_token = api_token

    def get_destination_info(self, name: str) -> dict:
        url = "https://api.tripadvisor.com/locations/search"
        headers = get_headers()
        params = {
            'query': name,
            'key': self.api_token,
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if 'data' in data and data['data']:
                return data['data'][0]  # Assuming first result is the best match
            else:
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching destination info: {e}")
            return None

# Example usage:
if __name__ == "__main__":
    api_token = os.getenv('TRIPADVISOR_API_TOKEN')
    if api_token:
        info_fetcher = TravelInfo(api_token)
        destination_name = "Paris"  # Example destination name
        destination_info = info_fetcher.get_destination_info(destination_name)
        if destination_info:
            print(f"Destination Name: {destination_info['name']}")
            print(f"Location: {destination_info['location']}")
            print(f"Description: {destination_info['description']}")
            # Add more fields as per the API response structure
        else:
            print(f"Destination '{destination_name}' not found or API error.")
    else:
        print("TripAdvisor API token not found.")
