from dash import Dash, dcc, html
import plotly.graph_objects as go

# Tworzenie figury z mapą Kalifornii bez danych hrabstw
fig = go.Figure(go.Choropleth(
    locationmode='USA-states',
    z=[],
    colorscale=[[0, 'white'], [1, 'white']],
    autocolorscale=False,
    marker_line_color='black',
    showscale=False
))

# Aktualizacja ustawień geograficznych mapy
fig.update_geos(
    projection_type='mercator',
    scope='usa',
    center={'lat': 37.5, 'lon': -119},  # Środek Kalifornii
    fitbounds="locations",  # Dopasowanie mapy do granic
    visible=False
)

# Aktualizacja układu figury
fig.update_layout(
    title_text='Mapa Kalifornii',
    geo=dict(
        showframe=False,
        showcoastlines=False,
        showland=True,
        landcolor='lightgray',
        showcountries=False,
        subunitcolor='black'
    ),
    margin={"r":0, "t":0, "l":0, "b":0}
)

# Tworzenie aplikacji Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Mapa Kalifornii"),
    dcc.Graph(figure=fig)
])

if __name__ == '__main__':
    app.run_server(port=8080)
