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

with st.sidebar:
    image = "https://forteus-media-research.s3.eu-west-1.amazonaws.com/public/images/Final+Logo+Forteus+by+Numeus+light.png"  # Replace with the actual path to your photo
    image_size = (300, 200)  # Replace with the desired width and height of the image in pixels
        #st.image(image, width=image_size[0], use_column_width=False)
    st.markdown(
            f'<div style="display: flex; justify-content: center;"><img src="{image}" width="{image_size[0]}"></div>',
            unsafe_allow_html=True)
    st.markdown('<div style="display: flex; justify-content: center;"><h1>July Market Update</h1></div>', unsafe_allow_html=True)
        #st.markdown("# July Market Update")

st.title('Performance and Factors')

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

tab1,tab2 = st.tabs(["Performance", "Risk Factors"])

# Create a requests_cache session with a cache expiration time of 1 hour
session1 = CachedSession('cache1', expire_after=timedelta(hours=1))

with tab1:
    def create_plot1():
        url1 = "https://www.theblock.co/api/charts/chart/crypto-markets/prices/crypto-total-marketcap"
        r1 = session1.get(url1)
        r_json1 = r1.json()

        output_dataframe1 = pd.DataFrame()
        series_dict1 = r_json1['chart']['jsonFile']['Series']
        for vol in series_dict1:
            df_ = pd.DataFrame(series_dict1[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'Market Cap'})
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%d %b %Y"))
            output_dataframe1 = pd.concat([df_, output_dataframe1])

        output_dataframe1['date'] = pd.to_datetime(output_dataframe1['date'])

        # Calculate the "All-Time High" and "Current Market Cap" values
        all_time_high = output_dataframe1['Market Cap'].max()
        current_market_cap = output_dataframe1['Market Cap'].iloc[-1]

        fig1 = px.area(output_dataframe1, x='date', y='Market Cap' , title='Crypto Total Marketcap')
        fig1.update_layout(
            xaxis_title="Date",
            yaxis_title="Market Cap (in Trillions USD)",
            hovermode="x",
        )
        fig1.update_xaxes(
            tickformat="%b-%y",  # Format x-axis tick labels as "Jun-22", "Jun-23", etc.
            tickmode="linear",  # Set tick mode to linear
            dtick="M12",  # Display tick labels every 12 months
        )

        fig1.update_traces(hovertemplate='<b>%{x|%d-%b-%y}</b><br>Market Cap: %{y}')
        fig1.update_traces(line_color="#7030A0")

        fig1.update_yaxes(tickprefix="$")

        # Add custom legend items as annotations
        fig1.add_annotation(
            xref="paper",
            yref="paper",
            x=0.02,
            y=0.98,
            xanchor="left",
            yanchor="top",
            text=f"All-Time High: ${all_time_high/1e12:.3f}T",
            showarrow=False,
            align="left",
            font=dict(
                family="Arial",
                size=12,
                color="black"
            )
        )

        fig1.add_annotation(
            xref="paper",
            yref="paper",
            x=0.02,
            y=0.94,
            xanchor="left",
            yanchor="top",
            text=f"Current Market Cap: ${current_market_cap/1e12:.3f}T",
            showarrow=False,
            align="left",
            font=dict(
                family="Arial",
                size=12,
                color="black"
            )
        )

        # Calculate the last year's market cap using the last date of the previous year
        last_year_market_cap = output_dataframe1.loc[output_dataframe1['date'].dt.year == last_year_date.year, 'Market Cap'].values[-1]

        # Calculate the last month's market cap
        last_month_market_cap = output_dataframe1.loc[output_dataframe1['date'].dt.year == last_month_date.year]
        last_month_market_cap = last_month_market_cap.loc[last_month_market_cap['date'].dt.month == last_month_date.month]
        last_month_market_cap = last_month_market_cap['Market Cap'].values[-1]

        # Calculate the last quarter's market cap
        # last_quarter_start_date = last_quarter_date - datetime.timedelta(days=89)  # Assuming 90 days per quarter
        last_quarter_market_cap = output_dataframe1.loc[(output_dataframe1['date'].dt.date >= last_quarter_start_date) & (output_dataframe1['date'].dt.date <= last_quarter_date)]
        last_quarter_market_cap = last_quarter_market_cap['Market Cap'].values[-1]

        # Calculate the last week's market cap
        last_week_market_cap = output_dataframe1.loc[(output_dataframe1['date'].dt.date >= last_week_start_date) & (output_dataframe1['date'].dt.date <= last_week_date)]
        last_week_market_cap = last_week_market_cap['Market Cap'].values[-1]

        # Format market cap values in trillions
        current_market_cap_str = f'{current_market_cap/1e12:.3f}T'
        last_week_market_cap_str = f'{last_week_market_cap/1e12:.3f}T'
        last_month_market_cap_str = f'{last_month_market_cap/1e12:.3f}T'
        last_year_market_cap_str = f'{last_year_market_cap/1e12:.3f}T'
        last_quarter_market_cap_str = f'{last_quarter_market_cap/1e12:.3f}T'

        # Calculate the change values as percentages
        last_week_change = ((current_market_cap - last_week_market_cap) / last_week_market_cap) * 100
        last_month_change = ((current_market_cap - last_month_market_cap) / last_month_market_cap) * 100
        last_year_change = ((current_market_cap - last_year_market_cap) / last_year_market_cap) * 100
        last_quarter_change = ((current_market_cap - last_quarter_market_cap) / last_quarter_market_cap) * 100

        # Create the market cap table
        market_cap_table = pd.DataFrame({
            'Period': ['WTD', 'MTD','QTD', 'YTD'],
            'Market Cap': [last_week_market_cap_str, last_month_market_cap_str,last_quarter_market_cap_str, last_year_market_cap_str],
            'Date': [last_week_date.strftime("%d %b %Y"), last_month_date.strftime("%d %b %Y"),last_quarter_date.strftime("%d %b %Y"), last_year_date.strftime("%d %b %Y")],
            'Change (%)': [f'{last_week_change:.2f}%', f'{last_month_change:.2f}%', f'{last_quarter_change:.2f}%', f'{last_year_change:.2f}%']
        })

        return fig1, market_cap_table
    
    def create_plot2():
        url2 = "https://www.theblock.co/api/charts/chart/crypto-markets/prices/bitcoin-dominance"
        r2 = session1.get(url2)
        r_json2 = r2.json()

        output_dataframe2 = pd.DataFrame()
        series_dict2 = r_json2['chart']['jsonFile']['Series']
        for vol in series_dict2:
            df_ = pd.DataFrame(series_dict2[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'Dominance'})
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%Y-%m-%d"))
            output_dataframe2 = pd.concat([df_, output_dataframe2])

        output_dataframe2['date'] = pd.to_datetime(output_dataframe2['date'])

        fig2 = px.line(output_dataframe2, x='date', y='Dominance', title='Bitcoin Dominance')
        fig2.update_layout(
            xaxis_title="Date",
            yaxis_title="Dominance (%)",
            hovermode="x"
        )

        fig2.update_xaxes(
            tickformat="%b-%y",  # Format x-axis tick labels as "Jun-22", "Jun-23", etc.
            tickmode="linear",  # Set tick mode to linear
            dtick="M12",  # Display tick labels every 12 months
        )
        
        # Update the line color to the custom color
        fig2.update_traces(line_color="#7030A0")

        fig2.update_traces(
            hovertemplate='<b>%{x|%d-%b-%y}</b><br>Dominance: %{y:.2f}%'
        )

        # Format y-axis tick labels as percentages
        fig2.update_yaxes(ticksuffix="%")

        current_dominance = output_dataframe2['Dominance'].iloc[-1]
        
        # Calculate the quarterly, monthly, and yearly maximum dominance values
        last_year_dominance = output_dataframe2.loc[output_dataframe2['date'].dt.year == last_year_date.year, 'Dominance'].values[-1]
        last_month_dominance = output_dataframe2.loc[output_dataframe2['date'].dt.year == last_month_date.year]
        last_month_dominance = last_month_dominance.loc[last_month_dominance['date'].dt.month == last_month_date.month]
        last_month_dominance = last_month_dominance['Dominance'].values[-1]

        last_quarter_dominance = output_dataframe2.loc[(output_dataframe2['date'].dt.date >= last_quarter_start_date) & (output_dataframe2['date'].dt.date <= last_quarter_date)]
        last_quarter_dominance = last_quarter_dominance['Dominance'].values[-1]
        last_week_dominance = output_dataframe2.loc[(output_dataframe2['date'].dt.date >= last_week_start_date) & (output_dataframe2['date'].dt.date <= last_week_date)]
        last_week_dominance = last_week_dominance['Dominance'].values[-1]

        # Format dominance values as percentages
        current_dominance_str = f'{current_dominance:.2f}%'
        last_week_dominance_str = f'{last_week_dominance:.2f}%'
        last_month_dominance_str = f'{last_month_dominance:.2f}%'
        last_year_dominance_str = f'{last_year_dominance:.2f}%'
        last_quarter_dominance_str = f'{last_quarter_dominance:.2f}%'

        # Calculate the change values as percentages
        last_week_change = current_dominance - last_week_dominance
        last_month_change = current_dominance - last_month_dominance
        last_year_change = current_dominance - last_year_dominance
        last_quarter_change = current_dominance - last_quarter_dominance

        # Create the dominance table
        dominance_table = pd.DataFrame({
            'Period': ['WTD', 'MTD', 'QTD', 'YTD'],
            'Dominance': [last_week_dominance_str, last_month_dominance_str, last_quarter_dominance_str, last_year_dominance_str],
            'Date': [last_week_date.strftime("%d %b %Y"), last_month_date.strftime("%d %b %Y"), last_quarter_date.strftime("%d %b %Y"), last_year_date.strftime("%d %b %Y")],
            'Δ': [f'{last_week_change:.2f}%', f'{last_month_change:.2f}%', f'{last_quarter_change:.2f}%', f'{last_year_change:.2f}%']
        })

        fig2.add_annotation(
            xref="paper",
            yref="paper",
            x=0.98,
            y=0.95,
            xanchor="right",
            yanchor="top",
            text=f"Current BTC Dominance: {current_dominance:.2f}%",
            showarrow=False,
            align="right",
            font=dict(
                family="Arial",
                size=12,
                color="black"
            )
        )

        return fig2, dominance_table

    plot1 = None
    plot2 = None
    market_cap_table = None
    dominance_table = None

    # Define a function to update the plot and table variables
    def update_plots_and_tables():
        global plot1, market_cap_table
        global plot2, dominance_table

        plot1, market_cap_table = create_plot1()
        plot2, dominance_table = create_plot2()

    # Call the function to update the plots and tables
    # Start a separate thread to create the plots
    plots_thread = Thread(target=update_plots_and_tables)
    plots_thread.start()

    # Wait for the plot creation thread to complete
    plots_thread.join()

    if plot1 is not None and plot2 is not None:
        button_ranges_market_cap = {
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
        "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
        "1Y": [datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()],
        "3Y": [datetime.datetime.now() - datetime.timedelta(days=1095), datetime.datetime.now()],
        "All": [plot1.data[0].x[0], plot1.data[0].x[-1]]  # Placeholder for 'All' button range
        }

        button_labels_market_cap = ["1W", "1M", "1Q", "1Y", "3Y", "All"]

        buttons = [
            {
                "label": button_label,
                "method": "relayout",
                "args": [
                    {"xaxis": {"range": button_ranges_market_cap[button_label], "tickformat": "%d-%b-%Y"}}
                ],
                }
            for button_label in button_labels_market_cap
        ]

        # Create the updatemenus configuration
        updatemenus = [{
            "type": "buttons",
            "buttons": buttons,
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

        plot1.update_layout(
            title=dict(
                text="Crypto Total Marketcap",
                x=0.2,
                y=1,
                xanchor="center",
                yanchor="top"
            ),
            updatemenus=updatemenus
        )

        # Buttons for Dominance Graph

        button_ranges_dominance = {
        "1W": [datetime.datetime.now() - datetime.timedelta(weeks=1), datetime.datetime.now()],
        "1M": [datetime.datetime.now() - datetime.timedelta(days=30), datetime.datetime.now()],
        "1Q": [datetime.datetime.now() - datetime.timedelta(days=90), datetime.datetime.now()],
        "1Y": [datetime.datetime.now() - datetime.timedelta(days=365), datetime.datetime.now()],
        "3Y": [datetime.datetime.now() - datetime.timedelta(days=1095), datetime.datetime.now()],
        "All": [plot2.data[0].x[0], plot2.data[0].x[-1]]  # Placeholder for 'All' button range
        }

        button_labels_dominance = ["1W", "1M", "1Q", "1Y", "3Y", "All"]

        dominance_buttons = [
            {
                "label": button_label,
                "method": "relayout",
                "args": [
                    {"xaxis": {"range": button_ranges_dominance[button_label], "tickformat": "%d-%b-%Y"}}
                ],
                }
            for button_label in button_labels_dominance
        ]

        # Create the updatemenus configuration for Dominance Graph
        dominance_updatemenus = [{
            "type": "buttons",
            "buttons": dominance_buttons,
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
        plot2.update_layout(
            title=dict(
                text="Bitcoin Dominance",
                x=0.2,
                y=1,
                xanchor="center",
                yanchor="top"
            ),
            updatemenus=dominance_updatemenus
        )

        col1, col2 = st.columns(2)

        col1.plotly_chart(plot1, use_container_width=True)
        col1.dataframe(market_cap_table, hide_index = True)
        col2.plotly_chart(plot2, use_container_width=True)
        col2.dataframe(dominance_table, hide_index = True)

    def create_plot12():
        url12 = "https://www.theblock.co/api/charts/chart/crypto-markets/prices/bitcoin-vs-top-20-marketcap-price-performance-1m"
        r12 = session1.get(url12)
        r_json12 = r12.json()

        output_dataframe12 = pd.DataFrame()
        series_dict12 = r_json12['chart']['jsonFile']['Series']
        
        for vol in series_dict12:
            df_ = pd.DataFrame(series_dict12[vol]['Data']).rename(columns={'Name': 'Token', 'Result': 'Token Performance'})
            df_['Performance Type'] = vol
            output_dataframe12 = pd.concat([df_, output_dataframe12])

        # Create bar chart
        fig12 = go.Figure()   

        # Group the data by 'Performance Type' and iterate over each group
        for performance_type, group in output_dataframe12.groupby('Performance Type'):
            if performance_type == 'Negative Performance':
                fig12.add_trace(
                    go.Bar(
                        x=group['Token'],
                        y=group['Token Performance'],
                        name=performance_type,  # Set the name for the legend
                        marker_color= '#FF9999'  # Set the color of the bars for negative performance
                    )
                )
            else:
                fig12.add_trace(
                    go.Bar(
                        x=group['Token'],
                        y=group['Token Performance'],
                        name=performance_type,  # Set the name for the legend
                        marker_color="#7030A0"  # Set the color of the bars for non-negative performance
                    )
                )

            #fig2.update_traces(line_color="#7030A0")    '#1f77b4

            fig12.data = fig12.data[::-1]

            # Set axis labels and title
            fig12.update_layout(
                xaxis_title='Tokens',
                yaxis_title='Performance (%)',
                title="BTC vs Top 20 MarketCap (1M)"
            )

            # Set the y-axis range to start from -50 and extend up to the maximum value in the data
            y_max = output_dataframe12['Token Performance'].max()
            fig12.update_yaxes(range=[-50, y_max])

            fig12.update_yaxes(ticksuffix="%")


            fig12.update_layout(
                    legend=dict(
                    orientation="h",
                    y=-0.3,  # Adjust the value to control the vertical position of the legend
                    x=0.5,  # Adjust the value to control the horizontal position of the legend
                    xanchor='center'
                    )
                )

        return fig12


    plot12 = None

    # Define a function to update the plot and table variables
    def update_plots_and_tables():
        global plot12
        plot12 = create_plot12()

    # Call the function to update the plots and tables
    # Start a separate thread to create the plots
    plots_thread = Thread(target=update_plots_and_tables)
    plots_thread.start()

    # Wait for the plot creation thread to complete
    plots_thread.join()

    if plot12 is not None:

        col1, col2 = st.columns(2)
        col1.plotly_chart(plot12, use_container_width=True)

with tab2:
    def create_plot45():
        basic = HTTPBasicAuth('numeus', '3upqwx0@Y67he7XD')
        data_risk = session1.get('https://reporting-api.eltican.com/risk_factors_perf', auth=basic).json()
        df_risk = pd.DataFrame(data_risk)

        # Convert 'risk_date' to pandas DateTime objects
        df_risk['risk_date'] = pd.to_datetime(df_risk['risk_date'])

        # Drop any rows with dates before 13 Aug 2021
        df_risk = df_risk[df_risk['risk_date'] >= '2021-08-13']

        # Set the columns to be plotted on the y-axis
        columns_to_plot = ['cryptoindex','financing', 'liquidity', 'momentum','meanrevertion','size','volatility']
        # Convert columns to percentages
        df_risk[columns_to_plot] *= 100

        # Calculate cumulative sum based on a starting value of 100
        for column in columns_to_plot:
            df_risk[column] = df_risk[column].cumsum()

        # Create an interactive line plot using Plotly
        fig_risk = go.Figure()
        for column in columns_to_plot:
            fig_risk .add_trace(go.Scatter(x=df_risk['risk_date'], y=df_risk[column], mode='lines', name=column))

        # Update layout for better visualization
        fig_risk.update_layout(
            title='Risk Factors by Sectors (Eltican)',
            xaxis_title='Risk Date',
            yaxis_title='Percentage (%)',
            hovermode='x',
        )

        fig_risk.update_layout(
                legend=dict(
                orientation="h",
                y=-0.2,  # Adjust the value to control the vertical position of the legend
                x=0.5,  # Adjust the value to control the horizontal position of the legend
                xanchor='center'
                )
            )

        fig_risk.update_yaxes(ticksuffix="%")

        indicator_rates_table_data = []

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

        for column in columns_to_plot:
            current_indicator_rates = df_risk[column].iloc[-1]
            # Calculate the current, last year, last month, last quarter btc_option_skew_delta values
            last_year_indicator_rates = df_risk.loc[df_risk['risk_date'].dt.year == last_year_date.year, column].values[-1]
            last_month_indicator_rates = df_risk.loc[(df_risk['risk_date'].dt.year == last_month_date.year) & (df_risk['risk_date'].dt.month == last_month_date.month), column].values[-1]
            last_quarter_indicator_rates = df_risk.loc[(df_risk['risk_date'].dt.date >= last_quarter_start_date) & (df_risk['risk_date'].dt.date <= last_quarter_date), column].values[-1]
            last_week_indicator_rates = df_risk.loc[(df_risk['risk_date'].dt.date >= last_week_start_date) & (df_risk['risk_date'].dt.date <= last_week_date), column].values[-1]

            # Calculate the change values as percentages
            last_week_change = current_indicator_rates - last_week_indicator_rates
            last_month_change = current_indicator_rates - last_month_indicator_rates
            last_year_change = current_indicator_rates - last_year_indicator_rates
            last_quarter_change = current_indicator_rates - last_quarter_indicator_rates

            # Format eth_funding_ratesvalues as percentages
            current_indicator_rates_str =  f'{current_indicator_rates:.2f}%'
            last_week_indicator_rates_str = f'{last_week_indicator_rates:.2f}%'
            last_month_indicator_rates_str = f'{last_month_indicator_rates:.2f}%'
            last_year_indicator_rates_str = f'{last_year_indicator_rates:.2f}%'
            last_quarter_indicator_rates_str = f'{last_quarter_indicator_rates:.2f}%'

                # Create a dictionary for the indicator's eth_funding_rates data
            indicator_data = {
                    'Indicator': column,
                    'WTD': last_week_indicator_rates_str,
                    'WTD (Δ)': f'{last_week_change:.2f}%',
                    'MTD': last_month_indicator_rates_str,
                    'MTD (Δ)': f'{last_month_change:.2f}%',
                    'QTD': last_quarter_indicator_rates_str,
                    'QTD (Δ)': f'{last_quarter_change:.2f}%',
                    'YTD': last_year_indicator_rates_str,
                    'YTD (Δ)': f'{last_year_change:.2f}%'
                }

                # Append the indicator's data to the eth_funding_rates_table_data list
            indicator_rates_table_data.append(indicator_data)

        # Create the eth_funding_rates_table DataFrame
        indicator_rates_table = pd.DataFrame(indicator_rates_table_data)

        return fig_risk, indicator_rates_table
    
    def create_plot46():

        basic = HTTPBasicAuth('numeus', '3upqwx0@Y67he7XD')
        data_exposures_counterparty = session1.get('https://reporting-api.eltican.com/exposures', auth=basic).json()

        # Extract exposures data
        exposures_list_counterparty = data_exposures_counterparty.get('exposures', [])

        # Convert the exposures list to a DataFrame
        df_exposures_counterparty = pd.DataFrame(exposures_list_counterparty)

        # Group the DataFrame by 'counterparty' and sum the 'exposure' for each counterparty
        grouped_df_counterparty = df_exposures_counterparty.groupby('counterparty')['exposure'].sum().reset_index()

        # Create the donut chart using Plotly
        fig_donut = go.Figure(data=[go.Pie(labels=grouped_df_counterparty['counterparty'],
                                            values=grouped_df_counterparty['exposure'],
                                            hole=0.5)])

        fig_donut.update_layout(
                legend=dict(
                    orientation="h",
                    y=-0.2,  # Adjust the value to control the vertical position of the legend
                    x=0.5,  # Adjust the value to control the horizontal position of the legend
                    xanchor='center'
                )
            )

            # Set the title for the chart
        fig_donut.update_layout(title='AUM By Counterparty')

        return fig_donut
    
    def create_plot47():
        basic = HTTPBasicAuth('numeus', '3upqwx0@Y67he7XD')
        data_exposures_coin = session1.get('https://reporting-api.eltican.com/exposures', auth=basic).json()

        # Extract exposures data
        exposures_list_coin = data_exposures_coin.get('exposures', [])

        # Convert the exposures list to a DataFrame
        df_exposures_coin = pd.DataFrame(exposures_list_coin)

        # Group the DataFrame by 'coin' and sum the 'exposure' for each coin
        grouped_df_coin = df_exposures_coin.groupby('coin')['exposure'].sum().reset_index()

        # Create the donut chart using Plotly
        fig_donut_coin = go.Figure(data=[go.Pie(labels=grouped_df_coin['coin'],
                                        values=grouped_df_coin['exposure'],
                                        hole=0.5)])
        
        fig_donut_coin.update_layout(
                legend=dict(
                orientation="h",
                y=-0.2,  # Adjust the value to control the vertical position of the legend
                x=0.5,  # Adjust the value to control the horizontal position of the legend
                xanchor='center'
                )
            )

        # Create the donut chart using Plotly
        #fig_donut = go.Figure(data_exposures=[go.Pie(labels=df_exposures['ExposureType'],
                                        #values=df_exposures['ExposureValue'],
                                        #hole=0.5)])

        # Set the title for the chart
        fig_donut_coin.update_layout(title='AUM By Coin')

        # Render the donut chart using Streamlit
        return fig_donut_coin
    
    #plot45, indicator_rates_table = create_plot45()
    #plot46 = create_plot46()
    #plot47 = create_plot47()

    #if plot45 is not None and plot47 is not None and plot46 is not None:

        #col1, col2 = st.columns(2)
        #col1.plotly_chart(plot45, use_container_width=True)
        #col1.dataframe(indicator_rates_table, hide_index = True)
        #col2.plotly_chart(plot46, use_container_width=True)
        #col2.dataframe(grouped_df_counterparty_pivot) #, hide_index = True)

        #col1, col2 = st.columns(2)
        #col1.plotly_chart(plot47, use_container_width=True)

    plot45, indicator_rates_table = create_plot45()
    plot46 = create_plot46()
    plot47 = create_plot47()

    if plot45 is not None and plot46 is not None and plot47 is not None:
        col1, col2 = st.columns(2)
        col1.plotly_chart(plot45, use_container_width=True)
        col1.dataframe(indicator_rates_table, hide_index=True)
        col2.plotly_chart(plot46, use_container_width=True)

        col1, col2 = st.columns(2)
        col1.plotly_chart(plot47, use_container_width=True)