
import pandas as pd 
from dash import Dash, html, dcc, Input, Output,dash_table,State
from django_plotly_dash import DjangoDash
import numpy as np 

import plotly.graph_objects as go 
import plotly.express as px

from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv
from dotenv import dotenv_values
from src.app_dash.module.templateGraphPlotly import *
from src.app_dash.module.connectionDB import *

import textwrap
load_dotenv()
config = dotenv_values(".env")


#### TEMPLATES ####
color_kvk ="#ec4899"
color_background="#e2e8f0"
color_background_bg_plot = "rgba(255,255,255,1)"
color_background_plot = "#ffffff"
color_text  = "#475569"
color_plot = "#475569"

color =['#3775b7',
 '#5ac6f8',
 '#d26047',
 '#cd5138',
 "#65a30d",
 '#d26047',
 '#cd5138',
 '#d26047',
 '#cd5138',
 '#f3b33e',
 '#be842d']

def get_templates(fig):
    style_graph=TemplateGraphPlotly(fig=fig,
    family_font = "Arial Black",tickangle = 0,paper_bgcolor = color_background_bg_plot ,
    plot_bg_color=color_background_plot,color = color_text,size=12,linewidth=2,linecolor = "black",color_plot=color_plot)
    fig.update_annotations(font_size=12)
    style_graph.get_template_axes()
    style_graph.get_template_layout()
    fig.update_traces(line=dict(width=4))
    fig.update_yaxes(title="")
    fig.update_xaxes(title="")


    fig.update_xaxes(tickangle=45)
    return style_graph

def get_templates_histo(fig):
    style_graph=TemplateGraphPlotly(fig=fig,
    family_font = "Arial Black",tickangle = 0,paper_bgcolor = color_background_bg_plot ,
    plot_bg_color=color_background_plot,color = color_text,size=12,linewidth=2,linecolor = "black",color_plot=color_plot)
    fig.update_annotations(font_size=12)
    style_graph.get_template_axes()
    style_graph.get_template_layout()
    
    fig.update_yaxes(title="")
    fig.update_xaxes(title="")


    fig.update_xaxes(tickangle=45)
    return style_graph


external_stylesheets = ['https://cdn.jsdelivr.net/npm/tailwindcss/dist/tailwind.min.css',
                        'https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css'
                    ]
className={
    "graph":"shadow-lg shadow-indigo-500 rounded-xl bg-white my-1 p-1 md:my-2 md:p-2 mx-1  w-full xl:w-6/12 w-max-full",
    "graph-1/3":"shadow-lg shadow-indigo-500 rounded-xl bg-white my-1 p-1 md:my-2 md:p-2 mx-1  w-full lg:w-4/12",
    "graph-full":"shadow-lg shadow-indigo-500 rounded-xl bg-white sm:m-1 sm:p-1 md:m-2 md:p-2 w-full",
    "graph-xl":"shadow-lg shadow-indigo-500 rounded-xl bg-white sm:m-1 sm:p-1 md:m-2 md:p-2 w-full",
    "tab_class":"bg-blue-300 border-t-0 p-3 m-2 font-semibold border-0",
    "tab_selected":"bg-white p-3 m-2 font-semibold border-0",
}

password = os.getenv("password")
user = os.getenv("user")
host = os.getenv("host")
port = os.getenv("port")
db = os.getenv("db")
connection =ConnectionMySQL(host,port,user,password,db)
db_=connection.get_connection()



app = DjangoDash(name ='app_imdb',external_stylesheets=external_stylesheets)

df = pd.read_sql_query("SELECT * FROM imdb WHERE  decade > 0 AND genre != -9999 AND runtimeminutes > '0' AND averagerating >0 ",db_)
df=df.replace(",",".",regex=True)
df=df.astype({"averagerating":"float","numvotes":"float","startyear":"int16","decade":"int16","runtimeminutes":"int16"})

genres = df.genre.unique()

df_actor = pd.read_sql_query("SELECT * FROM actor WHERE nb_film > 10 AND age > 0 AND age_in_movie > 0",db_)

df_actor=df_actor.rename(columns={"genres":"genre"})
df_actor=df_actor.replace(",",".",regex=True)
df_actor.decade=df_actor.decade.astype("float")
df_actor=df_actor.astype({"decade":"int16","age":"float","nb_film":"float","film_per_decade":"float","age_in_movie":"float","startYear":"int"})

