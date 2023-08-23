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

st.title('Funding')

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

session4 = CachedSession('cache4', expire_after=timedelta(hours=1))

def create_plot9():
    url9 = "https://www.theblock.co/api/charts/chart/crypto-markets/futures/btc-funding-rates"
    r9 = session4.get(url9)
    r_json9 = r9.json()

    output_dataframe9 = pd.DataFrame()
    series_dict9 = r_json9['chart']['jsonFile']['Series']
    for vol in series_dict9:
        df_ = pd.DataFrame(series_dict9[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Funding'})
        df_['Exchange'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe9 = pd.concat([df_,output_dataframe9])

    # Convert date column to datetime format
    output_dataframe9['date'] = pd.to_datetime(output_dataframe9['date'])

    fig9 = go.Figure()
    btc_funding_rates_table_data = []

    exclude_token = ['KuCoin', 'FTX','Gate.io', 'ByBit']
    # Specify the desired color for the specific Exp indicator
    custom_color = '#FB4570'

    for token, group in output_dataframe9.groupby('Exchange'):
        if token not in exclude_token:
            fig9.add_trace(go.Scatter(
                        x=group['date'],
                        y=group['Funding'],
                        mode='lines',
                        name=token,
                        line=dict(color=custom_color if token == 'Bitfinex' else None)))

            fig9.update_layout(
                            xaxis=dict(
                            title="Date",
                            tickformat="%b-%y",
                            tickmode="linear",
                            dtick="M6"  # Display tick labels every 6 days
                        ),
                            yaxis=dict(title="Funding (%)"),
                            hovermode="x"
                        )

            fig9.update_layout(
                            legend=dict(
                            orientation="h",
                            y=-0.2,  # Adjust the value to control the vertical position of the legend
                            x=0.5,  # Adjust the value to control the horizontal position of the legend
                            xanchor='center'
                            )
                        )

            fig9.update_traces(
                            hovertemplate='<b>%{x|%d-%b-%y}</b><br>Funding: %{y:.2f}%'
                        )

            fig9.update_yaxes(ticksuffix="%")

            current_btc_funding_rates = group['Funding'].iloc[-1]

            # Calculate the current, last year, last month, last quarter btc_option_skew_delta values
            last_year_btc_funding_rates = group.loc[group['date'].dt.year == last_year_date.year, 'Funding'].values[-1]
            last_month_btc_funding_rates = group.loc[(group['date'].dt.year == last_month_date.year) & (group['date'].dt.month == last_month_date.month), 'Funding'].values[-1]
            last_quarter_btc_funding_rates = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date), 'Funding'].values[-1]
            last_week_btc_funding_rates = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date), 'Funding'].values[-1]

            # Calculate the change values as percentages
            last_week_change = current_btc_funding_rates - last_week_btc_funding_rates
            last_month_change = current_btc_funding_rates - last_month_btc_funding_rates
            last_year_change = current_btc_funding_rates - last_year_btc_funding_rates
            last_quarter_change = current_btc_funding_rates - last_quarter_btc_funding_rates

            # Format eth_funding_ratesvalues as percentages
            current_btc_funding_rates_str = f'{current_btc_funding_rates:.2f}%'
            last_week_btc_funding_rates_str = f'{last_week_btc_funding_rates:.2f}%'
            last_month_btc_funding_rates_str = f'{last_month_btc_funding_rates:.2f}%'
            last_year_btc_funding_rates_str = f'{last_year_btc_funding_rates:.2f}%'
            last_quarter_btc_funding_rates_str = f'{last_quarter_btc_funding_rates:.2f}%'

            # Create a dictionary for the indicator's btc_funding_rates data
            indicator_data = {
                'Indicator': token,
                'WTD': last_week_btc_funding_rates_str,
                'WTD (Δ)': f'{last_week_change:.2f}%',
                'MTD': last_month_btc_funding_rates_str,
                'MTD (Δ)': f'{last_month_change:.2f}%',
                'QTD': last_quarter_btc_funding_rates_str,
                'QTD (Δ)': f'{last_quarter_change:.2f}%',
                'YTD': last_year_btc_funding_rates_str,
                'YTD (Δ)': f'{last_year_change:.2f}%'
            }

            # Append the indicator's data to the btc_funding_rates_table_data list
            btc_funding_rates_table_data.append(indicator_data)

        # Create the bbtc_funding_rates_table DataFrame
        btc_funding_rates_table = pd.DataFrame(btc_funding_rates_table_data)


    return fig9, btc_funding_rates_table

