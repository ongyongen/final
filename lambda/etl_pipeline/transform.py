"""
eeeeeeeee
"""

import re
from datetime import datetime
import constants.dataframe as DATAFRAME
import pandas as pd

def create_template_df():

    """
    Create a template dataframe for the cleaned restaurants data

    Input : None
    Output : dataframe 
    """
    columns = {
        DATAFRAME.RESTAURANT_ID: pd.Series(dtype='int'),
        DATAFRAME.RESTAURANT_NAME: pd.Series(dtype='str'),
        DATAFRAME.COUNTRY: pd.Series(dtype='str'),
        DATAFRAME.CITY: pd.Series(dtype='str'),
        DATAFRAME.USER_RATING_VOTES: pd.Series(dtype='str'),
        DATAFRAME.USER_AGGREGATE_RATING: pd.Series(dtype='str'),
        DATAFRAME.CUISINES: pd.Series(dtype='str'),
        DATAFRAME.COUNTRY_ID: pd.Series(dtype='int'),
        DATAFRAME.RATING_TEXT: pd.Series(dtype='str'),
        DATAFRAME.PHOTO_URL: pd.Series(dtype='str'),
        DATAFRAME.EVENTS: pd.Series(dtype='object'),
        DATAFRAME.EVENT_ID: pd.Series(dtype='str'),
        DATAFRAME.EVENT_TITLE: pd.Series(dtype='str'),
        DATAFRAME.EVENT_START_DATE: pd.Series(dtype='str'),
        DATAFRAME.EVENT_END_DATE: pd.Series(dtype='str'),
        DATAFRAME.EVENT_START_DATE_DT: pd.Series(dtype='str'),
        DATAFRAME.EVENT_END_DATE_DT: pd.Series(dtype='str'),
    }
    
    df = pd.DataFrame(columns)

    return df

def map_country_code_to_country_name(d_countries, country_code):

    """
    Takes in a country code and returns the associated country name
    based on the countries dictionary of { country code : country name }
    If country code does not exist, return NA

    Input : string
    Output : string 
    """
        
    if country_code in d_countries:
        return d_countries[country_code]
    else:
        return DATAFRAME.NA_VALUE
    
def parse_restaurant_records_into_df(d_countries, restaurant_records):

    """
    Collect restaurant record data into the template dataframe for
    cleaned restaurants data

    Input : list
    Output : dataframe 
    """

    df = create_template_df()

    for index, record in enumerate(restaurant_records):        
        restaurant = record["restaurant"]
        
        df.loc[index, DATAFRAME.RESTAURANT_ID] = restaurant["R"]["res_id"]
        df.loc[index, DATAFRAME.RESTAURANT_NAME] = restaurant["name"]
        df.loc[index, DATAFRAME.COUNTRY_ID] = restaurant["location"]["country_id"]
        df.loc[index, DATAFRAME.CITY] = restaurant["location"]["city"]
        df.loc[index, DATAFRAME.USER_RATING_VOTES] = restaurant["user_rating"]["votes"]
        df.loc[index, DATAFRAME.USER_AGGREGATE_RATING] = restaurant["user_rating"]["aggregate_rating"]
        df.loc[index, DATAFRAME.CUISINES] = restaurant["cuisines"]
        df.loc[index, DATAFRAME.RATING_TEXT] = restaurant["user_rating"]["rating_text"]
        df.loc[index, DATAFRAME.COUNTRY] = map_country_code_to_country_name(d_countries, restaurant["location"]["country_id"])

        # Account for the fact that some restaurant records do not contain zomato events field
        if "zomato_events" in record["restaurant"]:
            events = restaurant["zomato_events"]
            df.at[index, DATAFRAME.EVENTS] = events
        else:
            df.at[index, DATAFRAME.EVENTS] = DATAFRAME.EMPTY_EVENTS_CELL
    
    return df


