import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

########### Set up the chart
beers=['Blood Orange Ale', 'Snake Dog IPA', 'Imperial Porter', 'Double Dog IPA'] #changed Chesapeake Stout to Blood Orange Ale
ibu_values=[40, 60, 85, 75] #35 to 40
abv_values=[7.0, 7.1, 9.2, 4.3] #5.4 to 7.0
color1='yellow' #changed lightblue to yellow
color2='darkgreen'

bitterness = go.Bar(
    x=beers,
    y=ibu_values,
    name='IBU',
    marker={'color':color1}
)
alcohol = go.Bar(
    x=beers,
    y=abv_values,
    name='ABV',
    marker={'color':color2}
)

beer_data = [bitterness, alcohol]
beer_layout = go.Layout(
    barmode='group',
    title = 'Beer Comparison'
)

beer_fig = go.Figure(data=beer_data, layout=beer_layout)

########### Display the chart

app = dash.Dash()
server = app.server

app.layout = html.Div(children=[
    html.H1('Flying Dog Beers'),
    dcc.Graph(
        id='flyingdog',
        figure=beer_fig
    ),
    html.A('Code on Github', href='https://github.com/austinlasseter/flying-dog-beers'),
    html.Br(),
    html.A('Data Source', href='https://www.flyingdog.com/beers/'),
    ]
)

if __name__ == '__main__':
    app.run_server()
