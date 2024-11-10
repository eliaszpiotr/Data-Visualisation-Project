from dash import Dash, dcc, html
import plotly.graph_objects as go
import pandas as pd
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

# Stworzenie oryginalnej mapy Kalifornii z punktami wypadków
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

# Dodanie punktów wypadków
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
    title_text='Mapa wypadków drogowych w Kalifornii',
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='mercator'
    ),
    margin={"r":0,"t":50,"l":0,"b":0}
)

# Lista cech i nazwy wierszy
features = ['Bump', 'Crossing', 'Give_Way', 'Junction', 'Railway', 'Stop', 'Traffic_Signal']
row_names = ['Bump', 'Crossing', 'Give Way', 'Junction', 'Railway', 'Stop', 'Traffic\nSignal']

# Funkcja do tworzenia mapy z punktami w zależności od cechy i poziomu Severity
def create_feature_map(feature, severity_level):
    filtered_data = data[(data[feature] == 1) & (data['Severity'] == severity_level)]
    fig = go.Figure(go.Choropleth(
        geojson=counties_geojson,
        locations=county_names,
        z=z_values,
        featureidkey="properties.name",
        colorscale=[[0, 'white'], [1, 'white']],
        showscale=False,
        marker_line_color='black',
        marker_line_width=0.5
    ))
    if not filtered_data.empty:
        fig.add_trace(go.Scattergeo(
            lon=filtered_data['Start_Lng'],
            lat=filtered_data['Start_Lat'],
            mode='markers',
            hoverinfo='skip',
            marker=dict(
                size=4,
                color='red',
                opacity=0.6
            )
        ))
    fig.update_geos(
        fitbounds="locations",
        visible=False
    )
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='mercator'
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig

# Tworzenie aplikacji Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Mapa wypadków drogowych w Kalifornii", style={'font-family': 'Arial, sans-serif', 'font-size': '32px'}),
    dcc.Graph(figure=fig_main, style={'margin-bottom': '20px'}),

    html.H2("Mapa cech wypadków według poziomu Severity", style={'font-family': 'Arial, sans-serif', 'font-size': '24px'}),

    # Siatka mapek z nazwami wierszy
    html.Div([
        html.Div([
            html.Div(row_names[i], style={'text-align': 'center', 'font-weight': 'bold', 'width': '80px',
                                          'font-family': 'Arial, sans-serif'}),
            html.Div(
                [dcc.Graph(figure=create_feature_map(features[i], severity),
                           style={'height': '140px', 'width': '180px'}) for severity in range(1, 5)],
                style={'display': 'grid', 'grid-template-columns': 'repeat(4, 1fr)', 'gap': '10px'}
            )
        ], style={'display': 'flex', 'align-items': 'center'})
        for i in range(len(features))
    ], style={'display': 'grid', 'grid-template-rows': f'repeat({len(features)}, auto)', 'gap': '10px'})
], style={'font-family': 'Arial, sans-serif'})

if __name__ == '__main__':
    app.run_server(port=8080)
