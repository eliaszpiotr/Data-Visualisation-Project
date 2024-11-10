from dash import Dash, dcc, html
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import json
import requests

# Wczytanie danych z pliku CSV (dodaj odpowiednią ścieżkę)
data = pd.read_csv('Data/data.csv')

# Filtrowanie danych tylko dla Kalifornii
data = data[data['State'] == 'CA']  # Upewnij się, że kolumna 'State' istnieje i zawiera kody stanów

data = data.sample(frac=0.5, random_state=42)

# Załadowanie danych GeoJSON dla hrabstw Kalifornii
geojson_url = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/california-counties.geojson'
response = requests.get(geojson_url)
counties_geojson = response.json()

# Przygotowanie listy nazw hrabstw
county_names = [feature['properties']['name'] for feature in counties_geojson['features']]
z_values = [1]*len(county_names)  # Przypisanie stałej wartości do z

# Wczytanie pliku shapefile z drogami
roads_gdf = gpd.read_file('tl_2020_06_prisecroads/tl_2020_06_prisecroads.shp')

# Upewnienie się, że geometria jest w odpowiednim układzie współrzędnych (WGS84)
if roads_gdf.crs != 'EPSG:4326':
    roads_gdf = roads_gdf.to_crs('EPSG:4326')

# Konwersja geometrii dróg do GeoJSON
roads_json = json.loads(roads_gdf.to_json())

# Stworzenie oryginalnej mapy Kalifornii z drogami
fig_main = go.Figure(go.Choropleth(
    geojson=counties_geojson,
    locations=county_names,
    z=z_values,
    featureidkey="properties.name",
    colorscale=[[0, 'white'], [1, 'white']],  # Ustawienie białego koloru dla wszystkich hrabstw
    showscale=False,
    marker_line_color='black',  # Kolor linii obrysu hrabstw
    marker_line_width=0.5
))

# Dodanie dróg jako nowej warstwy
for feature in roads_json['features']:
    fig_main.add_trace(go.Scattergeo(
        lon=feature['geometry']['coordinates'][0],
        lat=feature['geometry']['coordinates'][1],
        mode='lines',
        line=dict(width=0.5, color='gray'),
        showlegend=False,
        hoverinfo='none'
    ))

# Dodanie punktów wypadków (opcjonalnie)
fig_main.add_trace(go.Scattergeo(
    lon=data['Start_Lng'],
    lat=data['Start_Lat'],
    mode='markers',
    hoverinfo='skip',
    marker=dict(
        size=4,
        color='red',
        opacity=0.6
    )
))

# Aktualizacja ustawień geograficznych mapy
fig_main.update_geos(
    fitbounds="locations",
    visible=False
)

# Aktualizacja układu figury
fig_main.update_layout(
    title_text='Mapa Kalifornii z drogami',
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='mercator'
    ),
    margin={"r":0,"t":50,"l":0,"b":0}
)

# Tworzenie aplikacji Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Mapa Kalifornii z drogami", style={'font-family': 'Arial, sans-serif', 'font-size': '32px'}),
    dcc.Graph(figure=fig_main, style={'margin-bottom': '20px'}),
])

if __name__ == '__main__':
    app.run_server(port=8080)
