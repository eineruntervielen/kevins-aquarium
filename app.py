"""Dodgy little DASHboard for my buddy Kev who likes to know a little bit
to much about his fishes...
"""
# Builtins
import os
import json
import sqlite3
import urllib.request
import datetime as dt

# Third-party libraries
import pandas as pd
import plotly.express as px

from dash import Dash, html, dcc
from dash.dependencies import Output, Input

# Environment variables
URL_API = os.environ.get('URL_API')
DB_PATH = os.environ.get('DB_PATH')

# Queries
INSERT_NEW_RECORD = "INSERT INTO RECORDS VALUES (?, ?, ?, ?, ?, ?, ?)"
SELECT_ALL_RECORDS = "SELECT * from RECORDS"


def insert_new_record():
    """Fetches a new record from Kev's api and stores the value in
    a dodgy little database
    """
    with sqlite3.connect(DB_PATH) as con:
        with urllib.request.urlopen(URL_API) as f:
            entry_value = json.loads(f.read().decode("utf-8"))
            index_key = dt.datetime.now()
            record = (index_key, *list(entry_value.values()))
        cur = con.cursor()
        cur.execute(INSERT_NEW_RECORD, record)


# Initializes a Dash application
app = Dash(
    name=__name__,
    title="Aquarium")

# Sets the layout
app.layout = html.Div(
    id="main-content",
    children=[
        dcc.Interval(
            id="interval-component",
            interval=3000,
            n_intervals=0,
        ),
        html.H1(id="main-header", children=["🐢 Kevins Aquarium 🐟"]),
        html.Div(
            id="plot-grid",
            children=[
                dcc.Graph(id="live-update-graph", animate=True),
                dcc.Graph(id="some-other-graph", animate=True),
            ],
        ),
    ],
)


@app.callback(
    Output("live-update-graph", "figure"),
    Input("interval-component", "n_intervals"))
def update_live_data(n):
    insert_new_record()
    con = sqlite3.connect(DB_PATH)
    temp_df = pd.read_sql_query(sql=SELECT_ALL_RECORDS, con=con, parse_dates=['DATETIME'], index_col=['DATETIME'])
    fig = px.scatter(
        data_frame=temp_df,
        x=temp_df.index,
        y=temp_df.columns
    )
    fig.update_traces(mode="lines+markers")
    fig.update_layout(
        xaxis=dict(
            range=(
                [
                    min(temp_df.index - dt.timedelta(seconds=3)),
                    max(temp_df.index + dt.timedelta(seconds=3)),
                ]
            )
        )
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
