# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State#, Event
import pandas as pd
import collections

triples = pd.read_csv('./assets/SEMMEDDB_TRIPLES_FINAL.csv')

# DFs for PART 1
df_subj = triples.copy()
df_subj = df_subj[df_subj['IS_MASTER_GENE']=='subject']
df_subj = df_subj[['SUBJECT', 'RELATION', 'OBJECT', 'PMID']].copy()
df_subj['PMID'] = df_subj['PMID'].apply(lambda x: x.split(','))
df_subj['PMID_Count'] = df_subj['PMID'].apply(lambda x: len(x))
df_subj = df_subj[['SUBJECT', 'RELATION', 'OBJECT', 'PMID_Count']]#, 'PMID']]
items_subj = sorted(df_subj['SUBJECT'].unique().tolist())

df_obj = triples.copy()
df_obj = df_obj[df_obj['IS_MASTER_GENE']=='object']
df_obj = df_obj[['SUBJECT', 'RELATION', 'OBJECT', 'PMID']].copy()
df_obj['PMID'] = df_obj['PMID'].apply(lambda x: x.split(','))
df_obj['PMID_Count'] = df_obj['PMID'].apply(lambda x: len(x))
df_obj = df_obj[['SUBJECT', 'RELATION', 'OBJECT', 'PMID_Count']]#, 'PMID']]
items_obj = sorted(df_obj['OBJECT'].unique().tolist())


# DFs for PART 2
df_subj2 = triples.copy()
df_subj2 = df_subj2[df_subj2['IS_MASTER_GENE']=='subject']
df_subj2 = df_subj2[['SUBJECT', 'RELATION', 'OBJECT', 'PMID']]
df_subj2['PMID'] = df_subj2['PMID'].apply(lambda x: len(x.split(',')))
grouped = df_subj2.groupby(['RELATION', 'OBJECT']).agg({'SUBJECT': ['count'], 'PMID': ['sum']})
df_subj2 = pd.DataFrame((grouped.reset_index()))
df_subj2.columns=(['RELATION', 'OBJECT', 'Subject_Count', 'PMID_Count'])
df_subj2_rels = sorted(df_subj2['RELATION'].unique().tolist())

df_obj2 = triples.copy()
df_obj2 = df_obj2[df_obj2['IS_MASTER_GENE']=='object']
df_obj2 = df_obj2[['SUBJECT', 'RELATION', 'OBJECT', 'PMID']]
df_obj2['PMID'] = df_obj2['PMID'].apply(lambda x: len(x.split(',')))
grouped = df_obj2.groupby(['RELATION', 'SUBJECT']).agg({'OBJECT': ['count'], 'PMID': ['sum']})
df_obj2 = pd.DataFrame((grouped.reset_index()))
df_obj2.columns=(['RELATION', 'SUBJECT', 'Object_Count', 'PMID_Count']) # rename
df_obj2_rels = sorted(df_obj2['RELATION'].unique().tolist())


# DFs for PART 3
df_subj3 = triples.copy()
df_subj3 = df_subj3[df_subj3['IS_MASTER_GENE']=='subject']
df_subj3 = df_subj3[['SUBJECT', 'RELATION', 'OBJECT', 'PMID']].copy()
df_subj3['PMID_Count'] = df_subj3['PMID'].apply(lambda x: len(x.split(',')))
df_subj3['PMID'] = df_subj3['PMID'].apply(lambda x: x.split('\,'))
df_subj3 = df_subj3[['SUBJECT', 'RELATION', 'OBJECT', 'PMID_Count', 'PMID']]
items_rels31 = sorted(df_subj3['RELATION'].unique().tolist())
items_subj3 = sorted(df_subj3['SUBJECT'].unique().tolist())

df_obj3 = triples.copy()
df_obj3 = df_obj3[df_obj3['IS_MASTER_GENE']=='object']
df_obj3 = df_obj3[['SUBJECT', 'RELATION', 'OBJECT', 'PMID']].copy()
df_obj3['PMID_Count'] = df_obj3['PMID'].apply(lambda x: len(x.split(',')))
df_obj3['PMID'] = df_obj3['PMID'].apply(lambda x: x.split('\,'))
df_obj3 = df_obj3[['SUBJECT', 'RELATION', 'OBJECT', 'PMID_Count', 'PMID']]
items_rels32 = sorted(df_obj3['RELATION'].unique().tolist())
items_obj3 = sorted(df_obj3['OBJECT'].unique().tolist())


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally = False
server = app.server
app.title = 'SemmedDB Triple Explorer'

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

