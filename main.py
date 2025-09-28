# app.py

import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. Dados
# ---------------------------------------------------------
df = pd.read_csv("combined_data.csv")
df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
for col in [
    'Chuva (mm)', 'Temp. Ins. (C)', 'Umi. Ins. (%)',
    'Pressao Ins. (hPa)', 'Pressao Max. (hPa)', 'Pressao Min. (hPa)',
    'Vel. Vento (m/s)', 'Dir. Vento (m/s)'
]:
    if col in df.columns:
        df[col] = (
            df[col].astype(str)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )


# ---------------------------------------------------------
# 2. Gráficos auxiliares
# ---------------------------------------------------------
def create_temp_heatmap():
    df_h = df.copy()
    df_h['Dia'], df_h['Mes'] = df_h['Data'].dt.day, df_h['Data'].dt.month
    pivot = df_h.pivot_table('Temp. Ins. (C)', 'Dia', 'Mes', 'mean')
    z, txt = pivot.values, pivot.round(1).astype(str)
    mask = np.isnan(z)
    z[mask], txt[mask] = None, ''
    fig = go.Figure(go.Heatmap(
        z=z, x=[f"Mês {m}" for m in pivot.columns], y=pivot.index,
        colorscale='Viridis', text=txt, texttemplate='%{text}',
        hoverongaps=False, showscale=True
    ))
    fig.update_layout(margin=dict(t=40, l=40, b=40, r=40),
                      paper_bgcolor='white', plot_bgcolor='white')
    return fig


def create_wind_pattern():
    wd = df.dropna(subset=['Vel. Vento (m/s)', 'Dir. Vento (m/s)'])
    if wd.empty:
        return go.Figure().update_layout(title="No wind data")
    dirs, sp = wd['Dir. Vento (m/s)'], wd['Vel. Vento (m/s)']
    rad = np.radians(90 - dirs)
    x, y = sp * np.cos(rad), sp * np.sin(rad)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers',
                             marker=dict(size=4, color='#567ace', opacity=0.6), showlegend=False))
    maxr = max(sp.max(), 5) * 1.1
    # círculos
    for r in [2.5, 3.5, 4.5]:
        th = np.linspace(0, 2 * np.pi, 100)
        fig.add_trace(go.Scatter(x=r * np.cos(th), y=r * np.sin(th),
                                 mode='lines', line=dict(dash='dot', color='#ccc'), showlegend=False))
    card = [('N', 0), ('E', 90), ('S', 180), ('W', 270)]
    for lab, ang in card:
        a = np.radians(90 - ang)
        xe, ye = maxr * np.cos(a), maxr * np.sin(a)
        fig.add_annotation(x=xe, y=ye, text=lab, showarrow=False, font=dict(size=12))
    fig.update_layout(
        margin=dict(t=40, l=40, b=40, r=40),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        paper_bgcolor='white', plot_bgcolor='white'
    )
    return fig


# ---------------------------------------------------------
# 3. Layout e estilo
# ---------------------------------------------------------
app = Dash(__name__)
app.title = "Weather Station de João Pessoa"

# Cores
DARK_BLUE = "#0f3d6e"
MEDIUM_BLUE = "#567ace"
LIGHT_GRAY = "#f7f9fc"

