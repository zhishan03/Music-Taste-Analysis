import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import random
from matplotlib import rcParams

def get_cluster(row):
    if row['k_means'] == 0:
        val = 'Neutral Dance'
    elif row['k_means'] == 1:
        val = 'Depressing Dance'
    elif row['k_means'] == 2:
        val = 'Happy Dance'
    else:
        val = 'Acoustic Melody'
    return val

def summary_poster(artist_df, color_dict):
    #MAKE SUBPLOTS
    fig = make_subplots(
        rows=3, cols=2, 
        column_widths=[0.8, 0.9],
        row_heights=[0.5, 0.6, 0.6],
        specs=[[{"type": "pie", "colspan": 2}, None],
            [{"type": "bar", "colspan": 2}, None],
            [ {"type":"scatter", "colspan": 2}, None]],
            subplot_titles=('Overall Share of Songs among Clusters', 
                            '#Songs on Billboard Charts across Years', 
                            'Music Timeline by Billboard Song Rank'),
            vertical_spacing=0.1, horizontal_spacing= 0.09)
    #PIE
    #data for pie
    pie_data = artist_df.groupby('cluster')['Title'].count()

    fig.add_trace(go.Pie(labels = pie_data.index,
                            values = pie_data.values,
                            hole = 0.4,
                            legendgroup = 'grp1',
                            showlegend=False),
                row = 1, col = 1)
    fig.update_traces(hoverinfo = 'label+percent',
                        textinfo = 'value+percent',
                        textfont_color = 'white',
                        marker = dict(colors = pie_data.index.map(color_dict),
                                    line=dict(color='white', width=1)),
                        row = 1, col = 1)

    #STACKED BAR
    pivot_artist_df = artist_df.groupby(['year','cluster'])['Title'].count()
    pivot_artist_df = pivot_artist_df.unstack()
    pivot_artist_df.fillna(0, inplace = True)

    #plot params
    labels = pivot_artist_df.columns    

    for i, label_name in enumerate(labels):
        x = pivot_artist_df.iloc[:,i].index
        fig.add_trace(go.Bar(x = x, 
                                y = pivot_artist_df.iloc[:,i],
                                name = label_name,
                                hovertemplate='<b>Year: %{x}</b><br>#Songs: %{y}',
                                marker_color = pd.Series([label_name]*len(x)).map(color_dict),
                                legendgroup = 'grp2',
                                showlegend=True),
                                row = 2, col = 1)
    fig.update_yaxes(title_text = '#Songs',linecolor = 'grey', mirror = True, 
                        title_standoff = 0, gridcolor = 'grey', gridwidth = 0.1,
                        zeroline = False,
                        row = 2, col = 1)
    fig.update_xaxes(linecolor = 'grey', mirror = True, dtick = 5,
                     row = 2, col = 1)

    #SCATTER
    fig.add_trace(go.Scatter(
                x=artist_df['year'],
                y=artist_df['track_popularity'],
                mode = 'markers',
                marker_color = artist_df['cluster'].map(color_dict),
                customdata = artist_df.loc[:,['year','track_popularity','Title']],
                hovertemplate='<b>Year: %{customdata[0]}</b><br>Popularity: %{customdata[1]} <br>Title: %{customdata[2]}',
                legendgroup = 'grp1',
                showlegend=False
                ),
                row = 3, col = 1
                )
    fig.update_traces(marker = dict(symbol = 'triangle-right', size = 12
                                    #,line = dict(color = 'grey', width = 0.5)
                                    ),
                      name = "",
                      row = 3, col =1)
    fig.update_yaxes(title = 'Track Popularity',showgrid=True, 
                    mirror = True, zeroline = False, linecolor = 'grey',
                    title_standoff = 0, gridcolor = 'grey', gridwidth = 0.1,
                    row = 3, col = 1)
    fig.update_xaxes(title="",showgrid=True, mirror = True,
                    linecolor = 'grey', range = [1969,2021],
                    gridcolor = 'grey', gridwidth = 0.1
                    , row = 3, col =1)

    fig.update_layout( # customize font and margins
                        barmode = 'stack',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        #plot_bgcolor = '#0E1117',#'black',
                        font_family= 'Nunito',#"Helvetica",
                        width=800,
                        height=1000,
                        template = 'plotly_dark',
                        legend=dict(title="", orientation = 'v',
                                    font=dict(size = 10),
                                    bordercolor = 'LightGrey',
                                    borderwidth=0.5),
                        margin = dict(l = 40, t = 40, r = 40, b = 40)
                    )
    
    return fig

