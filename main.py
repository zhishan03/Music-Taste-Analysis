import streamlit as st
import numpy as np
import pandas as pd
from Helper import summary_poster, get_cluster, get_hist, get_summary_plot
import base64

stats_df = pd.read_excel("./data/data.xlsx")
# stats_df = load_data("./data/data.xlsx")
color_map_df = pd.read_excel("./data/color_map_df.xlsx")

def main():
    """### gif from local file"""
    file_ = open("imgs/giphy.gif", "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()

    # st.sidebar.markdown(
    #     f'<img src="data:image/gif;base64,{data_url}" alt="cassette gif" width="200" height="80">',
    #     unsafe_allow_html=True,
    # )
    st.markdown("# Music Data Trends 🎶")
    st.markdown('<style>description{font-family: Arial, Helvetica, sans-serif;}</style>', unsafe_allow_html=True)
    st.markdown("<description>Hi There! This project scrapes the Hot 100 songs from 1980 to 2020 on Wikipedia and" + 
                "extracts their audio features from Spotify API. It then performs clustering to find shifts" +
                " in music trends. You can also explore the dataset on your own by using the controls on the" +
                " left-hand panel.</description>", unsafe_allow_html=True) 
    """ --- """

    menu = ["Data Exploration", "Plot"]
    choice = st.sidebar.selectbox("Menu",menu)
    color_dict = dict(zip(color_map_df['cluster'], color_map_df['colors']))

    if(choice == "Plot"):
        with st.expander("Feature Definitions:"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Acousticness**")
                st.markdown("A measure from 0.0 to 1.0 of whether the track is acoustic.")

                st.markdown("**Danceability**")
                st.markdown("Danceability describes how suitable a track is for dancing based on a" +
                            " combination of musical elements including tempo, rhythm stability, beat" +
                            " strength, and overall regularity. A value of 0.0 is least danceable and 1.0" +
                            " is most danceable.")

                st.markdown("**Energy**")
                st.markdown("Energy is a measure from 0.0 to 1.0 and represents a perceptual measure" +
                            " of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy.")
                
            with col2:
                st.markdown("**Instrumenalness**")
                st.markdown("Predicts whether a track contains no vocals. The closer the instrumentalness"+
                            " value is to 1.0, the greater likelihood the track contains no vocal content.")

                st.markdown("**Liveliness**")
                st.markdown("Detects the presence of an audience in the recording. Higher liveness values"+
                            " represent an increased probability that the track was performed live.")
                
                st.markdown("**Speechiness**")
                st.markdown("Speechiness detects the presence of spoken words in a track. The more exclusively"+
                            " speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value.")

        stats_df['cluster'] = stats_df.apply(get_cluster, axis=1)
        st.markdown("### Features distributions")
        feature = st.selectbox('Select a feature', pd.Index(list(['danceability', 'energy'])).join(stats_df.columns[6:10], how='outer'))
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Avg {feature.capitalize()} Value:** {round(stats_df[feature].mean(), 2)}")
    
        with col2:
            st.markdown(f"**Std {feature.capitalize()} Value:** {round(stats_df[feature].std(), 2)}")
        
        #---------------------------------------------------------------#
            # CREATE SUMMARY PLOTS
        #---------------------------------------------------------------#
        fig = get_hist(stats_df, feature)
        st.write(fig)
        fig = get_summary_plot(stats_df, feature, color_dict)
        st.write(fig)

    else:
        sorted_artists = stats_df.groupby('Artist(s)')['Title'].count()\
        .sort_values(ascending=False).index
        select_artist = st.sidebar.selectbox("Select Artist",sorted_artists)
        select_decade = st.sidebar.selectbox("Select Decade",['All', '1980s', '1990s', '2000s', '2010s'])
        song_df = stats_df[stats_df['Artist(s)'] == select_artist]

        all_song_df = song_df[['Title', 'year', 'track_popularity']].copy()
        if (select_decade == '1980s'):
            all_song_df = all_song_df[(1980 <= all_song_df['year']) & (all_song_df['year'] < 1990)]
            song_df = song_df[(1980 <= song_df['year']) & (song_df['year'] < 1990)]
        elif (select_decade == '1990s'):
            all_song_df = all_song_df[(1990 <= all_song_df['year']) & (all_song_df['year'] < 2000)]
            song_df = song_df[(1990 <= song_df['year']) & (song_df['year'] < 2000)]
        elif (select_decade == '2000s'):
            all_song_df = all_song_df[(2000 <= all_song_df['year']) & (all_song_df['year'] < 2010)]
            song_df = song_df[(2000 <= song_df['year']) & (song_df['year'] < 2010)]
        elif (select_decade == '2010s'):
            all_song_df = all_song_df[(2010 <= all_song_df['year']) & (all_song_df['year'] < 2020)]
            song_df = song_df[(2010 <= song_df['year']) & (song_df['year'] < 2020)]
        else:
            all_song_df = all_song_df

        if song_df.empty:
            st.markdown(f"**Hey, it looks like {select_artist} does not have any song on Billboard in {select_decade}**")
        else:
            major_cluster = song_df.groupby('k_means')['Title'].count()\
            .sort_values(ascending = False).index[0]
            
            if (major_cluster == 0):
                song_type = 'Neutral Dance'
            elif (major_cluster == 1):
                song_type = 'Depressing Dance'
            elif (major_cluster == 2):
                song_type = 'Happy Dance'
            else:
                song_type = 'Acoustic Melody'
            
            st.markdown(f"**All of {select_artist}'s Songs from the Dataset:** ")
            st.dataframe(all_song_df)
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Total Songs on Billboard:** {all_song_df.shape[0]}")
                st.markdown(f"**Top Song:** " +\
                        f"{song_df.loc[song_df['track_popularity']==np.max(song_df['track_popularity']),'Title'].values[0]}")
        
            with col2:
                st.markdown(f"**Major Cluster:** {song_type}")

            song_df['cluster'] = song_df.apply(get_cluster, axis=1)
            st.text("")
            #---------------------------------------------------------------#
            # CREATE SUMMARY POSTER
            #---------------------------------------------------------------#
            fig = summary_poster(song_df, color_dict)
            st.write(fig)



    with st.expander("Cluster Definitions:"):
        col1, col2 = st.columns(2)
            
        with col1:
            st.markdown("**Happy Dance**")
            st.markdown("This cluster of songs is very upbeat and conveys strong positivity to its listeners.")
            """
            Examples:
            - "Hey Look Ma, I Made It" by Panic!at the Disco
            - "Adore You" by Harry Styles
            - "All I Want for Christmas Is You" by Mariah Carey
            ---
            """

            st.markdown("**Neutral Dance**")
            st.markdown("This cluster of songs is upbeat but also contains a hint of acoustic with moderate positivity")
            """
            Examples:
            - "Dance Monkey" by Tones and I
            - "Dynamite" by BTS
            - "Señorita" by Shawn Mendes and Camila Cabello
            """
                
        with col2:
            st.markdown("**Depressed Dance**")
            st.markdown("This cluster includes upbeat but negative songs. They convey emotions such as sadness, depression and anger")
            """
            Examples:
            - "Blinding Lights" by The Weeknd 
            - "Circles"	by Post Malone
            - "Thank U, Next" by Ariana Grande
            """
            st.markdown('\n')
            """
            ---
            """

            st.markdown("**Acoustic Melody**")
            st.markdown("This cluster of songs are the most acoustic; That is, the songs are not as noisy and electric as others")
            """
            Examples:
            - "Night Changes" by One Direction
            - "Let It Go" by James Bay
            - "Lost Boy" by Ruth B
            """

main()