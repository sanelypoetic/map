import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import random
import time

@st.cache_data
def load_india_shapefile():

    gdf = gpd.read_file('India_State_Boundary.shp', engine='fiona')
    return gdf

def draw_map(gdf, correct=None):
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.boundary.plot(ax=ax, linewidth=1)
    
    if correct:
        gdf.loc[gdf['NAME_1'] == correct, 'geometry'].plot(ax=ax, color='white')
    
    plt.axis('off')
    st.pyplot(fig)

gdf = load_india_shapefile()

score = 0
start_time = time.time()

states_list = gdf['NAME_1'].tolist()
random.shuffle(states_list)

for state in states_list:
    st.write(f"Locate the state/union territory: **{state}**")
    
    draw_map(gdf)
    
    st.write("Click on the map where you think the state/UT is located:")
    click = st.pyplot_click()
    
    clicked_state = None
    for idx, row in gdf.iterrows():
        if row['geometry'].contains(gpd.points_from_xy([click.x], [click.y])[0]):
            clicked_state = row['NAME_1']
            break
    
    if clicked_state == state:
        st.write("Correct!")
        score += 1
        draw_map(gdf, correct=state)
    else:
        st.write(f"Wrong! You clicked on {clicked_state if clicked_state else 'an empty area'}")
        draw_map(gdf)

end_time = time.time()
total_time = end_time - start_time

st.write(f"Game over! Your score: {score}/{len(states_list)}")
st.write(f"Time taken: {total_time:.2f} seconds")
