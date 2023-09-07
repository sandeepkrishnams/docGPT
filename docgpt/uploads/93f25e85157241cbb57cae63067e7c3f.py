import requests
import json
from solr_api import SOLR_CORE, SOLR_TIME_OUT


def create_core(name, configset='_default'):
    payload = {
        "create": {
            "name": name,
            "configSet": configset
        }
    }

    json_payload = json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(
            SOLR_CORE, data=json_payload, headers=headers, timeout=SOLR_TIME_OUT)
    except requests.exceptions.ConnectTimeout:
        print("Timeout error: The connection to the server timed out.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    else:
        if response.status_code == 200:
            print("Core created successfully:")
            response_data = response.json()
            print("Core name:", response_data["core"])
        elif response.status_code == 500:
            print("Error: ", json.loads(response.text)['error']['msg'])
        else:
            print("Failed to create core. Status code:", response.status_code)
            print("Response content:", response.text)


create_core('sandeep')