def create_plot10():
    url10 = "https://www.theblock.co/api/charts/chart/crypto-markets/futures/eth-funding-rates"
    r10 = session4.get(url10)
    r_json10 = r10.json()

    output_dataframe10 = pd.DataFrame()
    series_dict10 = r_json10['chart']['jsonFile']['Series']
    for vol in series_dict10:
        df_ = pd.DataFrame(series_dict10[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Funding'})
        df_['Exchange'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe10 = pd.concat([df_,output_dataframe10])

    # Convert date column to datetime format
    output_dataframe10['date'] = pd.to_datetime(output_dataframe10['date'])

    fig10 = go.Figure()
    eth_funding_rates_table_data = []

    exclude_token = ['KuCoin', 'FTX','Gate.io','ByBit']
    # Specify the desired color for the specific Exp indicator
    custom_color = '#FB4570'

    for token, group in output_dataframe10.groupby('Exchange'):
        if token not in exclude_token:
            fig10.add_trace(go.Scatter(
                        x=group['date'],
                        y=group['Funding'],
                        mode='lines',
                        name=token,
                        line=dict(color=custom_color if token == 'Bitfinex' else None)))

            fig10.update_layout(
                            xaxis=dict(
                            title="Date",
                            tickformat="%b-%y",
                            tickmode="linear",
                            dtick="M6"  # Display tick labels every 6 days
                        ),
                            yaxis=dict(title="Funding (%)"),
                            hovermode="x"
                        )

            fig10.update_layout(
                            legend=dict(
                            orientation="h",
                            y=-0.2,  # Adjust the value to control the vertical position of the legend
                            x=0.5,  # Adjust the value to control the horizontal position of the legend
                            xanchor='center'
                            )
                        )

            fig10.update_traces(
                            hovertemplate='<b>%{x|%d-%b-%y}</b><br>Funding: %{y:.2f}%'
                        )

            fig10.update_yaxes(ticksuffix="%")

            current_eth_funding_rates = group['Funding'].iloc[-1]

            # Calculate the current, last year, last month, last quarter btc_option_skew_delta values
            last_year_eth_funding_rates = group.loc[group['date'].dt.year == last_year_date.year, 'Funding'].values[-1]
            last_month_eth_funding_rates = group.loc[(group['date'].dt.year == last_month_date.year) & (group['date'].dt.month == last_month_date.month), 'Funding'].values[-1]
            last_quarter_eth_funding_rates = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date), 'Funding'].values[-1]
            last_week_eth_funding_rates = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date), 'Funding'].values[-1]

            # Calculate the change values as percentages
            last_week_change = current_eth_funding_rates - last_week_eth_funding_rates
            last_month_change = current_eth_funding_rates - last_month_eth_funding_rates
            last_year_change = current_eth_funding_rates - last_year_eth_funding_rates
            last_quarter_change = current_eth_funding_rates - last_quarter_eth_funding_rates

            # Format eth_funding_ratesvalues as percentages
            current_eth_funding_rates_str =  f'{current_eth_funding_rates:.2f}%'
            last_week_eth_funding_rates_str = f'{last_week_eth_funding_rates:.2f}%'
            last_month_eth_funding_rates_str = f'{last_month_eth_funding_rates:.2f}%'
            last_year_eth_funding_rates_str = f'{last_year_eth_funding_rates:.2f}%'
            last_quarter_eth_funding_rates_str = f'{last_quarter_eth_funding_rates:.2f}%'

            # Create a dictionary for the indicator's eth_funding_rates data
            indicator_data = {
                'Indicator': token,
                'WTD': last_week_eth_funding_rates_str,
                'WTD (Δ)': f'{last_week_change:.2f}%',
                'MTD': last_month_eth_funding_rates_str,
                'MTD (Δ)': f'{last_month_change:.2f}%',
                'QTD': last_quarter_eth_funding_rates_str,
                'QTD (Δ)': f'{last_quarter_change:.2f}%',
                'YTD': last_year_eth_funding_rates_str,
                'YTD (Δ)': f'{last_year_change:.2f}%'
            }

            # Append the indicator's data to the eth_funding_rates_table_data list
            eth_funding_rates_table_data.append(indicator_data)

        # Create the eth_funding_rates_table DataFrame
        eth_funding_rates_table = pd.DataFrame(eth_funding_rates_table_data)

    return fig10, eth_funding_rates_table

