#%%
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
#%%
# Config:
endpoints = json.loads(open('endpoints.json', 'r').read())
trips = json.loads(open('trips.json', 'r').read())

# User selection
template = 'sample-1'

#%%
### GENERATE MASTER DATA - REFRESH DAILY
# Get all Routes
all_routes = nextbus_api(endpoints['routes'])

# Generate master dataframes
stops_master = {}
for i,routes in all_routes.iterrows():
    route = str(routes['id'])
    params = {'route': route}
    route_df = nextbus_api(get_api_url(endpoints['route'], params))

    # Generate Stops Master Dataframe    
    stop_df = pd.DataFrame(route_df[0]['stops'])
    stop_df = stop_df[stop_df['showDestinationSelector']]  
    stops_master[route] = stop_df
############

#%%
# Select Stop and Destination from stops_master
user_route = trips[template]['route']
stop_name = trips[template]['stop']
destination_name = trips[template]['destination']

stop = stops_master[user_route]
#direction_id = stop[stop['name'] == stop_name].reset_index()['directions'].iloc[0][0]
stop_id = stop[stop['name'] == stop_name].reset_index()['id'].iloc[0]
destination_id = stop[stop['name'] == destination_name].reset_index()['id'].iloc[0]
direction_id = user_route + '_0_var0'

#%%
# Get Stop prediction
params = { 'route':user_route, 'stop':stop_id, 'destination':destination_id, 'direction':direction_id }
nextbus_api(get_api_url(endpoints['stops'], params))
