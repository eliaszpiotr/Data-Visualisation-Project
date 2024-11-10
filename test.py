from dash import Dash, dcc, html
import plotly.graph_objects as go
import pandas as pd

# Wczytanie danych z pliku CSV (w razie potrzeby dodaj odpowiednią ścieżkę)
data = pd.read_csv('Data/data.csv')

data = data.sample(frac=0.05, random_state=42)

# # Konwersja kolumny 'Start_Time' na format daty z obsługą błędów
# data['Start_Time'] = pd.to_datetime(data['Start_Time'], errors='coerce')
# data_2023 = data[data['Start_Time'].dt.year == 2023]
# data_2023 = data_2023.dropna(subset=['Start_Time'])

# Stworzenie oryginalnej mapy USA z punktami
fig_main = go.Figure(go.Choropleth(
    locationmode='USA-states',
    z=[],
    colorscale=[[0, 'white'], [1, 'white']],
    autocolorscale=False,
    marker_line_color='black',
    showscale=False
))
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
fig_main.update_layout(
    title_text='USA Road Map with Accident Points',
    geo=dict(
        scope='usa',
        projection=go.layout.geo.Projection(type='albers usa'),
        showlakes=False,
        lakecolor='rgb(255, 255, 255)',
        showland=True,
        landcolor='lightgray',
        showcoastlines=False,
        showcountries=False,
        showocean=False
    ),
    margin=dict(l=0, r=0, t=50, b=0)
)

# Lista cech i nazwy wierszy
features = ['Bump', 'Crossing', 'Give_Way', 'Junction', 'Railway', 'Stop', 'Traffic_Signal']# Użycie cech jako nazw wierszy
row_names = ['Bump', 'Crossing', 'Give Way', 'Junction', 'Railway', 'Stop', 'Traffic\nSignal']

# Funkcja do tworzenia mapy z punktami w zależności od cechy i poziomu Severity
def create_feature_map(feature, severity_level):
    filtered_data = data[(data[feature] == 1) & (data['Severity'] == severity_level)]
    fig = go.Figure(go.Choropleth(
        locationmode='USA-states',
        z=[],
        colorscale=[[0, 'white'], [1, 'white']],
        autocolorscale=False,
        marker_line_color='black',
        showscale=False
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
    fig.update_layout(
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=False,
            lakecolor='rgb(255, 255, 255)',
            showland=True,
            landcolor='lightgray',
            showcoastlines=False,
            showcountries=False,
            showocean=False,
            center={'lat': 38, 'lon': -97},
            lonaxis=dict(range=[-125, -66]),
            lataxis=dict(range=[24, 50])
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig


# Layout aplikacji Dash
app = Dash(__name__)

# Layout aplikacji Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Original Map with Accident Points", style={'font-family': 'Arial, sans-serif', 'font-size': '32px'}),
    # Zmiana czcionki dla nagłówka
    dcc.Graph(figure=fig_main, style={'margin-bottom': '20px'}),  # Oryginalna mapa

    html.H2("Feature-based Map Grid by Severity", style={'font-family': 'Arial, sans-serif', 'font-size': '24px'}),
    # Zmiana czcionki dla podnagłówka

    # Siatka mapek z nazwami wierszy
    html.Div([
        html.Div([
            html.Div(row_names[i], style={'text-align': 'center', 'font-weight': 'bold', 'width': '80px',
                                          'font-family': 'Arial, sans-serif'}),  # Zmiana czcionki dla nazw wierszy
            html.Div(
                [dcc.Graph(figure=create_feature_map(features[i], severity),
                           style={'height': '140px', 'width': '180px'}) for severity in range(1, 5)],
                style={'display': 'grid', 'grid-template-columns': 'repeat(4, 1fr)', 'gap': '10px'}
            )
        ], style={'display': 'flex', 'align-items': 'center'})
        for i in range(7)
    ], style={'display': 'grid', 'grid-template-rows': 'repeat(7, auto)', 'gap': '10px'})
    # Dostosowanie odstępu między wierszami mapek
], style={'font-family': 'Arial, sans-serif'})  # Zmiana czcionki dla całej aplikacji

if __name__ == '__main__':
    app.run_server(port=8080)