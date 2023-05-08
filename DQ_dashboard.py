from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import json
from pandas import json_normalize
pd.set_option('display.max_colwidth', None)
from sqlalchemy import create_engine
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

def read_table(tablename):
    conn_string = 'postgresql+psycopg2://root:root@51.141.228.69/Data_Migration_Pipeline'
    db = create_engine(conn_string)
    conn = db.connect()
    source_table = pd.read_sql_table(tablename, conn)
    return source_table
source_table=read_table('Accounts_DQ_check_result')
# print(source_table)
# exit(0)
# dq_checks=pd.DataFrame()
# for file in json_data:
#     # dict_json[file]=json_data[file]
#     # pd.concat([dq_checks, json_normalize(json_data[file])]) 
#      dq_checks=pd.concat([dq_checks, json_normalize(json_data[file])])
# # Create the Dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__,external_stylesheets=external_stylesheets)

# Set up the app layout
file_dropdown = dcc.Dropdown(source_table['rule_name'].unique(),source_table['rule_name'][0])
# file_dropdown2 = dcc.Dropdown(options=dq_checks['source'].unique())  # value='New York'

app.layout = html.Div(children=[
    html.Div([
        html.H1(children='Data Quality Checks Report')
    ],className='row'),
    html.Div([html.Div(children=[
        html.Div([
            dcc.Graph(id='checks-graph3',config={
            'displayModeBar': False
            })
            ])
        ],className='three columns')
    ],className='row'),
    
    html.Div([html.H2('Filter by Rule Name')],className='row'),
    html.Div(children=[
        html.Div([html.H1(children='')],className='four columns'),
        html.Div([file_dropdown],className='four columns')
        ],className='row'),
    html.Div(children=[
        html.Div([
            dcc.Graph(id='checks-graph',config={
            'displayModeBar': False
            })],
            className="four columns"),
        html.Div([
            dcc.Graph(id='checks-graph2',config={
            'displayModeBar': False
            })],
            className="four columns"),
        html.Div([
            dcc.Graph(id='checks-graph4',config={
            'displayModeBar': False
            })],
            className='four columns')
    ],className='row'),
    ])

source_table['count'] = 1
source_table['validation_date'] = pd.to_datetime(source_table.validation_time).dt.date
source_table['validation_datetime'] = pd.to_datetime(source_table.validation_time).dt.time


@app.callback(
    Output(component_id='checks-graph', component_property='figure'),
    Input(component_id=file_dropdown, component_property='value')
)
def update_graph1(selected_check):
    
    filtered_table = source_table[source_table['rule_name'] == selected_check]
    grouped_table = filtered_table.groupby(['validation_date','validation_datetime','rule_name']).count().reset_index()

    fig = px.scatter(grouped_table,x='validation_date',y='validation_datetime',size='count',color='rule_name')
    fig.update_layout(title='Rule applied on date and time')
                    
    return fig

@app.callback(
    Output(component_id='checks-graph2', component_property='figure'),
    Input(component_id=file_dropdown, component_property='value')
)
def update_graph2(selected_check):
    
    filtered_checks = source_table[source_table['rule_name'] == selected_check]
    filtered_checks['count']=0
    filtered_checks=filtered_checks.groupby(['success']).count().reset_index()

    fig = px.pie(filtered_checks,
                    values='count',
                    names='success',
                    hover_data='success',
                    title=f'Success/failure % for rule applied: {selected_check}')
    
    return fig

# print(list(source_table.groupby('rule_name').count()['row_count']))#.extend(list(source_table.count())))
# print(list(source_table.groupby('rule_name').count()['row_count'])+[source_table.groupby('rule_name').count()['row_count'].sum()])
# print(source_table.groupby('rule_name').count()['row_count'].sum())


@app.callback(
    Output(component_id='checks-graph3', component_property='figure'),
    Input(component_id=file_dropdown, component_property='value')
)
def update_graph3(selected_check):
    fig = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        measure = len(source_table['rule_name'].unique())*["relative"]+["total"],
        x = list(source_table['rule_name'].unique())+['Total'],
        textposition='auto',
        text = list(source_table.groupby('rule_name').count()['row_count'])+[source_table.groupby('rule_name').count()['row_count'].sum()],
        y = list(source_table.groupby('rule_name').count()['row_count'])+[source_table.groupby('rule_name').count()['row_count'].sum()],
        connector = {"line":{"color":"rgb(63, 63, 63)"}}
        ))
    fig.update_layout(
        title = "Break-up of rules applied on table"
    )
                    
    return fig

@app.callback(
    Output(component_id='checks-graph4', component_property='figure'),
    Input(component_id=file_dropdown, component_property='value')
)
def update_graph4(selected_check):
    filtered_checks = source_table[source_table['rule_name'] == selected_check]
    filtered_checks['count']=0
    filtered_checks=filtered_checks.groupby(['success', 'validation_date']).count().reset_index()
    
    fig = px.line(filtered_checks,
    x='validation_date',
    y='count',
    color='success',
    title=f'Data Quality Checks for {selected_check}')
    return fig
# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)