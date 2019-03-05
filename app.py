import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash_table_experiments as dt
import pandas as pd
import numpy as np
from pubmed_lookup import PubMedLookup
from pubmed_lookup import Publication
import time

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://codepen.io/chriddyp/pen/brPBPO.css']

semmed = pd.read_csv('./assets/SEMMEDDB_TRIPLES_FINAL.csv')
pkinfam = pd.read_csv('./assets/pkinfam.tsv', sep='\t')
results = pd.read_csv('./assets/RESULTS-FINAL.csv', sep='\t',
                      usecols=['ProteinKinase_ID', 'KinaseLabel', 'ProteinSubstrate_ID', 'SubstrateLabel', 'Site', 'Score'])
email = 'raoul.biagioni@ie.fujitsu.com'

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions']=True
server = app.server

app.layout = html.Div([
    html.H4('LinkPhinder demo'),

    html.Div([
        html.Div([
            # 'A',

            dcc.Dropdown(
                # value='Enter a value...',
                options = [],
                id='dropdown-selected'
            ),
            html.Div(id='output'),

            dcc.Tabs(id="tabs-example", value='tab-1-example', children=[
                    dcc.Tab(label='Kinase View', value='tab-1-example'),
                    dcc.Tab(label='Substrate View', value='tab-2-example'),
            ]),
            html.Div(id='tabs-content-example'),

        ], className='six columns'),

        html.Div([
            html.Div([
                html.P('Phosphorylation Sites', style={'font-weight': 'bold',
                                                       'background-color': 'rgb(112, 205, 130)'}),
                html.Div(id='sites'),
                html.Br(),
            ]),

            # semmedDB
            html.P('Contextual Information from SemmedDB', style={'font-weight': 'bold',
                                                                  'background-color': 'rgb(112, 205, 130)'}),
            html.Div(id='tabs-content-example-right'),
            html.Div(id='articles'),
            html.Br(),
        ], className='six columns'),

    ], className='row'),

], className='ten columns offset-by-one')


@app.callback(
    Output('dropdown-selected', 'options'),
    [Input('dropdown-selected', 'value')])
def set_options_1_rel_left(subject):
    options = [{'label': i, 'value': i} for i in sorted(results['KinaseLabel'].unique().tolist())]
    return options

@app.callback(Output('tabs-content-example', 'children'),
              [Input('tabs-example', 'value'),
               Input('dropdown-selected', 'value')])
def render_content(tab, entity=None):
    if tab == 'tab-1-example':
        rows, related = get_rows(entity, 1)
        if entity=='' or entity is None:
            return html.Div([
                html.P('Please Select a Gene Name')
                ])
        else:
            return html.Div([
                html.H4('{} as Kinase'.format(entity)),
                html.Div([
                    dt.DataTable(
                        rows = rows,
                        columns=['KinaseLabel', 'SubstrateLabel', 'Score Range'],
                        row_selectable=True,
                        filterable=True,
                        sortable=True,
                        selected_row_indices=[],
                        editable=False,
                        id='tbl')
                ]),

        ])
    elif tab == 'tab-2-example':
        rows, related = get_rows(entity, 2)
        return html.Div([
            html.H4('{} as Substrate'.format(entity)),
            html.Div([
                dt.DataTable(
                    rows=rows,  # df_subj.to_dict('records'),
                    columns=['KinaseLabel', 'SubstrateLabel', 'Score Range'],
                    row_selectable=True,
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    editable=False,
                    id='tbl')
            ]),
        ])


@app.callback(Output('tabs-content-example-right', 'children'),
              [Input('tabs-example', 'value'),
               Input('dropdown-selected', 'value')])
def render_content_right(tab, entity):
    print(tab)

    if tab == 'tab-1-example':
        _, related = get_rows(entity, 1)
        rows, articles = get_semmed(entity, related, 1)
        time.sleep(2)
        if len(rows) == 0:
            if entity is None:
                return html.P('')
            else:
                return html.P('No contextual information available for {}'.format(entity))
        else:
            return html.Div([
                html.Div([
                    dt.DataTable(
                        rows=rows,
                        columns=['SUBJECT', 'RELATION', 'OBJECT', 'PMID'],
                        row_selectable=False,
                        filterable=False,
                        sortable=True,
                        selected_row_indices=[],
                        editable=False,
                        id='tbl3')
                ]),
                html.Br(),
                html.Div(get_article_data(articles))
            ], style={'margin-top':30})
    elif tab == 'tab-2-example':
        _, related = get_rows(entity, 2)
        rows, articles = get_semmed(entity, related, 2)
        time.sleep(2)
        if len(rows) == 0:
            if entity is None:
                return html.P('')
            else:
                return html.P('No contextual information available for {}'.format(entity))
        else:
            return html.Div([
                html.Div([
                    dt.DataTable(
                        rows=rows,
                        columns=['SUBJECT', 'RELATION', 'OBJECT', 'PMID'],
                        row_selectable=False,
                        filterable=False,
                        sortable=True,
                        selected_row_indices=[],
                        editable=False,
                        id='tbl4')
                ]),
                html.Br(),
                html.Div(get_article_data(articles))
            ], style={'margin-top':30})




