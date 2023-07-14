import requests
import pandas as pd
import datetime
import json
import plotly.express as px
import streamlit as st
import numpy as np
from threading import Thread
import plotly.graph_objects as go

with st.sidebar:
    image = "https://forteus-media-research.s3.eu-west-1.amazonaws.com/public/images/Final+Logo+Forteus+by+Numeus+light.png"  # Replace with the actual path to your photo
    image_size = (300, 200)  # Replace with the desired width and height of the image in pixels
        #st.image(image, width=image_size[0], use_column_width=False)
    st.markdown(
            f'<div style="display: flex; justify-content: center;"><img src="{image}" width="{image_size[0]}"></div>',
            unsafe_allow_html=True)
    st.markdown('<div style="display: flex; justify-content: center;"><h1>July Market Update</h1></div>', unsafe_allow_html=True)
        #st.markdown("# July Market Update")

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

def create_plot3():
    url3 = "https://www.theblock.co/api/charts/chart/on-chain-metrics/bitcoin/transactions-on-the-bitcoin-network-daily"
    r3 = requests.get(url3)
    r_json3 = r3.json()

    output_dataframe3 = pd.DataFrame()
    series_dict3 = r_json3['chart']['jsonFile']['Series']
    for vol in series_dict3:
        df_ = pd.DataFrame(series_dict3[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Transactions'})
        #df_['Token'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        #df_.drop_duplicates(subset='date', keep='last', inplace=True)
        output_dataframe3 = pd.concat([df_,output_dataframe3])

    # Convert date column to datetime format
    output_dataframe3['date'] = pd.to_datetime(output_dataframe3['date'])

    fig3 = px.line(output_dataframe3, x='date', y='Transactions', title='Transactions on the Bitcoin Network (Daily, 7DMA)')
    fig3.update_layout(
        xaxis_title="Date",
        yaxis_title="Transactions (in Thousands)",
        hovermode="x"
    )

    fig3.update_xaxes(
        tickformat="%b-%y",  # Format x-axis tick labels as "Jun-22", "Jun-23", etc.
        tickmode="linear",  # Set tick mode to linear
        dtick="M24",  # Display tick labels every 12 months
    )

    fig3.update_traces(
        hovertemplate='<b>%{x|%d-%b-%y}</b><br>Transactions: %{y}'
    )

    current_btc_transactions = output_dataframe3['Transactions'].iloc[-1]

    # Calculate the last year's transactions using the last date of the previous year
    last_year_btc_transactions = output_dataframe3.loc[output_dataframe3['date'].dt.year == last_year_date.year, 'Transactions'].values[-1]

    # Calculate the last month's btc_transactions
    last_month_btc_transactions = output_dataframe3.loc[output_dataframe3['date'].dt.year == last_month_date.year]
    last_month_btc_transactions = last_month_btc_transactions.loc[last_month_btc_transactions['date'].dt.month == last_month_date.month]
    last_month_btc_transactions = last_month_btc_transactions['Transactions'].values[-1]

    # Calculate the last quarter's btc_transactions
    # last_quarter_start_date = last_quarter_date - datetime.timedelta(days=89)  # Assuming 90 days per quarter
    last_quarter_btc_transactions= output_dataframe3.loc[(output_dataframe3['date'].dt.date >= last_quarter_start_date) & (output_dataframe3['date'].dt.date <= last_quarter_date)]
    last_quarter_btc_transactions = last_quarter_btc_transactions['Transactions'].values[-1]

    # Calculate the last week's btc_transactions
    last_week_btc_transactions = output_dataframe3.loc[(output_dataframe3['date'].dt.date >= last_week_start_date) & (output_dataframe3['date'].dt.date <= last_week_date)]
    last_week_btc_transactions = last_week_btc_transactions['Transactions'].values[-1]

    # Format btc transactions values in thousands
    current_btc_transactions_str = f'{current_btc_transactions/1e3:.3f}K'
    last_week_btc_transactions_str = f'{last_week_btc_transactions/1e3:.3f}K'
    last_month_btc_transactions_str = f'{last_month_btc_transactions/1e3:.3f}K'
    last_year_btc_transactions_str = f'{last_year_btc_transactions/1e3:.3f}K'
    last_quarter_btc_transactions_str = f'{last_quarter_btc_transactions/1e3:.3f}K'

    # Calculate the change values as percentages
    last_week_change = ((current_btc_transactions - last_week_btc_transactions) / last_week_btc_transactions) * 100
    last_month_change = ((current_btc_transactions - last_month_btc_transactions) / last_month_btc_transactions) * 100
    last_year_change = ((current_btc_transactions - last_year_btc_transactions) / last_year_btc_transactions) * 100
    last_quarter_change = ((current_btc_transactions - last_quarter_btc_transactions) / last_quarter_btc_transactions) * 100

    # Create the market cap table
    btc_transactions_table = pd.DataFrame({
        'Period': ['WTD', 'MTD','QTD', 'YTD'],
        'Transactions': [last_week_btc_transactions_str, last_month_btc_transactions_str,last_quarter_btc_transactions_str, last_year_btc_transactions_str],
        'Date': [last_week_date.strftime("%d %b %Y"), last_month_date.strftime("%d %b %Y"),last_quarter_date.strftime("%d %b %Y"), last_year_date.strftime("%d %b %Y")],
        'Change (%)': [f'{last_week_change:.2f}%', f'{last_month_change:.2f}%', f'{last_quarter_change:.2f}%', f'{last_year_change:.2f}%']
    })

    return fig3, btc_transactions_table

def create_plot4():
    url4 = "https://www.theblock.co/api/charts/chart/on-chain-metrics/ethereum/transactions-on-the-ethereum-network-daily"
    r4 = requests.get(url4)
    r_json4 = r4.json()

    output_dataframe4 = pd.DataFrame()
    series_dict4 = r_json4['chart']['jsonFile']['Series']
    for vol in series_dict4:
        df_ = pd.DataFrame(series_dict4[vol]['Data']).rename(columns = {'Timestamp': 'date', 'Result' : 'Transactions'})
        #df_['Token'] = vol
        df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp (x, tz = datetime.timezone.utc).strftime("%Y-%m-%d"))
        output_dataframe4 = pd.concat([df_,output_dataframe4])

    # Convert date column to datetime format
    output_dataframe4['date'] = pd.to_datetime(output_dataframe4['date'])

    fig4 = px.line(output_dataframe4, x='date', y='Transactions', title='Transactions on the Ethereum Network (Daily, 7DMA)')
    fig4.update_layout(
        xaxis_title="Date",
        yaxis_title="Transactions (in Millions)",
        hovermode="x"
    )

    fig4.update_xaxes(
        tickformat="%b-%y",  # Format x-axis tick labels as "Jun-22", "Jun-23", etc.
        tickmode="linear",  # Set tick mode to linear
        dtick="M12" # Display tick labels every 12 months
    )

    fig4.update_traces(
        hovertemplate='<b>%{x|%d-%b-%y}</b><br>Transactions: %{y}'
    )

    current_eth_transactions = output_dataframe4['Transactions'].iloc[-1]

    # Calculate the last year's transactions using the last date of the previous year
    last_year_eth_transactions = output_dataframe4.loc[output_dataframe4['date'].dt.year == last_year_date.year, 'Transactions'].values[-1]

    # Calculate the last month's eth_transactions
    last_month_eth_transactions = output_dataframe4.loc[output_dataframe4['date'].dt.year == last_month_date.year]
    last_month_eth_transactions = last_month_eth_transactions.loc[last_month_eth_transactions['date'].dt.month == last_month_date.month]
    last_month_eth_transactions = last_month_eth_transactions['Transactions'].values[-1]

    # Calculate the last quarter's eth_transactions
    # last_quarter_start_date = last_quarter_date - datetime.timedelta(days=89)  # Assuming 90 days per quarter
    last_quarter_eth_transactions= output_dataframe4.loc[(output_dataframe4['date'].dt.date >= last_quarter_start_date) & (output_dataframe4['date'].dt.date <= last_quarter_date)]
    last_quarter_eth_transactions = last_quarter_eth_transactions['Transactions'].values[-1]

    # Calculate the last week's eth_transactions
    last_week_eth_transactions = output_dataframe4.loc[(output_dataframe4['date'].dt.date >= last_week_start_date) & (output_dataframe4['date'].dt.date <= last_week_date)]
    last_week_eth_transactions = last_week_eth_transactions['Transactions'].values[-1]

    # Format eth transactions values in thousands
    current_eth_transactions_str = f'{current_eth_transactions/1e6:.3f}M'
    last_week_eth_transactions_str = f'{last_week_eth_transactions/1e6:.3f}M'
    last_month_eth_transactions_str = f'{last_month_eth_transactions/1e6:.3f}M'
    last_year_eth_transactions_str = f'{last_year_eth_transactions/1e6:.3f}M'
    last_quarter_eth_transactions_str = f'{last_quarter_eth_transactions/1e6:.3f}M'

    # Calculate the change values as percentages
    last_week_change = ((current_eth_transactions - last_week_eth_transactions) / last_week_eth_transactions) * 100
    last_month_change = ((current_eth_transactions - last_month_eth_transactions) / last_month_eth_transactions) * 100
    last_year_change = ((current_eth_transactions - last_year_eth_transactions) / last_year_eth_transactions) * 100
    last_quarter_change = ((current_eth_transactions - last_quarter_eth_transactions) / last_quarter_eth_transactions) * 100

    # Create the eth transactions table
    eth_transactions_table = pd.DataFrame({
        'Period': ['WTD', 'MTD','QTD', 'YTD'],
        'Transactions': [last_week_eth_transactions_str, last_month_eth_transactions_str,last_quarter_eth_transactions_str, last_year_eth_transactions_str],
        'Date': [last_week_date.strftime("%d %b %Y"), last_month_date.strftime("%d %b %Y"),last_quarter_date.strftime("%d %b %Y"), last_year_date.strftime("%d %b %Y")],
        'Change (%)': [f'{last_week_change:.2f}%', f'{last_month_change:.2f}%', f'{last_quarter_change:.2f}%', f'{last_year_change:.2f}%']
    })

    return fig4, eth_transactions_table

plot3 = None
plot4 = None
btc_transactions_table = None
eth_transactions_table = None

# Define a function to update the plot and table variables
def update_plots_and_tables():
    global plot3, btc_transactions_table
    global plot4, eth_transactions_table

    plot3, btc_transactions_table = create_plot3()
    plot4, eth_transactions_table  = create_plot4()

# Call the function to update the plots and tables
# Start a separate thread to create the plots
plots_thread = Thread(target=update_plots_and_tables)
plots_thread.start()

# Wait for the plot creation thread to complete
plots_thread.join()

if plot3 is not None and plot4 is not None:
    # Buttons for BTC Transactions Graph
    button_ranges_btc_transactions = {
    "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
    "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
    "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
    "1Y": [datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()],
    "3Y": [datetime.datetime.now() - datetime.timedelta(days=1095), datetime.datetime.now()],
    "All": [plot3.data[0].x[0], plot3.data[0].x[-1]]  # Placeholder for 'All' button range
    }

    button_labels_btc_transactions = ["1W", "1M", "1Q", "1Y", "3Y", "All"]

    btc_transactions_buttons = [
        {
            "label": button_label,
            "method": "relayout",
            "args": [
                {"xaxis": {"range": button_ranges_btc_transactions[button_label], "tickformat": "%d-%b-%Y"}}
            ],
            }
        for button_label in button_labels_btc_transactions
    ]

    # Create the updatemenus configuration for BTC Transactions Graph
    btc_transactions_updatemenus = [{
        "type": "buttons",
        "buttons": btc_transactions_buttons,
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
        "pad": {"r": 5, "t": 5}
    }]

    # Update the layout for BTC Transactions Graph
    plot3.update_layout(
        title=dict(
            text="Transactions (BTC Network)",
            x=0.2,
            y=1,
            xanchor="center",
            yanchor="top"
        ),
        updatemenus=btc_transactions_updatemenus
    )

    # Buttons for ETH Transactions Graph
    button_ranges_eth_transactions = {
    "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
    "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
    "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
    "1Y": [datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()],
    "3Y": [datetime.datetime.now() - datetime.timedelta(days=1095), datetime.datetime.now()],
    "All": [plot4.data[0].x[0], plot4.data[0].x[-1]]  # Placeholder for 'All' button range
    }

    button_labels_eth_transactions = ["1W", "1M", "1Q", "1Y", "3Y", "All"]

    eth_transactions_buttons = [
        {
            "label": button_label,
            "method": "relayout",
            "args": [
                {"xaxis": {"range": button_ranges_eth_transactions[button_label], "tickformat": "%d-%b-%Y"}}
            ],
            }
        for button_label in button_labels_eth_transactions
    ]

    # Create the updatemenus configuration for ETH Transactions Graph
    eth_transactions_updatemenus = [{
        "type": "buttons",
        "buttons": eth_transactions_buttons,
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
        "pad": {"r": 5, "t": 5}
    }]

    # Update the layout for ETH Transactions Graph
    plot4.update_layout(
        title=dict(
            text="Transactions (ETH Network)",
            x=0.2,
            y=1,
            xanchor="center",
            yanchor="top"
        ),
        updatemenus=eth_transactions_updatemenus
    )

    col1, col2 = st.columns(2)

    col1.plotly_chart(plot3, use_container_width=True)
    col1.dataframe(btc_transactions_table, hide_index = True)
    col2.plotly_chart(plot4, use_container_width=True)
    col2.dataframe(eth_transactions_table, hide_index = True)