# colors = {
#     'background': '#111111',
#     'text': '#7FDBFF'
# }


app.layout = html.Div(children=[

    html.H1('SemmedDB Triple Explorer', style={'textAlign': 'center'}),
    html.P('''
            The Semantic MEDLINE Database (SemMedDB) is a repository of semantic predications (subject-predicate-object triples) extracted
            from approx. 29.7M PubMed citations.
           '''),
    dcc.Markdown('''[Find out more](https://skr3.nlm.nih.gov/SemMedDB/)'''),


##########
# PART 1 #
##########

    # Row 0
    html.Div(
        [
        # Subject left drop down
        html.Div(
            [
            html.H3('Subject View'),
            ], className='six columns'),

        # Object right drop down
        html.Div(
            [
            html.H3('Object View'),
            ], className='six columns'),
        ], className='row'),

    # Row 1
    html.Div(
        [
        # Subject left drop down
        html.Div(
            [
                html.Div('Subject', className='three columns'),
                html.Div(
                    [
                    dcc.Dropdown(
                    id='subj-dropdown',
                    options= [{'label': item, 'value': item} for item in items_subj])
                    ], className='four columns'),
            ], className='six columns'),

        # Object right drop down
        html.Div(
[
                html.Div('Object', className='three columns'),
                html.Div(
                    [
                    dcc.Dropdown(
                    id='obj-dropdown',
                    options=[{'label': item, 'value': item} for item in items_obj])
                    ], className='four columns'),
            ], className='six columns'),
        ], className='row'),

    # Row 2
    html.Div(
        [
            # Relation left  drop down
            html.Div(
                [
                    html.Div('Relation', className='three columns'),
                    html.Div(
                        [
                        dcc.Dropdown(id='rel-dropdown-l')
                        ], className='four columns'),
                ], className='six columns'),

            # Relation right drop down
            html.Div(
                [
                    html.Div('Relation', className='three columns'),
                    html.Div(
                        [
                        dcc.Dropdown(id='rel-dropdown-r')
                        ], className='four columns'),
                ], className='six columns'),
        ], className='row'),

    # Row 3
    html.Div(
        [
        # Table 1
        html.Div(
            [
                dt.DataTable(
                rows=[],#df_subj.to_dict('records'),
                columns=df_subj.columns,
                row_selectable=False,
                filterable=True,
                sortable=True,
                selected_row_indices=[],
                editable=False,
                id='datatable-1-l')
            ], style = layout_table, className='six columns'),

        # Table 2
        html.Div(
            [
                dt.DataTable(
                rows=[],#df_obj.to_dict('records'),
                columns=df_obj.columns,
                row_selectable=False,
                filterable=True,
                sortable=True,
                selected_row_indices=[],
                editable=False,
                id='datatable-1-r')
            ], style = layout_table, className='six columns'),
        ]
        , className='row'),

##########
# PART 2 #
##########

    # Row 0
    html.Div(
        [
        # Subject left drop down
        html.Div(
            [
            html.H4('Most Common RELATION by OBJECT type'),
            ], className='six columns'),

        # Object right drop down
        html.Div(
            [
            html.H4('Most Common RELATION by SUBJECT type'),
            ], className='six columns'),
        ], className='row'),

    # Row 1
    html.Div(
        [
            # Relation left  drop down
            html.Div(
                [
                    html.Div('Relation', className='three columns'),
                    html.Div(
                        [
                        dcc.Dropdown(
                            id='rel21-dropdown',
                            options= [{'label': item, 'value': item} for item in df_subj2_rels]),
                        ], className='four columns'),
                ], className='six columns'),

            # Relation right drop down
            html.Div(
                [
                    html.Div('Relation', className='three columns'),
                    html.Div(
                        [
                        dcc.Dropdown(id='rel22-dropdown',
                        options= [{'label': item, 'value': item} for item in df_obj2_rels]),
                        ], className='four columns'),
                ], className='six columns'),
        ], className='row'),

    # Row 2
    html.Div(
        [
        # Table 1
        html.Div(
            [
                dt.DataTable(
                rows=[],#df_subj2.to_dict('records'),
                columns=df_subj2.columns,
                row_selectable=False,
                filterable=True,
                sortable=True,
                # selected_row_indices=[],
                editable=False,
                id='datatable-2-l')
            ], style = layout_table, className='six columns'),

        # Table 2
        html.Div(
            [
                dt.DataTable(
                rows=[],#df_obj2.to_dict('records'),
                columns=['SUBJECT', 'RELATION', 'Object_Count', 'PMID_Count'],
                row_selectable=False,
                filterable=True,
                sortable=True,
                # selected_row_indices=[],
                editable=False,
                id='datatable-2-r')
            ], style = layout_table, className='six columns'),
        ]
        , className='row'),


##########
# PART 3 #
##########

    # Row 0
    html.Div(
        [
        # Subject left drop down
        html.Div(
            [
            html.H4('SUBJECTS for a given RELATION-OBJECT combination'),
            ], className='six columns'),

        # Object right drop down
        html.Div(
            [
            html.H4('OBJECTS for a given SUBJECT-RELATION combination'),
            ], className='six columns'),
        ], className='row'),

    # Row 1
    html.Div(
        [
        # Relation left drop down
        html.Div(
            [
                html.Div('Relation', className='two columns'),
                html.Div(
                    [
                    dcc.Dropdown(
                    id='rel31-dropdown',
                    options= [{'label': item, 'value': item} for item in items_rels31])
                    ], className='four columns'),
            ], className='six columns'),

        # Relation right drop down
        html.Div(
            [
                html.Div('Relation', className='two columns'),
                html.Div(
                    [
                    dcc.Dropdown(
                    id='rel32-dropdown',
                    options=[{'label': item, 'value': item} for item in items_rels32])
                    ], className='four columns'),
            ], className='six columns'),
        ], className='row'),

    # Row 2
    html.Div(
        [
        # Object left drop down
        html.Div(
            [
                html.Div('Object', className='two columns'),
                html.Div(
                    [
                    dcc.Dropdown(id='obj3-dropdown')
                    ], className='six columns'),
            ], className='six columns'),

        # Subject right drop down
        html.Div(
            [
                html.Div('Subject', className='two columns'),
                html.Div(
                    [
                    dcc.Dropdown(id='subj3-dropdown')
                    ], className='six columns'),
            ], className='six columns'),
        ], className='row'),

    # Row 3
    html.Div(
        [
        # Table 1
        html.Div(
            [
                dt.DataTable(
                rows=[],#df_subj3.to_dict('records'),
                columns=['SUBJECT', 'PMID_Count', 'PMID'],
                row_selectable=False,
                filterable=True,
                sortable=True,
                # selected_row_indices=[],
                editable=False,
                id='datatable-3-l')
            ], style = layout_table, className='six columns'),

        # Table 2
        html.Div(
            [
                dt.DataTable(
                rows=[],#df_obj3.to_dict('records'),
                columns=['OBJECT', 'PMID_Count', 'PMID'],
                row_selectable=False,
                filterable=True,
                sortable=True,
                # selected_row_indices=[],
                editable=False,
                id='datatable-3-r')
            ], style = layout_table, className='six columns'),
        ]
        , className='row'),
], className='ten columns offset-by-one') # end main Div


