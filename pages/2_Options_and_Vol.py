import requests
import pandas as pd
import datetime
import json
import plotly.express as px
import streamlit as st
import numpy as np
from threading import Thread
import plotly.graph_objects as go
from requests_cache import CachedSession
from datetime import timedelta
from pathlib import Path
import validators
import base64
import ccxt
import asyncio
import nest_asyncio

def add_logo(logo_url: str):
    """Add a logo (from logo_url) on the top of the navigation page of a multipage app.
    Taken from https://discuss.streamlit.io/t/put-logo-and-title-above-on-top-of-page-navigation-in-sidebar-of-multipage-app/28213/6

    The url can either be a url to the image, or a local path to the image.

    Args:
        logo_url (str): URL/local path of the logo
    """

    if validators.url(logo_url) is True:
        logo = f"url({logo_url})"
    else:
        logo = f"url(data:image/png;base64,{base64.b64encode(Path(logo_url).read_bytes()).decode()})"

    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: {logo};
                background-repeat: no-repeat;
                padding-top: 70px;
                background-position: center 50px;
                background-size: contain;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

add_logo("https://forteus-media-research.s3.eu-west-1.amazonaws.com/public/images/Final+Logo+Forteus+by+Numeus+light.png")

st.title('Options and Vol')

# Calculate the last year's market cap and date
current_date = datetime.datetime.now().date()
last_year_date = datetime.date(current_date.year - 1, 12, 31)
last_month_date = datetime.date(current_date.year, current_date.month - 1, 30)
last_quarter_date = datetime.date(current_date.year, ((current_date.month - 1) // 3) * 3 + 1, 1) - datetime.timedelta(days=1)
last_quarter_start_date = last_quarter_date - datetime.timedelta(days=89)
weekday = current_date.weekday()
days_to_subtract = (weekday - 4) % 7  # Calculate the number of days to subtract to reach the previous Friday
last_week_date = current_date - datetime.timedelta(days=days_to_subtract)
last_week_start_date = last_week_date - datetime.timedelta(days=6)  # Assuming 7 days in a week

#session3 = CachedSession('cache3', expire_after=timedelta(hours=1))

@st.cache_data(ttl=3600)
def create_plot6():
    url6 = "https://www.theblock.co/api/charts/chart/crypto-markets/options/btc-atm-implied-volatility"
    r6 = requests.get(url6)
    r_json6 = r6.json()

    output_dataframe6 = pd.DataFrame()
    series_dict6 = r_json6['chart']['jsonFile']['Series']
    for vol in series_dict6:
        df_ = pd.DataFrame(series_dict6[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Volatility'})
        df_['ATM'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe6 = pd.concat([df_,output_dataframe6])

    # Convert date column to datetime format
    output_dataframe6['date'] = pd.to_datetime(output_dataframe6['date'])

    fig6 = go.Figure()
    implied_btc_volatility_table_data = []

    # Specify the desired color for the specific ATM indicator
    custom_color = '#D3D3D3'

    for token, group in output_dataframe6.groupby('ATM'):
        fig6.add_trace(go.Scatter(
            x=group['date'],
            y=group['Volatility'],
            mode='lines',
            name=token,
            line=dict(color=custom_color if token == 'ATM 7' else None))
        )

        fig6.update_layout(
            xaxis=dict(
            title="Date",
            tickformat="%b-%y"
        ),
            yaxis=dict(title="Volatility (%)"),
            hovermode="x"
        )

        fig6.update_layout(
            legend=dict(
            orientation="h",
            y=-0.2,  # Adjust the value to control the vertical position of the legend
            x=0.5,  # Adjust the value to control the horizontal position of the legend
            xanchor='center'
            )
        )

        fig6.update_traces(
            hovertemplate='<b>%{x|%d-%b-%y}</b><br>Volatility: %{y:.2f}%'
        )

        fig6.update_yaxes(ticksuffix="%")

        current_implied_btc_volatility = group['Volatility'].iloc[-1]

        # Calculate the current, last year, last month, last quarter implied_btc_volatility values
        last_year_implied_btc_volatility = group.loc[group['date'].dt.year == last_year_date.year, 'Volatility'].values[-1]
        last_month_implied_btc_volatility = group.loc[(group['date'].dt.year == last_month_date.year) & (group['date'].dt.month == last_month_date.month), 'Volatility'].values[-1]
        last_quarter_implied_btc_volatility = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date), 'Volatility'].values[-1]
        last_week_implied_btc_volatility = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date), 'Volatility'].values[-1]

        # Calculate the change values as percentages
        last_week_change = current_implied_btc_volatility - last_week_implied_btc_volatility
        last_month_change = current_implied_btc_volatility - last_month_implied_btc_volatility
        last_year_change = current_implied_btc_volatility - last_year_implied_btc_volatility
        last_quarter_change = current_implied_btc_volatility - last_quarter_implied_btc_volatility

        # Format implied_btc_volatility values as percentages
        current_implied_btc_volatility_str = f'{current_implied_btc_volatility:.2f}%'
        last_week_implied_btc_volatility_str = f'{last_week_implied_btc_volatility:.2f}%'
        last_month_implied_btc_volatility_str = f'{last_month_implied_btc_volatility:.2f}%'
        last_year_implied_btc_volatility_str = f'{last_year_implied_btc_volatility:.2f}%'
        last_quarter_implied_btc_volatility_str = f'{last_quarter_implied_btc_volatility:.2f}%'

        # Create a dictionary for the indicator's implied_btc_volatility data
        indicator_data = {
            'Indicator': token,
            'WTD': last_week_implied_btc_volatility_str,
            'WTD (Δ)': f'{last_week_change:.2f}%',
            'MTD': last_month_implied_btc_volatility_str,
            'MTD (Δ)': f'{last_month_change:.2f}%',
            'QTD': last_quarter_implied_btc_volatility_str,
            'QTD (Δ)': f'{last_quarter_change:.2f}%',
            'YTD': last_year_implied_btc_volatility_str,
            'YTD (Δ)': f'{last_year_change:.2f}%'
        }

        # Append the indicator's data to the implied_btc_volatility_table_data list
        implied_btc_volatility_table_data.append(indicator_data)

    # Create the implied_btc_volatility_table DataFrame
    implied_btc_volatility_table = pd.DataFrame(implied_btc_volatility_table_data)

    return fig6, implied_btc_volatility_table

@st.cache_data(ttl=3600)
def create_plot11():
    url11 = "https://www.theblock.co/api/charts/chart/crypto-markets/options/eth-atm-implied-volatility"
    r11 = requests.get(url11)
    r_json11 = r11.json()

    output_dataframe11 = pd.DataFrame()
    series_dict11 = r_json11['chart']['jsonFile']['Series']
    for vol in series_dict11:
        df_ = pd.DataFrame(series_dict11[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Volatility'})
        df_['ATM'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe11 = pd.concat([df_,output_dataframe11])

    # Convert date column to datetime format
    output_dataframe11['date'] = pd.to_datetime(output_dataframe11['date'])

    fig11 = go.Figure()
    implied_eth_volatility_table_data = []

    # Specify the desired color for the specific ATM indicator
    custom_color = '#D3D3D3'

    for token, group in output_dataframe11.groupby('ATM'):
        fig11.add_trace(go.Scatter(
            x=group['date'],
            y=group['Volatility'],
            mode='lines',
            name=token,
            line=dict(color=custom_color if token == 'ATM 7' else None))
        )

        fig11.update_layout(
            xaxis=dict(
            title="Date",
            tickformat="%b-%y"
        ),
            yaxis=dict(title="Volatility (%)"),
            hovermode="x"
        )

        fig11.update_layout(
            legend=dict(
            orientation="h",
            y=-0.2,  # Adjust the value to control the vertical position of the legend
            x=0.5,  # Adjust the value to control the horizontal position of the legend
            xanchor='center'
            )
        )

        fig11.update_traces(
            hovertemplate='<b>%{x|%d-%b-%y}</b><br>Volatility: %{y:.2f}%'
        )

        fig11.update_yaxes(ticksuffix="%")

        current_implied_eth_volatility = group['Volatility'].iloc[-1]

        # Calculate the current, last year, last month, last quarter implied_eth_volatility values
        last_year_implied_eth_volatility = group.loc[group['date'].dt.year == last_year_date.year, 'Volatility'].values[-1]
        last_month_implied_eth_volatility = group.loc[(group['date'].dt.year == last_month_date.year) & (group['date'].dt.month == last_month_date.month), 'Volatility'].values[-1]
        last_quarter_implied_eth_volatility = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date), 'Volatility'].values[-1]
        last_week_implied_eth_volatility = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date), 'Volatility'].values[-1]

        # Calculate the change values as percentages
        last_week_change = current_implied_eth_volatility - last_week_implied_eth_volatility
        last_month_change = current_implied_eth_volatility - last_month_implied_eth_volatility
        last_year_change = current_implied_eth_volatility - last_year_implied_eth_volatility
        last_quarter_change = current_implied_eth_volatility - last_quarter_implied_eth_volatility

        # Format implied_eth_volatility values as percentages
        current_implied_eth_volatility_str = f'{current_implied_eth_volatility:.2f}%'
        last_week_implied_eth_volatility_str = f'{last_week_implied_eth_volatility:.2f}%'
        last_month_implied_eth_volatility_str = f'{last_month_implied_eth_volatility:.2f}%'
        last_year_implied_eth_volatility_str = f'{last_year_implied_eth_volatility:.2f}%'
        last_quarter_implied_eth_volatility_str = f'{last_quarter_implied_eth_volatility:.2f}%'

        # Create a dictionary for the indicator's implied_btc_volatility data
        indicator_data = {
            'Indicator': token,
            'WTD': last_week_implied_eth_volatility_str,
            'WTD (Δ)': f'{last_week_change:.2f}%',
            'MTD': last_month_implied_eth_volatility_str,
            'MTD (Δ)': f'{last_month_change:.2f}%',
            'QTD': last_quarter_implied_eth_volatility_str,
            'QTD (Δ)': f'{last_quarter_change:.2f}%',
            'YTD': last_year_implied_eth_volatility_str,
            'YTD (Δ)': f'{last_year_change:.2f}%'
        }

        # Append the indicator's data to the implied_eth_volatility_table_data list
        implied_eth_volatility_table_data.append(indicator_data)

    # Create the implied_eth_volatility_table DataFrame
    implied_eth_volatility_table = pd.DataFrame(implied_eth_volatility_table_data)

    return fig11, implied_eth_volatility_table

