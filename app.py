# -*- coding: utf-8 -*-
import sys
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
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

app = dash.Dash(__name__) #__name__, external_stylesheets=external_stylesheets
app.title = 'Movin\'OnUP!'

# API keys and datasets 
mapbox_access_token = 'pk.eyJ1IjoiZHluZGwiLCJhIjoiY2p4M2gyYm9wMDBzbDRhbmxzYWMya2tvZCJ9.xWu9JsGNMrFmk6yiydXlqw'

print('so far so good!')

# loading data
path = 'https://github.com/dyndl/Movin-On-UP/MOU_data/'
#path = r'C:\DRO\DCL_rawdata_files' # use your path
all_files = glob.glob(path + 'ZILLOW2/Z*_MSPAHforecast.csv')

print(path + 'ZILLOW2/Z*_MSPAHforecast.csv')
print('-----------------------------------------')
print(all_files)

li = []

LA_zipcodes = ['90014','90013','90017','90006','90029','90071','90037','90008',\
               '90018','90023','90031','90822','90731','90028','90019','90025',\
               '90049','91406','91405','91335','90065','90062','90003','90043',\
               '90291','90304','91605','90020','91356','91364','91303','90057',\
               '90015','90007','90033','90035','90012','91607','90004','91604',\
               '90059','90010','90064','90011','91331','90061','90032','90044',\
               '90502','90063','90744','90292','91340','91402','91324','90021',\
               '90079','90026','90016','90710','90248','90732','90717','90046',\
               '90038','90069','90048','90036','90211','90404','90024','90067',\
               '90077','90034','90402','91423','90210','91403','91411','91401',\
               '91436','91316','91343','91325','91201','90041','90042','91205',\
               '90039','91204','90305','90047','90001','90058','90066','90293',\
               '90094','90056','90045','90405','90230','91602','91608','91601',\
               '91606','91214','91352','91040','91504','91342','91306','91326',\
               '91344','91304','90002','90247','91345','90005','91367','90027',\
               '91030','90501','90068','90272','90232','91505','91206','91311',\
               '90301','90212','91307','90804','90740','90403','91301','90814','90302']

LA_other_zipcodes = ['90009','90030','90050','90051','90052','90053','90054',\
'90055','90060','90070','90072','90074','90075','90076','90078','90079','90080',\
'90081','90082','90083','90084','90085','90086','90087','90088','90090','90091',\
'90093','90095','90096','90099','90134','90189'] 

count = 0
for filename in all_files:
    LA_zipcode = filename.split('_', 2)[1].split('Z')[2]    
    if LA_zipcode not in LA_other_zipcodes:
        df = pd.read_csv(filename, index_col=None, header=0)
        df['zipcode'] = LA_zipcode
        lat_lon = search.by_zipcode(LA_zipcode).values()[7:9]
        df['Latitude'] = lat_lon[0]
        df['Longitude'] = lat_lon[1]
        li.append(df)
        count+=1
print(df)
userforecast = pd.concat(li, axis=0, ignore_index=True)
forecast_data = userforecast[['ds','zipcode','trend','trend_lower','trend_upper','Latitude','Longitude']]
#data = pd.DataFrame([],columns = ['Rankings', 'Zipcode', 'Trend','Avg. ROI','ROI Rank' ,'Wealth Rank','Latitude','Longitude'])
ranked_data = pd.DataFrame([],columns = ['Rankings', 'Zipcode', 'Trend','Avg. ROI','ROI Rank' ,'Wealth Rank','Latitude','Longitude'])

#set initial values for min and max budget price
minMSP = 250000
maxMSP = 600000

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'light_text': '#D8D8D8'
}

# Boostrap CSS.
# app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
app.config['suppress_callback_exceptions']=True

