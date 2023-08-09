import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import leafmap.foliumap as leafmap



# cosmetic config
st.set_page_config(page_title='Dashboard', layout='wide')

st.title('Formula One - Data Pitstop - 1950 to 2023')

st.sidebar.title('About')
st.sidebar.info('F1 stats and maps for 35 race circuits')

# Add a dropdown to enable user to choose type of basemap  
base_map = st.selectbox('Select a basemap', ['OpenStreetMap', 'Stamen Terrain', 'Stamen Toner'])

# specify file path and filenames
data_url = 'https://raw.githubusercontent.com/Stephen137/formula_one/main/data/'
geojson_file = 'f1-circuits.geojson'
csv_file = 'f1_summary.csv'

@st.cache_data
# custom function to load in our spatial data
def read_gdf(url):
    gdf = gpd.read_file(url)
    return gdf

@st.cache_data
# custom function to load circuit statistics
def read_csv(url):
    df = pd.read_csv(url)
    return df

# Process start
data_load_state = st.text('Engines revving...')  

# Concatenate file names
geojson_url = data_url + geojson_file
f1_summary_url = data_url + csv_file

# create circuits GeoDataFrame
circuits_gdf = read_gdf(geojson_url)

# create non spatial F1 stats DataFrame
f1_stats_df = read_csv(f1_summary_url)

# Process complete
data_load_state.text('Lights out and away we go ... !')

# add a dropdown for circuit selection and filter dataset based on user choice
circuits = circuits_gdf.sort_values(by="Name").Name.unique()
# circuits = f1_stats_df.sort_values(by="circuit_name").circuit_name.unique()
circuit = st.sidebar.selectbox('Select a Circuit', circuits)

circuit_df = f1_stats_df[f1_stats_df['circuit_name'] == circuit]

# create a map
m = leafmap.Map(
    layers_control=True,
    draw_control=False,
    measure_control=False,
    fullscreen_control=False,
    tiles=base_map,
    hover_style={"fillOpacity": 0.7},
)

# add circuits layer
m.add_gdf(
    gdf=circuits_gdf,
    zoom_to_layer=False,
    layer_name='circuits',
    info_mode='on_hover',
    style={'color': '#7fcdbb', 'fillOpacity': 0.3, 'weight': 0.5},
    hover_style={"fillOpacity": 0.7},
    )

# filter for user circuit selection
selected_gdf = circuits_gdf[circuits_gdf['Name'] == circuit]

# add the user selected circuits layer
m.add_gdf(
    gdf=selected_gdf,
    layer_name='selected',
    zoom_to_layer=True,
    info_mode='on_hover',
    style={'color': 'red', 'fill': None, 'weight': 2},
    hover_style={"fillOpacity": 0.7},
 )

m_streamlit = m.to_streamlit(600, 600)

# Drop invalid values 
circuit_df = circuit_df[circuit_df['fastestLapTime'] != '\\N']

# filter for fastest lap
fastest_lap = circuit_df[["driver_name", "fastestLapTime", "race_date"]]
fastest_lap = fastest_lap.groupby(by=["fastestLapTime"]).min()

# fastest lap details based on user circuit selection
try:
    fastest_lap_time = fastest_lap.index[0]
except IndexError:
    pass

try:
    fastest_lap_driver = fastest_lap.driver_name[0]
except IndexError:
    pass

try:
    fastest_lap_date = fastest_lap.race_date[0]
except:
    pass

try: 
    st.text(f'The fastest lap time recorded at {circuit} is {fastest_lap_time}, clocked by {fastest_lap_driver} on {fastest_lap_date}.')
except NameError:
    pass

st.text(f'The bar chart below provides a breakdown of the champagne soaked podium finishers : ')

# add a stacked horizontal bar chart to show podium finishes for selected circuit
position = circuit_df[["driver_name", "positionOrder"]]
podium = position.query('positionOrder in [1,2,3]') 

podium_pivot = podium.pivot_table(index="driver_name", columns="positionOrder", aggfunc="size", fill_value=0)

st.bar_chart(podium_pivot)


st.text(f'The bar chart below shows the number of major incidents by year : ')

# add a stacked horizontal bar chart to show serious accidents for selected circuit
status = circuit_df[["driver_name", "year", "status"]]
accident = status.query('status in ["Accident","Collision", "Spun off", "Fatal accident","Collision damage","Damage"]')

accident_pivot = accident.pivot_table(index="year", columns="status", aggfunc="size", fill_value=0)

st.bar_chart(accident_pivot)

starters = len(circuit_df.grid)
finishers = len(circuit_df[circuit_df['statusId'] == 1])
try:
    finish_per_cent = round(finishers / starters * 100,2)
except ZeroDivisionError:
    pass

try:
    st.text(f'From a total of {starters} drivers who have started a race at {circuit}, {finish_per_cent} % completed the race.')
except ZeroDivisionError:
    pass
except NameError:
    pass