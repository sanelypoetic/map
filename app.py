import json
import random
import time
import os
import pandas as pd
import streamlit as st
import geopandas as gpd
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, TapTool, CustomJS, ColumnDataSource
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.io import curdoc

# Temporary file to store scores
SCORE_FILE = "scores.csv"

# Load the GeoJSON data
geojson_file = "Indian_States.geojson"
geo_df = gpd.read_file(geojson_file)
geojson_str = geo_df.to_json()

# Function to save time to file
def save_time(name, time_elapsed):
    if os.path.exists(SCORE_FILE):
        df = pd.read_csv(SCORE_FILE)
    else:
        df = pd.DataFrame(columns=["Name", "Time"])

    new_entry = pd.DataFrame({"Name": [name], "Time": [time_elapsed]})
    df = pd.concat([df, new_entry], ignore_index=True)
    df.sort_values(by="Time", ascending=True, inplace=True)
    df.to_csv(SCORE_FILE, index=False)

# Function to display the leaderboard
def show_leaderboard():
    if os.path.exists(SCORE_FILE):
        df = pd.read_csv(SCORE_FILE)
        top5 = df.head(5)
        leaderboard_text = "Leaderboard (Top 5 Fastest Times):\n"
        for i, row in top5.iterrows():
            leaderboard_text += f"{i+1}. {row['Name']}: {row['Time']} seconds\n"
    else:
        leaderboard_text = "No scores yet!"
    
    return leaderboard_text

# Initialize or reset the game state
def reset_game():
    state_list = geo_df['NAME_1'].tolist()
    random_state = random.choice(state_list)
    start_time = time.time()
    return state_list, random_state, start_time

# Streamlit app begins here
st.title("India States/UTs Identification Game")

# User name input
if "name" not in st.session_state:
    st.session_state.name = None

if st.session_state.name is None:
    st.session_state.name = st.text_input("Enter your name to start the game:")

# Start game button
if st.session_state.name and "start_time" not in st.session_state:
    if st.button("Start Game"):
        st.session_state.state_list, st.session_state.random_state, st.session_state.start_time = reset_game()

# Display welcome message, game status, and leaderboard
if st.session_state.name:
    st.header(f"Hello, {st.session_state.name}!")
    
    if "start_time" in st.session_state:
        st.subheader(f"Find the State/UT: **{st.session_state.random_state}**")
        
        # Bokeh Plot
        geo_source = GeoJSONDataSource(geojson=geojson_str)
        p = figure(title="India Map", tools="tap", width=800, height=800)
        p.patches('xs', 'ys', fill_alpha=0.7, line_color='black', fill_color='Color', source=geo_source)
        
        tap_callback = CustomJS(args=dict(source=geo_source), code="""
            const indices = source.selected.indices;
            const selected_state = source.data['NAME_1'][indices[0]];
            document.getElementById('state_name').value = selected_state;
        """)
        
        tap_tool = TapTool(callback=tap_callback)
        p.add_tools(tap_tool)
        
        script, div = components(p)
        st.write(div, unsafe_allow_html=True)
        st.write(script, unsafe_allow_html=True)
        
        # Hidden input to capture Bokeh callback value
        state_name = st.text_input(label='', value='', key='state_name')
        
        if state_name:
            if state_name == st.session_state.random_state:
                st.session_state.state_list.remove(state_name)
                st.success(f"Correct! You found {state_name}.")
                if st.session_state.state_list:
                    st.session_state.random_state = random.choice(st.session_state.state_list)
                    st.subheader(f"Next state: **{st.session_state.random_state}**")
                else:
                    elapsed_time = time.time() - st.session_state.start_time
                    save_time(st.session_state.name, elapsed_time)
                    st.success(f"Congratulations! You've found all the states/UTs in {elapsed_time:.2f} seconds!")
                    del st.session_state.start_time  # End the game
            else:
                st.error(f"Wrong! That was {state_name}. Try again.")
                st.session_state.random_state = random.choice(st.session_state.state_list)

        st.subheader("Leaderboard")
        st.text(show_leaderboard())
        
        # Restart game button
        if st.button("Restart Game"):
            st.session_state.state_list, st.session_state.random_state, st.session_state.start_time = reset_game()
            st.experimental_rerun()
