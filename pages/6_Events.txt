import requests
import pandas as pd
import datetime
import schedule
import time
import json
import plotly.express as px
import streamlit as st
import numpy as np
from threading import Thread
import plotly.graph_objects as go
from requests.auth import HTTPBasicAuth
import pytz
from requests_cache import CachedSession
from datetime import timedelta
from plotly.subplots import make_subplots  # Import make_subplots function
import base64
from pathlib import Path
import validators
from streamlit_option_menu import option_menu

st.set_page_config(
    # Set page configuration
    layout="wide")

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

current_date = datetime.datetime.now().date()
last_year_date = datetime.date(current_date.year - 1, 12, 31)
last_month_date = datetime.date(current_date.year, current_date.month - 1, 30)
last_quarter_date = datetime.date(current_date.year, ((current_date.month - 1) // 3) * 3 + 1, 1) - datetime.timedelta(days=1)
last_quarter_start_date = last_quarter_date - datetime.timedelta(days=89)
weekday = current_date.weekday()
days_to_subtract = (weekday - 4) % 7  # Calculate the number of days to subtract to reach the previous Friday
last_week_date = current_date - datetime.timedelta(days=days_to_subtract)
last_week_start_date = last_week_date - datetime.timedelta(days=6)  # Assuming 7 days in a week

# Create a requests_cache session with a cache expiration time of 1 hour
session6 = CachedSession('cache6', expire_after=timedelta(hours=1))

st.title("Events")

tab1,tab2 = st.tabs(["Liquidations","Others"])

with tab1:
    def load_btc_price_data():
        url70 = "https://www.theblock.co/api/charts/chart/crypto-markets/prices/btc-price"
        r70 = session6.get(url70)
        r_json70 = r70.json()

        output_dataframe70 = pd.DataFrame()
        series_dict70 = r_json70['chart']['jsonFile']['Series']
        for vol in series_dict70:
            df_ = pd.DataFrame(series_dict70[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'BTC Price'})
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%Y-%m-%d"))
            output_dataframe70 = pd.concat([df_, output_dataframe70])

        output_dataframe70['date'] = pd.to_datetime(output_dataframe70['date'])
        # Filter the DataFrame to include dates after December 31, 2022
        specific_date = datetime.datetime(2023, 5, 24)
        output_dataframe70 = output_dataframe70[output_dataframe70['date'] > specific_date]

        return output_dataframe70

    def load_eth_price_data():
        url71 = "https://www.theblock.co/api/charts/chart/crypto-markets/prices/eth-price"
        r71 = session6.get(url71)
        r_json71 = r71.json()

        output_dataframe71 = pd.DataFrame()
        series_dict71 = r_json71['chart']['jsonFile']['Series']
        for vol in series_dict71:
            df_ = pd.DataFrame(series_dict71[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'ETH Price'})
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%Y-%m-%d"))
            output_dataframe71 = pd.concat([df_, output_dataframe71])

        output_dataframe71['date'] = pd.to_datetime(output_dataframe71['date'])
        # Filter the DataFrame to include dates after December 31, 2022
        specific_date = datetime.datetime(2023, 5, 24)
        output_dataframe71 = output_dataframe71[output_dataframe71['date'] > specific_date]

        return output_dataframe71

    # Load and preprocess data for BTC liquidation graph
    def load_liquidation_data():
        url72 = "https://www.theblock.co/api/charts/chart/crypto-markets/futures/btc-liquidations"
        r72 = session6.get(url72)
        r_json72 = r72.json()

        output_dataframe72 = pd.DataFrame()
        series_dict72 = r_json72['chart']['jsonFile']['Series']
        for vol in series_dict72:
            df_ = pd.DataFrame(series_dict72[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'Liquidations'})
            df_['Type'] = vol
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%Y-%m-%d"))
            output_dataframe72 = pd.concat([df_, output_dataframe72])

        output_dataframe72['date'] = pd.to_datetime(output_dataframe72['date'])
        return output_dataframe72

    def create_combined_plot():
        btc_price_data = load_btc_price_data()
        liquidation_data = load_liquidation_data()
        eth_price_data = load_eth_price_data()

        max_range_liquidation = liquidation_data['Liquidations'].max()
        max_range_btc = btc_price_data['BTC Price'].max()
        min_range_liquidation = liquidation_data['Liquidations'].min()
        min_range_btc = btc_price_data['BTC Price'].min()
        max_range_eth = eth_price_data['ETH Price'].max()
        min_range_eth = eth_price_data['ETH Price'].min()

        #fig = make_subplots(specs=[[{"secondary_y": True}]])
        #fig = make_subplots(specs=[[{"secondary_y": True}, {"secondary_y": True}]])
        fig = go.Figure()

        # Add primary y-axis (BTC Liquidations)
        for performance_type, group in liquidation_data.groupby('Type'):
            if performance_type == 'Shorts':
                fig.add_trace(
                    go.Bar(
                        x=group['date'],
                        y=group['Liquidations'],
                        name=performance_type,
                        marker_color='#FF9999'
                    )#,secondary_y=False
                )
            else:
                fig.add_trace(
                    go.Bar(
                        x=group['date'],
                        y=group['Liquidations'],
                        name=performance_type,
                        marker_color="#7030A0"
                    )#,secondary_y=False

                )

        # Add secondary y-axis (ETH Price)
        fig.add_trace(
            go.Scatter(
                x=btc_price_data['date'],
                y=btc_price_data['BTC Price'],
                mode='lines',
                name='BTC Price',
                yaxis='y2',
                line=dict(color='grey')
            )#,secondary_y=True
        )

        fig.add_trace(
            go.Scatter(
                x=eth_price_data['date'],
                y=eth_price_data['ETH Price'],
                mode='lines',
                name='ETH Price',
                yaxis='y3',
                line=dict(color='#165BAA')
            )#,secondary_y=True
        )

        fig.update_layout(
        yaxis=dict(
            title="BTC Liquidations",
            side="right",
            range=[min_range_liquidation, max_range_liquidation]
        ),
        yaxis2=dict(
            title="BTC Price",
            side="left",
            range=[min_range_btc, max_range_btc],
            overlaying="y",
            tickmode="sync",
            anchor="x"
        ),
        yaxis3=dict(
            title="ETH Price",
            side="left",
            range=[min_range_eth, max_range_eth],
            overlaying="y",
            tickmode="sync",
            anchor="free",
            autoshift=True,
            shift=-20
        )
    )

        fig.update_layout(
                        legend=dict(
                        orientation="h",
                        y=-0.3,  # Adjust the value to control the vertical position of the legend
                        x=0.5,  # Adjust the value to control the horizontal position of the legend
                        xanchor='center'
                        ), width=1000
                    )
        
        # Layout settings
        fig.update_layout(
            title='BTC Liquidations and BTC/ETH Price',
            xaxis_title="Date",
            #yaxis_title="BTC Liquidations",
            hovermode="x"
        )

        # Set y-axis titles
        #fig.update_yaxes(title_text="BTC Liquidations")#, secondary_y=False)
        #fig.update_yaxes(title_text="BTC Price")#, secondary_y=True)
        #fig.update_yaxes(title_text="ETH Price")

        fig.update_yaxes(tickprefix="$")

        x_tickvals = liquidation_data['date'][::10]
        x_ticklabels = x_tickvals.dt.strftime('%d-%b-%Y')
        fig.update_xaxes(tickvals=x_tickvals, ticktext=x_ticklabels)

        return fig

    def load_vol_of_vol_data():
        url71 = "https://www.theblock.co/api/charts/chart/crypto-markets/options/btc-dvol-index-vol-of-vol"
        r71 = requests.get(url71)
        r_json71 = r71.json()

        # Extract data for the primary y-axis (Vol of Vol)
        vol_of_vol_data = pd.DataFrame(r_json71['chart']['jsonFile']['Series']['Vol of Vol']['Data'])
        vol_of_vol_data['date'] = pd.to_datetime(vol_of_vol_data['Timestamp'], unit='s')
        vol_of_vol_data.rename(columns={'Result': 'Vol of Vol'}, inplace=True)

        # Extract data for the secondary y-axis (DVol Index)
        dvol_index_data = pd.DataFrame(r_json71['chart']['jsonFile']['Series']['DVol Index']['Data'])
        dvol_index_data['date'] = pd.to_datetime(dvol_index_data['Timestamp'], unit='s')
        dvol_index_data.rename(columns={'Result': 'DVol Index'}, inplace=True)

        output_dataframe71 = pd.merge(vol_of_vol_data[['date', 'Vol of Vol']], dvol_index_data[['date', 'DVol Index']], on='date')
        specific_date = datetime.datetime(2023, 5, 24)
        output_dataframe71 = output_dataframe71[output_dataframe71['date'] > specific_date]

        return output_dataframe71

    # Load and preprocess data for BTC liquidation graph
    def load_implied_volatility_data():
        url74 = "https://www.theblock.co/api/charts/chart/crypto-markets/options/btc-atm-implied-volatility"
        r74 = session6.get(url74)
        r_json74 = r74.json()

        output_dataframe74 = pd.DataFrame()
        series_dict74 = r_json74['chart']['jsonFile']['Series']
        for vol in series_dict74:
            if vol == 'ATM 30':
                df_ = pd.DataFrame(series_dict74[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'Volatility'})
                df_['ATM'] = vol
                df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%Y-%m-%d"))
                output_dataframe74 = pd.concat([df_, output_dataframe74])

        output_dataframe74['date'] = pd.to_datetime(output_dataframe74['date'])
        specific_date = datetime.datetime(2023, 5, 24)
        output_dataframe74 = output_dataframe74[output_dataframe74['date'] > specific_date]

        return output_dataframe74

    def create_combined_plot1():
        implied_volatility_data = load_implied_volatility_data()
        vol_of_vol_data = load_vol_of_vol_data()

        max_range_volatility = implied_volatility_data['Volatility'].max()
        min_range_volatility = implied_volatility_data['Volatility'].min()
        max_range_vol_of_vol = vol_of_vol_data['Vol of Vol'].max()
        min_range_vol_of_vol = vol_of_vol_data['Vol of Vol'].min()
        max_range_dvol = vol_of_vol_data['DVol Index'].max()
        min_range_dvol = vol_of_vol_data['DVol Index'].min()

        fig1 = go.Figure()

        fig1.add_trace(go.Scatter(x=vol_of_vol_data['date'], y=vol_of_vol_data['Vol of Vol'], name='Vol of Vol', yaxis='y', line=dict(color='orange')))

        # Add DVol Index trace to the secondary y-axis
        fig1.add_trace(go.Scatter(x=vol_of_vol_data['date'], y=vol_of_vol_data['DVol Index'], name='DVol Index', yaxis='y2'))

        # Add secondary y-axis (ETH Price)
        fig1.add_trace(
            go.Scatter(
                x=implied_volatility_data['date'],
                y=implied_volatility_data['Volatility'],
                mode='lines',
                name='BTC Implied Volatility',
                yaxis='y3',
                line=dict(color='#00BFFF')
            )#,secondary_y=True
        )

        fig1.update_layout(
        yaxis=dict(
            title="BTC Vol of Vol",
            side="left",
            range=[min_range_vol_of_vol, max_range_vol_of_vol]
        ),
        yaxis2=dict(
            title="BTC DVol Index",
            side="right",
            range=[min_range_dvol, max_range_dvol],
            overlaying="y",
            tickmode="sync",
            anchor="x"
        ),
        yaxis3=dict(
            title="BTC Implied Volatility",
            side="right",
            range=[min_range_volatility, max_range_volatility],
            overlaying="y",
            tickmode="sync",
            anchor="free",
            autoshift=True,
            shift=18,
            ticksuffix="%"
        )
    )

        fig1.update_layout(
                        legend=dict(
                        orientation="h",
                        y=-0.3,  # Adjust the value to control the vertical position of the legend
                        x=0.5,  # Adjust the value to control the horizontal position of the legend
                        xanchor='center'
                        ), width=1000
                    )
        
        # Layout settings
        fig1.update_layout(
            title='BTC DVol Index & Vol of Vol (Deribit) & Implied Volatility',
            xaxis_title="Date",
            #yaxis_title="BTC Liquidations",
            hovermode="x"
        )

        x_tickvals = vol_of_vol_data['date'][::10]
        x_ticklabels = x_tickvals.dt.strftime('%d-%b-%Y')
        fig1.update_xaxes(tickvals=x_tickvals, ticktext=x_ticklabels)

        return fig1
    
    def load_btc_OI_data():
        url18 = "https://www.theblock.co/api/charts/chart/crypto-markets/futures/aggregated-open-interest-of-bitcoin-futures-daily"
        r18 = session6.get(url18)
        r_json18 = r18.json()

        output_dataframe18 = pd.DataFrame()
        series_dict18 = r_json18['chart']['jsonFile']['Series']
        for vol in series_dict18:
            df_ = pd.DataFrame(series_dict18[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'OI'})
            df_['Exchange'] = vol
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
            #df_.drop_duplicates(subset='date', keep='last', inplace=True)
            output_dataframe18 = pd.concat([df_,output_dataframe18])

        # Convert date column to datetime format
        output_dataframe18['date'] = pd.to_datetime(output_dataframe18['date'])
        specific_date = datetime.datetime(2023, 5, 24)
        output_dataframe18 = output_dataframe18[output_dataframe18['date'] > specific_date]

        summed_dataframe = output_dataframe18.groupby('date')['OI'].sum().reset_index()

        return summed_dataframe

    def load_eth_OI_data():
        url19 = "https://www.theblock.co/api/charts/chart/crypto-markets/futures/aggregated-open-interest-of-ethereum-futures-daily"
        r19 = session6.get(url19)
        r_json19 = r19.json()

        output_dataframe19 = pd.DataFrame()
        series_dict19 = r_json19['chart']['jsonFile']['Series']
        for vol in series_dict19:
            df_ = pd.DataFrame(series_dict19[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'OI'})
            df_['Exchange'] = vol
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
            #df_.drop_duplicates(subset='date', keep='last', inplace=True)
            output_dataframe19 = pd.concat([df_,output_dataframe19])

        # Convert date column to datetime format
        output_dataframe19['date'] = pd.to_datetime(output_dataframe19['date'])
        specific_date = datetime.datetime(2023, 5, 24)
        output_dataframe19 = output_dataframe19[output_dataframe19['date'] > specific_date]

        summed_dataframe1 = output_dataframe19.groupby('date')['OI'].sum().reset_index()

        return summed_dataframe1
    
    def load_value_locked_data():
        url24 = "https://www.theblock.co/api/charts/chart/decentralized-finance/total-value-locked-tvl/value-locked-by-blockchain"
        r24 = session6.get(url24)
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
        specific_date = datetime.datetime(2023, 5, 24)
        output_dataframe24 = output_dataframe24[output_dataframe24['date'] > specific_date]

        summed_dataframe2 = output_dataframe24.groupby('date')['Value'].sum().reset_index()

        return summed_dataframe2

    def create_combined_plot2():
        btc_OI_data = load_btc_OI_data()
        eth_OI_data = load_eth_OI_data()
        value_locked_data = load_value_locked_data()

        max_range_btc_OI = btc_OI_data['OI'].max()
        min_range_btc_OI = btc_OI_data['OI'].min()
        #max_range_eth_OI = eth_OI_data['OI'].max()
        #min_range_eth_OI = eth_OI_data['OI'].min()
        max_range_value_locked = value_locked_data['Value'].max()
        min_range_value_locked = value_locked_data['Value'].min()

        fig2 = go.Figure()

        fig2.add_trace(go.Scatter(
            x=eth_OI_data['date'],
            y=eth_OI_data['OI'],
            fill='tonexty',  # Fill the area below the line
            mode='lines',    # Display as lines
            name='ETH Futures',
            line=dict(color='#00BFFF'),
            fillcolor='rgba(0, 191, 255, 0.5)',
            yaxis='y'
        ))

        fig2.add_trace(go.Scatter(
            x=btc_OI_data['date'],
            y=btc_OI_data['OI'],
            fill='tonexty',  # Fill the area below the line
            mode='lines',    # Display as lines
            name='BTC Futures',
            line=dict(color='#165BAA'),
            fillcolor='rgba(22, 91, 170, 0.5)',
            yaxis='y'
        ))

        fig2.add_trace(
            go.Scatter(
                x=value_locked_data['date'],
                y=value_locked_data['Value'],
                mode='lines',
                name='DeFi TVL',
                line=dict(color='orange'),
                yaxis='y2'
            )
        )

        # Set up the secondary y-axis
        fig2.update_layout(
            yaxis2=dict(
                title='DeFi TVL',  # Secondary y-axis title
                overlaying='y',    # Overlay the secondary y-axis on top of the primary y-axis
                side='right',
                tickmode="sync"       # Position of the secondary y-axis
            )
        )

        fig2.update_layout(
                        legend=dict(
                        orientation="h",
                        y=-0.3,  # Adjust the value to control the vertical position of the legend
                        x=0.5,  # Adjust the value to control the horizontal position of the legend
                        xanchor='center'
                        ), width=1000
                    )
        
        # Layout settings
        fig2.update_layout(
            title='Aggregated Open Interest BTC/ETH Futures & DeFi TVL',
            xaxis_title="Date",
            yaxis_title="Aggregated Open Interest",
            hovermode="x"
        )

        fig2.update_yaxes(tickprefix="$")

        x_tickvals = btc_OI_data['date'][::10]
        x_ticklabels = x_tickvals.dt.strftime('%d-%b-%Y')
        fig2.update_xaxes(tickvals=x_tickvals, ticktext=x_ticklabels)

        return fig2
    

    # Call the function to get the combined plot
    combined_plot = None
    combined_plot1 = None
    combined_plot2 = None

    # Define a function to update the plot and table variables
    def update_plots_and_tables():
        global combined_plot
        global combined_plot1
        global combined_plot2   

        combined_plot = create_combined_plot()
        combined_plot1 = create_combined_plot1()
        combined_plot2 = create_combined_plot2()

    # Call the function to update the plots and tables
    # Start a separate thread to create the plots
    plots_thread = Thread(target=update_plots_and_tables)
    plots_thread.start()

    # Wait for the plot creation thread to complete
    plots_thread.join()

    #if combined_plot is not None and plot71 is not None:

        # Use Streamlit's selectbox to create a single set of buttons
    selected_range = st.selectbox("Select Timeframe:", ["All", "1W", "1M"])

    button_ranges_combined = {
        "All": [combined_plot.data[0].x[0], combined_plot.data[0].x[-1]],  # Placeholder for 'All' button range
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()]
        }

        #button_labels_combined = ["1W", "1M", "All"]
    
    # Apply the selected range to both plots
    combined_plot.update_xaxes(range=button_ranges_combined[selected_range])
    combined_plot1.update_xaxes(range=button_ranges_combined[selected_range])
    combined_plot2.update_xaxes(range=button_ranges_combined[selected_range])
        
    combined_plot
    combined_plot2
    combined_plot1