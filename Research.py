import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import datetime
from datetime import timedelta
import openpyxl

st.set_page_config(
    # Set page configuration
    page_title="MMA", layout="wide")

with st.sidebar:
    image = "https://forteus-media-research.s3.eu-west-1.amazonaws.com/public/images/Final+Logo+Forteus+by+Numeus+light.png"  # Replace with the actual path to your photo
    image_size = (300, 200)  # Replace with the desired width and height of the image in pixels
        #st.image(image, width=image_size[0], use_column_width=False)
    st.markdown(
            f'<div style="display: flex; justify-content: center;"><img src="{image}" width="{image_size[0]}"></div>',
            unsafe_allow_html=True)
    st.markdown('<div style="display: flex; justify-content: center;"><h1>July Market Update</h1></div>', unsafe_allow_html=True)
        #st.markdown("# July Market Update")

def main():
    st.title("Research")

    selected = option_menu(
        menu_title=None,
        options=["Events", "Tasks", "Selection Status"],
        icons=["calendar", "clipboard"],
        orientation="horizontal"
    )

    if selected == "Events":
        show_events()
    elif selected == "Tasks":
        show_tasks()
    elif selected == "Selection Status":
        show_selection_status()

def show_events():
    #EVENTS
    # Read the Excel file into a pandas DataFrame
    df_events = pd.read_excel("https://forteus-media-research.s3.eu-west-1.amazonaws.com/public/mma_reporting/output.xlsx",engine='openpyxl')

    column_name_mapping_events = {
        'STARTDATE': 'Date',
        'ALIAS': 'Funds',
        'NAME': 'Interaction',
        'NAME.1': 'Subject',
        'NAME.2': 'Selection Status',
        'PLACE': 'Location',
        'TOPIC': 'Summary'
        # Add more column mappings as needed
    }

    # Use the rename() method to rename the columns
    df_events.rename(columns=column_name_mapping_events, inplace=True)

    # Convert the 'STARTDATE' column to a datetime object
    df_events['Date'] = pd.to_datetime(df_events['Date']).dt.date
    #selections_to_drop = ['Universe']
    interactions_to_drop = ['Presentation','Conference','News']
    #df = df[~df['Selection'].isin(selections_to_drop)]
    df_events = df_events[~df_events['Interaction'].isin(interactions_to_drop)]
    #df = df.dropna(subset=['Selection'])

    # Add "category" column based on conditions
    df_events['Category'] = df_events['Selection Status'].apply(lambda x: 'Priority' if x in ['Under Observation', 'Under Review', 'Under DDR', 'Candidate', 'Candidate RC', 'Approval RC', 'Approved'] else 'Others')

    # Reorder the columns with 'Date' as the first column
    df_events = df_events[['Date', 'Funds', 'Selection Status', 'Interaction', 'Subject','Summary','Location', 'Category']]

    # Sort the DataFrame based on the 'STARTDATE' column in descending order
    df_sorted_events = df_events.sort_values(by='Date', ascending=False)

    # Function to filter DataFrame based on selected date range
    def filter_dataframe_events(df_events, start_date_events, end_date_events, interaction_events, category_filter_events): #selection,):
        
        start_date_events = pd.to_datetime(start_date_events).date() if start_date_events else df_events['Date'].min()
        end_date_events = pd.to_datetime(end_date_events).date() if end_date_events else df_events['Date'].max()

        # Filter based on selection if it's not None, otherwise, include all selections
        #mask_selection = df['Selection'].isin(selection) if selection else [True] * len(df)

        # Filter based on interaction if it's not None, otherwise, include all interactions
        mask_interaction_events = df_events['Interaction'].isin(interaction_events) if interaction_events else [True] * len(df_events)

        # Filter based on category if it's not None, otherwise, include all categories
        mask_category_events = df_events['Category'].isin(category_filter_events) if category_filter_events else [True] * len(df_events)


        # Combine date, selection, and interaction filters using the logical AND (&) operator
        mask_combined_events = (df_events['Date'] >= start_date_events) & (df_events['Date'] <= end_date_events) & mask_interaction_events & mask_category_events #& mask_selection
        
        filtered_df_events = df_events.loc[mask_combined_events].copy()

        return filtered_df_events

    # Streamlit app
    def main_events():
        # Initialize the variables with default values
        start_date_events = None
        end_date_events = None
        interaction_events = None
        category_filter_events = None

        # Date inputs for start and end date
        #start_date_events = st.date_input("Start Date")
        #end_date_events = st.date_input("End Date")

        # Get unique selection values from the 'SELECTION' column
        #selection_options = df['Selection'].unique().tolist()
        interaction_options_events = df_events['Interaction'].unique().tolist()
        category_options_events = df_events['Category'].unique().tolist()

        # Add Selectbox to choose the selection filter
        #selection = st.multiselect("Selection", selection_options)
        col1, col2 = st.columns(2)
        with col1:
            interaction_events = st.multiselect("Interaction", interaction_options_events)
            timeframe_filter = st.selectbox("Timeframe", ["1W", "2W", "3W", "1M", "1Q", "1Y","All"])
        with col2:
            category_filter_events = st.multiselect("Category", category_options_events)
            st.write("<p style='font-size: smaller; font-style: italic;'>Priority funds includes funds 'Under Observation', 'Candidate', 'Candidate RC', 'Under DDR', 'Approval RC', 'Under Review', and 'Approved'.</p>", unsafe_allow_html=True)

        # Add "Reset Filters" button
        if st.button("Reset Filters (Events)"):
            # Clear the date input and selectbox values
            start_date_events = None
            end_date_events = None
            interaction_events = None
            category_filter_events = None
            timeframe_filter = None

        # Make a copy of the DataFrame before filtering
        filtered_df_events = df_sorted_events.copy()

        if timeframe_filter != "None":
            # Filter the DataFrame based on the selected timeframe
            today = pd.Timestamp.today().date()
            if timeframe_filter == "1W":
                start_date_events = today - timedelta(weeks=1)
                end_date_events = today
            elif timeframe_filter == "2W":
                start_date_events = today - timedelta(weeks=2)
                end_date_events = today
            elif timeframe_filter == "3W":
                start_date_events = today - timedelta(weeks=3)
                end_date_events = today
            elif timeframe_filter == "1M":
                start_date_events = today - pd.DateOffset(months=1)
                end_date_events = today
            elif timeframe_filter == "1Q":
                start_date_events = today - pd.DateOffset(months=3)
                end_date_events = today
            elif timeframe_filter == "1Y":
                start_date_events = today - pd.DateOffset(years=1)
                end_date_events = today
            elif timeframe_filter == "All":
                start_date_events = None 
                end_date_events = None

        if start_date_events and end_date_events or interaction_events or category_filter_events: #or selection:
            # Filter the DataFrame based on selected date range, selection, and interaction
            filtered_df_events = filter_dataframe_events(filtered_df_events, start_date_events, end_date_events, interaction_events, category_filter_events) #selection, interaction, category_filter)
            # Drop the "Category" column from the filtered DataFrame
            filtered_df_events.drop(columns=['Category'], inplace=True)

            st.write("Events:")
            st.dataframe(filtered_df_events, hide_index=True)
        else:
            filtered_df_events.drop(columns=['Category'], inplace=True)
            # If no filters are selected, display the full DataFrame
            st.write("Events:")
            st.dataframe(filtered_df_events, hide_index=True)

    if __name__ == "__main__":
        main_events()