@app.callback(Output('sites', 'children'),
              [Input('tbl', 'id'),
               Input('tbl', 'rows'),
               Input('tbl', 'selected_row_indices')
               ])
def show_sites_1(id, rows, selected_row_indices):
    if len(selected_row_indices) == 0:
        return html.P('Please select a row in main table on the left.')
    else:
        selected_rows = [rows[i] for i in selected_row_indices]
        rows =  get_site_rows(selected_rows)
        return dt.DataTable(rows=rows,
                            columns=['KinaseLabel', 'SubstrateLabel', 'Site', 'Score'],
                            row_selectable=False,
                            filterable=False,
                            sortable=True,
                            selected_row_indices=[],
                            editable=False)




def get_site_rows(selected_rows):
    kinase, substrate = '', ''
    df_aux = results.copy()
    for row in selected_rows:
        for k, v in row.items():
            if k == 'KinaseLabel':
                kinase = v
            if k == 'SubstrateLabel':
                substrate = v
        print(kinase, substrate)
        # if id == 'tbl1':
        df_aux = df_aux.loc[(df_aux['KinaseLabel'] == kinase) & (df_aux['SubstrateLabel'] == substrate)]
        df_aux['Score'] = df_aux['Score'].apply(lambda x: np.round(x, 3))
        rows = df_aux[['KinaseLabel', 'SubstrateLabel', 'Site', 'Score']].to_dict('records')
        return rows




def get_rows(entity, tab):
    if entity is None:
        return [], []
    else:
        if tab==1:
            df1 = results.loc[results['KinaseLabel'] == entity].copy()
        elif tab==2:
            df1 = results.loc[results['SubstrateLabel'] == entity].copy()

        df1['Score'] = df1['Score'].apply(lambda x: np.round(x, 3))
        grouped1 = df1.groupby(['KinaseLabel', 'SubstrateLabel']).agg({'Score': ['min', 'max']})
        grouped1.columns = grouped1.columns.map('_'.join)
        grouped1 = grouped1.sort_values(by='Score_min', ascending=False).reset_index()
        grouped1['Score Range'] = grouped1.apply(lambda row: str(row['Score_min']) + ' - ' + str(row['Score_max']), axis=1)
        grouped1.drop(['Score_min', 'Score_max'], axis=1, inplace=True)
        grouped1 = grouped1.reset_index()
        if len(grouped1) >= 0:
            rows = grouped1.to_dict('records')
            if tab==1:
                related = grouped1.SubstrateLabel.unique().tolist()
            elif tab==2:
                related = grouped1.KinaseLabel.unique().tolist()
            return rows, related
        else:
            return [], []




def get_semmed(entity, related, tab):
    df_subj = semmed.copy()

    if tab == 1:
        df_subj = df_subj[(df_subj.SUBJECT == entity) & (df_subj.OBJECT.isin(related))]
    elif tab==2:
        df_subj = df_subj[(df_subj.OBJECT == entity) & (df_subj.SUBJECT.isin(related))]

    df_subj = df_subj[['SUBJECT', 'RELATION', 'OBJECT', 'PMID']]
    # df_subj['PMID'] = df_subj['PMID'].apply(lambda x: x.split(','))
    # df_subj['PMID'] = df_subj['PMID'].apply(lambda x: len(x))
    # df_subj = df_subj[['SUBJECT', 'RELATION', 'OBJECT', 'PMID_Count']]  # , 'PMID']]
    # items_subj = sorted(df_subj['SUBJECT'].unique().tolist())
    rows = df_subj.to_dict('records')
    articles = df_subj.PMID.tolist()
    return rows, articles

def get_article_data(articles):
    grid_layout = []
    if len(articles) > 0:
        for article in articles:
            print(article)
            pubmedid = article
            url = 'http://www.ncbi.nlm.nih.gov/pubmed/'+str(pubmedid)
            print('url', url)
            lookup = PubMedLookup(url, email)
            try:
                publication = Publication(lookup)
            except:
                continue
            grid_layout.append(grid_row(pubmedid, publication.title, url))
    return grid_layout

def grid_row(pubmedid, title, url):
    return html.Div([
        html.P('\n\nArticle {}'.format(pubmedid), style={'font-weight': 'bold'}),
        html.A(title, href=url, target="_blank")
    ], style={'padding-top': '0.9em', 'padding-bottom': '0.4em'})

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=True, host = '0.0.0.0', port = 8080)
