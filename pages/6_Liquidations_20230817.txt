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

with st.sidebar:
    image = "https://forteus-media-research.s3.eu-west-1.amazonaws.com/public/images/Final+Logo+Forteus+by+Numeus+light.png"  # Replace with the actual path to your photo
    image_size = (300, 200)  # Replace with the desired width and height of the image in pixels
        #st.image(image, width=image_size[0], use_column_width=False)
    st.markdown(
            f'<div style="display: flex; justify-content: center;"><img src="{image}" width="{image_size[0]}"></div>',
            unsafe_allow_html=True)
    st.markdown('<div style="display: flex; justify-content: center;"><h1>August Market Update</h1></div>', unsafe_allow_html=True)
        #st.markdown("# July Market Update")

st.title('Liquidations')

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

# Create a requests_cache session with a cache expiration time of 1 hour
session6 = CachedSession('cache6', expire_after=timedelta(hours=1))

def create_plot70():
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

    # Calculate the "All-Time High" and "Current Market Cap" values
    current_btc_price = output_dataframe70['BTC Price'].iloc[-1]

    fig70 = px.line(output_dataframe70, x='date', y='BTC Price' , title='BTC Price')
    fig70.update_layout(
            xaxis_title="Date",
            yaxis_title="BTC Price",
            hovermode="x",
        )
    fig70.update_xaxes(
            tickformat="%b-%y",  # Format x-axis tick labels as "Jun-22", "Jun-23", etc.
            tickmode="linear",  # Set tick mode to linear
            dtick="M12",  # Display tick labels every 12 months
        )

    fig70.update_traces(hovertemplate='<b>%{x|%d-%b-%y}</b><br>BTC Price: %{y}')
    fig70.update_traces(line_color="#7030A0")

    fig70.update_yaxes(tickprefix="$")

    fig70.add_annotation(
            xref="paper",
            yref="paper",
            x=0.02,
            y=0.94,
            xanchor="left",
            yanchor="top",
            text=f"Current BTC Price: ${current_btc_price/1e3:.3f}K",
            showarrow=False,
            align="left",
            font=dict(
                family="Arial",
                size=12,
                color="white"
            )
        )
    return fig70

def create_plot71():
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

    # Calculate the "All-Time High" and "Current Market Cap" values
    current_eth_price = output_dataframe71['ETH Price'].iloc[-1]

    fig71 = px.line(output_dataframe71, x='date', y='ETH Price' , title='ETH Price')
    fig71.update_layout(
            xaxis_title="Date",
            yaxis_title="ETH Price",
            hovermode="x",
        )
    fig71.update_xaxes(
            tickformat="%b-%y",  # Format x-axis tick labels as "Jun-22", "Jun-23", etc.
            tickmode="linear",  # Set tick mode to linear
            dtick="M12",  # Display tick labels every 12 months
        )

    fig71.update_traces(hovertemplate='<b>%{x|%d-%b-%y}</b><br>ETH Price: %{y}')
    fig71.update_traces(line_color="#7030A0")

    fig71.update_yaxes(tickprefix="$")

    fig71.add_annotation(
            xref="paper",
            yref="paper",
            x=0.02,
            y=0.94,
            xanchor="left",
            yanchor="top",
            text=f"Current ETH Price: ${current_eth_price/1e3:.3f}K",
            showarrow=False,
            align="left",
            font=dict(
                family="Arial",
                size=12,
                color="white"
            )
        )
    
    return fig71