def show_tasks():
    #TASKS
    # Read the Excel file into a pandas DataFrame
    df_tasks = pd.read_excel("https://forteus-media-research.s3.eu-west-1.amazonaws.com/public/mma_reporting/output2.xlsx",engine='openpyxl')

    column_name_mapping_tasks = {
        'AssignedTo': 'Assigned To',
        'ALIAS': 'Funds',
        'STATUS': 'Status',
        'COMMENTS': 'Comment',
        'NAME': 'Selection Status',
        'STARTDATE': 'Start Date',
        'ENDDATE': 'End Date'
        # Add more column mappings as needed
    }
    # Use the rename() method to rename the columns
    df_tasks.rename(columns=column_name_mapping_tasks, inplace=True)

    # Convert the 'STARTDATE' column to a datetime object
    df_tasks['Start Date'] = pd.to_datetime(df_tasks['Start Date']).dt.date
    df_tasks['End Date'] = pd.to_datetime(df_tasks['End Date']).dt.date

    # Get today's date
    today = datetime.datetime.now().date()

    # Function to classify status based on start and end dates in the same row
    def classify_status(row):
        start_date = row['Start Date']
        end_date = row['End Date']

        if end_date < today:
            return 'Completed'
        elif start_date > today:
            return 'Upcoming'
        else:
            return 'Outstanding'

    # Create the 'Status Date' column using the classify_status function
    df_tasks['Status Date'] = df_tasks.apply(classify_status, axis=1)

    # Add "category" column based on conditions
    df_tasks['Category'] = df_tasks['Selection Status'].apply(lambda x: 'Priority' if x in ['Under Observation', 'Under Review', 'Under DDR', 'Candidate', 'Candidate RC', 'Approval RC', 'Approved'] else 'Others')

    # Reorder the columns with 'Date' as the first column
    df_tasks = df_tasks[['Status','Status Date','Assigned To', 'Start Date', 'End Date', 'Funds', 'Selection Status', 'Category', 'Comment']]

    # Sort the DataFrame based on the 'STARTDATE' column in descending order
    df_sorted_tasks = df_tasks.sort_values(by='Start Date', ascending=False)

    # Function to filter DataFrame based on selected date range
    def filter_dataframe_tasks(df_tasks, assignedto_tasks, category_filter_tasks, status_filter_tasks): #selection,):

        # Filter based on interaction if it's not None, otherwise, include all interactions
        mask_assignedto_tasks = df_tasks['Assigned To'].isin(assignedto_tasks) if assignedto_tasks else [True] * len(df_tasks)

        # Filter based on category if it's not None, otherwise, include all categories
        mask_category_tasks = df_tasks['Category'].isin(category_filter_tasks) if category_filter_tasks else pd.Series([True] * len(df_tasks))

        mask_status_tasks = df_tasks['Status Date'].isin(status_filter_tasks) if status_filter_tasks else [True] * len(df_tasks)

        # Combine date, selection, and interaction filters using the logical AND (&) operator
        mask_combined_tasks = mask_assignedto_tasks & mask_category_tasks & mask_status_tasks #& mask_selection
        filtered_df_tasks = df_tasks.loc[mask_combined_tasks].copy()

        return filtered_df_tasks

    # Function to apply row highlighting based on "Status Date" column
    #def highlight_status_date(val):
        #if val == 'Upcoming':
            #return 'background-color: #89CFF0; color: white'
        #elif val == 'Outstanding':
            #return 'background-color: #FFDB58; color: black'  # Mustard Yellow
        #elif val == 'Completed':
            #return 'background-color: green; color: white'
        #else:
            #return ''

        # Streamlit app
    def main_tasks():

        def highlight_row_by_status_date(row):
        # Add your condition here to check the "Status Date" value
            if row['Status Date'] == 'Upcoming':
                return ['background-color: #BDD7EE; color: blue'] * len(row)
            elif row['Status Date'] == 'Completed':
                return ['background-color: #C6EFCE; color: green'] * len(row)
            elif row['Status Date'] == 'Outstanding':
                return ['background-color: #FFFFCC; color:  #CCCC00'] * len(row)
            else:
                return [''] * len(row)
        # Add bold title "Events"
        #st.markdown("<h2>Tasks</h2>", unsafe_allow_html=True)

        # Get unique selection values from the 'SELECTION' column
        #selection_options = df['Selection'].unique().tolist()
        assignedto_options_tasks = df_tasks['Assigned To'].unique().tolist()
        status_options_tasks = df_tasks['Status Date'].unique().tolist()
        category_options_tasks = df_tasks['Category'].unique().tolist()

        # Add Selectbox to choose the selection filter
        #selection = st.multiselect("Selection", selection_options)
        col1, col2 = st.columns(2)
        with col1:
            assignedto_tasks = st.multiselect("Assigned To", assignedto_options_tasks)
            status_filter_tasks = st.multiselect("Status Date", status_options_tasks)
        with col2:
            category_filter_tasks = st.multiselect("Category", category_options_tasks)
            st.write("<p style='font-size: smaller; font-style: italic;'>Priority funds includes funds 'Under Observation', 'Candidate', 'Candidate RC', 'Under DDR', 'Approval RC', 'Under Review', and 'Approved'.</p>", unsafe_allow_html=True)

        # Add "Reset Filters" button
        if st.button("Reset Filters (Tasks)"):
            #selection = None
            assignedto_tasks = None
            category_filter_tasks = None
            status_filter_tasks = None

        # Make a copy of the DataFrame before filtering
        filtered_df_tasks = df_sorted_tasks.copy()

        if assignedto_tasks or category_filter_tasks or status_filter_tasks:
            filtered_df_tasks = filter_dataframe_tasks(filtered_df_tasks, assignedto_tasks, category_filter_tasks, status_filter_tasks) #selection, interaction, category_filter)
            filtered_df_tasks_dropped = filtered_df_tasks.drop(columns=['Category', 'Status'])

            styled_df = filtered_df_tasks_dropped.style.apply(highlight_row_by_status_date, axis=1)

            st.write("Tasks:")
            st.dataframe(styled_df, hide_index=True)

        else:
            filtered_df_tasks_dropped = filtered_df_tasks.drop(columns=['Category', 'Status'])
            styled_df = filtered_df_tasks_dropped.style.apply(highlight_row_by_status_date, axis=1)

            st.write("Tasks:")
            st.dataframe(styled_df, hide_index=True)


    if __name__ == "__main__":
        main_tasks()

