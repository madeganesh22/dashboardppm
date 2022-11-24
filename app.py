# 1. Import Dash
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd
from statistics import mode
import plotly.express as px

# 2. Create a Dash app instance
app = dash.Dash(
    external_stylesheets=[dbc.themes.SPACELAB],
    name = 'Global Power Plant'
)

app.title = 'Power Plant Dashbord Analytics'


## ---- Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
    ],
    brand="Global Power Plant Dashboard Analytics",
    brand_href="#",
    color="light",
)


## --- Import Dataset GPP
gpp=pd.read_csv('power_plant.csv')


### CARD CONTENT
total_country = [
    dbc.CardHeader('Number of Country', style={"color":"black"}),
    dbc.CardBody([
        html.H1([gpp['country_long'].nunique()])
    ]),
]

total_pp = [
    dbc.CardHeader('Total Power Plant', style={"color":"black"}),
    dbc.CardBody([
        html.H1(gpp['name of powerplant'].nunique())
    ]),
]

total_fuel = [
    dbc.CardHeader('Most Used Fuel', style={"color":"black"}),
    dbc.CardBody([
        html.H1(f"{mode(gpp['primary_fuel'])} = {len(gpp[gpp['primary_fuel']==(gpp.describe(include='object')).loc['top','primary_fuel']])}")
    ])
]


## --- Visualization


#### CHOROPLETH
# Data aggregation
agg1 = pd.crosstab(
    index=[gpp['country code'], gpp['start_year']],
    columns='No of Power Plant'
).reset_index()

# Visualization
plot_map = px.choropleth(agg1.sort_values(by="start_year"),
             locations='country code',
              color_continuous_scale='tealgrn',
             color='No of Power Plant',
             animation_frame='start_year',
             template='ggplot2')


#### -----LAYOUT-----
# Everithing we see on screen/ our web -> UI (user interface)

app.layout = html.Div([
    navbar,
    
    html.Br(),
    
    ## --Component Main Page---

    html.Div([


        ## --ROW1--
        dbc.Row([
            ### COLUMN 1
            dbc.Col(
                [
                    dbc.Card(total_country, color='#D8F1D4',),
                    html.Br(),
                    dbc.Card(total_pp, color='#D6EBFE',),
                    html.Br(),
                    dbc.Card(total_fuel, color='#F5CBCC'),
                ],
                width=3),

            ### COLUMN 2
            dbc.Col([
                dcc.Graph(figure=plot_map),
            ], width=9),
        ]),

        html.Hr(),

        ## --ROW2--
        dbc.Row([
            ### COLUMN 1
            dbc.Col([
                html.H1('Analysis by Country'),
                dbc.Tabs([
                    ## --- TAB 1: RANKING
                    dbc.Tab(
                        dcc.Graph(
                            id='plotranking',
                        ),
                        label='Ranking'),

                    ## --- TAB 2: DISTRIBUTION
                    dbc.Tab(
                        dcc.Graph(
                            id='plotdistribut',
                        ),
                        label='Distribution'),
                ]),
            ], width=8),

            ### COLUMN 2
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Select Country'),
                    dbc.CardBody(
                        dcc.Dropdown(
                            id='choose_country',
                            options=gpp['country_long'].unique(),
                            value='Indonesia',
                        ),
                    ),
                ]),
                dcc.Graph(
                    id='plotpie',
                ),
            ], 
            width=4),
        ]),



    ], style={
        'paddingLeft':'30px',
        'paddingRight':'30px',
    })

])

### Callback Plot Ranking
@app.callback(
    Output(component_id='plotranking', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)

def update_plot1(country_name):
    # Data aggregation
    gpp_indo = gpp[gpp['country_long'] == country_name]

    top_indo = gpp_indo.sort_values('capacity in MW').tail(10)

    # Visualize
    plot_ranking = px.bar(
        top_indo,
        x = 'capacity in MW',
        y = 'name of powerplant',
        color_discrete_sequence=['#003F5C'],
        template = 'ggplot2',
        title = f'Rangking of Overall Power Plants in {str(country_name)}'
    )

    return plot_ranking

### Callback Plot Distribution
@app.callback(
    Output(component_id='plotdistribut', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)
def update_output2(country_name):
    gpp_indo = gpp[gpp['country_long'] == country_name]

    plot_distribut = px.box(
        gpp_indo,
        color='primary_fuel',
        y='capacity in MW',
        template='ggplot2',
        color_discrete_sequence=[ "#003f5c","#ff6361","#bc5090","#ffa600","#58508d"],
        title='Distribution of capacity in MW in each fuel',
        labels={
        'primary_fuel': 'Type of Fuel'
        }
    ).update_xaxes(visible=False)



    return plot_distribut

### Callback Pie
@app.callback(
    Output(component_id='plotpie', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)

def update_plot3(country_name):
    # Data aggregation
    gpp_indo = gpp[gpp['country_long'] == country_name]


    # aggregation
    agg2=pd.crosstab(
        index=gpp_indo['primary_fuel'],
        columns='No of Power Plant'
    ).reset_index()

    # visualize
    plot_pie = px.pie(
        agg2,
        values='No of Power Plant',
        names='primary_fuel',
        color_discrete_sequence=['#003f5c', '#58508d', '#bc5090', '#ff6361', '#ffa600'],
        template='ggplot2',
        hole=0.4,
        title=f'Distribution of Fuel Type in {country_name}',
        labels={
            'primary_fuel': 'Type of Fuel'
        }
    )
    return plot_pie


# 3. Start the Dash server
if __name__ == "__main__":
    app.run_server()