def create_plot72():
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

    # Calculate the "All-Time High" and "Current Market Cap" values
    #current_eth_price = output_dataframe72['Liquidations'].iloc[-1]

    #fig72 = px.line(output_dataframe72, x='date', y='Liquidations' , title='BTC Liquidations')
    fig72 = go.Figure()

    grouped_data = output_dataframe72.groupby(['date', 'Type']).sum().reset_index()


    # Separate the data for Longs and Shorts
    #longs_data = output_dataframe72[output_dataframe72['Type'] == 'Longs']
    #shorts_data = output_dataframe72[output_dataframe72['Type'] == 'Shorts']

    # Plot Longs bars on the positive y-axis
    #fig72.add_trace(
        #go.Bar(
            #x=longs_data['date'],
           # y=longs_data['Liquidations'],
            #name='Longs',
            #marker_color="#7030A0"
        #)
    #)

    # Plot Shorts bars on the negative y-axis
    #fig72.add_trace(
        #go.Bar(
            #x=shorts_data['date'],
            #y=shorts_data['Liquidations'],  # Use negative values for Shorts
            #name='Shorts',
            #base=0,
            #marker_color='#FF9999'
        #)
    #)

    for performance_type, group in grouped_data.groupby('Type'):
        if performance_type == 'Shorts':
            fig72.add_trace(
                    go.Bar(
                        x=group['date'],
                        y=group['Liquidations'],
                        name=performance_type,  # Set the name for the legend
                        marker_color= '#FF9999' # Set the color of the bars for negative performance
                    )
                )
        else:
            fig72.add_trace(
                    go.Bar(
                        x=group['date'],
                        y=group['Liquidations'],
                        name=performance_type,  # Set the name for the legend
                        marker_color="#7030A0"  # Set the color of the bars for non-negative performance
                    )
                )
            
    fig72.update_layout(
                    legend=dict(
                    orientation="h",
                    y=-0.3,  # Adjust the value to control the vertical position of the legend
                    x=0.5,  # Adjust the value to control the horizontal position of the legend
                    xanchor='center'
                    )
                )
         
    fig72.update_layout(
                xaxis_title="Date",
                yaxis_title="Liquidations",
                hovermode="x",
            )
        
    #fig72.data = fig72.data[::-1]
    #y_max = max(output_dataframe72['Liquidations'].max(), 0)
    #fig72.update_yaxes(range=[-200, y_max])

    #y_range = [
        #min(output_dataframe72['Liquidations'].min(), 0),  # Ensure y_range covers negative values
        #max(output_dataframe72['Liquidations'].max(), 0)   # Ensure y_range covers positive values
    #]
    #fig72.update_yaxes(range=y_range)

    #fig72.update_xaxes(
        #tickformat="%d-%b-%Y",  # Format x-axis tick labels as "Jun-22", "Jun-23", etc.
        ##tickmode="linear",  # Set tick mode to linear
        #dtick="D15"
    #)

    # Manually set tick values and labels for better alignment
    x_tickvals = output_dataframe72['date'][::15]
    x_ticklabels = x_tickvals.dt.strftime('%d-%b-%Y')
    fig72.update_xaxes(tickvals=x_tickvals, ticktext=x_ticklabels)

        #fig72.update_traces(hovertemplate='<b>%{x|%d-%b-%y}</b><br>ETH Price: %{y}')
        #fig72.update_traces(line_color="#7030A0")

    fig72.update_yaxes(tickprefix="$")
        
    return fig72