def get_hist(song_df, feature_name):
    # HISTOGRAM
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=song_df[feature_name],
        marker_color = '#444941',
        opacity=0.75,
        legendgroup = 'grp1',
        showlegend=False),
    )

    fig.update_yaxes(title = 'Count (of songs)',showgrid=True, 
                    mirror = True, zeroline = False, linecolor = 'grey',
                    title_standoff = 0, gridcolor = 'grey', gridwidth = 0.1)

    fig.update_layout(
        plot_bgcolor = '#f5f7f3',
        font_family= 'Nunito',
        bargap=0.2,
        bargroupgap=0.1,
        autosize=False,
        width=680,
        height=300,
        margin = dict(l = 50, t = 20, r = 20, b = 10)
    )
    return fig

def get_summary_plot(song_df, feature_name, color_dict):
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.5, 0.5],
        specs=[[{"type": "box", 'colspan':2}, None],
            [{"type": "scatter", 'colspan':2}, None]],
            subplot_titles=(f'Boxplot of {feature_name.capitalize()} among Clusters', 
                            f'Lineplot of {feature_name.capitalize()} across Years'),
            vertical_spacing=0.12, horizontal_spacing= 0.2)

    # BOX
    music_df_norm_melt = song_df.melt(id_vars = 'cluster',
                            value_vars = feature_name,
                            var_name = 'feature')

    fig.add_trace(go.Box(name='Acoustic Melody', y= music_df_norm_melt[music_df_norm_melt['cluster'] == 'Acoustic Melody'].value,
                        marker_color = '#064635', legendgroup = 'grp1', showlegend=True), row = 1, col = 1)
    fig.add_trace(go.Box(name='Depressing Dance', y= music_df_norm_melt[music_df_norm_melt['cluster'] == 'Depressing Dance'].value,
                        marker_color = '#519259', legendgroup = 'grp1', showlegend=True), row = 1, col = 1)
    fig.add_trace(go.Box(name='Happy Dance', y= music_df_norm_melt[music_df_norm_melt['cluster'] == 'Happy Dance'].value,
                        marker_color = '#F0BB62', legendgroup = 'grp1', showlegend=True), row = 1, col = 1)
    fig.add_trace(go.Box(name='Neutral Dance', y= music_df_norm_melt[music_df_norm_melt['cluster'] == 'Neutral Dance'].value,
                        marker_color = '#AE431E', legendgroup = 'grp1', showlegend=True), row = 1, col = 1)

    # Data Prep
    year_df = song_df.groupby(['year', 'cluster'])[feature_name].mean()
    year_df = year_df.unstack().reset_index()

    labels = year_df.columns[1:5]
    colors = ['#064635', '#519259', '#F0BB62', '#AE431E']

    mode_size = [8, 8, 12, 8]
    line_size = [2, 2, 4, 2]

    # Line Plot
    for i, label in enumerate(labels):
        data_df = year_df.loc[:,['year']]
        data_df[label] = [round(num, 2) for num in year_df[label].to_list()]
        data_df['label'] = label
        fig.add_trace(go.Scatter(
                    name=label,
                    x=year_df['year'],
                    y=year_df[label],
                    mode = 'lines',
                    line = dict(color=colors[i], width=line_size[i]),
                    customdata = data_df,
                    hovertemplate='<b>Year: %{customdata[0]}</b><br>Acoustic Value: %{customdata[1]}<br>Cluster: %{customdata[2]}',
                    legendgroup = 'grp1',
                    showlegend=False),
                    row = 2, col = 1
                    )
            
        fig.add_trace(go.Scatter(
            x=[year_df['year'][0], year_df['year'].iloc[-1]],
            y=[year_df[label][0], year_df[label].iloc[-1]],
            mode='markers',
            marker=dict(color=colors[i], size=mode_size[i]),
            customdata = data_df,
            hovertemplate='<b>Year: %{customdata[0]}</b><br>Acoustic Value: %{customdata[1]}<br>Cluster: %{customdata[2]}',
            showlegend=False),
            row = 2, col = 1
        )

    fig.update_yaxes(title = 'Acousticness',showgrid=True, 
                    mirror = True, zeroline = False, linecolor = 'grey',
                    title_standoff = 0, gridcolor = 'grey', gridwidth = 0.1, row = 2, col = 1)
    fig.update_xaxes(title="",showgrid=True, mirror = True,
                    linecolor = 'grey', range = [1979,2021],
                    gridcolor = 'grey', gridwidth = 0.1, row = 2, col = 1)
    
    fig.update_layout(
        plot_bgcolor = '#f5f7f3',
        barmode = 'stack',
        paper_bgcolor='rgba(0,0,0,0)',
        #plot_bgcolor = '#0E1117',#'black',
        font_family= 'Nunito',#"Helvetica",
        width=800,
        height=770,
        template = 'plotly_dark',
        legend=dict(title="", orientation = 'v',
                    font=dict(size = 10),
                    bordercolor = 'LightGrey',
                    borderwidth=0.5),
        margin = dict(l = 40, t = 30, r = 40, b = 40)
    )
    return fig