@st.cache_data(ttl=3600)
def create_plot7():
    url7 = "https://www.theblock.co/api/charts/chart/crypto-markets/options/btc-option-skew-delta-25"
    r7 = requests.get(url7)
    r_json7 = r7.json()

    output_dataframe7 = pd.DataFrame()
    series_dict7 = r_json7['chart']['jsonFile']['Series']
    for vol in series_dict7:
        df_ = pd.DataFrame(series_dict7[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Delta'})
        df_['Exp'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe7 = pd.concat([df_,output_dataframe7])

    # Convert date column to datetime format
    output_dataframe7['date'] = pd.to_datetime(output_dataframe7['date'])

    fig7 = go.Figure()
    btc_option_skew_delta_table_data = []

    # Specify the desired color for the specific Exp indicator
    custom_color = '#D3D3D3'

    # Exclude a specific token
    exclude_token = '90 Day Exp'

    for token, group in output_dataframe7.groupby('Exp'):
        if token != exclude_token:
            fig7.add_trace(go.Scatter(
                x=group['date'],
                y=group['Delta'],
                mode='lines',
                name=token,
                line=dict(color=custom_color if token == '60 Day Exp' else None))
            )

        fig7.update_layout(
                    title = 'BTC Option Skew Delta',
                    xaxis=dict(
                    title="Date",
                    tickformat="%b-%y"
                ),
                    yaxis=dict(title="Delta"),
                    hovermode="x"
                )

        fig7.update_layout(
                    legend=dict(
                    orientation="h",
                    y=-0.2,  # Adjust the value to control the vertical position of the legend
                    x=0.5,  # Adjust the value to control the horizontal position of the legend
                    xanchor='center'
                    )
                )

        fig7.update_traces(
                    hovertemplate='<b>%{x|%d-%b-%y}</b><br>Delta: %{y:.2f}%'
                )

        fig7.update_yaxes(ticksuffix="%")

        current_btc_option_skew_delta = group['Delta'].iloc[-1]

        # Calculate the current, last year, last month, last quarter btc_option_skew_delta values
        last_year_btc_option_skew_delta = group.loc[group['date'].dt.year == last_year_date.year, 'Delta'].values[-1]
        last_month_btc_option_skew_delta = group.loc[(group['date'].dt.year == last_month_date.year) & (group['date'].dt.month == last_month_date.month), 'Delta'].values[-1]
        last_quarter_btc_option_skew_delta = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date), 'Delta'].values[-1]
        last_week_btc_option_skew_delta = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date), 'Delta'].values[-1]

        # Calculate the change values as percentages
        last_week_change = current_btc_option_skew_delta - last_week_btc_option_skew_delta
        last_month_change = current_btc_option_skew_delta - last_month_btc_option_skew_delta
        last_year_change = current_btc_option_skew_delta - last_year_btc_option_skew_delta
        last_quarter_change = current_btc_option_skew_delta - last_quarter_btc_option_skew_delta

        # Format btc_option_skew_delta values as percentages
        current_btc_option_skew_delta_str = f'{current_btc_option_skew_delta:.2f}%'
        last_week_btc_option_skew_delta_str = f'{last_week_btc_option_skew_delta:.2f}%'
        last_month_btc_option_skew_delta_str = f'{last_month_btc_option_skew_delta:.2f}%'
        last_year_btc_option_skew_delta_str = f'{last_year_btc_option_skew_delta:.2f}%'
        last_quarter_btc_option_skew_delta_str = f'{last_quarter_btc_option_skew_delta:.2f}%'

        # Create a dictionary for the indicator's btc_option_skew_delta data
        indicator_data = {
                    'Indicator': token,
                    'WTD': last_week_btc_option_skew_delta_str,
                    'WTD (Δ)': f'{last_week_change:.2f}%',
                    'MTD': last_month_btc_option_skew_delta_str,
                    'MTD (Δ)': f'{last_month_change:.2f}%',
                    'QTD': last_quarter_btc_option_skew_delta_str,
                    'QTD (Δ)': f'{last_quarter_change:.2f}%',
                    'YTD': last_year_btc_option_skew_delta_str,
                    'YTD (Δ)': f'{last_year_change:.2f}%'
                }

                # Append the indicator's data to the btc_option_skew_delta_table_data list
        btc_option_skew_delta_table_data.append(indicator_data)

        # Create the btc_option_skew_delta_table DataFrame
    btc_option_skew_delta_table = pd.DataFrame(btc_option_skew_delta_table_data)

    return fig7, btc_option_skew_delta_table

