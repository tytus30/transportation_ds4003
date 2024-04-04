# %%
# import libraries
import pandas as pd
import numpy as np
#import seaborn as sns
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State

# %%
# data

data_upt = pd.read_csv("data1.csv")
data_quarter = pd.read_csv("data2.csv")
data_year = pd.read_csv("data3.csv")

# %%
data_upt.head()
#data_quarter.head()
#data_year.head()


# %%
# data cleaning, for some reason, my clean data csv files didn't save some objects correctly

# changing from obt to date time
data_upt['Week of'] = pd.to_datetime(data_upt['Week of'])
print(data_upt.dtypes)


# %%


# %%
# weekly ridership graph

# make the graph
fig1 = px.line(data_upt, x="Week of", y="Prediction", color="City")
# add a stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# initialize app
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Public Transportation Ridership Across America"

# define layout and elements
app.layout = html.Div([

    #titles and subheadings
    html.Div(className='row', children=[ #row makes this its own row
        html.H1("Public Transportation Ridership Across America")
    ]),


# making a region radioitem
    html.Div(children = [
        html.Label("Select a Region"),
        dcc.RadioItems( 
            id='region-radio',
            options=[{'label': region, 'value': region} for region in data_upt['Region'].unique()],
            value=data_upt['Region'].iloc[0]
            )
    ], style={'width': '50%', 'display': 'inline-block'}), #puts this in 50% of the screen),

# # making a city dropdown
#     html.Div(children = [    
#         dcc.Dropdown(
#             id='city-dropdown',
#             options=[{'label': city, 'value': city} for city in data_upt['City'].unique() if isinstance(city, str)], #by adding the isinstance ensures not collecting nulls
#             value=data_upt['City'].iloc[0], #intial value
#             multi=True
#             )
#     ]),

# making a rangeslider for years
    html.Div(children = [
        html.Label("Select the Range of Years"),
        dcc.RangeSlider( #making a range slider for the years of fig1
            id = 'pandas-range-slider',
            min = data_upt['Week of'].dt.year.min(), #finds the min in Week of column
            max = data_upt['Week of'].dt.year.max(), #finds the max in the Week of column
            step = .25, #step is currently every quarter (3 months)
            value = (data_upt['Week of'].dt.year.min(), data_upt['Week of'].dt.year.max()),  # set initial value to min and max years
            marks = {i: str(i) for i in range(data_upt['Week of'].dt.year.min(), data_upt['Week of'].dt.year.max()+1)}, # the marks are the years in the range of 2018-2024  
            tooltip={"placement": "bottom", "always_visible": True} #this adds a year pop-up to know which year is selected
            )
    ], style={'width': '50%', 'display': 'inline-block'}), #puts this in 50% of the screen

    html.Div(children = [
        dcc.Graph(
            id='weekly-ridership-graph',
            figure= fig1 #call the plotly graph from above
            ) 

    ]),

])

# define callback to update graph based on selected region, city, and year range
@app.callback(
    Output('weekly-ridership-graph', 'figure'),
    Input('region-radio', 'value'),
    Input('pandas-range-slider', 'value')
)
def update_graph(region, year_range):
    # filter data based on selected region and year range
    filtered_data = data_upt[data_upt['Region'] == region]
    filtered_data = filtered_data[filtered_data['Week of'].dt.year.between(year_range[0], year_range[1])]
    
    # figure
    fig = px.line(filtered_data, x="Week of", y="Prediction", color="City",
                  title=f"Weekly Ridership in {region}")
    fig.update_layout(xaxis_title='Time', yaxis_title='Ridership') # adds axis names
    return fig


# run app
if __name__ == '__main__':
    app.run_server(debug=True)


