# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
#import dash_table_experiments as dt
import pandas as pd
import numpy as np
import glob
from datetime import datetime
import dash_table as dt

from plotly import graph_objs as go
import plotly.plotly as py
from plotly.graph_objs import *

from uszipcode import Zipcode
from uszipcode import SearchEngine
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="Movin\'OnUp") #"specify_your_app_name_here"

#data from US CENSUS
search = SearchEngine(simple_zipcode=True)

# def update_table(userforecast, minMSP, maxMSP):
#     now = datetime.today().strftime('%Y')
#     table = userforecast[['zipcode','trend','trend_lower','trend_upper']].loc[userforecast['ds']==now]
#     featuresWithinBudget = table[np.logical_and(table['trend'] >=minMSP,table['trend'] < maxMSP)]
#     return featuresWithinBudget

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__) #__name__, external_stylesheets=external_stylesheets
app.title = 'Movin\'OnUP!'

# API keys and datasets 
mapbox_access_token = 'pk.eyJ1IjoiZHluZGwiLCJhIjoiY2p4M2gyYm9wMDBzbDRhbmxzYWMya2tvZCJ9.xWu9JsGNMrFmk6yiydXlqw'

# loading data
path = '/Users/dmlee/Desktop/Insight_DS/data/'
#path = r'C:\DRO\DCL_rawdata_files' # use your path
all_files = glob.glob(path + 'ZILLOW/Z*_MSPAHforecast.csv')

li = []

# for zipcode in LA_zipcodes:
#     MSPfile = 'ZILLOW/Z'+zipcode+'_MSPAH.csv' #MSP
#     forecaster = 'ZILLOW/Z'+zipcode+'_MSPAH'+'forecast'+'.csv'

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    LA_zipcode = filename.split('_', 2)[1].split('Z')[2]
    df['zipcode'] = LA_zipcode
    lat_lon = search.by_zipcode(LA_zipcode).values()[7:9]
    df['Latitude'] = lat_lon[0]
    df['Longitude'] = lat_lon[1]
    li.append(df)

userforecast = pd.concat(li, axis=0, ignore_index=True)
map_data = userforecast

#set initial values for min and max
minMSP = 0
maxMSP = 2000000

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'light_text': '#D8D8D8'
}

# Boostrap CSS.
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
app.config['suppress_callback_exceptions']=True

