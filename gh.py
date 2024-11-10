from dash import Dash, dcc, html
import plotly.graph_objects as go
import geopandas as gpd

# Wczytanie danych z pliku GeoJSON
file_path = 'National_Highway_System.geojson'
gdf = gpd.read_file(file_path)

# Stworzenie pustej mapy Kalifornii
fig_main = go.Figure(go.Choropleth(
    locationmode='USA-states',
    z=[],
    colorscale=[[0, 'white'], [1, 'white']],
    autocolorscale=False,
    marker_line_color='black',
    showscale=False
))

# Dodanie dróg do mapy
for _, row in gdf.iterrows():
    if row['geometry'].geom_type == 'LineString':
        coords = [(lon, lat) for lon, lat, *_ in row['geometry'].coords]  # Ignorowanie trzeciej wartości
        lons, lats = zip(*coords)
        fig_main.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            mode='lines',
            line=dict(width=1, color='blue'),
            hoverinfo='none'
        ))
    elif row['geometry'].geom_type == 'MultiLineString':
        for line in row['geometry'].geoms:
            coords = [(lon, lat) for lon, lat, *_ in line.coords]  # Ignorowanie trzeciej wartości
            lons, lats = zip(*coords)
            fig_main.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                mode='lines',
                line=dict(width=1, color='blue'),
                hoverinfo='none'
            ))

# Ustawienia mapy dla Kalifornii
fig_main.update_layout(
    title_text='California Road Map with Highways',
    geo=dict(
        scope='usa',
        projection=go.layout.geo.Projection(type='mercator'),
        center={'lat': 37.5, 'lon': -119},  # Środek Kalifornii
        fitbounds="locations",
        showlakes=False,
        lakecolor='rgb(255, 255, 255)',
        showland=True,
        landcolor='lightgray',
        showcoastlines=False,
        showcountries=False,
        showocean=False,
        lataxis=dict(range=[32, 42]),  # Zakres szerokości geograficznej Kalifornii
        lonaxis=dict(range=[-125, -114])  # Zakres długości geograficznej Kalifornii
    ),
    margin=dict(l=0, r=0, t=50, b=0)
)

# Layout aplikacji Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("California Map with Roads", style={'font-family': 'Arial, sans-serif', 'font-size': '32px'}),
    dcc.Graph(figure=fig_main)
], style={'font-family': 'Arial, sans-serif'})

if __name__ == '__main__':
    app.run_server(port=8080)