@st.cache_data(ttl=3600)
def create_plot5():
    url5 = "https://www.theblock.co/api/charts/chart/crypto-markets/prices/annualized-btc-volatility-30d"
    r5 = requests.get(url5)
    r_json5 = r5.json()

    output_dataframe5 = pd.DataFrame()
    series_dict5 = r_json5['chart']['jsonFile']['Series']
    for vol in series_dict5:
        df_ = pd.DataFrame(series_dict5[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Volatility'})
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe5 = pd.concat([df_,output_dataframe5])

    # Convert date column to datetime format
    output_dataframe5['date'] = pd.to_datetime(output_dataframe5['date'])

    fig5 = px.line(output_dataframe5, x='date', y='Volatility')

    fig5.update_layout(
            title="BTC Annualized Volatility",
            xaxis=dict(
            title="Date",
            tickformat="%b-%y"
        ),
            yaxis=dict(title="Volatility (%)"),
            hovermode="x"
        )
    fig5.update_traces(line_color="#7030A0")    

    current_annualized_btc_volatility = output_dataframe5['Volatility'].iloc[-1] 

    fig5.add_annotation(
        xref="paper",
        yref="paper",
        x=0.98,
        y=0.95,
        xanchor="right",
        yanchor="top",
        text=f"Current BTC Vol: {current_annualized_btc_volatility:.2f}%",
        showarrow=False,
        align="right",
        font=dict(
            family="Arial",
            size=12,
            color="white"
        )
    )

    fig5.update_traces(
            hovertemplate='<b>%{x|%d-%b-%y}</b><br>Volatility: %{y:.2f}%'
        )

    fig5.update_yaxes(ticksuffix="%")
    
    # Calculate the quarterly, monthly, and yearly annualized_btc_volatility values
    last_year_annualized_btc_volatility= output_dataframe5.loc[output_dataframe5['date'].dt.year == last_year_date.year, 'Volatility'].values[-1]
    last_month_annualized_btc_volatility = output_dataframe5.loc[output_dataframe5['date'].dt.year == last_month_date.year]
    last_month_annualized_btc_volatility = last_month_annualized_btc_volatility.loc[last_month_annualized_btc_volatility['date'].dt.month == last_month_date.month]
    last_month_annualized_btc_volatility = last_month_annualized_btc_volatility['Volatility'].values[-1]

    last_quarter_annualized_btc_volatility = output_dataframe5.loc[(output_dataframe5['date'].dt.date >= last_quarter_start_date) & (output_dataframe5['date'].dt.date <= last_quarter_date)]
    last_quarter_annualized_btc_volatility = last_quarter_annualized_btc_volatility['Volatility'].values[-1]
    last_week_annualized_btc_volatility = output_dataframe5.loc[(output_dataframe5['date'].dt.date >= last_week_start_date) & (output_dataframe5['date'].dt.date <= last_week_date)]
    last_week_annualized_btc_volatility = last_week_annualized_btc_volatility['Volatility'].values[-1]

    # Format annualized_btc_volatility values as percentages
    current_annualized_btc_volatility_str = f'{current_annualized_btc_volatility:.2f}%'
    last_week_annualized_btc_volatility_str = f'{last_week_annualized_btc_volatility:.2f}%'
    last_month_annualized_btc_volatility_str = f'{last_month_annualized_btc_volatility:.2f}%'
    last_year_annualized_btc_volatility_str = f'{last_year_annualized_btc_volatility:.2f}%'
    last_quarter_annualized_btc_volatility_str = f'{last_quarter_annualized_btc_volatility:.2f}%'

    # Calculate the change values as percentages
    last_week_change = current_annualized_btc_volatility - last_week_annualized_btc_volatility
    last_month_change = current_annualized_btc_volatility - last_month_annualized_btc_volatility
    last_year_change = current_annualized_btc_volatility - last_year_annualized_btc_volatility
    last_quarter_change = current_annualized_btc_volatility - last_quarter_annualized_btc_volatility

    # Create the annualized_btc_volatility table
    annualized_btc_volatility_table = pd.DataFrame({
        'Period': ['WTD', 'MTD', 'QTD', 'YTD'],
        'Volatility': [last_week_annualized_btc_volatility_str, last_month_annualized_btc_volatility_str, last_quarter_annualized_btc_volatility_str, last_year_annualized_btc_volatility_str],
        'Date': [last_week_date.strftime("%d %b %Y"), last_month_date.strftime("%d %b %Y"), last_quarter_date.strftime("%d %b %Y"), last_year_date.strftime("%d %b %Y")],
        'Δ': [f'{last_week_change:.2f}%', f'{last_month_change:.2f}%', f'{last_quarter_change:.2f}%', f'{last_year_change:.2f}%']
    })

    return fig5, annualized_btc_volatility_table

@st.cache_data(ttl=3600)
def create_plot13():
    url13 = "https://www.theblock.co/api/charts/chart/crypto-markets/options/aggregated-open-interest-of-bitcoin-options"
    r13 = requests.get(url13)
    r_json13 = r13.json()

    output_dataframe13 = pd.DataFrame()
    series_dict13 = r_json13['chart']['jsonFile']['Series']
    for vol in series_dict13:
        df_ = pd.DataFrame(series_dict13[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'OI'})
        df_['Exchange'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe13 = pd.concat([df_,output_dataframe13])

    # Convert date column to datetime format
    output_dataframe13['date'] = pd.to_datetime(output_dataframe13['date'])
    fig13 = go.Figure()
    open_interest_btc_options_table_data = []
    #stackgroup = 'open_interest'
    custom_color = 'grey'

    # Create a dictionary to store the total OI for each token
    token_oi = {}

    # Calculate the total OI for each token
    for token, group in output_dataframe13.groupby('Exchange'):
        token_oi[token] = group['OI'].sum()

    # Sort the tokens based on the total OI in descending order
    sorted_tokens = sorted(token_oi, key=token_oi.get, reverse=True)
  

    # Iterate over each token in the sorted order
    for token in sorted_tokens:
        group = output_dataframe13[output_dataframe13['Exchange'] == token]
        fig13.add_trace(go.Scatter(
                        x=group['date'],
                        y=group['OI'],
                        mode='lines',
                        fill='tonexty',
                        name=token,
                        stackgroup='one',
                        line=dict(color=custom_color if token == 'Binance' else None)))

        fig13.update_layout(
                            xaxis=dict(
                            title="Date",
                            tickformat="%b-%y"
                        ),
                            yaxis=dict(title="Open Interest (in Billions)"),
                            hovermode="x"
                        )

        fig13.update_layout(
                            legend=dict(
                            orientation="h",
                            y=-0.2,  # Adjust the value to control the vertical position of the legend
                            x=0.5,  # Adjust the value to control the horizontal position of the legend
                            xanchor='center'
                            )
                        )

        fig13.update_traces(
                            hovertemplate='<b>%{x|%d-%b-%y}</b><br>OI: %{y}'
                        )
        
        fig13.update_yaxes(tickprefix="$")

        # Calculate the last year's open_interest_btc_options using the last date of the previous year
        last_year_open_interest_btc_options = group.loc[group['date'].dt.year == last_year_date.year, 'OI'].values[-1]
        current_open_interest_btc_options = group['OI'].values[-1]

        # Calculate the last month's open_interest_btc_options
        last_month_open_interest_btc_options = group.loc[group['date'].dt.year == last_month_date.year]
        last_month_open_interest_btc_options = last_month_open_interest_btc_options.loc[last_month_open_interest_btc_options['date'].dt.month == last_month_date.month]
        last_month_open_interest_btc_options = last_month_open_interest_btc_options['OI'].values[-1]

        # Calculate the last quarter's open_interest_btc_options
        last_quarter_open_interest_btc_options = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date)]
        last_quarter_open_interest_btc_options = last_quarter_open_interest_btc_options['OI'].values[-1]

        # Calculate the last week's open_interest_btc_options
        last_week_open_interest_btc_options = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date)]
        last_week_open_interest_btc_options = last_week_open_interest_btc_options['OI'].values[-1]

        # Format open_interest_btc_options values in trillions
        current_open_interest_btc_options_str = f'{current_open_interest_btc_options/1e9:.3f}B'
        last_week_open_interest_btc_options_str = f'{last_week_open_interest_btc_options/1e9:.3f}B'
        last_month_open_interest_btc_options_str = f'{last_month_open_interest_btc_options/1e9:.3f}B'
        last_year_open_interest_btc_options_str = f'{last_year_open_interest_btc_options/1e9:.3f}B'
        last_quarter_open_interest_btc_options_str = f'{last_quarter_open_interest_btc_options/1e9:.3f}B'

        # Calculate the change values as percentages
        last_week_change = ((current_open_interest_btc_options - last_week_open_interest_btc_options) / last_week_open_interest_btc_options) * 100
        last_month_change = ((current_open_interest_btc_options - last_month_open_interest_btc_options) / last_month_open_interest_btc_options) * 100
        last_year_change = ((current_open_interest_btc_options - last_year_open_interest_btc_options) / last_year_open_interest_btc_options) * 100
        last_quarter_change = ((current_open_interest_btc_options - last_quarter_open_interest_btc_options) / last_quarter_open_interest_btc_options) * 100

        # Create a dictionary for the indicator's open_interest_btc_options data
        indicator_data = {
                'Indicator': token,
                'WTD': last_week_open_interest_btc_options_str,
                'WTD (Δ)': f'{last_week_change:.2f}%',
                'MTD': last_month_open_interest_btc_options_str,
                'MTD (Δ)': f'{last_month_change:.2f}%',
                'QTD': last_quarter_open_interest_btc_options_str,
                'QTD (Δ)': f'{last_quarter_change:.2f}%',
                'YTD': last_year_open_interest_btc_options_str,
                'YTD (Δ)': f'{last_year_change:.2f}%'
            }

        # Append the indicator's data to the open_interest_btc_options_table_data list
        open_interest_btc_options_table_data.append(indicator_data)

    # Create the bbtc_funding_rates_table DataFrame
    open_interest_btc_options_table = pd.DataFrame(open_interest_btc_options_table_data)

    return fig13, open_interest_btc_options_table

