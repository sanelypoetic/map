import streamlit as st
import geopandas as gpd

@st.cache_data
def load_india_shapefile():
    gdf = gpd.read_file('India_State_Boundary.shp')
    return gdf

# Load the shapefile data
gdf = load_india_shapefile()

# Print the columns to identify the correct one
st.write("Columns in the GeoDataFrame:")
st.write(gdf.columns)

# import streamlit as st
# import geopandas as gpd
# import plotly.express as px
# import random
# import time

# @st.cache_data
# def load_india_shapefile():
#     gdf = gpd.read_file('India_State_Boundary.shp')
#     return gdf

# def plot_map(gdf, correct_state=None):
#     # Plot the map using Plotly
#     fig = px.choropleth(gdf,
#                         geojson=gdf.geometry,
#                         locations=gdf.index,
#                         color=gdf['NAME_1'].apply(lambda x: 'Correct' if x == correct_state else 'State/UT'),
#                         hover_name=gdf['NAME_1'],
#                         hover_data={'NAME_1': False})
    
#     fig.update_geos(fitbounds="locations", visible=False)
#     fig.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
    
#     return fig

# # Load the shapefile data
# gdf = load_india_shapefile()

# # Initialize game variables
# score = 0
# start_time = time.time()

# # Get a randomized list of states/UTs
# states_list = gdf['NAME_1'].tolist()
# random.shuffle(states_list)

# # Main game loop
# for state in states_list:
#     st.write(f"Locate the state/union territory: **{state}**")
    
#     fig = plot_map(gdf)
#     selected_state = None
    
#     # Show the map and get user click
#     clicked = st.plotly_chart(fig, use_container_width=True)
    
#     # Placeholder to simulate state selection
#     clicked_state = st.selectbox("Choose the state/UT you clicked on:", gdf['NAME_1'].tolist())
    
#     if clicked_state == state:
#         st.write("Correct!")
#         score += 1
#         fig = plot_map(gdf, correct_state=state)
#         st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.write(f"Wrong! You selected {clicked_state} instead of {state}.")
#         fig = plot_map(gdf)
#         st.plotly_chart(fig, use_container_width=True)

# end_time = time.time()
# total_time = end_time - start_time

# # Display the final score and time taken
# st.write(f"Game over! Your score: {score}/{len(states_list)}")
# st.write(f"Time taken: {total_time:.2f} seconds")
