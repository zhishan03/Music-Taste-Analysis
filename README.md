# Music-Taste-Analysis

### Workflow Journey 
Oct 10: successfully extracted song audio features using Spotipy (python package for Spotify web API). But output contains a good number of NAs because the search
query can't find collab songs' ids (due to the artist name being in the format of 'artist 1 featuring artist 2')

Oct 11: used re.sub function in Python and solved the problem; generated audio features for songs from 2008-2020(yay!)