####################
# Callbacks PART 1 #
####################

# Table 1 left
@app.callback(
    Output('rel-dropdown-l', 'options'),
    [Input('subj-dropdown', 'value')])
def set_options_1_rel_left(subject):
    if subject is None or relation == 'All':
        return []
    else:
        df_aux = df_subj[df_subj['SUBJECT'] == subject]
        options = [{'label': i, 'value': i} for i in ['All']+df_aux['RELATION'].unique().tolist()]
        return options

@app.callback(
    Output('subj-dropdown', 'options'),
    [Input('rel-dropdown-l', 'value')])
def set_options_1_subj_left(relation):
    if relation is None or relation == 'All':
        df_aux = df_subj
        options = [{'label': i, 'value': i} for i in ['All']+df_aux['SUBJECT'].unique().tolist()]
        return options
    else:
        df_aux = df_subj[df_subj['RELATION'] == relation]
        options = [{'label': i, 'value': i} for i in ['All']+df_aux['SUBJECT'].unique().tolist()]
        return options

@app.callback(
    Output('datatable-1-l', 'rows'),
    [
        Input('subj-dropdown', 'value'),
        Input('rel-dropdown-l', 'value')
     ])
def update_datatable_1_left(x, y):
    if x is None and y is None:
        df_aux = df_subj
    elif not x is None and y is None:
        df_aux = df_subj[df_subj['SUBJECT'] == x]
    elif x is None and not y is None:
        df_aux = df_subj[df_subj['RELATION'] == y]
    else:
        df_aux = df_subj[(df_subj['SUBJECT'] == x) & (df_subj['RELATION'] == y)]

    df_aux = df_aux.sort_values(by='PMID_Count', ascending=False)
    rows = df_aux.to_dict('records')
    return rows