@st.cache_data(ttl=3600)
def create_plot14():
    url14 = "https://www.theblock.co/api/charts/chart/crypto-markets/options/aggregated-open-interest-of-ethereum-options"
    r14 = requests.get(url14)
    r_json14 = r14.json()

    output_dataframe14 = pd.DataFrame()
    series_dict14 = r_json14['chart']['jsonFile']['Series']
    for vol in series_dict14:
        df_ = pd.DataFrame(series_dict14[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'OI'})
        df_['Exchange'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe14 = pd.concat([df_,output_dataframe14])

    # Convert date column to datetime format
    output_dataframe14['date'] = pd.to_datetime(output_dataframe14['date'])
    fig14 = go.Figure()
    open_interest_eth_options_table_data = []
    #stackgroup = 'open_interest'
    custom_color = 'grey'

    # Create a dictionary to store the total OI for each token
    token_oi = {}

    # Calculate the total OI for each token
    for token, group in output_dataframe14.groupby('Exchange'):
        token_oi[token] = group['OI'].sum()

    # Sort the tokens based on the total OI in descending order
    sorted_tokens = sorted(token_oi, key=token_oi.get, reverse=True)
  

    # Iterate over each token in the sorted order
    for token in sorted_tokens:
        group = output_dataframe14[output_dataframe14['Exchange'] == token]
        fig14.add_trace(go.Scatter(
                        x=group['date'],
                        y=group['OI'],
                        mode='lines',
                        fill='tonexty',
                        name=token,
                        stackgroup='one',
                        line=dict(color=custom_color if token == 'Binance' else None)))

        fig14.update_layout(
                            xaxis=dict(
                            title="Date",
                            tickformat="%b-%y"
                        ),
                            yaxis=dict(title="Open Interest (in Billions)"),
                            hovermode="x"
                        )

        fig14.update_layout(
                            legend=dict(
                            orientation="h",
                            y=-0.2,  # Adjust the value to control the vertical position of the legend
                            x=0.5,  # Adjust the value to control the horizontal position of the legend
                            xanchor='center'
                            )
                        )

        fig14.update_traces(
                            hovertemplate='<b>%{x|%d-%b-%y}</b><br>OI: %{y}'
                        )
        
        fig14.update_yaxes(tickprefix="$")

        # Calculate the last year's open_interest_eth_options using the last date of the previous year
        last_year_open_interest_eth_options = group.loc[group['date'].dt.year == last_year_date.year, 'OI'].values[-1]
        current_open_interest_eth_options = group['OI'].values[-1]

        # Calculate the last month's open_interest_eth_options
        last_month_open_interest_eth_options = group.loc[group['date'].dt.year == last_month_date.year]
        last_month_open_interest_eth_options = last_month_open_interest_eth_options.loc[last_month_open_interest_eth_options['date'].dt.month == last_month_date.month]
        last_month_open_interest_eth_options = last_month_open_interest_eth_options['OI'].values[-1]

        # Calculate the last quarter's open_interest_eth_options
        last_quarter_open_interest_eth_options = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date)]
        last_quarter_open_interest_eth_options = last_quarter_open_interest_eth_options['OI'].values[-1]

        # Calculate the last week's open_interest_eth_options
        last_week_open_interest_eth_options = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date)]
        last_week_open_interest_eth_options = last_week_open_interest_eth_options['OI'].values[-1]

        # Format open_interest_beth_options values in trillions
        current_open_interest_eth_options_str = f'{current_open_interest_eth_options/1e9:.3f}B'
        last_week_open_interest_eth_options_str = f'{last_week_open_interest_eth_options/1e9:.3f}B'
        last_month_open_interest_eth_options_str = f'{last_month_open_interest_eth_options/1e9:.3f}B'
        last_year_open_interest_eth_options_str = f'{last_year_open_interest_eth_options/1e9:.3f}B'
        last_quarter_open_interest_eth_options_str = f'{last_quarter_open_interest_eth_options/1e9:.3f}B'

        # Calculate the change values as percentages
        last_week_change = ((current_open_interest_eth_options - last_week_open_interest_eth_options) / last_week_open_interest_eth_options) * 100
        last_month_change = ((current_open_interest_eth_options - last_month_open_interest_eth_options) / last_month_open_interest_eth_options) * 100
        last_year_change = ((current_open_interest_eth_options - last_year_open_interest_eth_options) / last_year_open_interest_eth_options) * 100
        last_quarter_change = ((current_open_interest_eth_options - last_quarter_open_interest_eth_options) / last_quarter_open_interest_eth_options) * 100

        # Create a dictionary for the indicator's open_interest_eth_options data
        indicator_data = {
                'Indicator': token,
                'WTD': last_week_open_interest_eth_options_str,
                'WTD (Δ)': f'{last_week_change:.2f}%',
                'MTD': last_month_open_interest_eth_options_str,
                'MTD (Δ)': f'{last_month_change:.2f}%',
                'QTD': last_quarter_open_interest_eth_options_str,
                'QTD (Δ)': f'{last_quarter_change:.2f}%',
                'YTD': last_year_open_interest_eth_options_str,
                'YTD (Δ)': f'{last_year_change:.2f}%'
            }

        # Append the indicator's data to the open_interest_eth_options_table_data list
        open_interest_eth_options_table_data.append(indicator_data)

    # Create the eth_funding_rates_table DataFrame
    open_interest_eth_options_table = pd.DataFrame(open_interest_eth_options_table_data)

    return fig14, open_interest_eth_options_table