df_producer = pd.read_sql_query("SELECT * FROM producer WHERE nb_film > 10 AND age > 0",db_)
df_producer=df_producer.replace(",",".",regex=True)
df_producer.decade=df_producer.decade.astype("float")
df_producer=df_producer.astype({"decade":"int16","age":"float","nb_film":"float","film_per_decade":"float","age_in_movie":"float","startYear":"int"})


connection.get_sql_engine().dispose()


def filter():
            
    content_div=html.Div(id="filter",children=[],className="flex flex-col p-2 m-2 xl:grid xl:grid-cols-12 gap-4")
    liste_content={
        "Genre":{
            "id":"genre",
            "option":[{"label":genre,"value":genre} for genre in sorted(genres)],
            "multi":True,
            "value":None
        },
        "note":{
            "id":"note",
            "option":[{"label":note,"value":note} for note in range(1,11)],
            "multi":True,
            "value":None
        },
        "Acteur/Actrice":{
            "id":"actor",
            "option":[{"label":row["primaryName"],"value":row["Nconst"]} for index,row in df_actor.loc[:,["Nconst","primaryName"]].drop_duplicates(subset="Nconst",keep="last").sort_values(by="primaryName").iterrows()],
            "multi":True,
            "value":None
        },
        "Producteur":
        {
            "id":"producer",
            "option":[{"label":row["primaryName"],"value":row["Nconst"]} for index,row in df_producer.loc[:,["Nconst","primaryName"]].drop_duplicates(subset="Nconst",keep="last").sort_values(by="primaryName").iterrows()],
            "multi":True,
            "value":None
        },
        "Décennie":{
            "id":"decade",
            "option":[{"label":decade,"value":decade} for decade in sorted(df.decade.unique())],
            "multi":True,
            "value":None
        },
        "Choix de visualisation":{
            "id":"see_value",
            "option":[{"label":val,"value":val} for val in sorted(["genre","decade"])],
            "multi":True,
            "value":"genre"

        }
    }

    for name,value in liste_content.items():
         content_div.children.append(
             html.Div(
                 children=[
                        html.H3(children=name,className="font-bold text-xl p-2 m-2 text-gray-700"),
                        dcc.Dropdown(
                            id=value.get("id"),
                            options=value.get("option"),
                            multi=value.get("multi"),
                            value=value.get("value"),
                            className="p-2 m-2 "
                        )
                 ],className="bg-white col-span-4 rounded-lg")
             )
    return content_div
        



        
def get_filter(df,genre,decade,actor=None,producer=None,averagerating=None,numvotes=None):
    dict_filter={ "genre":genre,"decade":decade,"averagerating":averagerating}
    df_copy=df.copy()
    for col,value in dict_filter.items():
        if value is not None and len(value) >0:
        
            if col == "averagerating":
    
                df_copy[col]=df_copy[col]//1
                df_copy[col]=df_copy[col].astype("int64")
                df_copy=df_copy[df_copy[col].isin(value)]
      
            else:
                df_copy=df_copy[df_copy[col].isin(value)]
        else:
            pass
    if (producer is not  None and len(producer) >0) and (actor is not None and len(actor)>0):

        df_copy=(df_copy.
             merge(df_actor.loc[:,["tconst","primaryName","Nconst","sexe"]][df_actor.Nconst.isin(actor)],how="inner",left_on="tconst",right_on="tconst")
             .merge(df_producer.loc[:,["tconst","primaryName","Nconst"]][df_producer.Nconst.isin(producer)],how="inner",left_on="tconst",right_on="tconst")
        )
    
    elif actor is not None and len(actor)>0:
        df_copy=df_copy.merge(df_actor.loc[:,["tconst","primaryName","Nconst","age","sexe"]][df_actor.Nconst.isin(actor)],how="inner",left_on="tconst",right_on="tconst")
    elif producer is not  None and len(producer) >0:
        df_copy=df_copy.merge(df_producer.loc[:,["tconst","primaryName","Nconst","age"]][df_producer.Nconst.isin(producer)],how="inner",left_on="tconst",right_on="tconst")
   # df_copy.genres=df_copy.genres.replace(".",",",regex=True)
    return df_copy

