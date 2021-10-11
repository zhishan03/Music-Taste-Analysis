from datetime import time
import pandas as pd # library for data analysis
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

cid = '41104157892647cc8be8b62bc85d470d'
secret = '71bf433f7d804596b05ddf21d43f2e52'
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(auth='TOKEN')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp = spotipy.Spotify(auth='TOKEN')

class spotify_track:
    '''Class to fetch track info from spotify web api based on title, artist and market'''
    def __init__(self, track_title, artist_name, pick=0, search_limit=5, search_market='US', search_type="track"):
        '''initializes and gets track id from spotipy'''
        self.pick = pick
        self.search_limit = search_limit
        self.search_market = search_market
        self.search_type = search_type

        self.search_title = track_title
        self.search_artist = artist_name

    def get_track_details(self):
        output = sp.search(q='artist:' + self.search_artist + ' track:' + self.search_title, type='track')
        try:
            # Get track details from output and store in dict
            track_details_dict = {
                'search_title': re.sub('%20', ' ', self.search_title),
                'search_artist': re.sub('%20', ' ', self.search_artist),
                'artist': output['tracks']['items'][self.pick]['artists'][0]['name'],
                'artist_uri': output['tracks']['items'][self.pick]['artists'][0]['uri'],
                'album': output['tracks']['items'][self.pick]['album']['name'],
                'album_uri': output['tracks']['items'][self.pick]['album']['uri'],
                'track': output['tracks']['items'][self.pick]['name'],
                'track_uri': output['tracks']['items'][self.pick]['id'],
                'track_popularity': output['tracks']['items'][self.pick]['popularity'],
                'duration_ms': output['tracks']['items'][self.pick]['duration_ms']
            }
        except:
            #if no search entry return NAs
            track_details_dict = {
                'search_title' : re.sub('%20', ' ',self.search_title),
                'search_artist' : re.sub('%20', ' ',self.search_artist),
                'artist' : 'NA',
                'artist_uri' : 'NA',
                'album' : 'NA',
                'album_uri' : 'NA',
                'track' : 'NA',
                'track_uri' : 'NA',
                'track_popularity' : 'NA',
                'duration_ms' : 'NA'
            }

        # add track uri to get audio features
        self.track_uri = track_details_dict['track_uri']

        return track_details_dict

    def get_audio_features(self):
        '''return dict consisting of track details and audio features'''
        track_details_dict = self.get_track_details()
        print(self.track_uri)
        #If the track is not available in spotify search returns NAs
        if self.track_uri == 'NA':
            features_req = {
                'danceability': 'NA',
                'energy': 'NA',
                'key': 'NA',
                'loudness': 'NA',
                'mode': 'NA',
                'speechiness': 'NA',
                'acousticness': 'NA',
                'instrumentalness': 'NA',
                'liveness': 'NA',
                'valence': 'NA',
                'tempo': 'NA',
                'type': 'NA',
                'id': 'NA',
                'uri': 'NA',
                'track_href': 'NA',
                'analysis_url': 'NA',
                'duration_ms': 'NA',
                'time_signature': 'NA'
            }

        else:
            try:
                features_req = sp.audio_features(self.track_uri)
                features_req = features_req[0]
            except:
                features_req = {
                'danceability': 'NA',
                'energy': 'NA',
                'key': 'NA',
                'loudness': 'NA',
                'mode': 'NA',
                'speechiness': 'NA',
                'acousticness': 'NA',
                'instrumentalness': 'NA',
                'liveness': 'NA',
                'valence': 'NA',
                'tempo': 'NA',
                'type': 'NA',
                'id': 'NA',
                'uri': 'NA',
                'track_href': 'NA',
                'analysis_url': 'NA',
                'duration_ms': 'NA',
                'time_signature': 'NA'
                }

        #Add audio feature details to the dict
        track_details_dict.update(features_req.items())

        return track_details_dict

def get_all_audio_features(all_tracks_df):
    # MAIN LOOP TO RUN ALONG THE TRACK LIST DF AND FETCH AUDIO FEATURES INTO DATAFRAME
    iter = 0
    t = spotify_track('Dynamite', 'BTS', 0).get_audio_features()
    collect_key = list(t.keys())
    collect_list = []

    for track, artist, year in all_tracks_df.loc[:, ['Title', 'Artist(s)', 'year']].itertuples(index=False):
        collect_dict = spotify_track(track, artist, 0).get_audio_features()
        collect_list.append(list(collect_dict.values()))

        na_rows = sum([x[2] == 'NA' for x in collect_list])  # /25

        print(f"{year}, {track} by {artist}, {iter} - No. of NA rows {na_rows}")
        iter += 1
        time.sleep(0.5)

    collect_df = pd.DataFrame(collect_list, columns=collect_key)

    # combine with the track list df from wiki scraper (all_tracks_df)
    comb_df = pd.merge(all_tracks_df, collect_df, how='left', left_index=True, right_index=True)

    # Write to file
    comb_df.to_csv('combined_track_audio_detials.csv')

    return comb_df