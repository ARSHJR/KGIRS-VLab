"""Dynamic editable in-memory knowledge graph lab."""
from datetime import datetime
import math
import random
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

TITLE="Dynamic Knowledge Graph Exploration Lab"
START_NODES=[{"name":"Aarush","type":"Person"},{"name":"Harshita","type":"Person"},{"name":"Nidhish","type":"Person"},{"name":"test","type":"Person"},{"name":"Jass","type":"Person"},{"name":"Yahya","type":"Person"},{"name":"Graph Queries","type":"Topic"}]
START_EDGES=[("Aarush","KNOWS","Harshita"),("Aarush","COLLABORATES_WITH","Nidhish"),("Harshita","KNOWS","test"),("Nidhish","KNOWS","Jass"),("test","LEARNS","Graph Queries"),("Jass","USES","Graph Queries"),("Yahya","MENTORS","Aarush"),("Yahya","KNOWS","Jass")]
BANK=[("What does a node represent?",["An entity","A chart colour","A file extension"],0),("What does a directed edge represent?",["A typed connection","A duplicate node","A page title"],0),("Why remove edges when removing a node?",["To prevent invalid connections","To increase page size","To hide labels"],0),("What is a one-hop connection?",["A direct neighbour","A deleted node","A graph title"],0),("What is a two-hop path?",["A connection through an intermediate node","A single node","An empty graph"],0),("Which traversal explores one path deeply?",["Depth-first search","Sorting","Tokenization"],0),("Why use node types?",["To classify entities","To draw more lines","To erase properties"],0),("What is an outgoing edge?",["An edge from the selected node","An edge with no label","An incoming edge"],0),("What is a path?",["A sequence of connected nodes","Only a single node","A node property"],0)]
N=5
def names():return [x["name"] for x in st.session_state.nodes]
def graph():
 names_=names(); size=max(len(names_),1);pos={n:(math.cos(2*math.pi*i/size),math.sin(2*math.pi*i/size)) for i,n in enumerate(names_)};f=go.Figure()
 for a,r,b in st.session_state.edges:
  x,y=pos[a];u,v=pos[b];f.add_trace(go.Scatter(x=[x,u],y=[y,v],mode="lines",line=dict(color="#94a3b8",width=2.5),showlegend=False));f.add_annotation(x=u,y=v,ax=x,ay=y,xref="x",yref="y",axref="x",ayref="y",text="",showarrow=True,arrowhead=3,arrowsize=1.2,arrowwidth=2.5,arrowcolor="#94a3b8");f.add_annotation(x=(x+u)/2,y=(y+v)/2,text=r,showarrow=False,font=dict(size=10,color="#e2e8f0"),bgcolor="#1f2937",borderpad=2)
 colours={"Person":"#2563eb","Topic":"#059669","Organization":"#7c3aed","Other":"#ea580c"}
 for x in st.session_state.nodes:
  n,t=x["name"],x["type"];a,b=pos[n];f.add_trace(go.Scatter(x=[a],y=[b],mode="markers+text",text=[n],textposition="top center",textfont=dict(color="#f8fafc",size=13),marker=dict(size=28,color=colours.get(t,colours["Other"]),line=dict(color="#f8fafc",width=1)),name=t))
 f.update_layout(title=f"Editable Graph: {len(names_)} nodes, {len(st.session_state.edges)} relationships",height=500,xaxis=dict(visible=False),yaxis=dict(visible=False),plot_bgcolor="#111827",paper_bgcolor="#111827",font=dict(color="#f8fafc"),legend=dict(orientation="h",y=-.12));return f
def direct(n):
 rows=[]
 for a,r,b in st.session_state.edges:
  if a==n:rows.append(("Outgoing",r,b))
  elif b==n:rows.append(("Incoming",r,a))
 return pd.DataFrame(rows,columns=["Direction","Relationship","Connected node"])
def paths(n):
 return pd.DataFrame([(n,m,e,r1,r2) for a,r1,m in st.session_state.edges if a==n for s,r2,e in st.session_state.edges if s==m],columns=["Start","Via","Destination","First relationship","Second relationship"])
def theory():
 st.header("Theory");st.markdown("A knowledge graph represents entities as nodes and meaningful connections as directed relationships. People, topics, and organizations can be nodes; labels such as KNOWS, USES, and MENTORS describe relationships.")
 st.subheader("Dynamic Graph Model");st.markdown("This lab stores graph data in Streamlit session memory. You can add nodes, add relationships, and remove them during execution. Removing a node also removes all relationships connected to it, keeping the graph consistent.")
 st.subheader("Graph Exploration");st.markdown("A direct search lists incoming and outgoing relationships for a selected node. A two-hop search follows one outgoing relationship to an intermediate node and one more relationship to a destination. This follows a depth-limited traversal idea.")
 st.info("Graph exploration provides context by showing both entities and their direct or indirect connections.")
 st.subheader("Procedure")
 for i,x in enumerate(["Inspect the initial graph.","Add a node and relationship.","Select any node and inspect direct connections.","Inspect two-hop paths.","Record trials, complete the quiz, and download the report."],1):st.write(f"{i}. {x}")