#  Layouts
layout_table = dict(
    autosize=True,
    height=500,
    font=dict(color="#191A1A"),
    titlefont=dict(color="#191A1A", size='14'),
    margin=dict(
        l=45,
        r=0,
        b=5,
        t=0
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
        l=-20,
        r=0,
        b=0,
        t=0
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

#app calls
#__________________________________
#__________________________________


app.layout = html.Div([

    #headers and initial user input
    #------------------------------
    html.Div([
        html.Div([
            html.H1(children='Movin\'OnUP!',
                    style={
                        'textAlign': 'left',
                        'color': colors['text']},
                    className = "nine columns"
            ),
            html.Img(
                src="https://assets-global.website-files.com/575a31d2ce5d01dc7a20de45/575a31d2ce5d01dc7a20ded3_insight_logo.png",
                className='three columns',
                style={
                    'height': '14%',
                    'width': '14%',
                    'float': 'right',
                    'position': 'relative',
                    'margin-top': 20,
                    'margin-right': 20
                },
            ),
            html.Div(children='''A home pre-search optimization app''', 
                    style={
                        'margin-top': 0,
                        'margin-right': 15,
                        'margin-bottom': 15,
                        'textAlign': 'left',
                        'color': colors['text']
                    },
                    className = 'nine columns'
            ),
            ], className = "row"
        )
    ]),

    #Right side
    #---------
    html.Div([
        html.Div([
            dcc.Input(id='minMSPinput', type='number', value=minMSP,
                        placeholder='Enter min. price', 
                        style={ 
                        'height': '20%',
                        'width': '42%',
                        'float': 'left',
                        'textAlign': 'left'
            }),
            dcc.Input(id='maxMSPinput', type='number', value=maxMSP,
                        placeholder='Enter max. price', 
                        style={
                        'height': '20%',
                        'width': '42%',
                        'float': 'left',
                        'textAlign': 'left'
            }),                
            html.Div(children='Min. Home Price   <--->   Max. Home Price (USD)',
                        style={
                        # 'float':'left',
                        'fontSize': 16,
                        'margin-top': 0,
                        'margin-right': 45,
                        'margin-bottom': 0,
                        'textAlign': 'left'
            }),             

            dcc.Graph(id='map-graph',
                      animate=True,
                      style={'margin-top': 0,'margin-bottom': 0,'padding-bottom':0}
            ),

            html.Div(id='Yearly-outlook-output-container',style={'fontSize': 16,'margin-top': 0,'padding-top':0,'textAlign': 'center'},
                children='Predicted Future Outlook'
            ),
            dcc.Slider(
                    id='Yearly_outlook',
                    min=0,
                    max=10,
                    value=0,
                    marks={
                        0: {'label': '   Now', 'style': {'color': '#77b0b1'}},
                        1: {'label': '1  Year'},
                        2: {'label': ''},
                        3: {'label': ''},
                        4: {'label': ''},                       
                        5: {'label': '5 Years'},
                        6: {'label': ''},
                        7: {'label': ''},
                        8: {'label': ''},
                        9: {'label': ''},
                        10: {'label': '10 Years', 'style': {'color': '#f50'}}
                    },
            ),

            ], className = "five columns"
        ),   

        html.Div([
            html.H2(id='Desirables-Value-header',style={'fontSize': 40,'margin-top': 0,'padding-bottom':0,'textAlign': 'center','color':'#f50'},
                children ='Desirables'
                ),
            html.Div(id='Wealth-Value-output-container',style={'fontSize': 16,'margin-top': 0,'padding-top':0,'textAlign': 'center'},
                children='Local Economics'
                ),
            dcc.Slider(
                    id='Wealth_Value',
                    min=0,
                    max=4,
                    value=2,
                    marks={
                        0: {'label': 'Not Important', 'style': {'color': '#77b0b1'}},
                        1: {'label': 'Less Important'},
                        2: {'label': 'Important'},
                        3: {'label': 'Very Important'},
                        4: {'label': 'Extremely Important', 'style': {'color': '#f50'}}
                    }
            ),

            html.Div(id='ROI-Value-output-container',style={'fontSize': 16,'margin-top': 0,'padding-top':60,'textAlign': 'center'},
                children='Home Apprecitaion'
                ),
            dcc.Slider(
                    id='ROI_Value',
                    min=0,
                    max=4,
                    value=2,
                    marks={
                        0: {'label': 'Not Important', 'style': {'color': '#77b0b1'}},
                        1: {'label': 'Less Important'},
                        2: {'label': 'Important'},
                        3: {'label': 'Very Important'},
                        4: {'label': 'Extremely Important', 'style': {'color': '#f50'}}
                    }
            ),

            html.Div(id='Crime-Value-output-container',style={'fontSize': 16,'margin-top': 0,'padding-top':60,'textAlign': 'center'},
                children='Public Safety'
                ),
            dcc.Slider(
                    id='Crime_Value',
                    min=0,
                    max=4,
                    value=2,
                    marks={
                        0: {'label': 'Not Important', 'style': {'color': '#77b0b1'}},
                        1: {'label': 'Less Important'},
                        2: {'label': 'Important'},
                        3: {'label': 'Very Important'},
                        4: {'label': 'Extremely Important', 'style': {'color': '#f50'}}
                    }
            ),

            ],className = "three columns"
        ),

        html.Div([
            dt.DataTable(
                id='datatable',
                data=ranked_data.to_dict('records'),
                columns=[{'id': c, 'name': c} for c in ranked_data.columns],
                #title='Best Locations in LA',
                row_selectable='multi',
                # filtering=True,
                sorting=True,
                virtualization=True
                # pagination_mode='fe',
                # # #selected_rows=[],
                # pagination_settings={
                #     "current_page": 0,
                #     "page_size": 10
                #     },
                )
            ],
            style = layout_table,
            className="four columns"
        )
        ],className= "row"
    ),

    html.Div([
        html.P('Developed by Duane M. Lee, Ph.D - ', style = {'display': 'inline'}
            ),
        html.A('duane.m.lee@gmail.com', href = 'mailto:duane.m.lee@gmail.com'
            )
        ], className = "twelve columns",
           style = {'fontSize': 18, 'padding-top': 25,'margin-top':20,'textAlign':'right'}
    )


],className = 'ten columns offset-by-one'
)


#callback section 
#-------------------

# @app.callback(
#     Output('map-graph', 'figure'),
#     [Input('datatable', 'data'),
#      Input('datatable', 'selected_rows')])
# def map_selection(data, selected_rows):
#     aux = pd.DataFrame(rows)
#     temp_df = aux.ix[selected_rows, :]
#     if len(selected_rows) == 0:
#         return gen_map(aux)
#     return gen_map(temp_df)

@app.callback(
    Output('datatable', 'data'),
    [Input('minMSPinput', 'value'),
     Input('maxMSPinput', 'value'),
     Input('Yearly_outlook', 'value'),
     Input('Wealth_Value', 'value'),
     ])
def update_selected_row_indices(minMSP, maxMSP,year,wealth):
    global forecast_data, ranked_data
    
    map_aux = forecast_data.copy()
    ranked_aux = ranked_data.copy()

    now = datetime.today().strftime('%Y')
    now0 = datetime.today()
    nowp = datetime.today().strftime('%Y-%m-%d')  
    selected_year = np.int(now) + year
    #print(selected_year,now)
    projected = now0.replace(year=selected_year).strftime('%Y-%m-%d')
    #print(selected_year,now,projected)
    map_aux['ds'] = pd.to_datetime(map_aux['ds'])

    five_years = np.int(now) + 5
    projected_5yrs = now0.replace(year=five_years).strftime('%Y-%m-%d')
    five_year_projection_arr = map_aux.ds.dt.strftime('%Y-%m-%d') == projected_5yrs
    now_projection_arr = map_aux.ds.dt.strftime('%Y-%m-%d') == nowp

    a = map_aux.zipcode.loc[five_year_projection_arr]
    b = map_aux.zipcode.loc[now_projection_arr]

    c = [a] + [b]
    c0 = [y for x in c for y in x]
    c1 = pd.DataFrame({'mergedzips':c0})
    nonmatchedarr = c1.drop_duplicates(keep=False)
    arr = [np.where(map_aux.zipcode.loc[now_projection_arr] == nonmatchedarr.mergedzips.values[i])[0][0] for i in range(len(nonmatchedarr))]

    adjust_arr = []
    i = 0
    j = 0
    for i in range(len(now_projection_arr)):
        if now_projection_arr.values[i] == True:
            j+=1
            if j in arr:
                adjust_arr.append(i) 

    now_projection_arr[adjust_arr] = False

# User weighting scores
#----------------------
    #ROI score
    avgROI = (map_aux.trend.loc[five_year_projection_arr].values - map_aux.trend.loc[now_projection_arr].values)/(5 * map_aux.trend.loc[now_projection_arr].values) * 100
    
    ROIraw = (map_aux.trend.loc[five_year_projection_arr].values - map_aux.trend.loc[now_projection_arr].values)/(5 * map_aux.trend.loc[now_projection_arr].values) \
    * np.exp((map_aux.trend_lower.loc[five_year_projection_arr].values - map_aux.trend_lower.loc[now_projection_arr].values)/(5 * map_aux.trend_lower.loc[now_projection_arr].values))
    ROIraw[ROIraw < 0] = 0
    ROIscore = ROIraw/np.max(ROIraw) * 100

    #Wealth score
    med_income = 50000
    wealth_factors = ( (med_income/np.max(med_income))**2 + (map_aux['trend'].loc[now_projection_arr].values/np.max(map_aux['trend'].loc[now_projection_arr].values))**2 )
    wealth_score = np.sqrt( wealth_factors/2 ) * 100

    overall_score = np.sqrt((ROIscore**2 + wealth_score**2)/2) * 100
    overall_rank = np.argsort(overall_score)


    projected_data = map_aux.loc[map_aux.ds.dt.strftime('%Y-%m-%d') == projected]

    #ranked table 
    ranked_aux['Rankings'] = overall_rank + 1
    ranked_aux['Zipcode'] = map_aux['zipcode'].loc[now_projection_arr].values
    ranked_aux['Trend'] = map_aux['trend'].loc[now_projection_arr].values
    ranked_aux['Avg. ROI'] = avgROI
    ranked_aux['ROI Rank'] = ROIscore
    ranked_aux['Wealth Rank'] = wealth_score
    ranked_aux['Latitude'] = map_aux['Latitude'].loc[now_projection_arr].values
    ranked_aux['Longitude'] = map_aux['Longitude'].loc[now_projection_arr].values
    
    #ranked data within budget
    ranked_budget_data = ranked_aux[np.logical_and(ranked_aux['Trend'] >= minMSP,ranked_aux['Trend'] < maxMSP)]
    ranked_budget_data.sort_values('Rankings',inplace = True)

    ranked_data = ranked_budget_data.to_dict('records')

    return ranked_data




if __name__ == "__main__":
    app.run_server(debug=False)

