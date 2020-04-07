

# import required packages
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from collections import Counter
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import networkx as nx
import base64
import io
import sys
from DoaProcessor import DoaProcessor
import plotly.graph_objs as go

user_selector=[]
time_scale=0



# Function to generate graph for each group
def generateElements(edge_list,sp_time):

    # Total speaking time
    total_sp = sum(sp_time.values())
    ele=[]
    G = nx.Graph()
    for edge in edge_list:

    # Check if the current edge already exist or not
        if G.has_edge(edge[0],edge[1]):

            # Get the weight of that edge
            w = G[edge[0]][edge[1]]['weight']

            # Remove it from the graph
            G.remove_edge(edge[0],edge[1])

            # Add it again with updated weight
            G.add_edge(edge[0],edge[1],weight=w+1)

        else:

            # If edge doesn't exist in the graph then add it with weight .5
            G.add_edge(edge[0],edge[1],weight=1)
    total_edges = len(edge_list)
    for n in list(G):
        user = 'User-'+str(n)
        speak_ratio = 200*sp_time[n]/total_sp
        t = {'id':n,'label':user,'width':speak_ratio}
        ele.append({'data':t})
    for e in G.edges:
        t = {'source':e[0],'target':e[1],'weight':G[e[0]][e[1]]['weight']*(30/total_edges)}
        ele.append({'data':t})

    return ele

app = dash.Dash(__name__,external_stylesheets=["/assets/bootstrap.css","/assets/plot.css"])
file_name = ""

error_flag = False
if len(sys.argv)!=3:

    print('Error: You have not specified the file name')
    print("Usage: python speech_analyzer.py csv-file-name no_speakers")
    sys.exit()
else:
    file_name = sys.argv[1]
    n = int(sys.argv[2])


# Creating object of ReAudio library object
re = DoaProcessor(file_name,n)


# Get unique groups
groups = re.getGroups()


group_options = []


for group in groups:
    group_options.append({'label':group,'value':group})
print(groups)
# Dictionary to store speaking time for each group
sp_time = {}


# Dictionary to store edge file for each groups
edge_file = {}


# Dictionary to store graph elements for dash
elements = {}


# Dictionary to store window wise speaking time
group_window_wise = {}

group_window_wise[0] = {}
group_window_wise[1] = {}
group_window_wise[2] = {}
group_window_wise[3] = {}
group_window_wise[4] = {}
group_window_wise[5] = {}
group_window_wise[6] = {}
group_window_wise[7] = {}



dir_freq = {}


# iterate over each group in group_ips
for group in groups:
    deg = re.getHighestNdegrees(group=group)
    re.setDegreeForSpeaker(deg)
    sp_time[group] = re.getSpeakingTime(plot=False,group=group)
    edge_file[group] = re.generateEdgeFile(group)
    elements[group] = generateElements(edge_file[group],sp_time[group])

    # Generate window wise speaking time for each group for each window
    group_window_wise[0][group] = re.generateWindowWiseSpeakingTime(window_size="30S")
    group_window_wise[1][group] = re.generateWindowWiseSpeakingTime(window_size="60S",time="min")
    group_window_wise[2][group] = re.generateWindowWiseSpeakingTime(window_size="2T",time="min")
    group_window_wise[3][group] = re.generateWindowWiseSpeakingTime(window_size="5T",time="min")
    group_window_wise[4][group] = re.generateWindowWiseSpeakingTime(window_size="15T",time="min")
    group_window_wise[5][group] = re.generateWindowWiseSpeakingTime(window_size="30T",time="min")
    group_window_wise[6][group] = re.generateWindowWiseSpeakingTime(window_size="60T",time="min")
    group_window_wise[7][group] = re.generateWindowWiseSpeakingTime(window_size="120T",time="hour")

    dir_freq[group] = {}

    group_frame = re.getGroupFrame(group=group)
    dfreq = Counter(group_frame['degree'])
    directions=  group_frame['degree'].unique()
    for dir in directions:
        dir_freq[group][dir] = group_frame.loc[group_frame['degree']==dir,:].shape[0]





default_group_value = 'group-1'

figure_data1=[]
final_df = re.generateWindowWiseSpeakingTime(window_size="30S")


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Number of speaker configuration


for i in range(4):
    user='u%d_speak'%(i+1)
    user_label = 'User-%d'%(i+1)
    figure_data1.append({'x':group_window_wise[0][default_group_value]['timestamp'],'y':group_window_wise[0][default_group_value][user],'type':'bar','name':user_label})



sp_user = [user for user in sp_time[default_group_value].keys()]
sp_duration = [sp for sp in sp_time[default_group_value].values()]