app.layout = html.Div(style={'backgroundColor': LIGHT_GRAY, 'fontFamily': 'Arial'}, children=[

    # Header
    html.Div(style={'backgroundColor': DARK_BLUE, 'padding': '20px 40px', 'display': 'flex',
                    'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
        html.Div([
            html.H1("Dashboard - Weather Station de João Pessoa", style={'color': 'white', 'margin': 0}),
            html.P("Análise metereológica de João Pessoa no ano de 2024",
                   style={'color': 'white', 'margin': 0, 'fontSize': '14px'})
        ]),
        html.Img(src="weather.png", style={'height': '40px'})
    ]),

    # Badges
    html.Div(style={'display': 'flex', 'gap': '10px', 'padding': '10px 40px'}, children=[
        html.Div("📅 Data Atualizada: 2025/09/28",
                 style={'backgroundColor': 'white', 'padding': '5px 10px', 'borderRadius': '4px',
                        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}),
        html.Div("📂 Data Source: Instituto Nacional de Metereologia do Brasil",
                 style={'backgroundColor': 'white', 'padding': '5px 10px', 'borderRadius': '4px',
                        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'})
    ]),

    # Cards métricas
    html.Div(
        style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap', 'padding': '20px 40px'},
        children=[
            # Total Records
            html.Div(
                style={
                    'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '4px',
                    'flex': '1', 'display': 'flex', 'justifyContent': 'space-between',
                    'alignItems': 'center', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                },
                children=[
                    html.Div([
                        html.H4("Total Records", style={'margin': '0 0 5px'}),
                        html.H2(f"{len(df)}", style={'margin': 0})
                    ]),
                    html.Div(
                        style={'backgroundColor': MEDIUM_BLUE, 'width': '6px',
                               'height': '60%', 'borderRadius': '3px'}
                    )
                ]
            ),

            # Temperatura Média
            html.Div(
                style={
                    'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '4px',
                    'flex': '1', 'display': 'flex', 'justifyContent': 'space-between',
                    'alignItems': 'center', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                },
                children=[
                    html.Div([
                        html.H4("Avg Temperature (°C)", style={'margin': '0 0 5px'}),
                        html.H2(f"{df['Temp. Ins. (C)'].mean():.2f}", style={'margin': 0})
                    ]),
                    html.Div(
                        style={'backgroundColor': MEDIUM_BLUE, 'width': '6px',
                               'height': '60%', 'borderRadius': '3px'}
                    )
                ]
            ),

            # Temperatura Máxima
            html.Div(
                style={
                    'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '4px',
                    'flex': '1', 'display': 'flex', 'justifyContent': 'space-between',
                    'alignItems': 'center', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                },
                children=[
                    html.Div([
                        html.H4("Max Temperature (°C)", style={'margin': '0 0 5px'}),
                        html.H2(f"{df['Temp. Ins. (C)'].max():.2f}", style={'margin': 0})
                    ]),
                    html.Div(
                        style={'backgroundColor': MEDIUM_BLUE, 'width': '6px',
                               'height': '60%', 'borderRadius': '3px'}
                    )
                ]
            ),

            # Umidade Média
            html.Div(
                style={
                    'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '4px',
                    'flex': '1', 'display': 'flex', 'justifyContent': 'space-between',
                    'alignItems': 'center', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                },
                children=[
                    html.Div([
                        html.H4("Avg Humidity (%)", style={'margin': '0 0 5px'}),
                        html.H2(f"{df['Umi. Ins. (%)'].mean():.2f}", style={'margin': 0})
                    ]),
                    html.Div(
                        style={'backgroundColor': MEDIUM_BLUE, 'width': '6px',
                               'height': '60%', 'borderRadius': '3px'}
                    )
                ]
            ),

            # Chuva Total
            html.Div(
                style={
                    'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '4px',
                    'flex': '1', 'display': 'flex', 'justifyContent': 'space-between',
                    'alignItems': 'center', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                },
                children=[
                    html.Div([
                        html.H4("Total Rainfall (mm)", style={'margin': '0 0 5px'}),
                        html.H2(f"{df['Chuva (mm)'].sum():.2f}", style={'margin': 0})
                    ]),
                    html.Div(
                        style={'backgroundColor': MEDIUM_BLUE, 'width': '6px',
                               'height': '60%', 'borderRadius': '3px'}
                    )
                ]
            ),
        ]
    ),

    # Controles
    html.Div(
        style={'display': 'flex', 'gap': '10px', 'alignItems': 'center', 'padding': '0 40px'},
        children=[

            html.Label("Temperature Type:", style={'color': DARK_BLUE}),
            dcc.Dropdown(
                id='temp-type',
                options=[
                    {'label': 'Instant Temp', 'value': 'Temp. Ins. (C)'},
                    {'label': 'Maximum Temp', 'value': 'Temp. Max. (C)'},
                    {'label': 'Minimum Temp', 'value': 'Temp. Min. (C)'}
                ],
                value='Temp. Ins. (C)',  # valor padrão
                clearable=False,
                style={'width': '150px'}
            ),

            html.Label("Time Aggregation:", style={'color': DARK_BLUE}),
            dcc.Dropdown(
                id='agg-choice',
                options=[
                    {'label': 'Hourly', 'value': 'H'},
                    {'label': 'Daily', 'value': 'D'}
                ],
                value='D',
                clearable=False,
                style={'width': '150px'}
            )
        ]
    ),

    # Gráficos
    html.Div(style={'padding': '20px 40px'}, children=[

        # Linha 1: Chuva e Temperatura
        html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
            html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '4px',
                            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}, children=[
                dcc.Graph(id='grafico-chuva')
            ]),
            html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '4px',
                            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}, children=[
                dcc.Graph(id='grafico-temp')
            ]),
        ]),

        # Linha 2: Umidade e Correlação
        html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
            html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '4px',
                            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}, children=[
                dcc.Graph(id='grafico-umid')
            ]),
            html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '4px',
                            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}, children=[
                dcc.Graph(id='grafico-correlacao')
            ]),
        ]),

        # Linha 3: Heatmap e Wind Pattern
        html.Div(style={'display': 'flex', 'gap': '20px'}, children=[
            html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '4px',
                            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}, children=[
                dcc.Graph(id='heatmap-temp')
            ]),
            html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '4px',
                            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}, children=[
                dcc.Graph(id='wind-pattern')
            ]),
        ]),
    ])

])


