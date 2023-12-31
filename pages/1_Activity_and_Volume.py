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

st.title('Activity and Volume')


# Define the selectbox and clear cache button
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

tab1,tab2,tab3 = st.tabs(["Spot", "Derivatives","Networks"])

#session2 = CachedSession('cache2', expire_after=timedelta(hours=1))

with tab1:
    @st.cache_data(ttl=3600)
    def create_plot8():
        url8 = "https://www.theblock.co/api/charts/chart/decentralized-finance/dex-non-custodial/dex-to-cex-spot-trade-volume"
        r8 = requests.get(url8)
        r_json8 = r8.json()

        output_dataframe8 = pd.DataFrame()
        series_dict8 = r_json8['chart']['jsonFile']['Series']
        for vol in series_dict8:
            df_ = pd.DataFrame(series_dict8[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'Volume'})
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%Y-%m-%d"))
            output_dataframe8 = pd.concat([df_, output_dataframe8])

        output_dataframe8['date'] = pd.to_datetime(output_dataframe8['date'])

        fig8 = px.line(output_dataframe8, x='date', y='Volume')
        fig8.update_layout(
            xaxis_title="Date",
            yaxis_title=" Trade Volume (%)",
            hovermode="x"
        )
        fig8.update_traces(line_color="#7030A0")    

        fig8.update_xaxes(
            tickformat="%b-%y"  # Format x-axis tick labels as "Jun-22", "Jun-23", etc.
        )

        fig8.update_traces(
            hovertemplate='<b>%{x|%d-%b-%y}</b><br>Volume: %{y:.2f}%'
        )

        # Format y-axis tick labels as percentages
        fig8.update_yaxes(ticksuffix="%")

        current_dex_to_cex_spot = output_dataframe8['Volume'].iloc[-1]
        
        # Calculate the quarterly, monthly, and yearly maximum dex_to_cex_spot values
        last_year_dex_to_cex_spot = output_dataframe8.loc[output_dataframe8['date'].dt.year == last_year_date.year, 'Volume'].values[-1]
        last_month_dex_to_cex_spot = output_dataframe8.loc[output_dataframe8['date'].dt.year == last_month_date.year]
        last_month_dex_to_cex_spot= last_month_dex_to_cex_spot.loc[last_month_dex_to_cex_spot['date'].dt.month == last_month_date.month]
        last_month_dex_to_cex_spot= last_month_dex_to_cex_spot['Volume'].values[-1]

        last_quarter_dex_to_cex_spot= output_dataframe8.loc[(output_dataframe8['date'].dt.date >= last_quarter_start_date) & (output_dataframe8['date'].dt.date <= last_quarter_date)]
        last_quarter_dex_to_cex_spot = last_quarter_dex_to_cex_spot['Volume'].values[-1]
        #last_week_dex_to_cex_spot = output_dataframe8.loc[(output_dataframe8['date'].dt.date >= last_week_start_date) & (output_dataframe8['date'].dt.date <= last_week_date)]
        #last_week_dex_to_cex_spot = last_week_dex_to_cex_spot['Volume'].values[-1]

        # Format dex_to_cex_spot values as percentages
        current_dex_to_cex_spot_str = f'{current_dex_to_cex_spot:.2f}%'
        #last_week_dex_to_cex_spot_str = f'{last_week_dex_to_cex_spot:.2f}%'
        last_month_dex_to_cex_spot_str = f'{last_month_dex_to_cex_spot:.2f}%'
        last_year_dex_to_cex_spot_str = f'{last_year_dex_to_cex_spot:.2f}%'
        last_quarter_dex_to_cex_spot_str = f'{last_quarter_dex_to_cex_spot:.2f}%'

        # Calculate the change values as percentages
        #last_week_change = current_dex_to_cex_spot - last_week_dex_to_cex_spot
        last_month_change = current_dex_to_cex_spot - last_month_dex_to_cex_spot
        last_year_change = current_dex_to_cex_spot - last_year_dex_to_cex_spot
        last_quarter_change = current_dex_to_cex_spot - last_quarter_dex_to_cex_spot

        # Create the dex_to_cex_spot table
        dex_to_cex_spot_table = pd.DataFrame({
            'Period': ['MTD', 'QTD', 'YTD'],
            'Volume': [last_month_dex_to_cex_spot_str, last_quarter_dex_to_cex_spot_str, last_year_dex_to_cex_spot_str],
            'Date': [last_month_date.strftime("%d %b %Y"), last_quarter_date.strftime("%d %b %Y"), last_year_date.strftime("%d %b %Y")],
            'Δ': [f'{last_month_change:.2f}%', f'{last_quarter_change:.2f}%', f'{last_year_change:.2f}%']
        })

        fig8.add_annotation(
            xref="paper",
            yref="paper",
            x=0.98,
            y=0.25,
            xanchor="right",
            yanchor="top",
            text=f"Current Trade Volume: {current_dex_to_cex_spot:.2f}%",
            showarrow=False,
            align="right",
            font=dict(
                family="Arial",
                size=12,
                color="white"
            )
        )

        return fig8, dex_to_cex_spot_table

    @st.cache_data(ttl=3600)
    def create_plot16():
        url16 = "https://www.theblock.co/api/charts/chart/crypto-markets/spot/cryptocurrency-exchange-volume-monthly"
        r16 = requests.get(url16)
        r_json16 = r16.json()

        output_dataframe16 = pd.DataFrame()
        series_dict16 = r_json16['chart']['jsonFile']['Series']
        for vol in series_dict16:
            df_ = pd.DataFrame(series_dict16[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'Volume'})
            df_['Exchange'] = vol
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%Y-%m-%d"))
            output_dataframe16 = pd.concat([df_, output_dataframe16])

        # Convert date column to datetime format
        output_dataframe16['date'] = pd.to_datetime(output_dataframe16['date'])
        exchange_to_exclude = 'Liquid'
        output_dataframe16 = output_dataframe16[output_dataframe16['Exchange'] != exchange_to_exclude]

        # Filter the dataframe for the last day
        last_date = output_dataframe16['date'].max()
        last_day_data = output_dataframe16[output_dataframe16['date'] == last_date]

        # Sort the exchanges based on their volumes on the last day
        sorted_tokens = last_day_data.groupby('Exchange')['Volume'].sum().sort_values(ascending=False)

        # Calculate the total volume on the last day
        total_volume_last_day = last_day_data['Volume'].sum()

        # Calculate the threshold for 80% of the total volume on the last day
        threshold = 0.80 * total_volume_last_day

        # Filter the exchanges based on the threshold
        filtered_tokens = []
        cumulative_volume = 0

        for exchange, volume in sorted_tokens.items():
            cumulative_volume += volume
            filtered_tokens.append(exchange)
            
            if cumulative_volume >= threshold:
                break
    
        remaining_tokens = output_dataframe16[~output_dataframe16['Exchange'].isin(filtered_tokens)]['Exchange'].unique()
        # Group the data by date and exchange to get the aggregated DataFrame for remaining_tokens
        remaining_tokens_data = output_dataframe16[output_dataframe16['Exchange'].isin(remaining_tokens)]
        remaining_tokens_data_grouped = remaining_tokens_data.groupby(['date', 'Exchange']).sum().reset_index()

        # Create a DataFrame for "Others" containing aggregated volume for remaining_tokens
        others_data = remaining_tokens_data_grouped.groupby('date')['Volume'].sum().reset_index()
        others_count = len(remaining_tokens)
        others_data['Exchange'] = f'+{others_count} Others'

        # Combine the data for filtered tokens and others into a single DataFrame
        combined_data = pd.concat([output_dataframe16[output_dataframe16['Exchange'].isin(filtered_tokens)], others_data])

        # Group the combined data by date and exchange to get the aggregated DataFrame
        output_dataframe_agg = combined_data.groupby(['date', 'Exchange']).sum().reset_index()
        total_volume_per_month = output_dataframe_agg.groupby('date')['Volume'].sum()

        # Sort the DataFrame based on the total volume of each token on the last day (in descending order)
        sorted_tokens = output_dataframe_agg.groupby('Exchange')['Volume'].sum().sort_values(ascending=False).index
        output_dataframe_agg['Exchange'] = pd.Categorical(output_dataframe_agg['Exchange'], categories=sorted_tokens, ordered=True)
        output_dataframe_agg.sort_values(['date', 'Exchange'], inplace=True)

        # Create the stacked bar chart
        fig16 = go.Figure()

        for token in output_dataframe_agg['Exchange'].unique():
            custom_color = 'grey' if token == 'Binance' else None
            group = output_dataframe_agg[output_dataframe_agg['Exchange'] == token]

            fig16.add_trace(go.Bar(
                x=group['date'],
                y=group['Volume'],
                name=token,
                marker=dict(color=custom_color)
            ))

        fig16.add_trace(go.Scatter(
                x=total_volume_per_month.index,
                y=total_volume_per_month.values,  # Using total volume for that specific date
                mode='lines+markers',
                name='Total Volume',
                line=dict(color='#7030A0', width=2)
            ))

        fig16.update_layout(
            barmode='stack',
            xaxis=dict(
                title="Date",
                tickformat="%b-%y",
                domain=[0, 1]
            ),
            yaxis=dict(
                title="Volume (in Trillions USD)"
            ),
            hovermode="x",
            legend=dict(
                orientation="h",
                y=-0.2,
                x=0.5,
                xanchor='center'
            )
        )

        fig16.update_traces(
            hovertemplate='<b>%{x|%d-%b-%y}</b><br>Volume: %{y}'
        )

        fig16.update_yaxes(tickprefix="$")

        monthly_exchange_volume_table_data = []

        for token in filtered_tokens:
            # Calculate the last year's value_locked_by_cat using the last date of the previous year
            group = output_dataframe16[output_dataframe16['Exchange'] == token]

            current_monthly_exchange_volume = group['Volume'].iloc[-1]

            # Calculate the current, last year, last month, last quarter implied_btc_volatility values
            last_year_monthly_exchange_volume = group.loc[group['date'].dt.year == last_year_date.year, 'Volume'].values[-1]
            last_month_monthly_exchange_volume = group.loc[(group['date'].dt.year == last_month_date.year) & (group['date'].dt.month == last_month_date.month), 'Volume'].values[-1]
            last_quarter_monthly_exchange_volume = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date), 'Volume'].values[-1]
            #last_week_monthly_exchange_volume = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date), 'Volume'].values[-1]

            # Format value_locked_by_cat values in trillions
            current_monthly_exchange_volume_str = f'{current_monthly_exchange_volume/1e9:.3f}B'
            #last_week_monthly_exchange_volume_str = f'{last_week_monthly_exchange_volume/1e9:.3f}B'
            last_month_monthly_exchange_volume_str = f'{last_month_monthly_exchange_volume/1e9:.3f}B'
            last_year_monthly_exchange_volume_str = f'{last_year_monthly_exchange_volume/1e9:.3f}B'
            last_quarter_monthly_exchange_volume_str = f'{last_quarter_monthly_exchange_volume/1e9:.3f}B'

            # Calculate the change values as percentages
            #last_week_change = ((current_monthly_exchange_volume - last_week_monthly_exchange_volume) / last_week_monthly_exchange_volume) * 100
            last_month_change = ((current_monthly_exchange_volume - last_month_monthly_exchange_volume) / last_month_monthly_exchange_volume) * 100
            last_year_change = ((current_monthly_exchange_volume - last_year_monthly_exchange_volume) / last_year_monthly_exchange_volume) * 100
            last_quarter_change = ((current_monthly_exchange_volume - last_quarter_monthly_exchange_volume) / last_quarter_monthly_exchange_volume) * 100

            # Create a dictionary for the indicator's value_locked_by_liq data
            indicator_data = {
                        'Indicator': token,
                        'MTD': last_month_monthly_exchange_volume_str,
                        'MTD (Δ)': f'{last_month_change:.2f}%',
                        'QTD': last_quarter_monthly_exchange_volume_str,
                        'QTD (Δ)': f'{last_quarter_change:.2f}%',
                        'YTD': last_year_monthly_exchange_volume_str,
                        'YTD (Δ)': f'{last_year_change:.2f}%'
                    }

            # Append the indicator's data to the value_locked_by_block_table_data list
            monthly_exchange_volume_table_data.append(indicator_data)

        # Create the eth_funding_rates_table DataFrame
        monthly_exchange_volume_table = pd.DataFrame(monthly_exchange_volume_table_data)

        return fig16, monthly_exchange_volume_table
    
    #@st.cache_data(ttl=3600)
    def main5():
        global selected_range2

        plot8, dex_to_cex_spot_table = create_plot8()
        plot16, monthly_exchange_volume_table = create_plot16()

        button_ranges_combined_2 = {
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
            (plot8, "DEX to CEX Spot Volume"),
            (plot16, "Monthly Exchange Volume"),

        ]

        for plot, title in plots_and_titles:
            plot.update_xaxes(
                range=button_ranges_combined_2[selected_range2],
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

        col1.plotly_chart(plot16, use_container_width=True)
        col1.dataframe(monthly_exchange_volume_table, hide_index = True)
        col2.plotly_chart(plot8, use_container_width=True)
        col2.dataframe(dex_to_cex_spot_table, hide_index = True)

    if __name__ == "__main__":
        main5()

with tab2:
    @st.cache_data(ttl=3600)
    def create_plot18():
        url18 = "https://www.theblock.co/api/charts/chart/crypto-markets/futures/aggregated-open-interest-of-bitcoin-futures-daily"
        r18 = requests.get(url18)
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
        fig18 = go.Figure()
        open_interest_btc_futures_table_data = []

        # Filter the dataframe for the last day
        last_date = output_dataframe18['date'].max()
        last_day_data = output_dataframe18[output_dataframe18['date'] == last_date]

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

        remaining_tokens = output_dataframe18[~output_dataframe18['Exchange'].isin(filtered_tokens)]['Exchange'].unique()
        # Group the data by date and exchange to get the aggregated DataFrame for remaining_tokens
        remaining_tokens_data = output_dataframe18[output_dataframe18['Exchange'].isin(remaining_tokens)]
        remaining_tokens_data_grouped = remaining_tokens_data.groupby(['date', 'Exchange']).sum().reset_index()

        # Create a DataFrame for "Others" containing aggregated volume for remaining_tokens
        others_data = remaining_tokens_data_grouped.groupby('date')['OI'].sum().reset_index()
        others_count = len(remaining_tokens)
        others_data['Exchange'] = f'+{others_count} Others'

        # Combine the data for filtered tokens and others into a single DataFrame
        combined_data = pd.concat([output_dataframe18[output_dataframe18['Exchange'].isin(filtered_tokens)], others_data])

        # Group the combined data by date and exchange to get the aggregated DataFrame
        output_dataframe_agg = combined_data.groupby(['date', 'Exchange']).sum().reset_index()

        # Sort the DataFrame based on the total volume of each token on the last day (in descending order)
        sorted_tokens = output_dataframe_agg.groupby('Exchange')['OI'].sum().sort_values(ascending=False).index
        output_dataframe_agg['Exchange'] = pd.Categorical(output_dataframe_agg['Exchange'], categories=sorted_tokens, ordered=True)
        output_dataframe_agg.sort_values(['date', 'Exchange'], inplace=True)
        custom_color = 'grey'
    
        # Iterate over each token in the sorted order
        for token in output_dataframe_agg['Exchange'].unique():
            group = output_dataframe_agg[output_dataframe_agg['Exchange'] == token]
            fig18.add_trace(go.Scatter(
                            x=group['date'],
                            y=group['OI'],
                            mode='lines',
                            fill='tonexty',
                            name=token,
                            stackgroup='one',
                            line=dict(color=custom_color if token == 'OKX' else None)))

            fig18.update_layout(
                                xaxis=dict(
                                title="Date",
                                tickformat="%b-%y"
                            ),
                                yaxis=dict(title="Open Interest (in Billions)"),
                                hovermode="x"
                            )

            fig18.update_layout(
                                legend=dict(
                                orientation="h",
                                y=-0.2,  # Adjust the value to control the vertical position of the legend
                                x=0.5,  # Adjust the value to control the horizontal position of the legend
                                xanchor='center'
                                )
                            )

            fig18.update_traces(
                                hovertemplate='<b>%{x|%d-%b-%y}</b><br>OI: %{y}'
                            )
            
            fig18.update_yaxes(tickprefix="$")

        for token in filtered_tokens:
            group = output_dataframe18[output_dataframe18['Exchange'] == token]

            # Calculate the last year's open_interest_btc_futures using the last date of the previous year
            last_year_open_interest_btc_futures = group.loc[group['date'].dt.year == last_year_date.year, 'OI'].values[-1]
            current_open_interest_btc_futures = group['OI'].values[-1]

            # Calculate the last month's open_interest_btc_futures
            last_month_open_interest_btc_futures = group.loc[group['date'].dt.year == last_month_date.year]
            last_month_open_interest_btc_futures = last_month_open_interest_btc_futures.loc[last_month_open_interest_btc_futures['date'].dt.month == last_month_date.month]
            last_month_open_interest_btc_futures= last_month_open_interest_btc_futures['OI'].values[-1]

            # Calculate the last quarter's open_interest_btc_futures
            last_quarter_open_interest_btc_futures = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date)]
            last_quarter_open_interest_btc_futures = last_quarter_open_interest_btc_futures['OI'].values[-1]

            # Calculate the last week's open_interest_btc_futures
            last_week_open_interest_btc_futures = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date)]
            last_week_open_interest_btc_futures = last_week_open_interest_btc_futures['OI'].values[-1]

            # Format open_interest_btc_futures values in trillions
            current_open_interest_btc_futures_str = f'{current_open_interest_btc_futures/1e9:.3f}B'
            last_week_open_interest_btc_futures_str = f'{last_week_open_interest_btc_futures/1e9:.3f}B'
            last_month_open_interest_btc_futures_str = f'{last_month_open_interest_btc_futures/1e9:.3f}B'
            last_year_open_interest_btc_futures_str = f'{last_year_open_interest_btc_futures/1e9:.3f}B'
            last_quarter_open_interest_btc_futures_str = f'{last_quarter_open_interest_btc_futures/1e9:.3f}B'

            # Calculate the change values as percentages
            last_week_change = ((current_open_interest_btc_futures- last_week_open_interest_btc_futures) / last_week_open_interest_btc_futures) * 100
            last_month_change = ((current_open_interest_btc_futures - last_month_open_interest_btc_futures) / last_month_open_interest_btc_futures) * 100
            last_year_change = ((current_open_interest_btc_futures - last_year_open_interest_btc_futures) / last_year_open_interest_btc_futures) * 100
            last_quarter_change = ((current_open_interest_btc_futures - last_quarter_open_interest_btc_futures) / last_quarter_open_interest_btc_futures) * 100

            # Create a dictionary for the indicator's open_interest_btc_futures data
            indicator_data = {
                        'Indicator': token,
                        'WTD': last_week_open_interest_btc_futures_str,
                        'WTD (Δ)': f'{last_week_change:.2f}%',
                        'MTD': last_month_open_interest_btc_futures_str,
                        'MTD (Δ)': f'{last_month_change:.2f}%',
                        'QTD': last_quarter_open_interest_btc_futures_str,
                        'QTD (Δ)': f'{last_quarter_change:.2f}%',
                        'YTD': last_year_open_interest_btc_futures_str,
                        'YTD (Δ)': f'{last_year_change:.2f}%'
                    }

            # Append the indicator's data to the open_interest_btc_futures_table_data list
            open_interest_btc_futures_table_data.append(indicator_data)

        # Create the bbtc_funding_rates_table DataFrame
        open_interest_btc_futures_table = pd.DataFrame(open_interest_btc_futures_table_data)

        return fig18, open_interest_btc_futures_table

    @st.cache_data(ttl=3600)
    def create_plot19():
        url19 = "https://www.theblock.co/api/charts/chart/crypto-markets/futures/aggregated-open-interest-of-ethereum-futures-daily"
        r19 = requests.get(url19)
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
        fig19 = go.Figure()
        open_interest_eth_futures_table_data = []

        # Filter the dataframe for the last day
        last_date = output_dataframe19['date'].max()
        last_day_data = output_dataframe19[output_dataframe19['date'] == last_date]

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

        remaining_tokens = output_dataframe19[~output_dataframe19['Exchange'].isin(filtered_tokens)]['Exchange'].unique()
        # Group the data by date and exchange to get the aggregated DataFrame for remaining_tokens
        remaining_tokens_data = output_dataframe19[output_dataframe19['Exchange'].isin(remaining_tokens)]
        remaining_tokens_data_grouped = remaining_tokens_data.groupby(['date', 'Exchange']).sum().reset_index()

        # Create a DataFrame for "Others" containing aggregated volume for remaining_tokens
        others_data = remaining_tokens_data_grouped.groupby('date')['OI'].sum().reset_index()
        others_count = len(remaining_tokens)
        others_data['Exchange'] = f'+{others_count} Others'

        # Combine the data for filtered tokens and others into a single DataFrame
        combined_data = pd.concat([output_dataframe19[output_dataframe19['Exchange'].isin(filtered_tokens)], others_data])

        # Group the combined data by date and exchange to get the aggregated DataFrame
        output_dataframe_agg = combined_data.groupby(['date', 'Exchange']).sum().reset_index()

        # Sort the DataFrame based on the total volume of each token on the last day (in descending order)
        sorted_tokens = output_dataframe_agg.groupby('Exchange')['OI'].sum().sort_values(ascending=False).index
        output_dataframe_agg['Exchange'] = pd.Categorical(output_dataframe_agg['Exchange'], categories=sorted_tokens, ordered=True)
        output_dataframe_agg.sort_values(['date', 'Exchange'], inplace=True)
        custom_color = 'grey'

        # Iterate over each token in the sorted order
        for token in output_dataframe_agg['Exchange'].unique():
            group = output_dataframe_agg[output_dataframe_agg['Exchange'] == token]
            fig19.add_trace(go.Scatter(
                            x=group['date'],
                            y=group['OI'],
                            mode='lines',
                            fill='tonexty',
                            name=token,
                            stackgroup='one',
                            line=dict(color=custom_color if token == 'OKX' else None)))

            fig19.update_layout(
                                xaxis=dict(
                                title="Date",
                                tickformat="%b-%y"
                            ),
                                yaxis=dict(title="Open Interest (in Billions)"),
                                hovermode="x"
                            )

            fig19.update_layout(
                                legend=dict(
                                orientation="h",
                                y=-0.2,  # Adjust the value to control the vertical position of the legend
                                x=0.5,  # Adjust the value to control the horizontal position of the legend
                                xanchor='center'
                                )
                            )

            fig19.update_traces(
                                hovertemplate='<b>%{x|%d-%b-%y}</b><br>OI: %{y}'
                            )
            
            fig19.update_yaxes(tickprefix="$")

        for token in filtered_tokens:
            group = output_dataframe19[output_dataframe19['Exchange'] == token]

            # Calculate the last year's open_interest_btc_futures using the last date of the previous year
            last_year_open_interest_eth_futures = group.loc[group['date'].dt.year == last_year_date.year, 'OI'].values[-1]
            current_open_interest_eth_futures = group['OI'].values[-1]

            # Calculate the last month's open_interest_btc_futures
            last_month_open_interest_eth_futures = group.loc[group['date'].dt.year == last_month_date.year]
            last_month_open_interest_eth_futures = last_month_open_interest_eth_futures.loc[last_month_open_interest_eth_futures['date'].dt.month == last_month_date.month]
            last_month_open_interest_eth_futures= last_month_open_interest_eth_futures['OI'].values[-1]

            # Calculate the last quarter's open_interest_btc_futures
            last_quarter_open_interest_eth_futures = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date)]
            last_quarter_open_interest_eth_futures = last_quarter_open_interest_eth_futures['OI'].values[-1]

            # Calculate the last week's open_interest_btc_futures
            last_week_open_interest_eth_futures = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date)]
            last_week_open_interest_eth_futures = last_week_open_interest_eth_futures['OI'].values[-1]

            # Format open_interest_eth_futures values in trillions
            current_open_interest_eth_futures_str = f'{current_open_interest_eth_futures/1e9:.3f}B'
            last_week_open_interest_eth_futures_str = f'{last_week_open_interest_eth_futures/1e9:.3f}B'
            last_month_open_interest_eth_futures_str = f'{last_month_open_interest_eth_futures/1e9:.3f}B'
            last_year_open_interest_eth_futures_str = f'{last_year_open_interest_eth_futures/1e9:.3f}B'
            last_quarter_open_interest_eth_futures_str = f'{last_quarter_open_interest_eth_futures/1e9:.3f}B'

            # Calculate the change values as percentages
            last_week_change = ((current_open_interest_eth_futures- last_week_open_interest_eth_futures) / last_week_open_interest_eth_futures) * 100
            last_month_change = ((current_open_interest_eth_futures - last_month_open_interest_eth_futures) / last_month_open_interest_eth_futures) * 100
            last_year_change = ((current_open_interest_eth_futures - last_year_open_interest_eth_futures) / last_year_open_interest_eth_futures) * 100
            last_quarter_change = ((current_open_interest_eth_futures - last_quarter_open_interest_eth_futures) / last_quarter_open_interest_eth_futures) * 100

                # Create a dictionary for the indicator's open_interest_eth_futures data
            indicator_data = {
                        'Indicator': token,
                        'WTD': last_week_open_interest_eth_futures_str,
                        'WTD (Δ)': f'{last_week_change:.2f}%',
                        'MTD': last_month_open_interest_eth_futures_str,
                        'MTD (Δ)': f'{last_month_change:.2f}%',
                        'QTD': last_quarter_open_interest_eth_futures_str,
                        'QTD (Δ)': f'{last_quarter_change:.2f}%',
                        'YTD': last_year_open_interest_eth_futures_str,
                        'YTD (Δ)': f'{last_year_change:.2f}%'
                    }

                # Append the indicator's data to the open_interest_eth_futures_table_data list
            open_interest_eth_futures_table_data.append(indicator_data)

        # Create the eth_funding_rates_table DataFrame
        open_interest_eth_futures_table = pd.DataFrame(open_interest_eth_futures_table_data)

        return fig19, open_interest_eth_futures_table

    @st.cache_data(ttl=3600)
    def create_plot20():
        url20 = "https://www.theblock.co/api/charts/chart/decentralized-finance/derivatives/perpetual-protocol-trade-volume"
        r20 = requests.get(url20)
        r_json20 = r20.json()

        output_dataframe20 = pd.DataFrame()
        series_dict20 = r_json20['chart']['jsonFile']['Series']
        for vol in series_dict20:
            df_ = pd.DataFrame(series_dict20[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'Volume'})
            df_['Exchange'] = vol
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%Y-%m-%d"))
            output_dataframe20 = pd.concat([df_, output_dataframe20])

        # Convert date column to datetime format
        output_dataframe20['date'] = pd.to_datetime(output_dataframe20['date'])
        perp_swap_trade_volume_table_data = []

        # Create the stacked bar chart
        fig20 = go.Figure()

        for token, group in output_dataframe20.groupby('Exchange'):
            custom_color = 'orange' if token == 'Synthetix' else None

            fig20.add_trace(go.Bar(
                x=group['date'],
                y=group['Volume'],
                name=token,
                legendgroup=token,
                marker = dict(color = custom_color)
            ))

            fig20.update_layout(
                barmode='stack',
                xaxis=dict(
                    title="Date",
                    tickformat="%b-%y",
                    domain=[0, 1]
                ),
                yaxis=dict(
                    title="Volume (in Billions USD)"
                ),
                hovermode="x",
                legend=dict(
                    orientation="h",
                    y=-0.2,
                    x=0.5,
                    xanchor='center'
                )
            )

            fig20.update_traces(
                hovertemplate='<b>%{x|%d-%b-%y}</b><br>Volume: %{y}'
            )

            fig20.update_yaxes(tickprefix="$")

            # Calculate the last year's perp_swap_trade_volume using the last date of the previous year
            last_year_perp_swap_trade_volume= group.loc[group['date'].dt.year == last_year_date.year, 'Volume'].values[-1]
            current_perp_swap_trade_volume = group['Volume'].values[-1]

            # Calculate the last month's operp_swap_trade_volume
            last_month_perp_swap_trade_volume = group.loc[group['date'].dt.year == last_month_date.year]
            last_month_perp_swap_trade_volume = last_month_perp_swap_trade_volume.loc[last_month_perp_swap_trade_volume['date'].dt.month == last_month_date.month]
            last_month_perp_swap_trade_volume = last_month_perp_swap_trade_volume['Volume'].values[-1]

            # Calculate the last quarter's perp_swap_trade_volume
            last_quarter_perp_swap_trade_volume = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date)]
            last_quarter_perp_swap_trade_volume = last_quarter_perp_swap_trade_volume['Volume'].values[-1]

            # Calculate the last week's perp_swap_trade_volume
            last_week_perp_swap_trade_volume = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date)]
            last_week_perp_swap_trade_volume = last_week_perp_swap_trade_volume['Volume'].values[-1]

            # Format perp_swap_trade_volume values in trillions
            current_perp_swap_trade_volume_str = f'{current_perp_swap_trade_volume/1e9:.3f}B'
            last_week_perp_swap_trade_volume_str = f'{last_week_perp_swap_trade_volume/1e9:.3f}B'
            last_month_perp_swap_trade_volume_str = f'{last_month_perp_swap_trade_volume/1e9:.3f}B'
            last_year_perp_swap_trade_volume_str = f'{last_year_perp_swap_trade_volume/1e9:.3f}B'
            last_quarter_perp_swap_trade_volume_str = f'{last_quarter_perp_swap_trade_volume/1e9:.3f}B'

            # Calculate the change values as percentages
            last_week_change = ((current_perp_swap_trade_volume - last_week_perp_swap_trade_volume) / last_week_perp_swap_trade_volume) * 100
            last_month_change = ((current_perp_swap_trade_volume- last_month_perp_swap_trade_volume) / last_month_perp_swap_trade_volume) * 100
            last_year_change = ((current_perp_swap_trade_volume - last_year_perp_swap_trade_volume) / last_year_perp_swap_trade_volume) * 100
            last_quarter_change = ((current_perp_swap_trade_volume - last_quarter_perp_swap_trade_volume) / last_quarter_perp_swap_trade_volume) * 100

                # Create a dictionary for the indicator's perp_swap_trade_volumes data
            indicator_data = {
                            'Indicator': token,
                            'WTD': last_week_perp_swap_trade_volume_str,
                            'WTD (Δ)': f'{last_week_change:.2f}%',
                            'MTD': last_month_perp_swap_trade_volume_str,
                            'MTD (Δ)': f'{last_month_change:.2f}%',
                            'QTD': last_quarter_perp_swap_trade_volume_str,
                            'QTD (Δ)': f'{last_quarter_change:.2f}%',
                            'YTD': last_year_perp_swap_trade_volume_str,
                            'YTD (Δ)': f'{last_year_change:.2f}%'
                        }

            # Append the indicator's data to the perp_swap_trade_volume_table_data list
            perp_swap_trade_volume_table_data.append(indicator_data)

        # Create the eth_funding_rates_table DataFrame
        perp_swap_trade_volume_table = pd.DataFrame(perp_swap_trade_volume_table_data)

        return fig20, perp_swap_trade_volume_table

    @st.cache_data(ttl=3600)
    def create_plot21():
        url21 = "https://www.theblock.co/api/charts/chart/decentralized-finance/derivatives/dex-to-cex-futures-trade-volume"
        r21 = requests.get(url21)
        r_json21 = r21.json()

        output_dataframe21 = pd.DataFrame()
        series_dict21 = r_json21['chart']['jsonFile']['Series']
        for vol in series_dict21:
            df_ = pd.DataFrame(series_dict21[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'Volume'})
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%Y-%m-%d"))
            output_dataframe21 = pd.concat([df_, output_dataframe21])

        output_dataframe21['date'] = pd.to_datetime(output_dataframe21['date'])

        fig21 = px.line(output_dataframe21, x='date', y='Volume')
        fig21.update_layout(
            xaxis_title="Date",
            yaxis_title=" Trade Volume (%)",
            hovermode="x"
        )

        fig21.update_xaxes(
            tickformat="%b-%y"  # Format x-axis tick labels as "Jun-22", "Jun-23", etc.
        )

        fig21.update_traces(
            hovertemplate='<b>%{x|%d-%b-%y}</b><br>Volume: %{y:.2f}%'
        )

        # Format y-axis tick labels as percentages
        fig21.update_yaxes(ticksuffix="%")

        current_dex_to_cex_futures = output_dataframe21['Volume'].iloc[-1]
        
        # Calculate the quarterly, monthly, and yearly maximum dex_to_cex_spot values
        last_year_dex_to_cex_futures = output_dataframe21.loc[output_dataframe21['date'].dt.year == last_year_date.year, 'Volume'].values[-1]
        last_month_dex_to_cex_futures = output_dataframe21.loc[output_dataframe21['date'].dt.year == last_month_date.year]
        last_month_dex_to_cex_futures= last_month_dex_to_cex_futures.loc[last_month_dex_to_cex_futures['date'].dt.month == last_month_date.month]
        last_month_dex_to_cex_futures= last_month_dex_to_cex_futures['Volume'].values[-1]

        last_quarter_dex_to_cex_futures = output_dataframe21.loc[(output_dataframe21['date'].dt.date >= last_quarter_start_date) & (output_dataframe21['date'].dt.date <= last_quarter_date)]
        last_quarter_dex_to_cex_futures = last_quarter_dex_to_cex_futures['Volume'].values[-1]
        #last_week_dex_to_cex_spot = output_dataframe8.loc[(output_dataframe8['date'].dt.date >= last_week_start_date) & (output_dataframe8['date'].dt.date <= last_week_date)]
        #last_week_dex_to_cex_spot = last_week_dex_to_cex_spot['Volume'].values[-1]

        # Format dex_to_cex_spot values as percentages
        current_dex_to_cex_futures_str = f'{current_dex_to_cex_futures:.2f}%'
        #last_week_dex_to_cex_spot_str = f'{last_week_dex_to_cex_futures:.2f}%'
        last_month_dex_to_cex_futures_str = f'{last_month_dex_to_cex_futures:.2f}%'
        last_year_dex_to_cex_futures_str = f'{last_year_dex_to_cex_futures:.2f}%'
        last_quarter_dex_to_cex_futures_str = f'{last_quarter_dex_to_cex_futures:.2f}%'

        # Calculate the change values as percentages
        #last_week_change = current_dex_to_cex_futures - last_week_dex_to_cex_futures
        last_month_change = current_dex_to_cex_futures - last_month_dex_to_cex_futures
        last_year_change = current_dex_to_cex_futures - last_year_dex_to_cex_futures
        last_quarter_change = current_dex_to_cex_futures - last_quarter_dex_to_cex_futures

        # Create the dex_to_cex_futures table
        dex_to_cex_futures_table = pd.DataFrame({
            'Period': ['MTD', 'QTD', 'YTD'],
            'Volume': [last_month_dex_to_cex_futures_str, last_quarter_dex_to_cex_futures_str, last_year_dex_to_cex_futures_str],
            'Date': [last_month_date.strftime("%d %b %Y"), last_quarter_date.strftime("%d %b %Y"), last_year_date.strftime("%d %b %Y")],
            'Δ': [f'{last_month_change:.2f}%', f'{last_quarter_change:.2f}%', f'{last_year_change:.2f}%']
        })

        fig21.add_annotation(
            xref="paper",
            yref="paper",
            x=0.98,
            y=0.25,
            xanchor="right",
            yanchor="top",
            text=f"Current Trade Volume: {current_dex_to_cex_futures:.2f}%",
            showarrow=False,
            align="right",
            font=dict(
                family="Arial",
                size=12,
                color="white"
            )
        )

        return fig21, dex_to_cex_futures_table

    @st.cache_data(ttl=3600)
    def create_plot22():
        url22 = "https://www.theblock.co/api/charts/chart/crypto-markets/futures/volume-of-bitcoin-futures-monthly"
        r22 = requests.get(url22)
        r_json22 = r22.json()

        output_dataframe22 = pd.DataFrame()
        series_dict22 = r_json22['chart']['jsonFile']['Series']
        for vol in series_dict22:
            df_ = pd.DataFrame(series_dict22[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'Volume'})
            df_['Exchange'] = vol
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%Y-%m-%d"))
            output_dataframe22 = pd.concat([df_, output_dataframe22])

        # Convert date column to datetime format
        output_dataframe22['date'] = pd.to_datetime(output_dataframe22['date'])
        fig22 = go.Figure()
        volume_btc_futures_table_data = []

        # Filter the dataframe for the last day
        last_date = output_dataframe22['date'].max()
        last_day_data = output_dataframe22[output_dataframe22['date'] == last_date]

        # Sort the exchanges based on their volumes on the last day
        sorted_tokens = last_day_data.groupby('Exchange')['Volume'].sum().sort_values(ascending=False)

        # Calculate the total volume on the last day
        total_volume_last_day = last_day_data['Volume'].sum()

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
        
        remaining_tokens = output_dataframe22[~output_dataframe22['Exchange'].isin(filtered_tokens)]['Exchange'].unique()
        # Group the data by date and exchange to get the aggregated DataFrame for remaining_tokens
        remaining_tokens_data = output_dataframe22[output_dataframe22['Exchange'].isin(remaining_tokens)]
        remaining_tokens_data_grouped = remaining_tokens_data.groupby(['date', 'Exchange']).sum().reset_index()

        # Create a DataFrame for "Others" containing aggregated volume for remaining_tokens
        others_data = remaining_tokens_data_grouped.groupby('date')['Volume'].sum().reset_index()
        others_count = len(remaining_tokens)
        others_data['Exchange'] = f'+{others_count} Others'

        # Combine the data for filtered tokens and others into a single DataFrame
        combined_data = pd.concat([output_dataframe22[output_dataframe22['Exchange'].isin(filtered_tokens)], others_data])

        # Group the combined data by date and exchange to get the aggregated DataFrame
        output_dataframe_agg = combined_data.groupby(['date', 'Exchange']).sum().reset_index()

        # Sort the DataFrame based on the total volume of each token on the last day (in descending order)
        sorted_tokens = output_dataframe_agg.groupby('Exchange')['Volume'].sum().sort_values(ascending=False).index
        output_dataframe_agg['Exchange'] = pd.Categorical(output_dataframe_agg['Exchange'], categories=sorted_tokens, ordered=True)
        output_dataframe_agg.sort_values(['date', 'Exchange'], inplace=True)
        custom_color = 'orange'

        for token in output_dataframe_agg['Exchange'].unique():
            group = output_dataframe_agg[output_dataframe_agg['Exchange'] == token]

            fig22.add_trace(go.Bar(
                x=group['date'],
                y=group['Volume'],
                name=token,
                marker = dict(color = custom_color if token == 'Binance' else None)
            ))

        fig22.update_layout(
            barmode='stack',
            xaxis=dict(
                title="Date",
                tickformat="%b-%y",
                domain=[0, 1]
            ),
            yaxis=dict(
                title="Volume (in Trillions USD)"
            ),
            hovermode="x",
            legend=dict(
                orientation="h",
                y=-0.2,
                x=0.5,
                xanchor='center'
            )
        )

        fig22.update_traces(
            hovertemplate='<b>%{x|%d-%b-%y}</b><br>Volume: %{y}'
        )

        fig22.update_yaxes(tickprefix="$")

        for token in filtered_tokens:
            # Calculate the last year's value_locked_by_cat using the last date of the previous year
            group = output_dataframe22[output_dataframe22['Exchange'] == token]
            current_volume_btc_futures = group['Volume'].iloc[-1]

            # Calculate the current, last year, last month, last quarter implied_btc_volatility values
            last_year_volume_btc_futures = group.loc[group['date'].dt.year == last_year_date.year, 'Volume'].values[-1]
            last_month_volume_btc_futures = group.loc[(group['date'].dt.year == last_month_date.year) & (group['date'].dt.month == last_month_date.month), 'Volume'].values[-1]
            last_quarter_volume_btc_futures = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date), 'Volume'].values[-1]
            #last_week_volume_btc_futures = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date), 'Volume'].values[-1]

            # Format value_locked_by_cat values in trillions
            current_volume_btc_futures_str = f'{current_volume_btc_futures/1e12:.3f}T'
            #last_week_volume_btc_futures_str = f'{last_week_volume_btc_futures/1e12:.3f}T'
            last_month_volume_btc_futures_str = f'{last_month_volume_btc_futures/1e12:.3f}T'
            last_year_volume_btc_futures_str = f'{last_year_volume_btc_futures/1e12:.3f}T'
            last_quarter_volume_btc_futures_str = f'{last_quarter_volume_btc_futures/1e12:.3f}T'

            # Calculate the change values as percentages
            #last_week_change = ((current_volume_btc_futures- last_week_volume_btc_futures) / last_week_volume_btc_futures) * 100
            last_month_change = ((current_volume_btc_futures - last_month_volume_btc_futures) / last_month_volume_btc_futures) * 100
            last_year_change = ((current_volume_btc_futures - last_year_volume_btc_futures) / last_year_volume_btc_futures) * 100
            last_quarter_change = ((current_volume_btc_futures - last_quarter_volume_btc_futures) / last_quarter_volume_btc_futures) * 100

            # Create a dictionary for the indicator's value_locked_by_liq data
            indicator_data = {
                        'Indicator': token,
                        'MTD': last_month_volume_btc_futures_str,
                        'MTD (Δ)': f'{last_month_change:.2f}%',
                        'QTD': last_quarter_volume_btc_futures_str,
                        'QTD (Δ)': f'{last_quarter_change:.2f}%',
                        'YTD': last_year_volume_btc_futures_str,
                        'YTD (Δ)': f'{last_year_change:.2f}%'
                    }

            # Append the indicator's data to the value_locked_by_block_table_data list
            volume_btc_futures_table_data.append(indicator_data)

        # Create the eth_funding_rates_table DataFrame
        volume_btc_futures_table = pd.DataFrame(volume_btc_futures_table_data)

        return fig22, volume_btc_futures_table
    
    @st.cache_data(ttl=3600)
    def create_plot28():
        url28 = "https://www.theblock.co/api/charts/chart/crypto-markets/futures/volume-of-ethereum-futures-monthly"
        r28 = requests.get(url28)
        r_json28 = r28.json()

        output_dataframe28 = pd.DataFrame()
        series_dict28 = r_json28['chart']['jsonFile']['Series']
        for vol in series_dict28:
            df_ = pd.DataFrame(series_dict28[vol]['Data']).rename(columns={'Timestamp': 'date', 'Result': 'Volume'})
            df_['Exchange'] = vol
            df_['date'] = df_['date'].apply(lambda x: datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc).strftime("%Y-%m-%d"))
            output_dataframe28 = pd.concat([df_, output_dataframe28])

        # Convert date column to datetime format
        output_dataframe28['date'] = pd.to_datetime(output_dataframe28['date'])
        fig28 = go.Figure()
        volume_eth_futures_table_data = []

        # Filter the dataframe for the last day
        last_date = output_dataframe28['date'].max()
        last_day_data = output_dataframe28[output_dataframe28['date'] == last_date]

        # Sort the exchanges based on their volumes on the last day
        sorted_tokens = last_day_data.groupby('Exchange')['Volume'].sum().sort_values(ascending=False)

        # Calculate the total volume on the last day
        total_volume_last_day = last_day_data['Volume'].sum()

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
        
        remaining_tokens = output_dataframe28[~output_dataframe28['Exchange'].isin(filtered_tokens)]['Exchange'].unique()
        # Group the data by date and exchange to get the aggregated DataFrame for remaining_tokens
        remaining_tokens_data = output_dataframe28[output_dataframe28['Exchange'].isin(remaining_tokens)]
        remaining_tokens_data_grouped = remaining_tokens_data.groupby(['date', 'Exchange']).sum().reset_index()

        # Create a DataFrame for "Others" containing aggregated volume for remaining_tokens
        others_data = remaining_tokens_data_grouped.groupby('date')['Volume'].sum().reset_index()
        others_count = len(remaining_tokens)
        others_data['Exchange'] = f'+{others_count} Others'

        # Combine the data for filtered tokens and others into a single DataFrame
        combined_data = pd.concat([output_dataframe28[output_dataframe28['Exchange'].isin(filtered_tokens)], others_data])

        # Group the combined data by date and exchange to get the aggregated DataFrame
        output_dataframe_agg = combined_data.groupby(['date', 'Exchange']).sum().reset_index()

        # Sort the DataFrame based on the total volume of each token on the last day (in descending order)
        sorted_tokens = output_dataframe_agg.groupby('Exchange')['Volume'].sum().sort_values(ascending=False).index
        output_dataframe_agg['Exchange'] = pd.Categorical(output_dataframe_agg['Exchange'], categories=sorted_tokens, ordered=True)
        output_dataframe_agg.sort_values(['date', 'Exchange'], inplace=True)
        custom_color = 'orange'

        for token in output_dataframe_agg['Exchange'].unique():
            group = output_dataframe_agg[output_dataframe_agg['Exchange'] == token]

            fig28.add_trace(go.Bar(
                x=group['date'],
                y=group['Volume'],
                name=token,
                marker = dict(color = custom_color if token == 'OKX' else None)
            ))

        fig28.update_layout(
            barmode='stack',
            xaxis=dict(
                title="Date",
                tickformat="%b-%y",
                domain=[0, 1]
            ),
            yaxis=dict(
                title="Volume (in Trillions USD)"
            ),
            hovermode="x",
            legend=dict(
                orientation="h",
                y=-0.2,
                x=0.5,
                xanchor='center'
            )
        )

        fig28.update_traces(
            hovertemplate='<b>%{x|%d-%b-%y}</b><br>Volume: %{y}'
        )

        fig28.update_yaxes(tickprefix="$")

        for token in filtered_tokens:
            # Calculate the last year's value_locked_by_cat using the last date of the previous year
            group = output_dataframe28[output_dataframe28['Exchange'] == token]
            current_volume_eth_futures = group['Volume'].iloc[-1]

            # Calculate the current, last year, last month, last quarter implied_btc_volatility values
            last_year_volume_eth_futures = group.loc[group['date'].dt.year == last_year_date.year, 'Volume'].values[-1]
            last_month_volume_eth_futures = group.loc[(group['date'].dt.year == last_month_date.year) & (group['date'].dt.month == last_month_date.month), 'Volume'].values[-1]
            last_quarter_volume_eth_futures = group.loc[(group['date'].dt.date >= last_quarter_start_date) & (group['date'].dt.date <= last_quarter_date), 'Volume'].values[-1]
            #last_week_volume_btc_futures = group.loc[(group['date'].dt.date >= last_week_start_date) & (group['date'].dt.date <= last_week_date), 'Volume'].values[-1]

            # Format value_locked_by_cat values in trillions
            current_volume_eth_futures_str = f'{current_volume_eth_futures/1e12:.3f}T'
            #last_week_volume_btc_futures_str = f'{last_week_volume_btc_futures/1e12:.3f}T'
            last_month_volume_eth_futures_str = f'{last_month_volume_eth_futures/1e12:.3f}T'
            last_year_volume_eth_futures_str = f'{last_year_volume_eth_futures/1e12:.3f}T'
            last_quarter_volume_eth_futures_str = f'{last_quarter_volume_eth_futures/1e12:.3f}T'

            # Calculate the change values as percentages
            #last_week_change = ((current_volume_btc_futures- last_week_volume_btc_futures) / last_week_volume_btc_futures) * 100
            last_month_change = ((current_volume_eth_futures - last_month_volume_eth_futures) / last_month_volume_eth_futures) * 100
            last_year_change = ((current_volume_eth_futures - last_year_volume_eth_futures) / last_year_volume_eth_futures) * 100
            last_quarter_change = ((current_volume_eth_futures - last_quarter_volume_eth_futures) / last_quarter_volume_eth_futures) * 100

            # Create a dictionary for the indicator's value_locked_by_liq data
            indicator_data = {
                        'Indicator': token,
                        'MTD': last_month_volume_eth_futures_str,
                        'MTD (Δ)': f'{last_month_change:.2f}%',
                        'QTD': last_quarter_volume_eth_futures_str,
                        'QTD (Δ)': f'{last_quarter_change:.2f}%',
                        'YTD': last_year_volume_eth_futures_str,
                        'YTD (Δ)': f'{last_year_change:.2f}%'
                    }

            # Append the indicator's data to the value_locked_by_block_table_data list
            volume_eth_futures_table_data.append(indicator_data)

        # Create the eth_funding_rates_table DataFrame
        volume_eth_futures_table = pd.DataFrame(volume_eth_futures_table_data)

        return fig28, volume_eth_futures_table
    
    def main3():
        global selected_range2

        plot18, open_interest_btc_futures_table = create_plot18()
        plot19, open_interest_eth_futures_table = create_plot19()
        plot20, perp_swap_trade_volume_table = create_plot20()
        plot21, dex_to_cex_futures_table = create_plot21()
        plot22, volume_btc_futures_table = create_plot22()
        plot28, volume_eth_futures_table = create_plot28()

        button_ranges_combined_2 = {
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
            (plot18, "Open Interest of BTC Futures"),
            (plot19, "Open Interest of ETH Futures"),
            (plot20, "Perp Swaps Trade Volume"),
            (plot21, "DEX to CEX Futures Volume"),
            (plot22, "Volume of BTC Futures"),
            (plot28, "Volume of ETH Futures")
        ]

        for plot, title in plots_and_titles:
            plot.update_xaxes(
                range=button_ranges_combined_2[selected_range2],
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

        col1.plotly_chart(plot18, use_container_width=True)
        col1.dataframe(open_interest_btc_futures_table, hide_index = True)
        col2.plotly_chart(plot19, use_container_width=True)
        col2.dataframe(open_interest_eth_futures_table, hide_index = True)

        col1, col2 = st.columns(2)

        col1.plotly_chart(plot20, use_container_width=True)
        col1.dataframe(perp_swap_trade_volume_table, hide_index = True)
        col2.plotly_chart(plot21, use_container_width=True)
        col2.dataframe(dex_to_cex_futures_table, hide_index = True)

        col1, col2 = st.columns(2)

        col1.plotly_chart(plot22, use_container_width=True)
        col1.dataframe(volume_btc_futures_table, hide_index = True)
        col2.plotly_chart(plot28, use_container_width=True)
        col2.dataframe(volume_eth_futures_table, hide_index = True)

    if __name__ == "__main__":
        main3()

with tab3:
    @st.cache_data(ttl=3600)
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

        fig3.update_traces(line_color="#7030A0")    

        fig3.update_xaxes(
            tickformat="%b-%y"  # Format x-axis tick labels as "Jun-22", "Jun-23", etc.
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

    @st.cache_data(ttl=3600)
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
        fig4.update_traces(line_color="#7030A0")    
    

        fig4.update_xaxes(
            tickformat="%b-%y"  # Format x-axis tick labels as "Jun-22", "Jun-23", etc.
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
    
    #@st.cache_data(ttl=3600)
    def main2():
        global selected_range2

        plot3, btc_transactions_table = create_plot3()
        plot4, eth_transactions_table  = create_plot4()

        button_ranges_combined_2 = {
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
            (plot3, "Transactions (BTC Network)"),
            (plot4, "Transactions (ETH Network)")
        ]

        for plot, title in plots_and_titles:
            plot.update_xaxes(
                range=button_ranges_combined_2[selected_range2],
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

        col1.plotly_chart(plot3, use_container_width=True)
        col1.dataframe(btc_transactions_table, hide_index = True)
        col2.plotly_chart(plot4, use_container_width=True)
        col2.dataframe(eth_transactions_table, hide_index = True)

    if __name__ == "__main__":
        main2()