#  Layouts
layout_table = dict(
    autosize=True,
    height=500,
    font=dict(color="#191A1A"),
    titlefont=dict(color="#191A1A", size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
)
layout_table['font-size'] = '12'
layout_table['margin-top'] = '20'

layout_map = dict(
    autosize=True,
    height=500,
    font=dict(color="#191A1A"),
    titlefont=dict(color="#191A1A", size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
    title='LA Home Location Desirables by Zipcode',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(
            lon=-118.2437,
            lat=34.0522
        ),
        zoom=10,
    )
)

# functions
def gen_map(map_data):
    # groupby returns a dictionary mapping the values of the first field
    # 'classification' onto a list of record dictionaries with that
    # classification value.
    return {
        "data": [{
                "type": "scattermapbox",
                "lat": list(map_data['Latitude']),
                "lon": list(map_data['Longitude']),
                "hoverinfo": "text",
                "hovertext": [["Name: {} <br>Type: {} <br>Provider: {}".format(i,j,k)]
                                for i,j,k in zip(map_data['Name'], map_data['Type'],map_data['Provider'])],
                "mode": "markers",
                "name": list(map_data['Name']),
                "marker": {
                    "size": 6,
                    "opacity": 0.7
                }
        }],
        "layout": layout_map
    }



#__________________________________
#__________________________________

app.layout = html.Div([

    #headers and initial user input
    #------------------------------
    #html.Div([
    #     html.Div([
    #         html.H1(children='Movin\'OnUP!',
    #                 style={
    #                     'textAlign': 'left',
    #                     'color': colors['text']},
    #                 className = "nine columns"
    #         ),

    #         html.Img(
    #             src="https://assets-global.website-files.com/575a31d2ce5d01dc7a20de45/575a31d2ce5d01dc7a20ded3_insight_logo.png",
    #             className='three columns',
    #             style={
    #                 'height': '14%',
    #                 'width': '14%',
    #                 'float': 'right',
    #                 'position': 'relative',
    #                 'margin-top': 20,
    #                 'margin-right': 20
    #             },
    #         ),

    #         html.Div(children='''A home pre-search optimization app''', 
    #                 style={
    #                     # 'height': '14%',
    #                     # 'width': '28',
    #                     # 'float': 'left',
    #                     # # 'position': 'fixed',
    #                     'margin-top': 15,
    #                     'margin-right': 15,
    #                     'margin-bottom': 15,
    #                     'textAlign': 'left',
    #                     'color': colors['text']
    #                 },
    #                 className = 'nine columns'
    #         ),
    #         ], className = "row"
    #     )
    # ]),

    #Left side
    #---------
	# html.Div([
 #        html.Div([
 #            dcc.Input(id='minMSPinput', type='number', value=minMSP,
 #                        placeholder='Enter min. price', 
 #                        style={ 
 #                        'height': '20%',
 #                        'width': '42%',
 #                        'float': 'left',
 #                        # 'position': 'fixed',
 #                        'textAlign': 'left'
 #                        #'color': colors['light_text']
 #            }),
 #            dcc.Input(id='maxMSPinput', type='number', value=maxMSP,
 #                        placeholder='Enter max. price', 
 #                        style={
 #                        'height': '20%',
 #                        'width': '42%',
 #                        'float': 'left',
 #                        # 'position': 'fixed',
 #                        'textAlign': 'left'
 #                        #'color': colors['light_text']
 #            }),          
 #            html.Div(id='userMSPoutput',
 #                        style={
 #                        'margin-top': 0,
 #                        'margin-right': 45,
 #                        'margin-bottom': 35,
 #                        'textAlign': 'left'
 #            }),
        
 #            html.Div(children='Min. Home Price   <--->   Max. Home Price',
 #                        style={
 #                        # 'float':'left',
 #                        'margin-top': 0,
 #                        'margin-right': 45,
 #                        'margin-bottom': 10,
 #                        'textAlign': 'left'
 #            }),             

 #            # dcc.Graph(
 #            #     id='interactive-choropeth-map',
 #            #     style={
 #            #         'margin-top': 0,
 #            #         'margin-right': 45,
 #            #         'margin-bottom': 0}
 #            #     ),

 #            #html.Div([
 #            dcc.Graph(id='map-graph',
 #                      animate=True,
 #                      style={'margin-top': '20'}
 #            #], className = "five columns"
 #            ),

 #            dcc.Slider(
 #                    id='Yearly_outlook',
 #                    min=0,
 #                    max=15,
 #                    value=1,
 #                    marks={
 #                        0: {'label': 'Now', 'style': {'color': '#77b0b1'}},
 #                        1: {'label': '1 Year'},
 #                        2: {'label': ''},
 #                        3: {'label': ''},
 #                        4: {'label': ''},                       
 #                        5: {'label': '5 Years'},
 #                        6: {'label': ''},
 #                        7: {'label': ''},
 #                        8: {'label': ''},
 #                        9: {'label': ''},
 #                        10: {'label': '10 Years'},
 #                        11: {'label': ''},
 #                        12: {'label': ''},
 #                        13: {'label': ''},
 #                        14: {'label': ''},
 #                        15: {'label': '15 Years', 'style': {'color': '#f50'}}
 #                    },
 #            ),
 #                html.Div(id='Yearly-outlook-output-container',style={'margin-top': 20}
 #                )
 #            ], className = "five columns"
 #        ),   

 #        html.Div([
 #            dcc.Slider(
 #                    id='Location_Value',
 #                    min=0,
 #                    max=4,
 #                    value=1,
 #                    marks={
 #                        0: {'label': 'Not Important', 'style': {'color': '#77b0b1'}},
 #                        1: {'label': 'Less Important'},
 #                        2: {'label': 'Important'},
 #                        3: {'label': 'Very Important'},
 #                        4: {'label': 'Extremely Important', 'style': {'color': '#f50'}}
 #                    }
 #            ),
 #            html.Div(id='Location-Value-output-container',style={'margin-top': 20}
 #            ),
 #            ],className = "three columns"
 #        )
 #    ]),

    # Map + table + Histogram
    #------------------------
    html.Div([
        # html.Div([
        #     dcc.Graph(id='map-graph',
        #               animate=True,
        #               style={'margin-top': '20'})
        #     ], className = "six columns"
        # ),
        html.Div([
            dt.DataTable(
                id='datatable',
                data=map_data.to_dict('records'),
                columns=map_data.columns,
                row_selectable='multi',
                filtering=True,
                sorting=True#,
                # pagination_mode='fe',
                # #selected_rows=[],
                # pagination_settings={
                #     "current_page": 0,
                #     "page_size": 10
                #     },
                )
            ],
            style = layout_table,
            className="six columns"
        ),
        # html.Div([
        #     dcc.Graph(
        #         id='bar-graph'
        #         )
        #     ], className= 'twelve columns'
        # ),
        html.Div([
            html.P('Developed by Duane M. Lee, Ph.D - ', style = {'display': 'inline'}
                ),
            html.A('duane.m.lee@gmail.com', href = 'mailto:duane.m.lee@gmail.com'
                )
            ], className = "twelve columns",
               style = {'fontSize': 18, 'padding-top': 20,'margin-top':20}
        )

        ], className = "row"
    ) 

],className = 'ten columns offset-by-one'
)
,,

#callback section 
#-------------------
# @app.callback(Output('userMSPoutput', 'children'),
#               [Input('minMSPinput', 'value'),
#                Input('maxMSPinput', 'value')])
# def selected_price_range(minMSP, maxMSP):
#     minmax = [minMSP,maxMSP]
#     return None #minMSP,maxMSP

# @app.callback(dash.dependencies.Output('Location-Value-output-container', 'children'),
#             [dash.dependencies.Input('Location_Value', 'value')])
# def location_value(Location_Value):
#     return None #Location_Value

# @app.callback(dash.dependencies.Output('Yearly-outlook-output-container', 'children'),
#             [dash.dependencies.Input('Yearly_outlook', 'value')])
# def show_yearly_outlook(Yearly_outlook):
#     return None #Yearly_outlook #u'{} Year Outlook'.format(Yearly_outlook)

# @app.callback(
#     Output('map-graph', 'figure'),
#     [Input('datatable', 'data'),
#      Input('datatable', 'selected_rows')])
# def map_selection(rows, selected_rows):
#     aux = pd.DataFrame(rows)
#     temp_df = aux.ix[selected_rows, :]
#     if len(selected_rows) == 0:
#         return gen_map(aux)
#     return gen_map(temp_df)

# @app.callback(
#     Output('datatable', 'data'),
#     [Input('minMSPinput', 'value'),
#      Input('maxMSPinput', 'value')])
# def update_selected_row_indices(minMSP, maxMSP):
#     map_aux = map_data.copy()
#     now = datetime.today().strftime('%Y')
#     table = map_aux[['zipcode','trend','trend_lower','trend_upper']].loc[map_aux['ds'] >= now]
#     #print(table)
#     featuresWithinBudget = table[np.logical_and(table['trend'] >= minMSP,table['trend'] < maxMSP)]
#     #print(featuresWithinBudget)
#     map_aux = featuresWithinBudget
#     # # Type filter
#     # map_aux = map_aux[map_aux['Type'].isin(type)]
#     # # Boroughs filter
#     # map_aux = map_aux[map_aux["Borough"].isin(borough)]

#     data = map_aux.to_dict('records')
#     print(data)
#     return data


if __name__ == "__main__":
    app.run_server(debug=True)