body = dbc.Container(
    [   dbc.Row([
            dbc.Col([
                html.H1("Direction of Arrival (DoA) Processor"),
                html.P("This web-app offers visualization of doa files collected from microphone arrays."+
                ". It is developed using Python Dash Framework and utilizes Bootstrap for styling the page.")
            ])
        ]),


        html.Hr(),
        dcc.Dropdown(
            id='group-selector',
            options=group_options,
            value=default_group_value
        ),
        dbc.Row([
            dbc.Col([
                html.H3("Direction of Arrival"),
                html.P("DoA (Direction of Arrival) represents the direction from which sound is detected by Raspberry prototype. DoA distribution (right figure) shows the freqeuncy of direction detected during recording. "),
                html.P("Voice activity detection (VAD) and Direction of Arrival (DoA) algorithms are used to detect voice and it's direction.")
            ],md=4),
            dbc.Col([
                html.H3("DoA  Distribution"),
                dcc.Graph(id='doa',
                figure={
                    'data':[
                        {'x':[dir for dir in dir_freq[default_group_value].keys()],'y':[dir for dir in dir_freq[default_group_value].values()],'type':'bar','name':'DoA distribution'}
                    ],
                    'layout':go.Layout(
                        xaxis={'title': 'Direction of Arrival (In degree)'},
                        yaxis={'title': 'Frequency'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
                    )
                })
            ],md=8)
        ]),
        dbc.Row([
            html.H3("Speaking Time")
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='spk',
                figure={
                    'data':[
                        {'x':sp_user,'y':sp_duration,'type':'bar','name':'Speaking Time'}
                    ],
                    'layout':go.Layout(
                        xaxis={'title': 'User'},
                        yaxis={'title': 'Speaking Time (sec.)'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 40},



                    )

                })
            ],md=5),
            dbc.Col([
                html.H3("How speaking time is computed?"),
                html.P("First of all, DoA distribution is computed (shown in above figure). From the distribution, frequent occuring directions are retrieved. Then these directions are processed to filter out a direction if it is close to another direction. Out of these, four directions are then extracted and assigned to users in clockwise."),
                html.P("Additionally, it also assume that speaker does not move while speaking.")
            ])

        ]),
        dbc.Row([
            html.H3("Group Dynamics"),

        ]),
        dbc.Row([
            cyto.Cytoscape(
                id='sna',
                elements=elements[default_group_value],
                style={'width': '600%', 'height': '350px'},
                layout={
                    'name': 'circle'
                },
                stylesheet=[
                    {
                        'selector':'node',
                        'style':{
                            'label':'data(label)',
                            'width':'data(width)',
                            'height':'data(width)'

                        }
                    },
                    {
                        'selector': '[weight]',
                        'style':{
                            'width':'data(weight)'

                        }

                    }

                ]
            )

        ]),
        html.H3("Speaking behavior over time"),
        html.P("You can select the time duration within which you want explore the speaking behavior."),
        html.Hr(),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='speech_graph_time',
                figure={
                    'data':figure_data1,
                    'layout':go.Layout(
                        xaxis={'title': 'Timestamp'},
                        yaxis={'title': 'Speaking Time(Sec)'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
                    )

                })
                ],md=10)
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Slider(
                id='window',
                min=0,
                max=10,
                step=None,
                marks = {
                    0 : '30Sec',
                    1 : '60Sec',
                    2 : '2Min',
                    3 : '5Min',
                    4 : '15Min',
                    5 : '30Min',
                    6 : '60Min',
                    7 : '2Hr'
                },
                value = 0

                )

            ])

        ])

    ])

app.layout = html.Div([body])


@app.callback(Output('speech_graph_time', 'figure'),
              [Input('window', 'value'),Input('group-selector','value')])
def display_value(value,group):
    time_window={0:'30S',1:'60S',2:'2T',3:'5T',4:'15T',5:'30T',6:'60T',7:'120T'}
    figure_data=[]

    for i in range(4):
        user='u%d_speak'%(i+1)
        user_label = 'User-%d'%(i+1)
        figure_data.append({'x':group_window_wise[value][group]['timestamp'],'y':group_window_wise[value][group][user],'type':'bar','name':user_label})

    figure={
        'data':figure_data,
        'layout':go.Layout(
            xaxis={'title': 'Timestamp'},
            yaxis={'title': 'Speaking Time '},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
        )

    }
    return figure



# Callback for direction of arrival distribution

@app.callback(Output('doa','figure'),[Input('group-selector','value')])
def update_doa(group):

    figure={
        'data':[
            {'x':[dir for dir in dir_freq[group].keys()],'y':[dir for dir in dir_freq[group].values()],'type':'bar','name':'DoA distribution'}
        ],
        'layout':go.Layout(
            xaxis={'title': 'Direction of Arrival (In degree)'},
            yaxis={'title': 'Frequency'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
        )
    }
    return figure

# Callback for speaking time Distribution
@app.callback(Output('spk','figure'),[Input('group-selector','value')])
def update_spk(group):

    sp_user = [user for user in sp_time[group].keys()]
    sp_duration = [sp for sp in sp_time[group].values()]
    figure={
        'data':[
            {'x':sp_user,'y':sp_duration,'type':'bar','name':'Speaking Time'}
        ],
        'layout':go.Layout(
            xaxis={'title': 'User'},
            yaxis={'title': 'Speaking Time (sec.)'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 40},



        )

    }
    return figure

# Callback for Network plotting
@app.callback(Output('sna','elements'),[Input('group-selector','value')])
def update_sna(group):

    return elements[group]
#return str(elements1)







if __name__ == '__main__':
    app.run_server(debug=False,host="0.0.0.0")
