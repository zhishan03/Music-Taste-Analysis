import requests
from dotenv import load_dotenv
import os


def get_access_token():
    '''Get Spotify access token'''

    load_dotenv(dotenv_path='Music/.env')

    client_id = os.getenv('clientid_spotify')
    client_secret = os.getenv('secret_spotify')
    AUTH_URL = 'https://accounts.spotify.com/api/token'
    print(client_id)
    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })

    # convert the response to JSON
    auth_response_data = auth_response.json()
    print(auth_response.status_code)
    # save the access token
    access_token = auth_response_data['access_token']

    headers = {
        'Authorization': f"Bearer {access_token}"
    }

    return headers