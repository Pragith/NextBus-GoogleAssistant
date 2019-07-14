import requests, json, time, pandas as pd

# Functions
def nextbus_api(endpoint, as_dataframe=True):
    # TODO - Input via GET request to my app's server:
    api_key = "2cbf03911d82034a2072e39a60ff5cf5"

    # Payload
    headers = {"Referer": "http://www.nextbus.com/"}
    params = {"key": api_key, "timestamp": int(time.time())}

    # Request
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response = json.loads(response.text)
        if as_dataframe:
            try:
                df = pd.DataFrame(response)
            except ValueError:
                df = pd.DataFrame.from_dict(response, orient='index')
            if len(df) == 1:
                response = response[0]
                if 'values' in response:
                    return pd.DataFrame.from_dict(response['values'])
                else:
                    return pd.DataFrame.from_dict(response)
            else:
                return df
        return response
    except requests.exceptions.RequestException as err:
        return { 'error': str(err) }

def get_api_url(base_url, params):
    for param in params:
        base_url = base_url.replace('<'+param+'>', params[param])
    print(base_url)
    return base_url