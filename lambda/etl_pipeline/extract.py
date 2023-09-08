"""
This file is for blah blah blah
"""
import requests
import constants.dataframe as DATAFRAME
import constants.urls as URLS


def extract_restaurants_data():
    """
    ddd
    """
    url = URLS.RESTAURANTS_DATA_URL
    response = requests.get(url, timeout=20)
    return response.json()


def extract_restaurant_records_from_parsed_json(data):
    """
    Extract out the restaurant data and collect them into a single list
    for ease of further processing

    Input : list
    Output : list
    """

    restaurant_records = []
    for record in data:
        total_records = record['results_shown']
        if total_records > 0:
            restaurant_records += record['restaurants']
    return restaurant_records


def extract_countries_data(countries):
    """
    Creates a dictionary to store key-value of pairs of
    { country code : country name } mapping

    Input : dataframe
    Output : dictionary
    """

    d_countries = {}
    for index in range(len(countries)):
        country_name = countries.loc[index, DATAFRAME.COUNTRY]
        country_code = countries.loc[index, DATAFRAME.COUNTRY_CODE]
        d_countries[country_code] = country_name
    return d_countries
