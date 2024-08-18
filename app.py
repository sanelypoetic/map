import streamlit as st
import geopandas as gpd
import plotly.express as px
import random
import time

@st.cache_data
def load_india_shapefile():
    gdf = gpd.read_file('India_State_Boundary.shp')
    return gdf

def plot_map(gdf, correct_state=None):
    fig = px.choropleth(gdf,
                        geojson=gdf.geometry,
                        locations=gdf.index,
                        color=gdf['State_Name'].apply(lambda x: 'Correct' if x == correct_state else 'State/UT'),
                        hover_name=gdf['State_Name'],
                        hover_data={'State_Name': False})
    
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
    
    return fig

gdf = load_india_shapefile()

score = 0
start_time = time.time()

states_list = gdf['State_Name'].tolist()
random.shuffle(states_list)

for state in states_list:
    st.write(f"Locate the state/union territory: **{state}**")
    
    fig = plot_map(gdf)
    selected_state = None
    
    clicked = st.plotly_chart(fig, use_container_width=True)
    
    clicked_state = st.selectbox("Choose the state/UT you clicked on:", gdf['State_Name'].tolist())
    
    if clicked_state == state:
        st.write("Correct!")
        score += 1
        fig = plot_map(gdf, correct_state=state)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write(f"Wrong! You selected {clicked_state} instead of {state}.")
        fig = plot_map(gdf)
        st.plotly_chart(fig, use_container_width=True)

end_time = time.time()
total_time = end_time - start_time

st.write(f"Game over! Your score: {score}/{len(states_list)}")
st.write(f"Time taken: {total_time:.2f} seconds")
