import os
import pandas as pd # library for data analysis
import requests # library to handle requests
from bs4 import BeautifulSoup # library to parse HTML documents
import time

# get track details
def get_track_details(target_url, target_year):
    response = requests.get(target_url + f"{target_year}")
    print(response.status_code)

    # parse data from the html into a beautifulsoup object
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': "wikitable"})

    df = pd.read_html(str(table))
    # convert list to dataframe
    df = pd.DataFrame(df[0])
    return df

def get_and_combine_track_details(target_url, min_year, max_year):
    """Get combined dataframe of track details from given wikipedia link \
        for the specified year-range. (Currently built for \
            Billboard-Year-End-Hot-100-Singles and for years 1970 to 2020)
    Args:
        target_url (string): Web link of the target url to scrape details from
        min_year (int): Start year
        max_year (int): End year (excluded, minimum range: 2 years)
    Returns:
        Pandas DataFrame: Combined dataframe for all the tracks in the specified year\
             range, consisting of track details : rank, title, artist
    """
    for year in range(min_year, max_year + 1):
        # get the response in the form of html
        os.system('cls')
        if year == min_year:
            complete_track_details = get_track_details(target_url, year)
        else:
            complete_track_details = complete_track_details.append(get_track_details(target_url, year),
                                                                   ignore_index = True)
        print(f"Latest year data scraped: {year}")
        time.sleep(1)
    return complete_track_details

url = "https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_"
get_and_combine_track_details(url,2018, 2020)