@app.callback(Output("key_number","children"),[Input("genre","value"),Input("decade","value"),Input("actor","value"),Input("producer","value"),Input("note","value")])
def key_number(genre,decade,actor,producer,note):
    df_=get_filter(df,genre,decade,actor,producer,averagerating=note)

    nb_ = len(df_)
    runtime = df_.runtimeminutes.mean()
    note_mean=df_.averagerating.mean()

    if actor is not None and len(actor) > 0 :
      
        actor = df_actor[df_actor.Nconst.isin(actor)].drop_duplicates("Nconst").primaryName
        actor = ",".join(actor)
        age = (max(df_.age))
    
    elif producer is not None and len(producer) > 0 :
 
        actor = df_producer[df_producer.Nconst.isin(producer)].drop_duplicates("Nconst").primaryName
  
        actor = ",".join(actor)
        age = (max(df_.age))
       
    else:
        actor=""
        age=''

    content_div = html.Div(children=[],className="flex flex-col xl:grid xl:grid-cols-12 gap-6 p-2 m-2")
    dict_content_div={
        "Nombre de films":'{:,.0f}'.format(nb_),
        f"Note moyenne {actor}":round( note_mean,2),
        "Temps moyen":round(runtime),
        "Age":age
    }

    for title,value in dict_content_div.items():
        print(title,value)
        content_div.children.append(
            html.Div(
                children=[
                    html.H4(title,className="font-bold p-2 m-2 text-2xl text-gray-700"),
                    html.P(value,className="font-medium p-2 m-2 text-xl text-gray-700")
                ],className="col-span-3 bg-gray-50 rounded-lg flex flex-row  justify-center items-center"
            )
        )
    
    return content_div

@app.callback(Output("count_movie","children"),[Input("genre","value"),
                                                Input("decade","value"),Input("note","value"),Input("actor","value"),Input('producer',"value"),Input("see_value","value")])
def get_count_movies(genre,decade,note,actor,producer,see_value):
    df_graph=get_filter(df,genre,decade,actor,producer,averagerating=note).sort_values(by="genre")

    if see_value == "genre":
        fig = px.histogram(data_frame =df_graph,x="genre",color_discrete_sequence=["#38bdf8"])
    else: 
        
        fig = px.histogram(data_frame =df_graph,x="decade",color_discrete_sequence=["#38bdf8"])
        fig.update_layout(xaxis=dict(dtick=10, tickangle=45))


    fig.update_xaxes(tickangle=(360-45))
    if genre is not None:
        fig.update_layout(title=f"Total contenus par {see_value} {','.join(genre)}")
    else:
        fig.update_layout(title=f"Total contenus par {see_value}")
    get_templates_histo(fig)

    return html.Div(id="",
                    children=[
                        dcc.Graph(id="contenu",figure=fig)
                    ])


@app.callback(Output("mean_note","children"),[Input("genre","value"),Input("decade","value"),Input("note","value"),Input("actor","value"),Input("producer","value"),Input("see_value","value")])
def get_genre(genre,decade,note,actor,producer,see_value):

    df_graph=get_filter(df,genre,decade,actor,producer,averagerating=note)

    if decade is not None and len(decade) >0:
        df_graph = df_graph.groupby(['decade','genre']).agg("mean",numeric_only=True).reset_index()
    else:
        if see_value=="decade":
            df_graph = df_graph.groupby(['decade']).agg("mean",numeric_only=True).reset_index()
        else:
            df_graph = df_graph.groupby('genre').agg("mean",numeric_only=True).reset_index()




    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if see_value == "genre":
    
        fig.add_trace(go.Bar(x=df_graph.genre,y=df_graph.averagerating,marker_color="#38bdf8",name="Note "))
        fig.add_trace(go.Scatter(x=df_graph.genre,y=df_graph.numvotes,marker_color="#f87171",line=dict(width=5),name="Votes "),secondary_y=True)
    
    else:
         df_graph = get_filter(df,genre,decade,actor,producer).groupby(['decade']).agg("mean",numeric_only=True).reset_index()
         fig.add_trace(go.Bar(x=df_graph.decade,y=df_graph.averagerating,marker_color="#38bdf8",name="Note "))
         fig.add_trace(go.Scatter(x=df_graph.decade,y=df_graph.numvotes,marker_color="#f87171",line=dict(width=5),name="Votes "),secondary_y=True)

    fig.update_xaxes(tickangle=(360-45))
    title="Note et vote moyen par "
    if genre is not None:
        fig.update_layout(title=f"{title} {see_value} {','.join(genre)}")
    else:
            fig.update_layout(title=f"{title} {see_value}")

    if see_value == "decade":
        fig.update_layout(xaxis=dict(dtick=10, tickangle=45))     

    fig.update_layout(hovermode="x unified")
   
    get_templates_histo(fig)
    return html.Div(id="",
                    children=[
                        dcc.Graph(id="note_mean",figure=fig)
                    ])