def show_selection_status():
    # Read the DataFrame from the Excel file
    df_selection = pd.read_excel("https://forteus-media-research.s3.eu-west-1.amazonaws.com/public/mma_reporting/output1.xlsx",engine='openpyxl')
    column_name_mapping_selection = {
        'ALIAS': 'Funds',
        'ISOSTATUS': 'Selection Status',
        'ISODATE': 'Selection Date',
        'VERSIONDATE': 'Other Date'
        # Add more column mappings as needed
    }

    # Use the rename() method to rename the columns
    df_selection.rename(columns=column_name_mapping_selection, inplace=True)

    # Convert the 'STARTDATE' column to a datetime object
    df_selection['Selection Date'] = pd.to_datetime(df_selection['Selection Date']).dt.date
    df_selection['Other Date'] = pd.to_datetime(df_selection['Other Date']).dt.date

    # Function to handle date selection
    def get_date(row):
        if not pd.isnull(row['Selection Date']):
            return row['Selection Date']
        else:
            return row['Other Date']

    # Apply the function to create a new column 'Date'
    df_selection['Date'] = df_selection.apply(get_date, axis=1)
    # Drop the 'Selection Date' and 'Other Date' columns, as we no longer need them
    df_selection.drop(columns=['Selection Date', 'Other Date'], inplace=True)
    # Filter rows with non-null 'Selection Status'
    df_selection = df_selection[df_selection['Selection Status'].notnull()]

    # Convert the 'Date' column to a datetime object
    df_selection['Date'] = pd.to_datetime(df_selection['Date']) #.dt.date
    
    def filter_dataframe_selection(df_selection, start_date_selection, end_date_selection): #selection,):
        
        start_date_selection = pd.to_datetime(start_date_selection) if start_date_selection else df_selection['Date'].min()
        end_date_selection = pd.to_datetime(end_date_selection) if end_date_selection else df_selection['Date'].max()

        # Combine date, selection, and interaction filters using the logical AND (&) operator
        mask_combined_selection = (df_selection['Date'] >= start_date_selection) & (df_selection['Date'] <= end_date_selection)
        # Create the 'Previous Status' column with all values set to None
        filtered_df_selection = df_selection.loc[mask_combined_selection].copy()
        # Identify rows where the status changed for each fund, including the previous status
        #filtered_df_selection['Previous Status'] = filtered_df_selection.groupby('Funds')['Selection Status'].shift(1)

        return filtered_df_selection

    # Streamlit web application
    def main_selection():

        def downgrade_check(previous_status, current_status):
            # Define the upgrade order and downgrade categories
            upgrade_order = ['Universe', 'Under Observation', 'Candidate', 'Candidate RC', 'Under DDR', 'Approval RC', 'Approved']
            downgrade_categories = {'Rejected', 'Fallen Angel', 'Under Review'}

            # Convert 'None' to 'Universe' for comparison
            if pd.isnull(previous_status):
                previous_status = 'Universe'

            # Check for downgrade based on downgrade categories
            return (previous_status not in downgrade_categories and current_status in downgrade_categories) or (upgrade_order.index(previous_status) > upgrade_order.index(current_status))

        def highlight_row_by_status_selection(row):
            # Get the status values for the row
            current_status = row['Selection Status']
            previous_status = row['Previous Status']

            # Check for 'NaN' (None) values in the 'Previous Status' column
            #if pd.isnull(previous_status):
                #previous_status = 'Universe'

            # Check for downgrade or upgrade based on the defined function
            if pd.notnull(previous_status) and previous_status == current_status:
                # Highlight as blue for same status
                return ['background-color: #BDD7EE; color: blue'] * len(row)
            elif downgrade_check(previous_status, current_status):
                # Highlight as red for downgrade
                return ['background-color: #FFC7CE; color: red'] * len(row)
            else:
                # Highlight as green for upgrade
                return ['background-color: #C6EFCE; color: green'] * len(row)

        start_date_selection = None
        end_date_selection = None

        col1, col2 = st.columns(2)
        with col1:
            timeframe_filter_selection = st.selectbox("Timeframe", ["1W", "2W", "3W", "1M", "1Q", "1Y","All"])
            st.write("<p style='font-size: smaller; font-style: italic;'>Funds highlighted in blue represent the re-validation of selection status (no change). Green highlights indicate promotion in selection status (upgrade) and red highlights indicate downgrade in selection status.</p>", unsafe_allow_html=True)

        # Add "Reset Filters" button
        if st.button("Reset Filters (Events)"):
            # Clear the date input and selectbox values
            start_date_selection = None
            end_date_selection = None
            timeframe_filter_selection = None

        filtered_df_selection = df_selection.copy()
        filtered_df_selection['Previous Status'] = filtered_df_selection.groupby('Funds')['Selection Status'].shift(1)

        if timeframe_filter_selection != "None":
            # Filter the DataFrame based on the selected timeframe
            today = pd.Timestamp.today().date()
            if timeframe_filter_selection == "1W":
                start_date_selection = today - pd.DateOffset(weeks=1)
                end_date_selection = today
            elif timeframe_filter_selection == "2W":
                start_date_selection = today - pd.DateOffset(weeks=2)
                end_date_selection = today
            elif timeframe_filter_selection == "3W":
                start_date_selection = today - pd.DateOffset(weeks=3)
                end_date_selection = today
            elif timeframe_filter_selection == "1M":
                start_date_selection = today - pd.DateOffset(months=1)
                end_date_selection = today
            elif timeframe_filter_selection == "1Q":
                start_date_selection = today - pd.DateOffset(months=3)
                end_date_selection = today
            elif timeframe_filter_selection == "1Y":
                start_date_selection = today - pd.DateOffset(years=1)
                end_date_selection = today
            elif timeframe_filter_selection == "All":
                start_date_selection = None 
                end_date_selection = None

            filtered_df_selection = filter_dataframe_selection(filtered_df_selection, start_date_selection, end_date_selection)
            # Identify rows where the status changed for each fund, including the previous status
            
        # Filter rows where the status changed or there was no previous status (NULL to non-NULL change)
        status_changed = filtered_df_selection[filtered_df_selection['Selection Status'] != filtered_df_selection['Previous Status']].copy()
        status_unchanged = filtered_df_selection[filtered_df_selection['Selection Status'] == filtered_df_selection['Previous Status']].copy()
        final_df_selection = pd.concat([status_changed, status_unchanged])
        final_df_selection.sort_values(by=['Funds', 'Date'], inplace=True)
        final_df_selection['Date'] = final_df_selection['Date'].dt.date
        final_df_selection = final_df_selection[["Funds", "Previous Status", "Selection Status", "Date"]]
        final_df_selection = final_df_selection.reset_index(drop=True)
        styled_final_df_selection = final_df_selection.style.apply(highlight_row_by_status_selection, axis=1)
        st.dataframe(styled_final_df_selection, hide_index=True)

        # Convert the 'Date' column to display only the date without the timestamp
        #status_changed['Date'] = status_changed['Date'].dt.date

        # Reorder the columns
        #status_changed = status_changed[["Funds", "Previous Status", "Selection Status", "Date"]]

        # Reset the index if desired
        #status_changed = status_changed.reset_index(drop=True)

        #styled_status_changed = status_changed.style.apply(highlight_row_by_status_selection, axis=1)
        #st.dataframe(styled_status_changed, hide_index=True)

        #st.subheader(f"Funds that changed status in the last {selected_timeframe}:")
        #st.dataframe(status_changed[["Funds", "Previous Status", "Selection Status", "Date"]].reset_index(drop=True), hide_index = True)

    if __name__ == "__main__":
        main_selection()