def create_plot15():
    url15 = "https://www.theblock.co/api/charts/chart/crypto-markets/spot/btc-spot-to-futures-volume"
    r15 = session4.get(url15)
    r_json15 = r15.json()

    output_dataframe15 = pd.DataFrame()
    series_dict15 = r_json15['chart']['jsonFile']['Series']
    for vol in series_dict15:
        df_ = pd.DataFrame(series_dict15[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'Volume'})
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%d %b %Y"))
        output_dataframe15 = pd.concat([df_, output_dataframe15])

    output_dataframe15['date'] = pd.to_datetime(output_dataframe15['date'])

    # Calculate the "All-Time High" and "Current Market Cap" values
    all_time_high = output_dataframe15['Volume'].max()
    all_time_low = output_dataframe15['Volume'].min()
    current_btc_spot_to_futures_volume = output_dataframe15['Volume'].iloc[-1]

    fig15 = px.line(output_dataframe15, x='date', y='Volume')
    fig15.update_layout(
        xaxis_title="Date",
        yaxis_title="Spot to Futures Volume",
        hovermode="x",
    )
    fig15.update_traces(line_color="#7030A0")

    fig15.update_xaxes(
        tickformat="%b-%y",  # Format x-axis tick labels as "Jun-22", "Jun-23", etc.
        tickmode="linear",  # Set tick mode to linear
        dtick="M6",  # Display tick labels every 12 months
    )

    fig15.update_traces(hovertemplate='<b>%{x|%d-%b-%y}</b><br>Ratio: %{y}')

    # Add custom legend items as annotations
    fig15.add_annotation(
        xref="paper",
        yref="paper",
        x=0.02,
        y=0.98,
        xanchor="left",
        yanchor="top",
        text=f"All-Time High: {all_time_high:.3f}",
        showarrow=False,
        align="left",
        font=dict(
            family="Arial",
            size=12,
            color="white"
        )
    )

    # Add custom legend items as annotations
    fig15.add_annotation(
        xref="paper",
        yref="paper",
        x=0.02,
        y=0.94,
        xanchor="left",
        yanchor="top",
        text=f"All-Time Low: {all_time_low:.3f}",
        showarrow=False,
        align="left",
        font=dict(
            family="Arial",
            size=12,
            color="white"
        )
    )

    fig15.add_annotation(
        xref="paper",
        yref="paper",
        x=0.02,
        y=0.90,
        xanchor="left",
        yanchor="top",
        text=f"Current: {current_btc_spot_to_futures_volume:.3f}",
        showarrow=False,
        align="left",
        font=dict(
            family="Arial",
            size=12,
            color="white"
        )
    )

    # Calculate the last year's btc_spot_to_futures_volume using the last date of the previous year
    last_year_btc_spot_to_futures_volume= output_dataframe15.loc[output_dataframe15['date'].dt.year == last_year_date.year, 'Volume'].values[-1]

    # Calculate the last month's btc_spot_to_futures_volume
    last_month_btc_spot_to_futures_volume = output_dataframe15.loc[output_dataframe15['date'].dt.year == last_month_date.year]
    last_month_btc_spot_to_futures_volume = last_month_btc_spot_to_futures_volume.loc[last_month_btc_spot_to_futures_volume['date'].dt.month == last_month_date.month]
    last_month_btc_spot_to_futures_volume = last_month_btc_spot_to_futures_volume['Volume'].values[-1]

    # Calculate the last quarter's btc_spot_to_futures_volume
    # last_quarter_start_date = last_quarter_date - datetime.timedelta(days=89)  # Assuming 90 days per quarter
    last_quarter_btc_spot_to_futures_volume = output_dataframe15.loc[(output_dataframe15['date'].dt.date >= last_quarter_start_date) & (output_dataframe15['date'].dt.date <= last_quarter_date)]
    last_quarter_btc_spot_to_futures_volume = last_quarter_btc_spot_to_futures_volume['Volume'].values[-1]

    # Calculate the last week's btc_spot_to_futures_volume
    last_week_btc_spot_to_futures_volume = output_dataframe15.loc[(output_dataframe15['date'].dt.date >= last_week_start_date) & (output_dataframe15['date'].dt.date <= last_week_date)]
    last_week_btc_spot_to_futures_volume = last_week_btc_spot_to_futures_volume['Volume'].values[-1]

    # Format btc_spot_to_futures_volumevalues in trillions
    current_btc_spot_to_futures_volume_str = f'{current_btc_spot_to_futures_volume:.3f}'
    last_week_btc_spot_to_futures_volume_str = f'{last_week_btc_spot_to_futures_volume:.3f}'
    last_month_btc_spot_to_futures_volume_str = f'{last_month_btc_spot_to_futures_volume:.3f}'
    last_year_btc_spot_to_futures_volume_str = f'{last_year_btc_spot_to_futures_volume:.3f}'
    last_quarter_btc_spot_to_futures_volume_str = f'{last_quarter_btc_spot_to_futures_volume:.3f}'

    # Calculate the change values as percentages
    last_week_change = ((current_btc_spot_to_futures_volume - last_week_btc_spot_to_futures_volume) / last_week_btc_spot_to_futures_volume) * 100
    last_month_change = ((current_btc_spot_to_futures_volume - last_month_btc_spot_to_futures_volume) / last_month_btc_spot_to_futures_volume) * 100
    last_year_change = ((current_btc_spot_to_futures_volume - last_year_btc_spot_to_futures_volume) / last_year_btc_spot_to_futures_volume) * 100
    last_quarter_change = ((current_btc_spot_to_futures_volume - last_quarter_btc_spot_to_futures_volume) / last_quarter_btc_spot_to_futures_volume) * 100

    # Create the market cap table
    btc_spot_to_futures_volume_table = pd.DataFrame({
        'Period': ['WTD', 'MTD','QTD', 'YTD'],
        'Volume': [last_week_btc_spot_to_futures_volume_str, last_month_btc_spot_to_futures_volume_str,last_quarter_btc_spot_to_futures_volume_str, last_year_btc_spot_to_futures_volume_str],
        'Date': [last_week_date.strftime("%d %b %Y"), last_month_date.strftime("%d %b %Y"),last_quarter_date.strftime("%d %b %Y"), last_year_date.strftime("%d %b %Y")],
        'Change (%)': [f'{last_week_change:.2f}%', f'{last_month_change:.2f}%', f'{last_quarter_change:.2f}%', f'{last_year_change:.2f}%']
    })

    return fig15, btc_spot_to_futures_volume_table


