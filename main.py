import requests, json, time, pandas as pd

# Functions
def generate_stops_master():
    try:
        # Get all Routes
        all_routes = nextbus_api(endpoints['routes'])

        # Generate master dataframes
        stops_master = {}
        stops_master_df = pd.DataFrame()
        for i, routes in all_routes.iterrows():
            route = str(routes['id'])
            params = {'route': route}
            route_df = nextbus_api(get_api_url(endpoints['route'], params))

            # Generate Stops Master Dataframe    
            stop_df = pd.DataFrame(route_df[0]['stops'])
            stop_df = stop_df[stop_df['showDestinationSelector']]  
            stop_df['route'] = route
            stops_master[route] = stop_df
            stops_master_df = stops_master_df.append(stop_df, ignore_index=True)

        stops_master_df.to_csv('stops_master.csv', index=False)
        return "I'm all refreshed!"
        
    except Exception as e:
        return "Oh-oh! I had the following error while trying to refresh: " + str(e)


def nextbus_api(endpoint, as_dataframe=True):
    # TODO - Input via GET request to my app's server:
    api_key = "1b9dc6b03b9d51407536eea824f32aff"

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
                return pd.DataFrame({"minutes":[row[0]['minutes'] for row in df['values'].tolist()]})
        return response
    except Exception as e:
        return 'API error: '+e

def get_api_url(base_url, params):
    for param in params:
        base_url = base_url.replace('<'+param+'>', params[param])
    return base_url

def voice_response(tag, minutes):
    next_bus = minutes[0]
    due_msg = 'now. ' if next_bus == '0' else 'in ' + next_bus + ' minutes. '
    
    msg = 'Your next bus {} is arriving {}'.format(tag, due_msg)

    if len(minutes) == 2:
        msg += 'Following it is arriving in {}.'.format(minutes[1])
    
    if len(minutes) > 2:
        msg += 'Following it are arriving in '
        msg += ', '.join(minutes[1:]) + ' minutes.'
        pos = msg.rfind(',')
        msg = msg[:pos] + ' and' + msg[pos+1:]
    return msg

def process_input(input_msg):
    if 'update routes' in input_msg:
        return generate_stops_master()
    else:
        stops_master_df = pd.read_csv('stops_master.csv')
        
        # Check for tag in input message
        response = -1
        for tag in tags:
            if tag['tag'] in input_msg:
                response = tag

        # Tag found!
        if response != -1:
            template = response['template']
            tag = response['tag']
            # Select Stop and Destination from stops_master
            user_route = trips[template]['route']
            stop_name = trips[template]['stop']
            destination_name = trips[template]['destination']

            stop = stops_master_df[stops_master_df['route'] == user_route]
            #direction_id = stop[stop['name'] == stop_name].reset_index()['directions'].iloc[0][0]
            stop_id = stop[stop['name'] == stop_name].reset_index()['id'].iloc[0]
            destination_id = stop[stop['name'] == destination_name].reset_index()['id'].iloc[0]
            direction_id = user_route + '_0_var0'

            # Get Stop prediction
            params = { 'route':user_route, 'stop':stop_id, 'destination':destination_id, 'direction':direction_id }
            minutes = nextbus_api(get_api_url(endpoints['stops'], params))
            minutes = minutes['minutes'].tolist()
            try:            
                minutes = nextbus_api(get_api_url(endpoints['stops'], params))
                minutes = minutes['minutes'].astype(str).tolist()
                return voice_response(tag, minutes)
            except Exception:
                return "Sorry, I had trouble fetching the time. Please try again."
        
        # Tag not found :(
        else:
            return "Sorry, I couldn't find a template from your message. Could you repeat that?"

# App Config:
endpoints = json.loads(open('endpoints.json', 'r').read())
trips = json.loads(open('trips.json', 'r').read())
tags = json.loads(open('tags.json', 'r').read())

# User selection
input_msg = "When's the Next bus from home?"
#input_msg = "update routes"

# App Execution:
input_msg = input_msg.lower()
print(process_input(input_msg))