#@st.cache_data(ttl=3600)
def main4():

    selected_range2 = st.sidebar.selectbox("Select Timeframe:", ["All", "1W", "1M", "1Q", "1Y"])

    if st.sidebar.button("Clear Cache"):
        # Clears all st.cache_resource caches:
        st.cache_data.clear()

    css = '''
        <style>
            [data-testid='stSidebarNav'] > ul {
                min-height: 55vh;
            }
        </style>
        '''

    st.markdown(css, unsafe_allow_html=True)

    plot6, implied_btc_volatility_table  = create_plot6()
    plot7, btc_option_skew_delta_table  = create_plot7()
    plot5, annualized_btc_volatility_table  = create_plot5()
    plot11, implied_eth_volatility_table = create_plot11()
    plot13, open_interest_btc_options_table = create_plot13()
    plot14, open_interest_eth_options_table = create_plot14()

    button_ranges_combined = {
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
        "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
        "1Y": [datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()],
        "All": None
        }

    tickformat = "%d-%b-%Y"  # The desired tick format

    # List of plots to update
    # Define a list of dictionaries containing plot objects and their titles
    plots_and_titles = [
        (plot6, "BTC ATM Implied Volatility"),
        (plot7, "BTC Option Skew Delta"),
        (plot5, "BTC Annualized Volatility"),
        (plot11, "ETH ATM Implied Volatility"),
        (plot13, "Open Interest of BTC Options"),
        (plot14, "Open Interest of ETH Options")
    ]

    for plot, title in plots_and_titles:
        plot.update_xaxes(
            range=button_ranges_combined[selected_range2],
            tickformat=tickformat
        )

        plot.update_layout(
            title=dict(
                text=title,
                x=0.2,
                y=0.9,
                xanchor="center",
                yanchor="top"
            )
        )

    col1, col2 = st.columns(2)

    col1.plotly_chart(plot13, use_container_width=True)
    col1.dataframe(open_interest_btc_options_table, hide_index = True)
    col2.plotly_chart(plot14, use_container_width=True)
    col2.dataframe(open_interest_eth_options_table, hide_index = True)

    col1, col2 = st.columns(2)

    col1.plotly_chart(plot6, use_container_width=True)
    col1.dataframe(implied_btc_volatility_table, hide_index = True)
    col2.plotly_chart(plot11, use_container_width=True)
    col2.dataframe(implied_eth_volatility_table, hide_index = True)

    col1, col2 = st.columns(2)
    col1.plotly_chart(plot7, use_container_width=True)
    col1.dataframe(btc_option_skew_delta_table, hide_index = True)
    col2.plotly_chart(plot5, use_container_width=True)
    col2.dataframe(annualized_btc_volatility_table, hide_index = True)

if __name__ == "__main__":
    main4()