plot9 = None
plot10 = None
plot15 = None
eth_funding_rates_table = None
btc_funding_rates_table = None
btc_spot_to_futures_volume_table = None

# Define a function to update the plot and table variables
def update_plots_and_tables():
    global plot9, btc_funding_rates_table
    global plot10, eth_funding_rates_table
    global plot15, btc_spot_to_futures_volume_table
    plot9, btc_funding_rates_table = create_plot9()
    plot10, eth_funding_rates_table = create_plot10()
    plot15, btc_spot_to_futures_volume_table = create_plot15()

# Call the function to update the plots and tables
# Start a separate thread to create the plots
plots_thread = Thread(target=update_plots_and_tables)
plots_thread.start()

# Wait for the plot creation thread to complete
plots_thread.join()

if plot9 is not None and plot10 is not None and plot15 is not None:
    # Buttons for BTC Transactions Graph
    button_ranges_btc_funding_rates = {
    "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
    "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
    "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
    "All": [plot9.data[0].x[0], plot9.data[0].x[-1]]  # Placeholder for 'All' button range
    }

    button_labels_btc_funding_rates = ["1W", "1M", "1Q", "All"]

    btc_funding_rates_buttons = [
        {
            "label": button_label,
            "method": "relayout",
            "args": [
                {"xaxis": {"range": button_ranges_btc_funding_rates[button_label], "tickformat": "%d-%b-%Y"}}
            ],
            }
        for button_label in button_labels_btc_funding_rates
    ]

    # Create the updatemenus configuration for btc_funding_rates Graph
    btc_funding_rates_updatemenus = [{
        "type": "buttons",
        "buttons": btc_funding_rates_buttons,
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

    # Update the layout for btc_funding_rates Graph
    plot9.update_layout(
        title=dict(
            text="BTC Funding Rates",
            x=0.2,
            y=1,
            xanchor="center",
            yanchor="top"
        ),
        updatemenus=btc_funding_rates_updatemenus
    )

    # Buttons for BTC Transactions Graph
    button_ranges_eth_funding_rates = {
    "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
    "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
    "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
    "All": [plot10.data[0].x[0], plot10.data[0].x[-1]]  # Placeholder for 'All' button range
    }

    button_labels_eth_funding_rates = ["1W", "1M", "1Q", "All"]

    eth_funding_rates_buttons = [
        {
            "label": button_label,
            "method": "relayout",
            "args": [
                {"xaxis": {"range": button_ranges_eth_funding_rates[button_label], "tickformat": "%d-%b-%Y"}}
            ],
            }
        for button_label in button_labels_btc_funding_rates
    ]

    # Create the updatemenus configuration for eth_funding_rates Graph
    eth_funding_rates_updatemenus = [{
        "type": "buttons",
        "buttons": eth_funding_rates_buttons,
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

    # Update the layout for eth_funding_rates Graph
    plot10.update_layout(
        title=dict(
            text="ETH Funding Rates",
            x=0.2,
            y=1,
            xanchor="center",
            yanchor="top"
        ),
        updatemenus=eth_funding_rates_updatemenus
    )

    # Buttons for BTC Transactions Graph
    button_ranges_btc_spot_to_futures_volume = {
    "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
    "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
    "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
    "1Y": [datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()],
    "3Y": [datetime.datetime.now() - datetime.timedelta(days=1095), datetime.datetime.now()],
    "All": [plot15.data[0].x[0], plot15.data[0].x[-1]]  # Placeholder for 'All' button range
    }

    button_labels_btc_spot_to_futures_volume = ["1W", "1M", "1Q", "1Y", "3Y", "All"]

    btc_spot_to_futures_volume_buttons = [
        {
            "label": button_label,
            "method": "relayout",
            "args": [
                {"xaxis": {"range": button_ranges_btc_spot_to_futures_volume[button_label], "tickformat": "%d-%b-%Y"}}
            ],
            }
        for button_label in button_labels_btc_spot_to_futures_volume
    ]

    # Create the updatemenus configuration for btc_funding_rates Graph
    btc_spot_to_futures_volume_updatemenus = [{
        "type": "buttons",
        "buttons": btc_spot_to_futures_volume_buttons,
        "x": 0.14,
        "y": -0.21,
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

    # Update the layout for btc_spot_to_futures_volume Graph
    plot15.update_layout(
        title=dict(
            text="Spot to Futures Volume",
            x=0.2,
            y=1,
            xanchor="center",
            yanchor="top"
        ),
        updatemenus=btc_spot_to_futures_volume_updatemenus
    )
    
    col1, col2 = st.columns(2)

    col1.plotly_chart(plot9, use_container_width=True)
    col1.dataframe(btc_funding_rates_table, hide_index = True)
    col2.plotly_chart(plot10, use_container_width=True)
    col2.dataframe(eth_funding_rates_table, hide_index = True)

    col1, col2 = st.columns(2)

    col1.plotly_chart(plot15, use_container_width=True)
    col1.dataframe(btc_spot_to_futures_volume_table, hide_index = True)