def process_event_data_for_restaurants(df):

    """
    For each restaurant record, extract event data if there's event(s)
    associated with the restaurant in April 2019. If there's no event(s) associated
    with the restaurant in April 2019, return NA for all event fields

    Input : dataframe
    Output : dataframe 
    """

    def extract_event_data_for_each_restaurant(events):

        """
        Helper function to extract event data if there's event(s)
        associated with the restaurant. If there's no event(s) associated
        with the restaurant in April 2019, return NA for all event fields

        Input : list
        Output : list 
        """
            
        if events != DATAFRAME.EMPTY_EVENTS_CELL:
            for record in events:
                event = record["event"]
                event_id = event["event_id"]
                photo_url = event["photos"][0]["photo"]["url"] if len(event["photos"]) > 0 else DATAFRAME.NA_VALUE
                event_title = re.sub(r'[\n\t]', '', event["title"]) 
                event_start_date = event["start_date"]
                event_end_date = event["end_date"]
                event_start_date_dt = datetime.strptime(event_start_date, '%Y-%m-%d')
                event_end_date_dt = datetime.strptime(event_end_date, '%Y-%m-%d')

                ## Check that event occurs within the month of April 2019
                if (
                    event_start_date_dt >= datetime.strptime('2019-04-01', '%Y-%m-%d')
                    and event_end_date_dt <= datetime.strptime('2019-04-30', '%Y-%m-%d')
                ):
                    return [
                        event_id,
                        photo_url,
                        event_title,
                        event_start_date,
                        event_end_date,
                        event_start_date_dt,
                        event_end_date_dt     
                    ]

        ## If restaurant has no events / has events but none of the events occur in April 2019,
        ## return NA for all event fields
        return [ DATAFRAME.NA_VALUE ] * DATAFRAME.NUM_OF_EVENTS_COLUMNS
        
    for index in range(len(df)):
        event_data = extract_event_data_for_each_restaurant(df.loc[index,DATAFRAME.EVENTS])
        [
            event_id, 
            photo_url, 
            event_title, 
            event_start_date, 
            event_end_date, 
            event_start_date_dt, 
            event_end_date_dt 

        ] = event_data

        df.loc[index, DATAFRAME.EVENT_ID] = event_id
        df.loc[index, DATAFRAME.PHOTO_URL] = photo_url
        df.loc[index, DATAFRAME.EVENT_TITLE] = event_title
        df.loc[index, DATAFRAME.EVENT_START_DATE] = event_start_date
        df.loc[index, DATAFRAME.EVENT_END_DATE] = event_end_date
        df.loc[index, DATAFRAME.EVENT_START_DATE_DT] = event_start_date_dt
        df.loc[index, DATAFRAME.EVENT_END_DATE_DT] = event_end_date_dt
    
    return df

def replace_na_cells(df, replacement_str):
    """
    dd
    """
    df = df.fillna(replacement_str)
    return df

def prepare_data_for_q1(df):

    """
    Do final processing for template dataframe and parse it to 
    fit the requirements of q1 (ie only include columns required by q1)
        - Only include columnes required in q1

    Input : dataframe
    Output : dataframe 
    """
    df = replace_na_cells(df, DATAFRAME.NA_VALUE)
    return df[[
        DATAFRAME.RESTAURANT_ID, 
        DATAFRAME.RESTAURANT_NAME, 
        DATAFRAME.COUNTRY, 
        DATAFRAME.CITY, 
        DATAFRAME.USER_RATING_VOTES, 
        DATAFRAME.USER_AGGREGATE_RATING, 
        DATAFRAME.CUISINES
    ]]

def prepare_data_for_q2(df):

    """
    Do final processing for template dataframe and parse it to 
    fit the requirements of q2 
        - Only include columns required in q2
        - Only include restaurant records with events in April 2019

    Note : Based on previous data cleaning steps, restaurants with no events
    in April 2019 would have NA for event title column

    Input : dataframe
    Output : dataframe 
    """

    df = replace_na_cells(df, DATAFRAME.NA_VALUE)
    df = df[df[DATAFRAME.EVENT_TITLE] != DATAFRAME.NA_VALUE]
    
    df = df.reset_index()
    df = df.drop(columns=["index", DATAFRAME.EVENTS])

    df = df[[
        DATAFRAME.EVENT_ID,
        DATAFRAME.RESTAURANT_ID,
        DATAFRAME.RESTAURANT_NAME,
        DATAFRAME.PHOTO_URL,
        DATAFRAME.EVENT_TITLE,
        DATAFRAME.EVENT_START_DATE,
        DATAFRAME.EVENT_END_DATE
    ]]

    return df



