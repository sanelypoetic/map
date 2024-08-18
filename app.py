import os
import json
import random
import time
import pandas as pd
import streamlit as st
from bokeh.plotting import figure, output_file, save
from bokeh.models import GeoJSONDataSource, TapTool, CustomJS
from bokeh.layouts import column, row
from bokeh.palettes import Viridis256

# File paths
GAME_HTML = "interactive_india_map.html"
SCORE_FILE = "scores.csv"

# Initialize or reset the game state
def reset_game():
    global state_list, random_state, start_time, score
    state_list = geo_df['NAME_1'].tolist()
    random_state = random.choice(state_list)
    start_time = time.time()
    score = 0

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

# Load the GeoJSON data
geojson_file = "Indian_States.geojson"
with open(geojson_file, "r") as file:
    geojson_data = json.load(file)

# Assign random colors to all states initially
for feature in geojson_data['features']:
    feature['properties']['Color'] = random.choice(Viridis256)

# Create GeoJSONDataSource
geo_source = GeoJSONDataSource(geojson=json.dumps(geojson_data))

# Define the Bokeh figure
p = figure(title="India Map", tools="tap", width=800, height=800, x_axis_location=None, y_axis_location=None)
p.grid.grid_line_color = None

# Create the patches representing the states
p.patches('xs', 'ys', fill_alpha=0.7, line_color='black', fill_color='Color', line_width=0.5, source=geo_source)

# Function to generate the Bokeh game and save it as an HTML file
def generate_bokeh_game():
    global start_time, random_state, state_list

    # Initialize the game state
    state_list = [feature['properties']['NAME_1'] for feature in geojson_data['features']]
    random_state = random.choice(state_list)
    start_time = time.time()

    # JavaScript code to update the game state when a state is clicked
    tap_callback = CustomJS(args=dict(source=geo_source), code="""
        const indices = source.selected.indices;
        if (indices.length > 0) {
            const state_name = source.data['NAME_1'][indices[0]];
            document.getElementById('selected_state').value = state_name;
        }
    """)

    tap_tool = TapTool(callback=tap_callback)
    p.add_tools(tap_tool)

    output_file(GAME_HTML)
    save(p)

# Streamlit UI
st.title("India States/UTs Identification Game")

# Run the Bokeh game generation every time the Streamlit app is run
generate_bokeh_game()

# Initialize or reset the game state
reset_game()

# Embed the Bokeh-generated HTML game as an iframe
if os.path.exists(GAME_HTML):
    with open(GAME_HTML, 'r') as f:
        st.components.v1.html(f.read(), height=900)
else:
    st.error("Game HTML not found. Please generate the Bokeh game first.")

# Hidden input to capture Bokeh callback value
selected_state = st.text_input(label='', value='', key='selected_state')

# Display feedback and score
if selected_state:
    if selected_state == random_state:
        st.success(f"Correct! You found {selected_state}.")
        state_list.remove(selected_state)
        score += 1
        if state_list:
            random_state = random.choice(state_list)
            st.subheader(f"Next state: **{random_state}**")
        else:
            elapsed_time = time.time() - start_time
            save_time("Player", elapsed_time)
            st.success(f"Congratulations! You've found all the states/UTs in {elapsed_time:.2f} seconds!")
            st.write(f"Final Score: {score}")
            st.session_state.start_time = None  # Reset for the next game
            st.stop()
    else:
        st.error(f"Wrong! That was {selected_state}. Try another one.")

# Display time elapsed
if "start_time" in st.session_state and st.session_state.start_time is not None:
    elapsed_time = time.time() - st.session_state.start_time
    st.write(f"Time Elapsed: {elapsed_time:.2f} seconds")
    st.write(f"Score: {score}")

# Show the leaderboard
st.subheader("Leaderboard")
st.text(show_leaderboard())

# Restart game option
if st.button("Restart Game"):
    reset_game()
    st.experimental_rerun()