@app.callback(Output("get_time","children"),[Input("genre","value"),Input("decade","value"),Input("note","value"),Input("actor","value"),Input("producer","value"),Input("see_value","value")])
def get_time_genre(genre,decade,note,actor,producer,see_value):

    df_graph = get_filter(df,genre,decade,actor,producer,averagerating=note)

    if decade is not None and len(decade) >0:
        df_graph = df_graph.groupby(['decade','genre']).agg("mean",numeric_only=True).reset_index()
    else:
        df_graph = df_graph.groupby('genre').agg("mean",numeric_only=True).reset_index()


    if see_value == "genre":
        fig = px.bar(data_frame =df_graph,x="genre",y="runtimeminutes",color_discrete_sequence=["#38bdf8"])
    else: 
        df_graph = get_filter(df,genre,decade,actor,producer).groupby(['decade']).agg("mean",numeric_only=True).reset_index()
        
        fig = px.bar(data_frame =df_graph,x="decade",y="runtimeminutes",color_discrete_sequence=["#38bdf8"])
        if actor is not None and len(actor)>0:
            fig.update_layout(xaxis=dict(dtick=10, tickangle=45))
        else:
            fig.update_layout(xaxis=dict(dtick=10, tickangle=45))

        


    fig.update_xaxes(tickangle=(360-45))
    title="Temps moyen par "
    if genre is not None:
        fig.update_layout(title=f"{title} {see_value} {','.join(genre)}")
    else:
            fig.update_layout(title=f"{title} {see_value}")
    get_templates_histo(fig)

    return html.Div(id="",
                    children=[
                        dcc.Graph(id="note_mean",figure=fig)
                    ])

@app.callback(Output("age_mean","children"),[Input("genre","value"),Input("decade","value"),Input("note","value"),Input("actor","value"),Input("see_value","value")])
def get_age_movie(genre,decade,note,actor,see_value):
    df_actor_copy = get_filter(df_actor,genre,decade)
    df_=get_filter(df,genre,decade,averagerating=note)
    df_=df_.loc[:,['tconst','genre',"decade","startyear","averagerating"]]
    df_actor_copy=df_actor_copy.loc[:,["tconst","nb_film","primaryName","sexe","age","age_in_movie","film_per_decade"]]
    df_copy=df_.merge(df_actor_copy,how="inner",left_on="tconst",right_on="tconst")
    df_copy=df_copy[df_copy.genre != "News"].sort_values(by="startyear")
    
    color=["#38bdf8","#f87171"]
    fig = go.Figure()

    

    if decade is not None and len(decade) >0:
        df_graph = df_copy.groupby(["sexe",'decade','genre']).agg("mean",numeric_only=True).reset_index()
    else:
        df_graph = df_copy.groupby(["sexe","genre"]).agg("mean",numeric_only=True).reset_index()

    if see_value == "genre":
        for index,sexe in enumerate(df_copy.sexe.unique()):
            df_=df_graph[df_graph.sexe==sexe].sort_values(by="genre")
         
            fig.add_trace(go.Bar(x=df_.genre,y=df_.age_in_movie,marker_color=color[index],name="Homme" if sexe == 0 else "Femme"))
    else: 
        df_graph = df_copy.groupby(['sexe','decade']).agg("mean",numeric_only=True).reset_index()

        for index,sexe in enumerate(df_copy.sexe.unique()):
            df_=df_graph[df_graph.sexe==sexe].sort_values(by="decade")
            fig.add_trace(go.Bar(x=df_.decade,y=df_.age_in_movie,marker_color=color[index],name="Homme" if sexe == 0 else "Femme"))
        fig.update_layout(xaxis=dict(dtick=10, tickangle=45))

             
        

    title="Age moyen des Acteurs et Actrices par "
    if genre is not None:
        fig.update_layout(title=f"{title} {see_value} {','.join(genre)}")
    else:
            fig.update_layout(title=f"{title} {see_value}")
    get_templates_histo(fig)
    return html.Div(id="",
                    children=[
                        dcc.Graph(id="distribution",figure=fig)
                    ])

