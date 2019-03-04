# https://plot.ly/python/reference/
# https://dash.plot.ly/interactive-graphing
import json
from textwrap import dedent as d

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import networkx as nx

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

G=nx.random_geometric_graph(10,0.125)

G = nx.Graph() # undirected!
G.add_edge('S', 'B', capacity=10)
G.add_edge('S', 'T', capacity=4)
G.add_edge('S', 'M', capacity=5)
G.add_edge('B', 'M', capacity=8)
G.add_edge('T', 'M', capacity=3)
G.add_edge('B', 'R', capacity=6)
G.add_edge('B', 'O', capacity=9)
G.add_edge('M', 'R', capacity=15)
G.add_edge('M', 'O', capacity=12)
G.add_edge('R', 'O', capacity=4)

fixed_positions = {'S':(1,2.5), 'B':(2.5,5), 'T':(3,1),
                   'M':(4.5,3), 'R':(7.5,5), 'O':(8.5,3)}
fixed_nodes = fixed_positions.keys()
pos = nx.spring_layout(G, pos=fixed_positions, fixed=fixed_nodes)


# pos=nx.get_node_attributes(G,'pos')
dmin=1
# ncenter=0
ncenter='S'
for n in pos:
    x,y=pos[n]
    d=(x-0.5)**2+(y-0.5)**2
    if d<dmin:
        ncenter=n
        dmin=d

p=nx.single_source_shortest_path_length(G,ncenter)

edge_trace = go.Scatter(
    x=[],
    y=[],
    line=dict(width=0.5,color='#888'),
    hoverinfo='none',
    mode='lines')

for edge in G.edges():
    for node in edge:
        x0, y0 = pos[node][0], pos[node][1]
        # x1, y1 = # G.node[edge[1]]['pos']
        edge_trace['x'] += tuple([x0])
        edge_trace['y'] += tuple([y0])



node_trace = go.Scatter(
    x=[],
    y=[],
    text=[],
    textposition='bottom center',
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=False,
        # colorscale options
        #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='YlGnBu',
        reversescale=True,
        color=[],
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line=dict(width=2)))

for node in G.nodes():
    x, y = pos[node][0], pos[node][1]
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])
    # node_trace['text'] += tuple([node])

# https://community.plot.ly/t/markers-text-mode-is-it-possible-to-have-different-text-and-hover-text/14656/4
annotations = []
for node, adjacencies in enumerate(G.adjacency()):
    node_trace['marker']['color']+=tuple([len(adjacencies[1])])
    node_info = '# of connections: '+str(len(adjacencies[1]))
    node_trace['text'] += tuple([node_info])

    annotations.append(
        dict(x=pos[adjacencies[0]][0],
             y=pos[adjacencies[0]][1],
             text=adjacencies[0],  # node name that will be displayed
             xanchor='left',
             xshift=10,
             font=dict(color='black', size=10),
             showarrow=False, arrowhead=1, ax=-10, ay=-10)
    )

# fig = go.Figure(data=[edge_trace, node_trace],
#              layout=go.Layout(
#                 title='<br>Network graph made with Python',
#                 titlefont=dict(size=16),
#                 showlegend=False,
#                 hovermode='closest',
#                 margin=dict(b=20,l=5,r=5,t=40),
#                 annotations=[ dict(
#                     text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
#                     showarrow=False,
#                     xref="paper", yref="paper",
#                     x=0.005, y=-0.002 ) ],
#                 xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#                 yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
#                 ), # end layout
#                 ) # end Figure


app.layout = html.Div([

    # html.Div([
    #
    #
    # dcc.Graph(
    #     id='basic-interactions',
    #     figure={
    #         'data': [
    #             {
    #                 'x': [1, 2, 3, 4],
    #                 'y': [4, 1, 3, 5],
    #                 'text': ['a', 'b', 'c', 'd'],
    #                 'customdata': ['c.a', 'c.b', 'c.c', 'c.d'],
    #                 'name': 'Trace 1',
    #                 'mode': 'markers',
    #                 'marker': {'size': 12}
    #             },
    #             {
    #                 'x': [1, 2, 3, 4],
    #                 'y': [9, 4, 1, 4],
    #                 'text': ['w', 'x', 'y', 'z'],
    #                 'customdata': ['c.w', 'c.x', 'c.y', 'c.z'],
    #                 'name': 'Trace 2',
    #                 'mode': 'markers',
    #                 'marker': {'size': 12}
    #             }
    #         ],
    #
    #         'layout': {
    #             'clickmode': 'event+select'
    #         }
    #     }
    # ),
    # ], style={'width': '49%', 'display': 'inline-block'}),
    #
    # html.Div(className='row', children=[
    #
    #         dcc.Markdown("""
    #             **Click Data**
    #             Click on points in the graph.
    #         """),
    #         html.Pre(id='click-data', style=styles['pre']),
    #
    # ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),

    html.Div([

        # https://plot.ly/python/user-guide/
        # https://github.com/jimmybow/visdcc/blob/master/README.md#3-animate-or-move-the-camera-
        dcc.Graph(id='basic-interactions2',
                  figure={
                      'data': [edge_trace, node_trace],

                      'layout':
                          {
                           'title': 'Dash Data Visualization',
                           'titlefont' : dict(size=14),
                           'showlegend': False,
                           'xaxis': dict(showgrid=False, zeroline=False, showticklabels=False),
                           'yaxis': dict(showgrid=False, zeroline=False, showticklabels=False),
                           'annotations': annotations,
                           'clickmode': 'event+select'
                          }
                  }),

    ], style={'width': '49%', 'display': 'inline-block'}),

    html.Div(className='row', children=[

        dcc.Markdown("""
            **Click Data**
            Click on points in the graph.
        """),
        html.Pre(id='click-data2', style=styles['pre']),

    ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),
])


# @app.callback(
#     Output('hover-data', 'children'),
#     [Input('basic-interactions', 'hoverData')])
# def display_hover_data(hoverData):
#     return json.dumps(hoverData, indent=2)


# @app.callback(
#     Output('click-data', 'children'),
#     [Input('basic-interactions', 'clickData')])
# def display_click_data(clickData):
#     return json.dumps(clickData, indent=2)

@app.callback(
    Output('click-data2', 'children'),
    [Input('basic-interactions2', 'clickData')])
def display_click_data_2(clickData):
    return json.dumps(clickData, indent=2)


# @app.callback(
#     Output('selected-data', 'children'),
#     [Input('basic-interactions', 'selectedData')])
# def display_selected_data(selectedData):
#     return json.dumps(selectedData, indent=2)
#
#
# @app.callback(
#     Output('relayout-data', 'children'),
#     [Input('basic-interactions', 'relayoutData')])
# def display_selected_data(relayoutData):
#     return json.dumps(relayoutData, indent=2)


if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(host = '0.0.0.0', port = 8080)