# ---------------------------------------------------------
# 4. Callbacks
# ---------------------------------------------------------
@app.callback(
    [
        Output('grafico-chuva', 'figure'),
        Output('grafico-temp', 'figure'),
        Output('grafico-umid', 'figure'),
        Output('grafico-correlacao', 'figure'),
        Output('heatmap-temp', 'figure'),
        Output('wind-pattern', 'figure')
    ],
    Input('agg-choice', 'value'),
    Input('temp-type', 'value')
)
def update_all(agg, temp_col):
    # 1. Fallback para temp_col
    if temp_col is None:
        temp_col = 'Temp. Ins. (C)'

    # 2. Agregação temporal
    if agg == "H":
        label, grp = "Hora", df.resample("H", on="Data")
    elif agg == "M":
        label, grp = "Mês", df.resample("M", on="Data")
    else:
        label, grp = "Dia", df.resample("D", on="Data")

    # 3. DataFrames agregados
    chuva = grp["Chuva (mm)"].sum().reset_index().rename(columns={"Data": "Periodo"})
    temp = grp[temp_col].mean().reset_index().rename(columns={"Data": "Periodo"})
    umid = grp["Umi. Ins. (%)"].mean().reset_index().rename(columns={"Data": "Periodo"})

    # 4. fig_chuva
    fig_chuva = go.Figure()
    fig_chuva.add_trace(go.Scatter(
        x=chuva["Periodo"], y=chuva["Chuva (mm)"],
        mode='lines',
        line=dict(color='#1e88e5', width=1),
        fill='tonexty',
        fillcolor='rgba(30,136,229,0.3)',
    ))
    fig_chuva.update_layout(
        title=f"Chuva (mm) por {label}",
        plot_bgcolor="#fafafa",
        paper_bgcolor="#fafafa",
        xaxis=dict(gridcolor="#e0f2ff"),
        yaxis=dict(gridcolor="#e0f2ff"),
        height=350
    )

    # 5. fig_temp
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=temp["Periodo"], y=temp[temp_col],
        mode='lines',
        line=dict(color='#1e88e5', width=2)
    ))
    fig_temp.update_layout(
        title=f"Temperatura ({temp_col}) por {label}",
        plot_bgcolor="#fafafa",
        paper_bgcolor="#fafafa",
        xaxis=dict(gridcolor="#e0f2ff"),
        yaxis=dict(gridcolor="#e0f2ff"),
        height=350
    )

    # 6. fig_umid
    fig_umid = go.Figure()
    fig_umid.add_trace(go.Scatter(
        x=umid["Periodo"], y=umid["Umi. Ins. (%)"],
        mode='lines',
        line=dict(color='#1e88e5', width=2)
    ))
    fig_umid.update_layout(
        title=f"Umidade Média (%) por {label}",
        plot_bgcolor="#fafafa",
        paper_bgcolor="#fafafa",
        xaxis=dict(gridcolor="#e0f2ff"),
        yaxis=dict(gridcolor="#e0f2ff"),
        height=350
    )

    # 7. fig_corr
    fig_corr = px.scatter(
        df, x="Pressao Ins. (hPa)", y="Umi. Ins. (%)",
        color=temp_col,
        color_continuous_scale="Blues",
        title="Correlação: Umidade x Pressão"
    )
    fig_corr.update_layout(
        plot_bgcolor="#fafafa",
        paper_bgcolor="#fafafa",
        height=350
    )

    # 8. Heatmap e Wind Pattern
    fig_heatmap = create_temp_heatmap()
    fig_wind = create_wind_pattern()

    return fig_chuva, fig_temp, fig_umid, fig_corr, fig_heatmap, fig_wind

# ---------------------------------------------------------
# 5. Run
# ---------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