if __name__ == "__main__":
    main()





    # Function to filter data based on the selected timeframe
    #def filter_by_timeframe(data, selected_timeframe):
        #if selected_timeframe == "All":
            #start_date = None
            #start_date = datetime.datetime(1970, 1, 1)    # Select all data if no timeframe is selected
        #else:
            #if selected_timeframe == "Last 7 Days":
                #start_date = datetime.datetime.now() - timedelta(days=7)
            #elif selected_timeframe == "Last 1 Month":
                #start_date = datetime.datetime.now() - timedelta(days=30)
            #elif selected_timeframe == "Last 2 Months":
                #start_date = datetime.datetime.now() - timedelta(days=60)
            #elif selected_timeframe == "Last 3 Months":
                #start_date = datetime.datetime.now() - timedelta(days=90)
            #elif selected_timeframe == "Last 4 Months":
                #start_date = datetime.datetime.now() - timedelta(days=120)
            #elif selected_timeframe == "Last 5 Months":
                #start_date = datetime.datetime.now() - timedelta(days=150)

        #Convert the start_date to datetime.date
        #start_date = start_date.date()

        # Filter the data based on the selected timeframe
        #filtered_data = data[data["Date"] >= start_date].copy()

        #return filtered_data

    # Streamlit web application
    #def main_selection():
        #st.markdown("<h2>Selection Status Change</h2>", unsafe_allow_html=True)
        # Add a sidebar to allow the user to select the timeframe
        
        #selected_timeframe = st.selectbox("Select Timeframe", ["All"]) #"Last 7 Days", "Last 1 Month", "Last 2 Months", "Last 3 Months", "Last 4 Months", "Last 5 Months"])
        #timeframe_filter = st.selectbox("Timeframe", ["1W", "2W", "3W", "1M", "1Q", "1Y","All"])
        # Filter data based on the selected timeframe
        #filtered_data = filter_by_timeframe(df_selection, selected_timeframe)

        # Identify rows where the status changed for each fund, including the previous status
        #filtered_data['Previous Status'] = filtered_data.groupby('Funds')['Selection Status'].shift(1)

        # Filter rows where the status changed or there was no previous status (NULL to non-NULL change)
        #status_changed = filtered_data[filtered_data['Selection Status'] != filtered_data['Previous Status']].copy()
        # Convert the 'Date' column to display only the date without the timestamp
        #status_changed['Date'] = status_changed['Date'].dt.date
        #status_changed.loc[:, 'Date'] = status_changed['Date'].dt.date

        # Display the table of funds with changed selection status
        #st.subheader(f"Funds that changed status in the last {selected_timeframe}:")
        #st.dataframe(status_changed[["Funds", "Previous Status", "Selection Status", "Date"]].reset_index(drop=True), hide_index = True)

    #if __name__ == "__main__":
        #main_selection()






    