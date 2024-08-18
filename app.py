import os
import json
import random
import time
import pandas as pd
import streamlit as st
from bokeh.plotting import figure, output_file, save
from bokeh.models import GeoJSONDataSource, HoverTool, TapTool, Div, CustomJS, TextInput, Button
from bokeh.layouts import column, row
from bokeh.io import curdoc
from bokeh.palettes import Viridis256

# File paths
GAME_HTML = "interactive_india_map.html"
SCORE_FILE = "scores.csv"

# Function to generate the Bokeh game and save it as an HTML file
def generate_bokeh_game():
    # Load the GeoJSON data from your local file
    with open("Indian_States.geojson", "r") as file:
        geojson_data = json.load(file)

    # Assign random colors to all states initially
    for feature in geojson_data['features']:
        feature['properties']['Color'] = random.choice(Viridis256)

    # Create GeoJSONDataSource
    geo_source = GeoJSONDataSource(geojson=json.dumps(geojson_data))

    # Define the Bokeh figure
    p = figure(title="India Map", tools="pan,wheel_zoom,reset", width=800, height=800, x_axis_location=None, y_axis_location=None)
    p.grid.grid_line_color = None

    # Create the patches representing the states
    p.patches('xs', 'ys', fill_alpha=0.7, line_color='black', fill_color='Color', line_width=0.5, source=geo_source)

    # Initialize the game state
    state_list = [feature['properties']['NAME_1'] for feature in geojson_data['features']]
    random_state = random.choice(state_list)
    start_time = time.time()

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
            leaderboard_text = "<h3>Leaderboard (Top 5 Fastest Times):</h3><ol>"
            for _, row in top5.iterrows():
                leaderboard_text += f"<li>{row['Name']}: {row['Time']} seconds</li>"
            leaderboard_text += "</ol>"
        else:
            leaderboard_text = "<h3>No scores yet!</h3>"
        
        return leaderboard_text

    # Div elements for displaying the timer, feedback, and leaderboard
    question_div = Div(text=f"<h2>Find the State/UT: <strong>{random_state}</strong></h2>", width=800)
    timer_div = Div(text=f"<h2>Time Elapsed: 0 seconds</h2>", width=200)
    feedback_div = Div(text="", width=400)
    leaderboard_div = Div(text=show_leaderboard(), width=400)
    name_display_div = Div(text="", width=300)

    # Text input for the user's name
    name_input = TextInput(value="", title="Enter your name:", width=300)

    # Button to start the game
    start_button = Button(label="Start Game", button_type="success", width=200)

    # Button to restart the game
    restart_button = Button(label="Restart Game", button_type="danger", width=200, disabled=True)

    # Callback to start the game
    def start_game():
        global start_time, random_state
        name = name_input.value.strip()
        if name:
            start_time = time.time()
            random_state = random.choice(state_list)
            question_div.text = f"<h2>Find the State/UT: <strong>{random_state}</strong></h2>"
            feedback_div.text = ""
            name_display_div.text = f"<h2>Hello, {name}!</h2>"
            name_input.visible = False
            start_button.visible = False
            restart_button.disabled = False
        else:
            feedback_div.text = "<p style='color:red;'>Please enter your name to start the game.</p>"

    start_button.on_click(start_game)

    # Callback to restart the game
    def restart_game():
        global state_list, random_state, start_time
        state_list = [feature['properties']['NAME_1'] for feature in geojson_data['features']]
        random_state = random.choice(state_list)
        start_time = time.time()
        question_div.text = f"<h2>Find the State/UT: <strong>{random_state}</strong></h2>"
        feedback_div.text = ""
        timer_div.text = f"<h2>Time Elapsed: 0 seconds</h2>"

    restart_button.on_click(restart_game)

    # JavaScript code to update the game state when a state is clicked
    tap_callback = CustomJS(args=dict(source=geo_source, div=question_div, timer_div=timer_div, feedback_div=feedback_div, leaderboard_div=leaderboard_div, state_list=state_list, start_time=start_time, name_input=name_input), code="""
        const selected_index = source.selected.indices[0];
        if (selected_index !== undefined) {
            const state_name = source.data['NAME_1'][selected_index];
            const target_state = div.text.match(/<strong>(.*?)<\/strong>/)[1];
            
            if (state_name === target_state) {
                state_list.splice(state_list.indexOf(state_name), 1);  // Remove correctly guessed state
                feedback_div.text = `<p style='color:green;'>Correct! You found ${state_name}.</p>`;
                if (state_list.length > 0) {
                    const new_state = state_list[Math.floor(Math.random() * state_list.length)];
                    div.text = `<h2>Find the State/UT: <strong>${new_state}</strong></h2>`;
                } else {
                    div.text = "<h2>Congratulations! You've found all the states/UTs!</h2>";
                    const elapsed_time = Math.floor(new Date().getTime() / 1000 - start_time);
                    save_time(name_input.value, elapsed_time);
                    leaderboard_div.text = show_leaderboard();
                    restart_button.disabled = True
                }
            } else {
                feedback_div.text = `<p style='color:red;'>Wrong! That was ${state_name}. Try another one.</p>`;
                if (state_list.length > 0) {
                    const new_state = state_list[Math.floor(Math.random() * state_list.length)];
                    div.text = `<h2>Find the State/UT: <strong>${new_state}</strong></h2>`;
                }
            }
            
            const elapsed_time = Math.floor(new Date().getTime() / 1000 - start_time);
            timer_div.text = `<h2>Time Elapsed: ${elapsed_time} seconds</h2>`;
        }
    """)

    # Add TapTool to figure
    tap_tool = TapTool(callback=tap_callback)
    p.add_tools(tap_tool)

    # Layout of the HTML page with the game controls and leaderboard
    game_layout = row(
        column(question_div, p),
        column(timer_div, feedback_div, leaderboard_div, restart_button)
    )

    layout = column(name_input, start_button, name_display_div, game_layout)

    # Output the plot to an HTML file
    output_file(GAME_HTML)
    save(p)  # Save the Bokeh plot as an HTML file

# Run the Bokeh game generation every time the Streamlit app is run
generate_bokeh_game()

# Streamlit UI
st.title("India States/UTs Identification Game")

# User name input
name = st.text_input("Enter your name to start the game:")

if name:
    st.subheader(f"Hello, {name}!")
    st.markdown("### Play the Game Below:")

    # Embed the Bokeh-generated HTML game as an iframe
    if os.path.exists(GAME_HTML):
        with open(GAME_HTML, 'r') as f:
            st.components.v1.html(f.read(), height=900)
    else:
        st.error("Game HTML not found. Please generate the Bokeh game first.")

    # Show the leaderboard
    st.subheader("Leaderboard")
    st.text(show_leaderboard())

    # Restart game option
    if st.button("Restart Game"):
        # Restart logic, perhaps you want to reload the game or simply refresh the page
        st.experimental_rerun()

    # Optionally, save the score manually
    if st.button("Save My Time"):
        # This would be where you capture the final time (you'll need to manage this logic externally)
        elapsed_time = st.number_input("Enter your time (in seconds):", min_value=0)
        if elapsed_time > 0:
            save_time(name, elapsed_time)
            st.success("Your time has been saved!")

            # Refresh leaderboard after saving time
            st.subheader("Leaderboard (Updated)")
            st.text(show_leaderboard())