# Table 1 right
@app.callback(
    Output('rel-dropdown-r', 'options'),
    [Input('obj-dropdown', 'value')])
def set_options_1_right(object):
    if object is None:
        return []
    else:
        df_aux = df_obj[df_obj['OBJECT'] == object]
        options = [{'label': i, 'value': i} for i in df_aux['RELATION'].unique().tolist()]
        return options

@app.callback(
    Output('datatable-1-r', 'rows'),
    [
        Input('obj-dropdown', 'value'),
        Input('rel-dropdown-r', 'value')
     ])
def update_datatable_1_right(x, y):
    if x is None and y is None:
        df_aux = df_obj
    elif not x is None and y is None:
        df_aux = df_obj[df_obj['OBJECT'] == x]
    elif x is None and not y is None:
        df_aux = df_obj[df_obj['RELATION'] == y]
    else:
        df_aux = df_obj[(df_obj['OBJECT'] == x) & (df_obj['RELATION'] == y)]

    df_aux = df_aux.sort_values(by='PMID_Count', ascending=False)
    rows = df_aux.to_dict('records')
    return rows


####################
# Callbacks PART 2 #
####################

# Table 2 left
@app.callback(
    Output('datatable-2-l', 'rows'),
    [Input('rel21-dropdown', 'value')]
)
def update_datatable_2_left(x):
    print(x)
    df_aux = df_subj2.copy()
    if x is None:
        df_aux = df_aux.sort_values(by=['Subject_Count', 'PMID_Count'], ascending=False)
        rows = df_aux.to_dict('records')
        return rows
    else:
        df_aux = df_aux[df_aux['RELATION'] == x]
        df_aux = df_aux.sort_values(by=['Subject_Count', 'PMID_Count'], ascending=False)
        rows = df_aux.to_dict('records')
        return rows

# Table 2 right
@app.callback(
    Output('datatable-2-r', 'rows'),
    [Input('rel22-dropdown', 'value')])
def update_datatable_2_right(x):
    if x is None:
        df_aux = df_obj2
        df_aux = df_aux.sort_values(by=['Object_Count', 'PMID_Count'], ascending=False)
        rows = df_aux.to_dict('records')
    else:
        df_aux = df_obj2[df_obj2['RELATION'] == x]
        df_aux = df_aux.sort_values(by=['Object_Count', 'PMID_Count'], ascending=False)
        rows = df_aux.to_dict('records')
    return rows


####################
# Callbacks PART 3 #
####################


# Table 3 left
@app.callback(
    Output('obj3-dropdown', 'options'),
    [Input('rel31-dropdown', 'value')])
def set_options_3_left(relation):
    df_aux = df_subj3.copy()
    if relation is None:
        return [items_rels31]
    else:
        df_aux = df_aux[df_aux['RELATION'] == relation]
        options = [{'label': i, 'value': i} for i in df_aux['OBJECT'].unique().tolist()]
        return options

@app.callback(
    Output('datatable-3-l', 'rows'),
    [
        Input('rel31-dropdown', 'value'),
        Input('obj3-dropdown', 'value')
     ])
def update_datatable_3_left(x, y):
    df_aux = df_subj3.copy()
    if x is None:
        return [items_rels32]
    else:
        df_aux = df_aux[(df_aux['RELATION'] == x) & (df_aux['OBJECT'] == y)]
        df_aux = df_aux.sort_values(by='PMID_Count', ascending=False)
        rows = df_aux.to_dict('records')
        return rows


# Table 3 right
@app.callback(
    Output('subj3-dropdown', 'options'),
    [Input('rel32-dropdown', 'value')])
def set_options_3_right(relation):
    df_aux = df_obj3.copy()
    if relation is None:
        return []
    else:
        df_aux = df_aux[df_aux['RELATION'] == relation]
        options = [{'label': i, 'value': i} for i in df_aux['SUBJECT'].unique().tolist()]
        return options

@app.callback(
    Output('datatable-3-r', 'rows'),
    [
        Input('rel32-dropdown', 'value'),
        Input('subj3-dropdown', 'value')
     ])
def update_datatable_3_right(x, y):
    df_aux = df_obj3.copy()
    if x is None:
        return []
    else:
        df_aux = df_aux[(df_aux['RELATION'] == x) & (df_aux['SUBJECT'] == y)]
        df_aux = df_aux.sort_values(by='PMID_Count', ascending=False)
        rows = df_aux.to_dict('records')
        return rows

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.server.run(debug=True, threaded=True)