def editor():
 st.header("Graph Editor");left,right=st.columns(2)
 with left:
  with st.form("addnode"):
   n=st.text_input("Node name").strip();t=st.selectbox("Node type",["Person","Topic","Organization","Other"])
   if st.form_submit_button("Add Node",type="primary"):
    if not n:st.error("Enter a node name.")
    elif n in names():st.error("That node already exists.")
    else:st.session_state.nodes.append({"name":n,"type":t});st.success(f"Added {n}.")
 with right:
  n=st.selectbox("Choose node to remove",names())
  if st.button("Remove Selected Node"):
   st.session_state.nodes=[x for x in st.session_state.nodes if x["name"]!=n];st.session_state.edges=[x for x in st.session_state.edges if n not in (x[0],x[2])];st.rerun()
 st.divider();nms=names()
 if len(nms)>1:
  left,right=st.columns(2)
  with left:
   with st.form("addedge"):
    a=st.selectbox("Source node",nms);r=st.text_input("Relationship type",placeholder="Example: KNOWS").strip().upper();b=st.selectbox("Target node",nms)
    if st.form_submit_button("Add Relationship",type="primary"):
     if a==b or not r:st.error("Use different nodes and enter a relationship.")
     elif (a,r,b) in st.session_state.edges:st.error("That relationship already exists.")
     else:st.session_state.edges.append((a,r,b));st.success("Relationship added.")
  with right:
   labels=[f"{a} --{r}--> {b}" for a,r,b in st.session_state.edges];chosen=st.selectbox("Relationship to remove",labels)
   if st.button("Remove Selected Relationship"):st.session_state.edges.pop(labels.index(chosen));st.rerun()
 st.subheader("Current Nodes");st.dataframe(pd.DataFrame(st.session_state.nodes),hide_index=True,use_container_width=True)
def explore():
 st.header("Dynamic Graph Exploration");st.info("This visualization updates after every graph edit.");st.plotly_chart(graph(),use_container_width=True);n=st.selectbox("Select a node to explore",names())
 patterns={"All nodes":"MATCH (n)\nRETURN n.name, labels(n);","All relationships":"MATCH (a)-[r]->(b)\nRETURN a.name, type(r), b.name;",f"Direct connections of {n}":f"MATCH (a {{name: '{n}'}})-[r]-(b)\nRETURN type(r), b.name;",f"Two-hop paths from {n}":f"MATCH (a {{name: '{n}'}})-[r1]->(m)-[r2]->(end)\nRETURN a.name, m.name, end.name;"}
 selected_pattern=st.selectbox("Graph Query Pattern",list(patterns))
 st.caption("Reference syntax for the selected exploration pattern. The result tables below are evaluated against the editable in-memory graph.")
 st.code(patterns[selected_pattern])
 d=direct(n);p=paths(n);a,b=st.columns(2)
 with a:st.subheader("Direct Connections");st.metric("Found",len(d));st.dataframe(d,hide_index=True,use_container_width=True)
 with b:st.subheader("Two-Hop Paths");st.metric("Found",len(p));st.dataframe(p,hide_index=True,use_container_width=True)
 if st.button("Record Exploration Trial",type="primary"):st.session_state.trials.append({"Trial #":len(st.session_state.trials)+1,"Selected node":n,"Direct connections":len(d),"Two-hop paths":len(p),"Timestamp":datetime.now().strftime("%H:%M:%S")});st.success("Trial recorded.")
 if st.session_state.trials:st.dataframe(pd.DataFrame(st.session_state.trials),hide_index=True,use_container_width=True)
def simulation():
 st.header("Simulation")
 st.caption("Build the graph, then explore the updated nodes and paths below.")
 editor()
 st.divider()
 explore()
def quiz():
 st.header("Quiz");st.caption("Five questions are randomly sampled from the question bank.")
 with st.form("quiz"):
  answers=[st.radio(q,o,key=f"q{i}") for i,(q,o,a) in enumerate(st.session_state.questions)];done=st.form_submit_button("Grade Quiz",type="primary")
 if done:st.session_state.score=sum(x==o[a] for x,(_,o,a) in zip(answers,st.session_state.questions));st.success(f"Score: {st.session_state.score}/{N}")
def report():
 st.header("Report Generation");a,b=st.columns(2);name=a.text_input("Student Name");roll=b.text_input("Roll Number",value="46");notes=st.text_area("Observations","The graph was modified dynamically and explored through direct and two-hop connections.");trials=pd.DataFrame(st.session_state.trials)
 text=f"{TITLE}\n\nStudent: {name}\nRoll: {roll}\nDate: {datetime.now().date()}\nGraph size: {len(st.session_state.nodes)} nodes, {len(st.session_state.edges)} relationships\nQuiz score: {st.session_state.score}/{N}\n\nTrials\n"+("No trials recorded." if trials.empty else trials.to_string(index=False))+f"\n\nObservations\n{notes}"
 st.download_button("Download Lab Report",text,"dynamic_graph_lab_report.txt","text/plain",type="primary")
def main():
 st.set_page_config(page_title=TITLE,page_icon="G",layout="wide")
 if "nodes" not in st.session_state:st.session_state.nodes=[x.copy() for x in START_NODES]
 if "edges" not in st.session_state:st.session_state.edges=START_EDGES.copy()
 if "trials" not in st.session_state:st.session_state.trials=[]
 if "score" not in st.session_state:st.session_state.score=0
 if "questions" not in st.session_state:
  st.session_state.questions=[]
  for q,o,a in random.sample(BANK,N):
   choices=o.copy();random.shuffle(choices);st.session_state.questions.append((q,choices,choices.index(o[a])))
 st.title(TITLE);page=st.sidebar.radio("Lab Navigator",["Theory","Simulation","Quiz","Report Generation"]);{"Theory":theory,"Simulation":simulation,"Quiz":quiz,"Report Generation":report}[page]()
if __name__=="__main__":main()