@app.callback(Output("movie_per","children"),[Input("genre","value"),Input("decade","value"),Input("note","value"),Input("actor","value"),Input("producer","value")])
def film_per_act(genre,decade,note,actor,producer):
    df_ = get_filter(df,genre,decade,actor,producer,averagerating=note)
    if actor is  None or len(actor) == 0:
        df_=df_.merge(df_actor.loc[:,["tconst","primaryName","sexe"]],how="inner",left_on="tconst",right_on="tconst")
   
        
    df_ = df_.groupby(["primaryName","sexe"])["tconst"].count().reset_index()
    df_.tconst=df_.tconst.astype("int64")
    df_=df_.sort_values(by="tconst",ascending=False).head(30)
    
    df_.sexe=df_.sexe.apply(lambda x:"Homme" if x ==0 else "Femme")
    color=["#38bdf8","#f87171"]

    fig = px.bar(data_frame= df_,y="tconst",x="primaryName",color="sexe",color_discrete_map = {"Homme": color[0], "Femme": color[1]})
    get_templates_histo(fig)
    fig.update_layout(
    xaxis={"categoryorder": "array", "categoryarray": df_["primaryName"]})
    fig.update_layout(title="Nombre de films par acteurs ou actrices",hovermode="closest")
    return html.Div(id="",
                    children=[
                        dcc.Graph(id="movie_per_actor_actress",figure=fig)
                    ])

@app.callback(Output("table_movie","children"),[Input("genre","value"),Input("note","value"),Input("actor","value"),Input("producer","value"),Input("decade","value")])
def get_table(genre,note,actor,producer,decade):
    cols =["recommandation","primarytitle","startyear","decade","runtimeminutes","genres","averagerating","numvotes"]    
    df_ = get_filter(df,genre,decade,actor,producer,averagerating=note)
       # return f'<a href="https://crossflix.kevinlamarque.fr/movie/{tconst}" target="_blank">Avoir une recommandation</a>'
    df_['tconst'] = df_['tconst'].apply(lambda x:f"[Avoir une recommandation](https://crossflix.kevinlamarque.fr/movie/{x})")
    df_=df_.sort_values(by=["decade","numvotes","averagerating"],ascending=[False,False,False])
    df_=df_.rename(columns={"tconst":"recommandation"})
    table =  dash_table.DataTable(
        id='table',
                columns=[{'name': col, 'id': col, 'type': 'text', 'presentation': 'markdown'} if col == 'recommandation'
                 else {'name': col, 'id': col} for col in cols],
        data=df_.to_dict('records'),
        page_action='native',
        page_size=25,
        sort_action="native",


    style_cell={
    'color': 'black',
    'backgroundColor': 'white',
    'textAlign': 'center',
    "fontSize": "1em",
    "fontWeight": "500",
    "fontFamily": "Arial",
    "border":"none",
},
style_data={
    "padding":"0.5em",
    "border-bottom":"1px solid black"
},
    style_header={
    'backgroundColor': '#38bdf8',
    'color': '#f8fafc',
    'fontWeight': 'bold',
    'fontSize':'1em',
    'padding':"0.75em",
    "margin":"0.25em"
})
    return table

app.layout=html.Div([

        html.Div(id="filter",children=filter()),
    
        html.Div(id="key_number",children=[]),
        html.Div(id="graph",children=[
            html.Div(id="count_movie",children=[],className="col-span-4 p-5 bg-white rounded-lg"),
            html.Div(id="mean_note",children=[],className="col-span-4 p-5 bg-white rounded-lg"),
            html.Div(id="get_time",children=[],className="col-span-4 p-5 bg-white rounded-lg"),
            html.Div(id="age_mean",children=[],className="col-span-6 p-5 bg-white rounded-lg"),
            html.Div(id="movie_per",children=[],className="col-span-6 p-5 bg-white rounded-lg"),
            html.Div(id='table_movie',children=[],className="col-span-12 p-5 bg-white rounded-lg"),

        ],className="flex flex-col xl:grid xl:grid-cols-12 gap-6 p-2 m-2 "),



      
    
],className="bg-gray-800 h-screen m-0 p-5")