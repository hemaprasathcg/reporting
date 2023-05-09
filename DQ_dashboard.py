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

# # Create the Dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__,external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

# Set up the app layout
file_dropdown = dcc.Dropdown(source_table['rule_name'].unique(),source_table['rule_name'][0])

app.layout = html.Div([
    html.H1(children='Data Quality Checks Report'),
    dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
        dcc.Tab(label='Summary', value='tab-1-example-graph'),
        dcc.Tab(label='Rule-Based', value='tab-2-example-graph'),
    ]),
    html.Div(id='tabs-content-example-graph')
])

fig = px.histogram(source_table,x='rule_name',color='rule_name',text_auto=True)
fig.update_layout(
    title = "No. of Rules applied on dataframe"
)

tab_one = html.Div([
            dcc.Graph(figure=fig,config={
            'displayModeBar': False
            })
            ],className='four columns')
        


tab_two = html.Div([html.H2('Filter by Rule Name')],className='row'),html.Div(children=[
        html.Div([html.H1(children='')],className='four columns'),
        html.Div([file_dropdown],className='four columns')
        ],className='row'),html.Div(children=[
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
    ],className='row')


@app.callback(Output('tabs-content-example-graph', 'children'),
              Input('tabs-example-graph', 'value'))
def render_content(tab):
    if tab == 'tab-1-example-graph':
        return tab_one
    elif tab == 'tab-2-example-graph':
        return tab_two

source_table['count'] = 1
source_table['validation_date'] = pd.to_datetime(source_table.validation_time).dt.date
source_table['validation_datetime'] = pd.to_datetime(source_table.validation_time).dt.time
print(source_table['validation_time'].sort_values())

@app.callback(
    Output(component_id='checks-graph', component_property='figure'),
    Input(component_id=file_dropdown, component_property='value')
)
def update_graph1(selected_check):
    
    filtered_table = source_table[source_table['rule_name'] == selected_check]
    grouped_table = filtered_table.groupby(['validation_date','rule_name']).count().reset_index()

    fig = px.scatter(grouped_table,x='validation_date',y='count',color='rule_name')
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