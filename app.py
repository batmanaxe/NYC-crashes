#Streamlit exercice


import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

"Représentation des accidents de la route à New york en fonction du lieu , du temps et de la gravité"



DATA_URL = ("C:/Users/batma_000/Desktop/cours python data/crash_nyc/Motor_Vehicle_Collisions_-_Crashes_course.csv")

st.title('Motor Vehicle Collisions in New York City.')
st.markdown("This application is a Streamlit dashboard that can be use \n to analyze vehicle collisions in NYC")

@st.cache(persist=True)
def load_data(rows):
    data = pd.read_csv(DATA_URL,nrows=rows,parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
    lowercase=lambda x : str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns={'crash_date_crash_time':'date/time'},inplace=True)
    return data

data = load_data(100000)
#data = data[0:100000]
original_data = data

st.header('Where are the most people injured in NYC?')
injured_people = st.slider("Number of persons injured in vehicle collisions",0, 19)

filtered_data =data[data['injured_persons']>=injured_people]
filtered_data_lat_lon=filtered_data[['latitude','longitude']].dropna(how="any")
#st.map(filtered_data_lat_lon)


st.header("How many collisions occur during a given tim of day")
hour = st.slider("Hour to look at",0,23)
data=data[data['date/time'].dt.hour==hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" %(hour,(hour+1) % 24))

midpoint = (np.average(data['latitude']),np.average(data['longitude']))


st.write(pdk.Deck(
	map_style="mapbox://styles/mapbox/light-v9",
	initial_view_state={"latitude":midpoint[0],
						"longitude":midpoint[1],
						"zoom":11,
						"pitch":50
						},
	layers=[
		pdk.Layer(
			"HexagonLayer",
			data = data[['date/time','latitude','longitude']],
			get_position=['longitude','latitude'],
			radius = 100,
			extruded=True,
			pickable=True,
			elevation_scale = 4,
			elevation_range = [0,1000],
			)
	]
))


st.subheader("Breakdown by minute between %i:00 and %i:00" %(hour,(hour+1) % 24))

filtered = data[
	(data['date/time'].dt.hour>= hour) & (data['date/time'].dt.hour <(hour+1))
]
hist=np.histogram(filtered['date/time'].dt.minute,bins=60,range=(0,60))[0]
chart_data =pd.DataFrame({'minute':range(60),'crashes':hist})
fig = px.bar(chart_data,x='minute',y='crashes', hover_data = ['minute','crashes'],height=400)
st.write(fig)


st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people',
	['Pedestrians','Cyclists','Motorists']
	)

if select == 'Pedestrians':
	st.write(original_data[original_data['injured_pedestrians']>=1][['on_street_name','injured_pedestrians']].sort_values(by =["injured_pedestrians"],ascending=False).dropna(how="any")[0:5])


elif select == 'Cyclists':
	st.write(original_data.query('injured_cyclists>=1')[['on_street_name','injured_cyclists']].sort_values(by =["injured_cyclists"],ascending=False).dropna(how="any")[0:5])


if select == 'Motorists':
	st.write(original_data.query('injured_motorists>=1')[['on_street_name','injured_motorists']].sort_values(by =["injured_motorists"],ascending=False).dropna(how="any")[0:5])


if st.checkbox ('Show Raw Data',False):
	st.subheader('Raw Data')
	st.write(data)