# %%
# import libraries
import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dash_table, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

# %%
# data

data_upt = pd.read_csv("data1.csv")
data_quarter = pd.read_csv("data2.csv")
data_year = pd.read_csv("data3.csv")

# %%
#data_upt.head()
data_quarter.head()
#data_year.head()

# %%
# data cleaning, for some reason, my clean data csv files didn't save some objects correctly

# changing from obt to date time
data_upt['Week of'] = pd.to_datetime(data_upt['Week of'])
# print(data_upt.dtypes)

# limiting from 2018-2024 time frame, drop all other rows
data_quarter = data_quarter.query('Year >= 2018')
print(data_quarter)



# %%
fig1 = px.line(data_upt, x="Week of", y="Prediction", color="City", symbol="Size")
fig1


# %%
# fig = px.treemap(
#     data_quarter,
#     values="Total Ridership",
#     color="Quarter"
#     # names=["Quarter", "Year", "Total Ridership","Heavy Rail","Light Rail"],
#     # parents=["Quarter", "Year", "Total Ridership","Heavy Rail","Light Rail"],
#     )
# # fig.update_traces(root_color="lightgrey")
# # fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
# fig.show()

pivot_data_quarter = data_quarter.drop("Total Ridership", axis=1)
pivot_data_quarter = pivot_data_quarter.melt(id_vars=['Quarter', 'Year'], var_name='form_type', value_name='count')
# pivot_data_quarter = pivot_data_quarter.sort_values("Year")

# print(pivot_data_quarter)

fig2 = px.treemap(
    pivot_data_quarter,
    path=[px.Constant("all"), "Year", "Quarter", "form_type"], 
    values="count",
    hover_data={"Year": True, "Quarter": True, "form_type": True, "count": True}, #shows this info when hovering above the treemap
    color="Year",  # Color the boxes based on the year
    color_continuous_scale=px.colors.sequential.Plasma,  # Choose a sequential color scale
    color_continuous_midpoint=2020,  # Center the color scale at 2020
    color_discrete_sequence=["blue", "red"],  # Assign specific colors to form types
    labels={"form_type": "Form Type"},
    title="Public Transportation Ridership"
    # branchvalues="total"
)
fig2.update_traces(root_color="lightgrey")
fig2.update_layout(margin = dict(t=50, l=25, r=25, b=25))
fig2.show()

# %%
pivot_data_quarter.head()

# %%
# weekly ridership graph
fig1 = px.line(data_upt, x="Week of", y="Prediction", color="City")

#treemap of quarter data
fig2 = px.treemap(
    pivot_data_quarter,
    path=[px.Constant("all"), "Year", "Quarter", "form_type"], 
    values="count",
    hover_data={"Year": True, "Quarter": True, "form_type": True, "count": True}, #shows this info when hovering above the treemap
    color="Year",  # Color the boxes based on the year
    color_continuous_scale=px.colors.sequential.Plasma,  # Choose a sequential color scale
    color_continuous_midpoint=2020,  # Center the color scale at 2020
    labels={"form_type": "Form Type"},
    title="Public Transportation Ridership"
)
fig2.update_traces(root_color="lightgrey")
fig2.update_layout(margin = dict(t=50, l=25, r=25, b=25))


# initialize app
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY]) #use this stylesheet
server = app.server
app.title = "Public Transportation Ridership Across America"

# define layout and elements
app.layout = html.Div([

    #titles and subheadings
    html.Div(className='row', style={'textAlign': 'center', 'backgroundColor': '#e9ecef'}, children=[ #row makes this its own row and stlye and everything
        html.H1("Public Transportation Ridership Across America"),
        # description
        html.P("Welcome to the Public Transportation Ridership Across America Dashboard! Dive into the complexities of public transportation ridership data, exploring trends and insights that shape the way people travel across regions. Use the interactive tools to uncover patterns, compare ridership figures, and gain a comprehensive view of public transportation trends. Whether you're a policy maker, researcher, or enthusiast, this dashboard offers a unique perspective on ridership patterns and behaviors."),

    ]),




# making a region radioitem
    html.Div(children = [
        html.Label("Select a Region"),
        dcc.RadioItems( 
            id='region-radio',
            options=[{'label': region, 'value': region} for region in data_upt['Region'].unique()],
            value=data_upt['Region'].iloc[0]
            )
    ], style={'width': '20%', 'display': 'inline-block'}), #puts this in 50% of the screen),



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
    ], style={'width': '80%', 'display': 'inline-block', 'position': 'absolute', 'top': '250px'}), #puts this in 80% of the screen as well as kinda above graph




# call the graph in
    html.Div(children = [
        dcc.Graph(
            id='weekly-ridership-graph',
            figure= fig1 #call the plotly graph from above
            ) 

    ]),



# call the table in
    html.Div(children = [
        html.H3("Data Table of Ridership by Mode"),
        html.P("Select rows from the table below to populate the treemap with corresponding data. The treemap provides a visual representation of the selected data, helping you explore public transportation ridership trends broken down by mode of transportation. For more information on the types of transportation modes, refer to Sprint 2 for a detailed data dictionary."),
        dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in data_quarter.columns
        ],
        data=data_quarter.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 12,
    ),

    html.Div(id='datatable-interactivity-container')
    ]),



# call the treemap in
    html.Div(children= [
        dcc.Graph(
            id='treemap',
            figure=fig2 #call the tree map from above
        )
    ]),

])




############################################################################################
#############################CALLBACKS######################################################
############################################################################################



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

# define callback to update styles of selected data table cells
@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

# define callback to update treemap based on selected rows in the data table
@app.callback(
    Output('treemap', 'figure'),
    Input('datatable-interactivity', 'derived_virtual_selected_rows'),
    State('datatable-interactivity', 'derived_virtual_data')
)
def update_treemap(selected_rows, rows):
    if selected_rows is None:
        selected_rows = []

    dff = pd.DataFrame(rows) if rows else data_quarter

    # Filter the pivot data based on selected rows in the datatable
    selected_quarters = dff.loc[selected_rows, 'Quarter'].unique()
    selected_years = dff.loc[selected_rows, 'Year'].unique()
    filtered_data = pivot_data_quarter[(pivot_data_quarter['Quarter'].isin(selected_quarters)) &
                                        (pivot_data_quarter['Year'].isin(selected_years))]

    # Update the treemap figure
    fig2 = px.treemap(
        filtered_data,
        path=[px.Constant("all"), "Year", "Quarter", "form_type"],
        values="count",
        hover_data={"Year": True, "Quarter": True, "form_type": True, "count": True}, #shows this info when hovering above the treemap
        labels={"form_type": "Form Type"},
        title="Public Transportation Ridership by Mode"
    )
    fig2.update_traces(root_color="lightgrey")
    fig2.update_layout(margin=dict(t=50, l=25, r=25, b=25))

    return fig2





# run app
# if __name__ == '__main__':
#     app.run(jupyter_mode='tab', debug=True)

if __name__ == '__main__':
    app.run_server(debug=True)


