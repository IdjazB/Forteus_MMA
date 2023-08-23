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

st.title('DeFi')

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

session5 = CachedSession('cache5', expire_after=timedelta(hours=1))

def create_plot23():
    url23 = "https://www.theblock.co/api/charts/chart/decentralized-finance/total-value-locked-tvl/total-value-locked-by-category"
    r23 = session5.get(url23)
    r_json23 = r23.json()

    output_dataframe23 = pd.DataFrame()
    series_dict23 = r_json23['chart']['jsonFile']['Series']
    for vol in series_dict23:
        df_ = pd.DataFrame(series_dict23[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Value'})
        df_['Exchange'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe23 = pd.concat([df_,output_dataframe23])

    # Convert date column to datetime format
    output_dataframe23['date'] = pd.to_datetime(output_dataframe23['date'])
    fig23 = go.Figure()
    value_locked_by_cat_table_data = []

    # Filter the dataframe for the last day
    last_date = output_dataframe23['date'].max()
    last_day_data = output_dataframe23[output_dataframe23['date'] == last_date]

    # Sort the exchanges based on their volumes on the last day
    sorted_tokens = last_day_data.groupby('Exchange')['Value'].sum().sort_values(ascending=False)

    # Calculate the total volume on the last day
    total_volume_last_day = last_day_data['Value'].sum()

    # Calculate the threshold for 80% of the total volume on the last day
    threshold = 0.91 * total_volume_last_day

    # Filter the exchanges based on the threshold
    filtered_tokens = []
    cumulative_volume = 0

    for exchange, volume in sorted_tokens.items():
        cumulative_volume += volume
        filtered_tokens.append(exchange)
        
        if cumulative_volume >= threshold:
            break

    remaining_tokens = output_dataframe23[~output_dataframe23['Exchange'].isin(filtered_tokens)]['Exchange'].unique()
    # Group the data by date and exchange to get the aggregated DataFrame for remaining_tokens
    remaining_tokens_data = output_dataframe23[output_dataframe23['Exchange'].isin(remaining_tokens)]
    remaining_tokens_data_grouped = remaining_tokens_data.groupby(['date', 'Exchange']).sum().reset_index()

    # Create a DataFrame for "Others" containing aggregated volume for remaining_tokens
    others_data = remaining_tokens_data_grouped.groupby('date')['Value'].sum().reset_index()
    others_count = len(remaining_tokens)
    others_data['Exchange'] = f'+{others_count} Others'

    # Combine the data for filtered tokens and others into a single DataFrame
    combined_data = pd.concat([output_dataframe23[output_dataframe23['Exchange'].isin(filtered_tokens)], others_data])

    # Group the combined data by date and exchange to get the aggregated DataFrame
    output_dataframe_agg = combined_data.groupby(['date', 'Exchange']).sum().reset_index()

    # Sort the DataFrame based on the total volume of each token on the last day (in descending order)
    sorted_tokens = output_dataframe_agg.groupby('Exchange')['Value'].sum().sort_values(ascending=False).index
    output_dataframe_agg['Exchange'] = pd.Categorical(output_dataframe_agg['Exchange'], categories=sorted_tokens, ordered=True)
    output_dataframe_agg.sort_values(['date', 'Exchange'], inplace=True)
    
    # Iterate over each token in the sorted order
    for token in output_dataframe_agg['Exchange'].unique():
        custom_color = 'orange' if token == 'Synthetics' else 'grey' if token == 'CDP' else None
        group = output_dataframe_agg[output_dataframe_agg['Exchange'] == token]
        fig23.add_trace(go.Scatter(
                            x=group['date'],
                            y=group['Value'],
                            mode='lines',
                            fill='tonexty',
                            name=token,
                            stackgroup='one',
                            line = dict(color = custom_color)))

        fig23.update_layout(
                                xaxis=dict(
                                title="Date",
                                tickformat="%b-%y",
                                tickmode="linear",
                                dtick="M6"  # Display tick labels every 6 days
                            ),
                                yaxis=dict(title="Value Locked (in Billions USD)"),
                                hovermode="x"
                            )

        fig23.update_layout(
                                legend=dict(
                                orientation="h",
                                y=-0.2,  # Adjust the value to control the vertical position of the legend
                                x=0.5,  # Adjust the value to control the horizontal position of the legend
                                xanchor='center'
                                )
                            )

        fig23.update_traces(
                                hovertemplate='<b>%{x|%d-%b-%y}</b><br>Value: %{y}'
                            )
            
        fig23.update_yaxes(tickprefix="$")

    for token in filtered_tokens:
        # Calculate the last year's value_locked_by_cat using the last date of the previous year
        group = output_dataframe23[output_dataframe23['Exchange'] == token]
        
        # Calculate the last year's value for the filtered token
        last_year_value_locked_by_cat = group[group['date'].dt.date == last_year_date]['Value'].values[-1]

        # Calculate the last month's value for the filtered token
        last_month_value_locked_by_cat = group[group['date'].dt.date == last_month_date]['Value'].values[-1]

        # Calculate the last quarter's value for the filtered token
        last_quarter_value_locked_by_cat = group[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date)]['Value'].values[-1]

        # Calculate the last week's value for the filtered token
        last_week_value_locked_by_cat = group[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date)]['Value'].values[-1]

        # Calculate the current day's value for the filtered token
        current_value_locked_by_cat = group[group['date'].dt.date == last_date.date()]['Value'].values[-1]

        # Format value_locked_by_cat values in trillions
        current_value_locked_by_cat_str = f'{current_value_locked_by_cat/1e9:.3f}B'
        last_week_value_locked_by_cat_str = f'{last_week_value_locked_by_cat/1e9:.3f}B'
        last_month_value_locked_by_cat_str = f'{last_month_value_locked_by_cat/1e9:.3f}B'
        last_year_value_locked_by_cat_str = f'{last_year_value_locked_by_cat/1e9:.3f}B'
        last_quarter_value_locked_by_cat_str = f'{last_quarter_value_locked_by_cat/1e9:.3f}B'

        # Calculate the change values as percentages
        last_week_change = ((current_value_locked_by_cat - last_week_value_locked_by_cat) / last_week_value_locked_by_cat) * 100
        last_month_change = ((current_value_locked_by_cat - last_month_value_locked_by_cat) / last_month_value_locked_by_cat) * 100
        last_year_change = ((current_value_locked_by_cat - last_year_value_locked_by_cat) / last_year_value_locked_by_cat) * 100
        last_quarter_change = ((current_value_locked_by_cat - last_quarter_value_locked_by_cat) / last_quarter_value_locked_by_cat) * 100

        # Create a dictionary for the indicator's value_locked_by_cat data
        indicator_data = {
                    'Indicator': token,
                    'WTD': last_week_value_locked_by_cat_str,
                    'WTD (Δ)': f'{last_week_change:.2f}%',
                    'MTD': last_month_value_locked_by_cat_str,
                    'MTD (Δ)': f'{last_month_change:.2f}%',
                    'QTD': last_quarter_value_locked_by_cat_str,
                    'QTD (Δ)': f'{last_quarter_change:.2f}%',
                    'YTD': last_year_value_locked_by_cat_str,
                    'YTD (Δ)': f'{last_year_change:.2f}%'
                }

        # Append the indicator's data to the value_locked_by_cat_table_data list
        value_locked_by_cat_table_data.append(indicator_data)

    # Create the eth_funding_rates_table DataFrame
    value_locked_by_cat_table = pd.DataFrame(value_locked_by_cat_table_data)

    return fig23, value_locked_by_cat_table

def create_plot24():
    url24 = "https://www.theblock.co/api/charts/chart/decentralized-finance/total-value-locked-tvl/value-locked-by-blockchain"
    r24 = session5.get(url24)
    r_json24 = r24.json()

    output_dataframe24 = pd.DataFrame()
    series_dict24 = r_json24['chart']['jsonFile']['Series']
    for vol in series_dict24:
        df_ = pd.DataFrame(series_dict24[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Value'})
        df_['Exchange'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe24 = pd.concat([df_,output_dataframe24])

    # Convert date column to datetime format
    output_dataframe24['date'] = pd.to_datetime(output_dataframe24['date'])
    fig24 = go.Figure()
    value_locked_by_block_table_data = []

    # Filter the dataframe for the last day
    last_date = output_dataframe24['date'].max()
    last_day_data = output_dataframe24[output_dataframe24['date'] == last_date]

    # Sort the exchanges based on their volumes on the last day
    sorted_tokens = last_day_data.groupby('Exchange')['Value'].sum().sort_values(ascending=False)

    # Calculate the total volume on the last day
    total_volume_last_day = last_day_data['Value'].sum()

    # Calculate the threshold for 80% of the total volume on the last day
    threshold = 0.90 * total_volume_last_day

    # Filter the exchanges based on the threshold
    filtered_tokens = []
    cumulative_volume = 0

    for exchange, volume in sorted_tokens.items():
        cumulative_volume += volume
        filtered_tokens.append(exchange)
        
        if cumulative_volume >= threshold:
            break
    
    remaining_tokens = output_dataframe24[~output_dataframe24['Exchange'].isin(filtered_tokens)]['Exchange'].unique()
    # Group the data by date and exchange to get the aggregated DataFrame for remaining_tokens
    remaining_tokens_data = output_dataframe24[output_dataframe24['Exchange'].isin(remaining_tokens)]
    remaining_tokens_data_grouped = remaining_tokens_data.groupby(['date', 'Exchange']).sum().reset_index()

    # Create a DataFrame for "Others" containing aggregated volume for remaining_tokens
    others_data = remaining_tokens_data_grouped.groupby('date')['Value'].sum().reset_index()
    others_count = len(remaining_tokens)
    others_data['Exchange'] = f'+{others_count} Others'

    # Combine the data for filtered tokens and others into a single DataFrame
    combined_data = pd.concat([output_dataframe24[output_dataframe24['Exchange'].isin(filtered_tokens)], others_data])

    # Group the combined data by date and exchange to get the aggregated DataFrame
    output_dataframe_agg = combined_data.groupby(['date', 'Exchange']).sum().reset_index()

    # Sort the DataFrame based on the total volume of each token on the last day (in descending order)
    sorted_tokens = output_dataframe_agg.groupby('Exchange')['Value'].sum().sort_values(ascending=False).index
    output_dataframe_agg['Exchange'] = pd.Categorical(output_dataframe_agg['Exchange'], categories=sorted_tokens, ordered=True)
    output_dataframe_agg.sort_values(['date', 'Exchange'], inplace=True)

    # Custom color in HEX format: #7030A0
    base_color = "#7030A0"

    # Function to convert HEX color to RGB format
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    # Function to convert RGB color to RGBA format with custom alpha value
    def rgb_to_rgba(rgb_color, alpha):
        return f"rgba{rgb_color + (alpha,)}"

    # Convert HEX color to RGB format
    rgb_color = hex_to_rgb(base_color)

    # Create a list of shades with varying alpha values based on the number of exchanges
    num_exchanges = len(output_dataframe_agg['Exchange'].unique())
    alpha_values = [1.0 - i / (num_exchanges - 1) for i in range(num_exchanges)]
    shades = [rgb_to_rgba(rgb_color, alpha) for alpha in alpha_values]

    # Iterate over each token in the sorted order
    for token in output_dataframe_agg['Exchange'].unique():
        custom_color = 'orange' if token == 'Arbitrum' else 'grey' if token == f'+{others_count} Others' else None
        group = output_dataframe_agg[output_dataframe_agg['Exchange'] == token]
        fig24.add_trace(go.Scatter(
                            x=group['date'],
                            y=group['Value'],
                            mode='lines',
                            fill='tonexty',
                            name=token,
                            stackgroup='one',
                            line=dict(color=custom_color)))

        fig24.update_layout(
                                xaxis=dict(
                                title="Date",
                                tickformat="%b-%y",
                                tickmode="linear",
                                dtick="M6"  # Display tick labels every 6 days
                            ),
                                yaxis=dict(title="Value Locked (in Billions USD)"),
                                hovermode="x"
                            )

        fig24.update_layout(
                                legend=dict(
                                orientation="h",
                                y=-0.2,  # Adjust the value to control the vertical position of the legend
                                x=0.5,  # Adjust the value to control the horizontal position of the legend
                                xanchor='center'
                                )
                            )

        fig24.update_traces(
                                hovertemplate='<b>%{x|%d-%b-%y}</b><br>Value: %{y}'
                            )
            
        fig24.update_yaxes(tickprefix="$")

    for token in filtered_tokens:
        # Calculate the last year's value_locked_by_cat using the last date of the previous year
        group = output_dataframe24[output_dataframe24['Exchange'] == token]
        
        # Calculate the last year's value for the filtered token
        last_year_value_locked_by_block = group[group['date'].dt.date == last_year_date]['Value'].values[-1]

        # Calculate the last month's value for the filtered token
        last_month_value_locked_by_block = group[group['date'].dt.date == last_month_date]['Value'].values[-1]

        # Calculate the last quarter's value for the filtered token
        last_quarter_value_locked_by_block = group[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date)]['Value'].values[-1]

        # Calculate the last week's value for the filtered token
        last_week_value_locked_by_block = group[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date)]['Value'].values[-1]

        # Calculate the current day's value for the filtered token
        current_value_locked_by_block = group[group['date'].dt.date == last_date.date()]['Value'].values[-1]

        # Format value_locked_by_cat values in trillions
        current_value_locked_by_block_str = f'{current_value_locked_by_block/1e9:.3f}B'
        last_week_value_locked_by_block_str = f'{last_week_value_locked_by_block/1e9:.3f}B'
        last_month_value_locked_by_block_str = f'{last_month_value_locked_by_block/1e9:.3f}B'
        last_year_value_locked_by_block_str = f'{last_year_value_locked_by_block/1e9:.3f}B'
        last_quarter_value_locked_by_block_str = f'{last_quarter_value_locked_by_block/1e9:.3f}B'

        # Calculate the change values as percentages
        last_week_change = ((current_value_locked_by_block - last_week_value_locked_by_block) / last_week_value_locked_by_block) * 100
        last_month_change = ((current_value_locked_by_block - last_month_value_locked_by_block) / last_month_value_locked_by_block) * 100
        last_year_change = ((current_value_locked_by_block - last_year_value_locked_by_block) / last_year_value_locked_by_block) * 100
        last_quarter_change = ((current_value_locked_by_block - last_quarter_value_locked_by_block) / last_quarter_value_locked_by_block) * 100

        # Create a dictionary for the indicator's value_locked_by_block data
        indicator_data = {
                    'Indicator': token,
                    'WTD': last_week_value_locked_by_block_str,
                    'WTD (Δ)': f'{last_week_change:.2f}%',
                    'MTD': last_month_value_locked_by_block_str,
                    'MTD (Δ)': f'{last_month_change:.2f}%',
                    'QTD': last_quarter_value_locked_by_block_str,
                    'QTD (Δ)': f'{last_quarter_change:.2f}%',
                    'YTD': last_year_value_locked_by_block_str,
                    'YTD (Δ)': f'{last_year_change:.2f}%'
                }

        # Append the indicator's data to the value_locked_by_block_table_data list
        value_locked_by_block_table_data.append(indicator_data)

    # Create the eth_funding_rates_table DataFrame
    value_locked_by_block_table = pd.DataFrame(value_locked_by_block_table_data)

    return fig24, value_locked_by_block_table

def create_plot25():
    url25 = "https://www.theblock.co/api/charts/chart/decentralized-finance/stablecoins/total-stablecoin-supply"
    r25 = session5.get(url25)
    r_json25 = r25.json()

    output_dataframe25 = pd.DataFrame()
    series_dict25 = r_json25['chart']['jsonFile']['Series']
    for vol in series_dict25:
        df_ = pd.DataFrame(series_dict25[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Value'})
        df_['Exchange'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe25 = pd.concat([df_,output_dataframe25])

    # Convert date column to datetime format
    output_dataframe25['date'] = pd.to_datetime(output_dataframe25['date'])
    total_stablecoin_supply_table_data = []

    # Filter the dataframe for the last day
    last_date = output_dataframe25['date'].max()
    last_day_data = output_dataframe25[output_dataframe25['date'] == last_date]

    # Sort the exchanges based on their volumes on the last day
    sorted_tokens = last_day_data.groupby('Exchange')['Value'].sum().sort_values(ascending=False)

    # Calculate the total volume on the last day
    total_volume_last_day = last_day_data['Value'].sum()

    # Calculate the threshold for 80% of the total volume on the last day
    threshold = 0.95 * total_volume_last_day

    # Filter the exchanges based on the threshold
    filtered_tokens = []
    cumulative_volume = 0

    for exchange, volume in sorted_tokens.items():
        cumulative_volume += volume
        filtered_tokens.append(exchange)
        
        if cumulative_volume >= threshold:
            break

    remaining_tokens = output_dataframe25[~output_dataframe25['Exchange'].isin(filtered_tokens)]['Exchange'].unique()
    # Group the data by date and exchange to get the aggregated DataFrame for remaining_tokens
    remaining_tokens_data = output_dataframe25[output_dataframe25['Exchange'].isin(remaining_tokens)]
    remaining_tokens_data_grouped = remaining_tokens_data.groupby(['date', 'Exchange']).sum().reset_index()

    # Create a DataFrame for "Others" containing aggregated volume for remaining_tokens
    others_data = remaining_tokens_data_grouped.groupby('date')['Value'].sum().reset_index()
    others_count = len(remaining_tokens)
    others_data['Exchange'] = f'+{others_count} Others'

    # Combine the data for filtered tokens and others into a single DataFrame
    combined_data = pd.concat([output_dataframe25[output_dataframe25['Exchange'].isin(filtered_tokens)], others_data])

    # Group the combined data by date and exchange to get the aggregated DataFrame
    output_dataframe_agg = combined_data.groupby(['date', 'Exchange']).sum().reset_index()

    # Custom color in HEX format: #7030A0
    #base_color = "#7030A0"

    # Function to convert HEX color to RGB format
    #def hex_to_rgb(hex_color):
        #hex_color = hex_color.lstrip("#")
        #return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    # Function to convert RGB color to RGBA format with custom alpha value
    #def rgb_to_rgba(rgb_color, alpha):
        #return f"rgba{rgb_color + (alpha,)}"

    # Convert HEX color to RGB format
    #rgb_color = hex_to_rgb(base_color)

    # Create a list of shades with varying alpha values based on the number of exchanges
    #num_exchanges = len(output_dataframe_agg['Exchange'].unique())
    #alpha_values = [1.0 - i / (num_exchanges - 1) for i in range(num_exchanges)]
    #shades = [rgb_to_rgba(rgb_color, alpha) for alpha in alpha_values]

    fig25 = go.Figure()

    for token in output_dataframe_agg['Exchange'].unique()[::-1]:
        custom_color = 'orange' if token == 'TUSD' else 'grey' if token == f'+{others_count} Others' else None
        group = output_dataframe_agg[output_dataframe_agg['Exchange'] == token]
        fig25.add_trace(go.Scatter(
            x=group['date'],
            y=group['Value'],
            mode='lines',
            fill='tonexty',
            name=token,
            stackgroup='one',
            line=dict(color=custom_color)))

    fig25.update_layout(
        xaxis=dict(
            title="Date",
            tickformat="%b-%y",
            tickmode="linear",
            dtick="M12"  # Display tick labels every 6 days
        ),
        yaxis=dict(title="Value Locked (in Billions USD)"),
        hovermode="x",
        legend=dict(
            orientation="h",
            y=-0.2,  # Adjust the value to control the vertical position of the legend
            x=0.5,  # Adjust the value to control the horizontal position of the legend
            xanchor='center'
        )
    )

    fig25.update_traces(
        hovertemplate='<b>%{x|%d-%b-%y}</b><br>Value: %{y}'
    )

    fig25.update_yaxes(tickprefix="$")      

    for token in filtered_tokens:
        group = output_dataframe25[output_dataframe25['Exchange'] == token]
        
        # Calculate the last year's value for the filtered token
        last_year_total_stablecoin_supply = group[group['date'].dt.date == last_year_date]['Value'].values[-1]

        # Calculate the last month's value for the filtered token
        last_month_total_stablecoin_supply = group[group['date'].dt.date == last_month_date]['Value'].values[-1]

        # Calculate the last quarter's value for the filtered token
        last_quarter_total_stablecoin_supply = group[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date)]['Value'].values[-1]

        # Calculate the last week's value for the filtered token
        last_week_total_stablecoin_supply = group[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date)]['Value'].values[-1]

        # Calculate the current day's value for the filtered token
        current_total_stablecoin_supply = group[group['date'].dt.date == last_date.date()]['Value'].values[-1]

        # Format value_locked_by_cat values in billions
        current_total_stablecoin_supply_str = f'{current_total_stablecoin_supply / 1e9:.3f}B'
        last_week_total_stablecoin_supply_str = f'{last_week_total_stablecoin_supply / 1e9:.3f}B'
        last_month_total_stablecoin_supply_str = f'{last_month_total_stablecoin_supply / 1e9:.3f}B'
        last_year_total_stablecoin_supply_str = f'{last_year_total_stablecoin_supply / 1e9:.3f}B'
        last_quarter_total_stablecoin_supply_str = f'{last_quarter_total_stablecoin_supply / 1e9:.3f}B'

        # Calculate the change values as percentages
        last_week_change = ((current_total_stablecoin_supply - last_week_total_stablecoin_supply) / last_week_total_stablecoin_supply) * 100
        last_month_change = ((current_total_stablecoin_supply - last_month_total_stablecoin_supply) / last_month_total_stablecoin_supply) * 100
        last_year_change = ((current_total_stablecoin_supply - last_year_total_stablecoin_supply) / last_year_total_stablecoin_supply) * 100
        last_quarter_change = ((current_total_stablecoin_supply - last_quarter_total_stablecoin_supply) / last_quarter_total_stablecoin_supply) * 100

        # Create a dictionary for the indicator's total_stablecoin_supply data
        indicator_data = {
            'Indicator': token,
            'WTD': last_week_total_stablecoin_supply_str,
            'WTD (Δ)': f'{last_week_change:.2f}%',
            'MTD': last_month_total_stablecoin_supply_str,
            'MTD (Δ)': f'{last_month_change:.2f}%',
            'QTD': last_quarter_total_stablecoin_supply_str,
            'QTD (Δ)': f'{last_quarter_change:.2f}%',
            'YTD': last_year_total_stablecoin_supply_str,
            'YTD (Δ)': f'{last_year_change:.2f}%'
        }

        # Append the indicator's data to the total_stablecoin_supply_table_data list
        total_stablecoin_supply_table_data.append(indicator_data)

    # Create the total_stablecoin_supply_table DataFrame
    total_stablecoin_supply_table = pd.DataFrame(total_stablecoin_supply_table_data)

    return fig25, total_stablecoin_supply_table

def create_plot26():
    url26 = "https://www.theblock.co/api/charts/chart/decentralized-finance/total-value-locked-tvl/value-locked-in-liquid-staking"
    r26= session5.get(url26)
    r_json26= r26.json()

    output_dataframe26 = pd.DataFrame()
    series_dict26 = r_json26['chart']['jsonFile']['Series']
    for vol in series_dict26:
        df_ = pd.DataFrame(series_dict26[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Value'})
        df_['Exchange'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe26 = pd.concat([df_,output_dataframe26])

    # Convert date column to datetime format
    output_dataframe26['date'] = pd.to_datetime(output_dataframe26['date'])
    value_locked_by_liq_table_data = []

    # Filter the dataframe for the last day
    last_date = output_dataframe26['date'].max()
    last_day_data = output_dataframe26[output_dataframe26['date'] == last_date]

    # Sort the exchanges based on their volumes on the last day
    sorted_tokens = last_day_data.groupby('Exchange')['Value'].sum().sort_values(ascending=False)

    # Calculate the total volume on the last day
    total_volume_last_day = last_day_data['Value'].sum()

    # Calculate the threshold for 80% of the total volume on the last day
    threshold = 0.90 * total_volume_last_day

    # Filter the exchanges based on the threshold
    filtered_tokens = []
    cumulative_volume = 0

    for exchange, volume in sorted_tokens.items():
        cumulative_volume += volume
        filtered_tokens.append(exchange)
        
        if cumulative_volume >= threshold:
            break
    
    remaining_tokens = output_dataframe26[~output_dataframe26['Exchange'].isin(filtered_tokens)]['Exchange'].unique()
    # Group the data by date and exchange to get the aggregated DataFrame for remaining_tokens
    remaining_tokens_data = output_dataframe26[output_dataframe26['Exchange'].isin(remaining_tokens)]
    remaining_tokens_data_grouped = remaining_tokens_data.groupby(['date', 'Exchange']).sum().reset_index()

    # Create a DataFrame for "Others" containing aggregated volume for remaining_tokens
    others_data = remaining_tokens_data_grouped.groupby('date')['Value'].sum().reset_index()
    others_count = len(remaining_tokens)
    others_data['Exchange'] = f'+{others_count} Others'

    # Combine the data for filtered tokens and others into a single DataFrame
    combined_data = pd.concat([output_dataframe26[output_dataframe26['Exchange'].isin(filtered_tokens)], others_data])

    # Group the combined data by date and exchange to get the aggregated DataFrame
    output_dataframe_agg = combined_data.groupby(['date', 'Exchange']).sum().reset_index()

    # Sort the DataFrame based on the total volume of each token on the last day (in descending order)
    sorted_tokens = output_dataframe_agg.groupby('Exchange')['Value'].sum().sort_values(ascending=False).index
    output_dataframe_agg['Exchange'] = pd.Categorical(output_dataframe_agg['Exchange'], categories=sorted_tokens, ordered=True)
    output_dataframe_agg.sort_values(['date', 'Exchange'], inplace=True)

    # Create a list of shades with varying alpha values
    # Custom color in HEX format: #7030A0
    #base_color = "#7030A0"

    # Function to convert HEX color to RGB format
    #def hex_to_rgb(hex_color):
        #hex_color = hex_color.lstrip("#")
        #return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    # Function to convert RGB color to RGBA format with custom alpha value
    #def rgb_to_rgba(rgb_color, alpha):
        #return f"rgba{rgb_color + (alpha,)}"

    # Convert HEX color to RGB format
    #rgb_color = hex_to_rgb(base_color)

    # Create a list of shades with varying alpha values based on the number of exchanges
    #num_exchanges = len(output_dataframe_agg['Exchange'].unique())
    #alpha_values = [1.0 - i / (num_exchanges - 1) for i in range(num_exchanges)]
    #shades = [rgb_to_rgba(rgb_color, alpha) for alpha in alpha_values]

    fig26 = go.Figure()

    # Iterate over each token in the sorted order
    for token in output_dataframe_agg['Exchange'].unique():
        #custom_color = shades.pop(0)
        custom_color = 'grey' if token == f'+{others_count} Others' else 'orange' if token == 'Coinbase Wrapped Staked ETH' else None
        group = output_dataframe_agg[output_dataframe_agg['Exchange'] == token]
        fig26.add_trace(go.Scatter(
                            x=group['date'],
                            y=group['Value'],
                            mode='lines',
                            #fill='tonexty',
                            name=token,
                            #stackgroup='one',
                            line=dict(color=custom_color)))

        fig26.update_layout(
                                xaxis=dict(
                                title="Date",
                                tickformat="%b-%y",
                                tickmode="linear",
                                dtick="M6"  # Display tick labels every 6 days
                            ),
                                yaxis=dict(title="Value Locked (in Billions USD)"),
                                hovermode="x"
                            )

        fig26.update_layout(
                                legend=dict(
                                orientation="h",
                                y=-0.2,  # Adjust the value to control the vertical position of the legend
                                x=0.5,  # Adjust the value to control the horizontal position of the legend
                                xanchor='center'
                                )
                            )

        fig26.update_traces(
                                hovertemplate='<b>%{x|%d-%b-%y}</b><br>Value: %{y}'
                            )
            
        fig26.update_yaxes(tickprefix="$")

    for token in filtered_tokens:
        # Calculate the last year's value_locked_by_cat using the last date of the previous year
        group = output_dataframe26[output_dataframe26['Exchange'] == token]
        
        # Calculate the last year's value for the filtered token
        last_year_value_locked_by_liq = group[group['date'].dt.date == last_year_date]['Value'].values[-1]

        # Calculate the last month's value for the filtered token
        last_month_value_locked_by_liq = group[group['date'].dt.date == last_month_date]['Value'].values[-1]

        # Calculate the last quarter's value for the filtered token
        last_quarter_value_locked_by_liq = group[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date)]['Value'].values[-1]

        # Calculate the last week's value for the filtered token
        last_week_value_locked_by_liq = group[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date)]['Value'].values[-1]

        # Calculate the current day's value for the filtered token
        current_value_locked_by_liq = group[group['date'].dt.date == last_date.date()]['Value'].values[-1]

        # Format value_locked_by_cat values in trillions
        current_value_locked_by_liq_str = f'{current_value_locked_by_liq/1e9:.3f}B'
        last_week_value_locked_by_liq_str = f'{last_week_value_locked_by_liq/1e9:.3f}B'
        last_month_value_locked_by_liq_str = f'{last_month_value_locked_by_liq/1e9:.3f}B'
        last_year_value_locked_by_liq_str = f'{last_year_value_locked_by_liq/1e9:.3f}B'
        last_quarter_value_locked_by_liq_str = f'{last_quarter_value_locked_by_liq/1e9:.3f}B'

        # Calculate the change values as percentages
        last_week_change = ((current_value_locked_by_liq - last_week_value_locked_by_liq) / last_week_value_locked_by_liq) * 100
        last_month_change = ((current_value_locked_by_liq - last_month_value_locked_by_liq) / last_month_value_locked_by_liq) * 100
        last_year_change = ((current_value_locked_by_liq - last_year_value_locked_by_liq) / last_year_value_locked_by_liq) * 100
        last_quarter_change = ((current_value_locked_by_liq - last_quarter_value_locked_by_liq) / last_quarter_value_locked_by_liq) * 100

        # Create a dictionary for the indicator's value_locked_by_liq data
        indicator_data = {
                    'Indicator': token,
                    'WTD': last_week_value_locked_by_liq_str,
                    'WTD (Δ)': f'{last_week_change:.2f}%',
                    'MTD': last_month_value_locked_by_liq_str,
                    'MTD (Δ)': f'{last_month_change:.2f}%',
                    'QTD': last_quarter_value_locked_by_liq_str,
                    'QTD (Δ)': f'{last_quarter_change:.2f}%',
                    'YTD': last_year_value_locked_by_liq_str,
                    'YTD (Δ)': f'{last_year_change:.2f}%'
                }

        # Append the indicator's data to the value_locked_by_block_table_data list
        value_locked_by_liq_table_data.append(indicator_data)

    # Create the eth_funding_rates_table DataFrame
    value_locked_by_liq_table = pd.DataFrame(value_locked_by_liq_table_data)

    return fig26, value_locked_by_liq_table

plot23 = None
plot24 = None
plot25 = None
plot26 = None
value_locked_by_cat_table = None
value_locked_by_block_table = None
total_stablecoin_supply_table = None
value_locked_by_liq_table = None

# Define a function to update the plot and table variables
def update_plots_and_tables():
    global plot23, value_locked_by_cat_table
    global plot24, value_locked_by_block_table
    global plot25, total_stablecoin_supply_table
    global plot26, value_locked_by_liq_table
    plot23, value_locked_by_cat_table = create_plot23()
    plot24, value_locked_by_block_table = create_plot24()
    plot25, total_stablecoin_supply_table = create_plot25()
    plot26, value_locked_by_liq_table = create_plot26()

# Call the function to update the plots and tables
# Start a separate thread to create the plots
plots_thread = Thread(target=update_plots_and_tables)
plots_thread.start()

# Wait for the plot creation thread to complete
plots_thread.join()

if plot23 is not None and plot24 is not None and plot25 is not None and plot26 is not None:

    button_ranges_value_locked_by_cat = {
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
        "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
        "1Y": [datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()],
        "3Y": [datetime.datetime.now() - datetime.timedelta(days=1095), datetime.datetime.now()],
        "All": [plot23.data[0].x[0], plot23.data[0].x[-1]]  # Placeholder for 'All' button range
        }

    button_labels_value_locked_by_cat = ["1W", "1M", "1Q", "1Y", "3Y", "All"]

    value_locked_by_cat_buttons = [
            {
                "label": button_label,
                "method": "relayout",
                "args": [
                    {"xaxis": {"range": button_ranges_value_locked_by_cat[button_label], "tickformat": "%d-%b-%Y"}}
                ],
                }
            for button_label in button_labels_value_locked_by_cat
        ]
    
    # Create the updatemenus configuration for value_locked_by_cat Graph
    value_locked_by_cat_updatemenus = [{
            "type": "buttons",
            "buttons": value_locked_by_cat_buttons,
            "x": 0.14,
            "y": 1.1,
            "xanchor": "center",
            "yanchor": "bottom",
            "direction": "right",
            "showactive": True,
            "active": -1,
            "bgcolor": "white",
            "bordercolor": "black",
            "borderwidth": 1,
            "pad": {"r": 5, "t": 5},
            "font": {"color": "#000000"}  
        }]

    # Update the layout for value_locked_by_cat Graph
    plot23.update_layout(
            title=dict(
                text="Value Locked by Category",
                x=0.2,
                y=1,
                xanchor="center",
                yanchor="top"
            ),
            updatemenus=value_locked_by_cat_updatemenus
        )

    button_ranges_value_locked_by_block = {
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
        "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
        "1Y": [datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()],
        "3Y": [datetime.datetime.now() - datetime.timedelta(days=1095), datetime.datetime.now()],
        "All": [plot24.data[0].x[0], plot24.data[0].x[-1]]  # Placeholder for 'All' button range
        }

    button_labels_value_locked_by_block = ["1W", "1M", "1Q", "1Y", "3Y", "All"]

    value_locked_by_block_buttons = [
            {
                "label": button_label,
                "method": "relayout",
                "args": [
                    {"xaxis": {"range": button_ranges_value_locked_by_block[button_label], "tickformat": "%d-%b-%Y"}}
                ],
                }
            for button_label in button_labels_value_locked_by_block
        ]

    # Create the updatemenus configuration for value_locked_by_block Graph
    value_locked_by_block_updatemenus = [{
            "type": "buttons",
            "buttons": value_locked_by_block_buttons,
            "x": 0.14,
            "y": 1.1,
            "xanchor": "center",
            "yanchor": "bottom",
            "direction": "right",
            "showactive": True,
            "active": -1,
            "bgcolor": "white",
            "bordercolor": "black",
            "borderwidth": 1,
            "pad": {"r": 5, "t": 5},
            "font": {"color": "#000000"} 
        }]

    # Update the layout for value_locked_by_block Graph
    plot24.update_layout(
            title=dict(
                text="Value Locked by Blockchain",
                x=0.2,
                y=1,
                xanchor="center",
                yanchor="top"
            ),
            updatemenus=value_locked_by_block_updatemenus
        )

    button_ranges_total_stablecoin_supply = {
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
        "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
        "1Y": [datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()],
        "3Y": [datetime.datetime.now() - datetime.timedelta(days=1095), datetime.datetime.now()],
        "All": [plot25.data[0].x[0], plot25.data[0].x[-1]]  # Placeholder for 'All' button range
        }

    button_labels_total_stablecoin_supply = ["1W", "1M", "1Q", "1Y", "3Y", "All"]

    total_stablecoin_supply_buttons = [
            {
                "label": button_label,
                "method": "relayout",
                "args": [
                    {"xaxis": {"range": button_ranges_total_stablecoin_supply[button_label], "tickformat": "%d-%b-%Y"}}
                ],
                }
            for button_label in button_labels_total_stablecoin_supply
        ]

    # Create the updatemenus configuration for total_stablecoin_supply Graph
    total_stablecoin_supply_updatemenus = [{
            "type": "buttons",
            "buttons": total_stablecoin_supply_buttons,
            "x": 0.14,
            "y": 1.1,
            "xanchor": "center",
            "yanchor": "bottom",
            "direction": "right",
            "showactive": True,
            "active": -1,
            "bgcolor": "white",
            "bordercolor": "black",
            "borderwidth": 1,
            "pad": {"r": 5, "t": 5},
            "font": {"color": "#000000"} 
        }]

    # Update the layout for total_stablecoin_supply Graph
    plot25.update_layout(
            title=dict(
                text="Total Stablecoin Supply",
                x=0.2,
                y=1,
                xanchor="center",
                yanchor="top"
            ),
            updatemenus=total_stablecoin_supply_updatemenus
        )


    button_ranges_value_locked_by_liq = {
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
        "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
        "1Y": [datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()],
        "All": [plot26.data[0].x[0], plot26.data[0].x[-1]]  # Placeholder for 'All' button range
        }

    button_labels_value_locked_by_liq = ["1W", "1M", "1Q", "1Y", "All"]

    value_locked_by_liq_buttons = [
            {
                "label": button_label,
                "method": "relayout",
                "args": [
                    {"xaxis": {"range": button_ranges_value_locked_by_liq[button_label], "tickformat": "%d-%b-%Y"}}
                ],
                }
            for button_label in button_labels_value_locked_by_liq
        ]

    # Create the updatemenus configuration for value_locked_by_block Graph
    value_locked_by_liq_updatemenus = [{
            "type": "buttons",
            "buttons": value_locked_by_liq_buttons,
            "x": 0.14,
            "y": 1.1,
            "xanchor": "center",
            "yanchor": "bottom",
            "direction": "right",
            "showactive": True,
            "active": -1,
            "bgcolor": "white",
            "bordercolor": "black",
            "borderwidth": 1,
            "pad": {"r": 5, "t": 5},
            "font": {"color": "#000000"} 
        }]

    # Update the layout for value_locked_by_block Graph
    plot26.update_layout(
            title=dict(
                text="Value Locked: Liquid Staking",
                x=0.2,
                y=1,
                xanchor="center",
                yanchor="top"
            ),
            updatemenus=value_locked_by_liq_updatemenus
        )    

    col1, col2 = st.columns(2)
    col1.plotly_chart(plot23, use_container_width=True)
    col1.dataframe(value_locked_by_cat_table, hide_index = True)
    col2.plotly_chart(plot24, use_container_width=True)
    col2.dataframe(value_locked_by_block_table, hide_index = True)

    col1, col2 = st.columns(2)
    col1.plotly_chart(plot25, use_container_width=True)
    col1.dataframe(total_stablecoin_supply_table, hide_index = True)
    col2.plotly_chart(plot26, use_container_width=True)
    col2.dataframe(value_locked_by_liq_table, hide_index = True)