def create_plot73():
    url73 = "https://www.theblock.co/api/charts/chart/crypto-markets/futures/aggregated-open-interest-of-bitcoin-futures-daily"
    r73 = session6.get(url73)
    r_json73 = r73.json()

    output_dataframe73 = pd.DataFrame()
    series_dict73= r_json73['chart']['jsonFile']['Series']
    for vol in series_dict73:
        df_ = pd.DataFrame(series_dict73[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'OI'})
        df_['Exchange'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe73 = pd.concat([df_,output_dataframe73])

    # Convert date column to datetime format
    output_dataframe73['date'] = pd.to_datetime(output_dataframe73['date'])
    fig73 = go.Figure()

    # Filter the dataframe for the last day
    last_date = output_dataframe73['date'].max()
    last_day_data = output_dataframe73[output_dataframe73['date'] == last_date]

    # Sort the exchanges based on their volumes on the last day
    sorted_tokens = last_day_data.groupby('Exchange')['OI'].sum().sort_values(ascending=False)

    # Calculate the total volume on the last day
    total_volume_last_day = last_day_data['OI'].sum()

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

    remaining_tokens = output_dataframe73[~output_dataframe73['Exchange'].isin(filtered_tokens)]['Exchange'].unique()
    # Group the data by date and exchange to get the aggregated DataFrame for remaining_tokens
    remaining_tokens_data = output_dataframe73[output_dataframe73['Exchange'].isin(remaining_tokens)]
    remaining_tokens_data_grouped = remaining_tokens_data.groupby(['date', 'Exchange']).sum().reset_index()

    # Create a DataFrame for "Others" containing aggregated volume for remaining_tokens
    others_data = remaining_tokens_data_grouped.groupby('date')['OI'].sum().reset_index()
    others_count = len(remaining_tokens)
    others_data['Exchange'] = f'+{others_count} Others'

    # Combine the data for filtered tokens and others into a single DataFrame
    combined_data = pd.concat([output_dataframe73[output_dataframe73['Exchange'].isin(filtered_tokens)], others_data])

    # Group the combined data by date and exchange to get the aggregated DataFrame
    output_dataframe_agg = combined_data.groupby(['date', 'Exchange']).sum().reset_index()

    # Sort the DataFrame based on the total volume of each token on the last day (in descending order)
    sorted_tokens = output_dataframe_agg.groupby('Exchange')['OI'].sum().sort_values(ascending=False).index
    output_dataframe_agg['Exchange'] = pd.Categorical(output_dataframe_agg['Exchange'], categories=sorted_tokens, ordered=True)
    output_dataframe_agg.sort_values(['date', 'Exchange'], inplace=True)
    custom_color = 'grey'

    total_aggregated_volume = output_dataframe_agg.groupby('date')['OI'].sum().reset_index()

    fig73 = px.area(
        title='Open Interest BTC Futures',
        x=total_aggregated_volume['date'],
        y=total_aggregated_volume['OI'],
    )

    fig73.update_layout(
    xaxis=dict(
        title="Date",
        tickformat="%b-%d",
        tickmode="linear",
        dtick="M6"  # Display tick labels every 6 days
    ),
    yaxis=dict(title="Total Aggregated Open Interest (in Billions)"),
    hovermode="x",
    legend=dict(
        orientation="h",
        y=-0.2,  # Adjust the value to control the vertical position of the legend
        x=0.5,  # Adjust the value to control the horizontal position of the legend
        xanchor='center'
    )
)

    fig73.update_traces(
        hovertemplate='<b>%{x|%d-%b-%y}</b><br>Total Aggregated OI: %{y}'
    )

    fig73.update_yaxes(tickprefix="$")
    fig73.update_traces(line_color="#7030A0")

    return fig73

def create_plot74():
    url74 = "https://www.theblock.co/api/charts/chart/decentralized-finance/total-value-locked-tvl/value-locked-by-blockchain"
    r74 = session6.get(url74)
    r_json74 = r74.json()

    output_dataframe74 = pd.DataFrame()
    series_dict74 = r_json74['chart']['jsonFile']['Series']
    for vol in series_dict74:
        df_ = pd.DataFrame(series_dict74[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Value'})
        df_['Exchange'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe74 = pd.concat([df_,output_dataframe74])

    # Convert date column to datetime format
    output_dataframe74['date'] = pd.to_datetime(output_dataframe74['date'])
    fig74 = go.Figure()

    # Filter the dataframe for the last day
    last_date = output_dataframe74['date'].max()
    last_day_data = output_dataframe74[output_dataframe74['date'] == last_date]

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
    
    remaining_tokens = output_dataframe74[~output_dataframe74['Exchange'].isin(filtered_tokens)]['Exchange'].unique()
    # Group the data by date and exchange to get the aggregated DataFrame for remaining_tokens
    remaining_tokens_data = output_dataframe74[output_dataframe74['Exchange'].isin(remaining_tokens)]
    remaining_tokens_data_grouped = remaining_tokens_data.groupby(['date', 'Exchange']).sum().reset_index()

    # Create a DataFrame for "Others" containing aggregated volume for remaining_tokens
    others_data = remaining_tokens_data_grouped.groupby('date')['Value'].sum().reset_index()
    others_count = len(remaining_tokens)
    others_data['Exchange'] = f'+{others_count} Others'

    # Combine the data for filtered tokens and others into a single DataFrame
    combined_data = pd.concat([output_dataframe74[output_dataframe74['Exchange'].isin(filtered_tokens)], others_data])

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

    total_aggregated_volume_blockchain = output_dataframe_agg.groupby('date')['Value'].sum().reset_index()

    fig74 = px.area(
        title='Open Interest BTC Futures',
        x=total_aggregated_volume_blockchain['date'],
        y=total_aggregated_volume_blockchain['Value'],
    )

    fig74.update_layout(
                                xaxis=dict(
                                title="Date",
                                tickformat="%b-%y",
                                tickmode="linear",
                                dtick="M6"  # Display tick labels every 6 days
                            ),
                                yaxis=dict(title="Value Locked (in Billions USD)"),
                                hovermode="x"
                            )

    fig74.update_layout(
                                legend=dict(
                                orientation="h",
                                y=-0.2,  # Adjust the value to control the vertical position of the legend
                                x=0.5,  # Adjust the value to control the horizontal position of the legend
                                xanchor='center'
                                )
                            )

    fig74.update_traces(
                                hovertemplate='<b>%{x|%d-%b-%y}</b><br>Value: %{y}'
                            )
            
    fig74.update_yaxes(tickprefix="$")
    fig74.update_traces(line_color="#7030A0")

    return fig74

plot70 = None
plot71 = None
plot72 = None
plot73 = None
plot74 = None

# Define a function to update the plot and table variables
def update_plots_and_tables():
    global plot70
    global plot71
    global plot72
    global plot73
    global plot74

    plot70 = create_plot70()
    plot71 = create_plot71()
    plot72 = create_plot72()
    plot73 = create_plot73()
    plot74 = create_plot74()

# Call the function to update the plots and tables
# Start a separate thread to create the plots
plots_thread = Thread(target=update_plots_and_tables)
plots_thread.start()

# Wait for the plot creation thread to complete
plots_thread.join()

if plot70 is not None and plot71 is not None and plot72 is not None and plot73 is not None and plot74 is not None:
    button_ranges_btc_price = {
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
        "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
        "1Y": [datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()],
        "3Y": [datetime.datetime.now() - datetime.timedelta(days=1095), datetime.datetime.now()],
        "All": [plot70.data[0].x[0], plot70.data[0].x[-1]]  # Placeholder for 'All' button range
        }

    button_labels_btc_price = ["1W", "1M", "1Q", "1Y", "3Y", "All"]

    premium_buttons_btc_price = [
            {
                "label": button_label,
                "method": "relayout",
                "args": [
                    {"xaxis": {"range": button_ranges_btc_price[button_label], "tickformat": "%d-%b-%Y"}}
                ],
                }
        for button_label in button_labels_btc_price
        ]

        # Create the updatemenus configuration for Dominance Graph
    premium_updatemenus_btc_price = [{
            "type": "buttons",
            "buttons": premium_buttons_btc_price,
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

        # Update the layout for Dominance Graph
    plot70.update_layout(
            title=dict(
                text="BTC Price",
                x=0.2,
                y=1,
                xanchor="center",
                yanchor="top"
            ),
        updatemenus=premium_updatemenus_btc_price
        )
    
    button_ranges_eth_price = {
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
        "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
        "1Y": [datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()],
        "3Y": [datetime.datetime.now() - datetime.timedelta(days=1095), datetime.datetime.now()],
        "All": [plot71.data[0].x[0], plot71.data[0].x[-1]]  # Placeholder for 'All' button range
        }

    button_labels_eth_price = ["1W", "1M", "1Q", "1Y", "3Y", "All"]

    premium_buttons_eth_price = [
            {
                "label": button_label,
                "method": "relayout",
                "args": [
                    {"xaxis": {"range": button_ranges_eth_price[button_label], "tickformat": "%d-%b-%Y"}}
                ],
                }
        for button_label in button_labels_eth_price
        ]

        # Create the updatemenus configuration for Dominance Graph
    premium_updatemenus_eth_price = [{
            "type": "buttons",
            "buttons": premium_buttons_eth_price,
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

        # Update the layout for Dominance Graph
    plot71.update_layout(
            title=dict(
                text="ETH Price",
                x=0.2,
                y=1,
                xanchor="center",
                yanchor="top"
            ),
        updatemenus=premium_updatemenus_eth_price
        )

    button_ranges_liquidations = {
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
        "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
        "All": [plot72.data[0].x[0], plot72.data[0].x[-1]]  # Placeholder for 'All' button range
        }

    button_labels_liquidations = ["1W", "1M", "1Q", "All"]

    premium_buttons_liquidations = [
            {
                "label": button_label,
                "method": "relayout",
                "args": [
                    {"xaxis": {"range": button_ranges_liquidations[button_label], "tickformat": "%d-%b-%Y"}}
                ],
                }
        for button_label in button_labels_liquidations
        ]

        # Create the updatemenus configuration for Dominance Graph
    premium_updatemenus_liquidations = [{
            "type": "buttons",
            "buttons": premium_buttons_liquidations,
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

        # Update the layout for Dominance Graph
    plot72.update_layout(
            title=dict(
                text="Liquidations (Long/Short)",
                x=0.2,
                y=1,
                xanchor="center",
                yanchor="top"
            ),
        updatemenus=premium_updatemenus_liquidations
        )
    
    button_ranges_btc_open_interest_volume = {
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
        "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
        "All": [plot73.data[0].x[0], plot73.data[0].x[-1]]  # Placeholder for 'All' button range
        }

    button_labels_btc_open_interest_volume = ["1W", "1M", "1Q", "All"]

    premium_buttons_btc_open_interest_volume = [
            {
                "label": button_label,
                "method": "relayout",
                "args": [
                    {"xaxis": {"range": button_ranges_btc_open_interest_volume[button_label], "tickformat": "%d-%b-%Y"}}
                ],
                }
        for button_label in button_labels_btc_open_interest_volume
        ]

        # Create the updatemenus configuration for Dominance Graph
    premium_updatemenus_btc_open_interest_volume = [{
            "type": "buttons",
            "buttons": premium_buttons_btc_open_interest_volume,
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

        # Update the layout for Dominance Graph
    plot73.update_layout(
            title=dict(
                text="Open Interest BTC Futures",
                x=0.2,
                y=1,
                xanchor="center",
                yanchor="top"
            ),
        updatemenus=premium_updatemenus_btc_open_interest_volume
        )
    
    button_ranges_value_locked_blockchain = {
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
        "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
        "All": [plot74.data[0].x[0], plot74.data[0].x[-1]]  # Placeholder for 'All' button range
        }

    button_labels_value_locked_blockchain = ["1W", "1M", "1Q", "All"]

    premium_buttons_value_locked_blockchain = [
            {
                "label": button_label,
                "method": "relayout",
                "args": [
                    {"xaxis": {"range": button_ranges_value_locked_blockchain[button_label], "tickformat": "%d-%b-%Y"}}
                ],
                }
        for button_label in button_labels_value_locked_blockchain
        ]

        # Create the updatemenus configuration for Dominance Graph
    premium_updatemenus_value_locked_blockchain = [{
            "type": "buttons",
            "buttons": premium_buttons_value_locked_blockchain,
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

        # Update the layout for Dominance Graph
    plot74.update_layout(
            title=dict(
                text="Total Value Locked in DeFi",
                x=0.2,
                y=1,
                xanchor="center",
                yanchor="top"
            ),
        updatemenus=premium_updatemenus_value_locked_blockchain
        )

    plot72
    plot70
    plot71
    plot73
    plot74
