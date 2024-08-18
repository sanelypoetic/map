import streamlit as st
import json
from bokeh.models import GeoJSONDataSource, HoverTool, TapTool, LinearColorMapper
from bokeh.plotting import figure
from bokeh.palettes import Viridis6
from bokeh.io import show
import random

@st.cache_data
def load_geojson_data():
    with open("Indian_States.geojson", "r") as file:
        geojson_data = json.load(file)
    return geojson_data

def create_bokeh_plot(geo_source):
    p = figure(title="India Map", tools="pan,wheel_zoom,reset,tap", width=800, height=800)
    p.grid.grid_line_color = None
    p.patches('xs', 'ys', source=geo_source,
              fill_color={'field': 'Color', 'transform': LinearColorMapper(palette=Viridis6)},
              line_color='black', line_width=0.5, fill_alpha=0.7)

    hover = HoverTool()
    hover.tooltips = [("State", "@State_Name")]
    p.add_tools(hover)

    return p

def main():
    geojson_data = load_geojson_data()

    for feature in geojson_data['features']:
        feature['properties']['Color'] = 'blue'

    geo_source = GeoJSONDataSource(geojson=json.dumps(geojson_data))
    plot = create_bokeh_plot(geo_source)

    state_list = [feature['properties']['NAME_1'] for feature in geojson_data['features']]
    random_state = random.choice(state_list)
    st.write(f"Find the state/UT: **{random_state}**")

    def callback(event):
        selected_state = None
        for feature in geojson_data['features']:
            if feature['properties']['NAME_1'] == random_state:
                feature['properties']['Color'] = 'green'
                selected_state = feature['properties']['NAME_1']
            else:
                feature['properties']['Color'] = 'blue'

        geo_source.geojson = json.dumps(geojson_data)
        if selected_state == random_state:
            st.success(f"Correct! You found {random_state}.")
        else:
            st.error(f"Wrong! You clicked on {selected_state}.")

    plot.on_event(TapTool, callback)
    st.bokeh_chart(plot)

if __name__ == "__main__":
    main()
