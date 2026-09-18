"""Streamlit virtual lab: Query Knowledge Graphs using Cypher. Neo4j is not required."""
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
try:
 from fpdf import FPDF
 PDF_READY=True
except ImportError:
 PDF_READY=False

TITLE="Query Knowledge Graphs using Cypher"
NODES=[("Aarush","Person"),("Harshita","Person"),("Nidhish","Person"),("goat","Person"),("Jass","Person"),("Yahya","Person"),("Cypher","Topic")]
EDGES=[("Aarush","KNOWS","Harshita"),("Aarush","COLLABORATES_WITH","Nidhish"),("Harshita","KNOWS","goat"),("Nidhish","KNOWS","Jass"),("goat","LEARNS","Cypher"),("Jass","USES","Cypher"),("Yahya","MENTORS","Aarush"),("Yahya","KNOWS","Jass")]
QUERIES={"All nodes":("MATCH (n) RETURN n.name, labels(n);","Retrieve all entities.","nodes"),"All relationships":("MATCH (a)-[r]->(b) RETURN a.name, type(r), b.name;","Retrieve directed graph relationships.","edges"),"Aarush's connections":("MATCH (a:Person {name: 'Aarush'})-[r]->(b) RETURN type(r), b.name;","One-hop retrieval.","aarush"),"Two-hop paths":("MATCH (a:Person {name: 'Aarush'})-[r1]->(m)-[r2]->(end) RETURN a,m,end;","Retrieve indirect connections.","twohop"),"Paths to Cypher":("MATCH p=(start)-[*1..3]->(t:Topic {name:'Cypher'}) RETURN start,t,length(p);","Variable-length multi-hop traversal.","paths")}
QUIZ=[("Which clause specifies a graph pattern?",["MATCH","RETURN","WHERE"],0),("What is (p:Person)?",["A Person node variable","A relationship","A property"],0),("What does type(r) return?",["Relationship type","Node label","Path length"],0),("Why use multi-hop queries?",["Find indirect connections","Delete nodes","Create labels"],0),("What does [*1..3] mean?",["One to three hops","Three nodes","All labels"],0)]
def run(kind):
 if kind=="nodes":return pd.DataFrame(NODES,columns=["Name","Label"])
 if kind=="edges":return pd.DataFrame(EDGES,columns=["Source","Relationship","Target"])
 if kind=="aarush":return pd.DataFrame([(r,b) for a,r,b in EDGES if a=="Aarush"],columns=["Relationship","Connected node"])
 if kind=="twohop":return pd.DataFrame([(a,m,e,r1,r2) for a,r1,m in EDGES if a=="Aarush" for s,r2,e in EDGES if s==m],columns=["Start","Via","End","R1","R2"])
 out=[]
 def visit(n,path):
  if len(path)>4:return
  if n=="Cypher" and len(path)>1:out.append((path[0],n,len(path)-1," -> ".join(path)))
  for a,r,b in EDGES:
   if a==n and b not in path:visit(b,path+[b])
 for n,l in NODES:visit(n,[n])
 return pd.DataFrame(out,columns=["Start","Destination","Hops","Path"]).drop_duplicates()
def visual():
 pos={"Aarush":(0,2),"Harshita":(2,3),"Nidhish":(2,1),"goat":(4,3),"Jass":(4,1),"Yahya":(-1,0),"Cypher":(6,2)};f=go.Figure()
 for a,r,b in EDGES:
  x,y=pos[a];u,v=pos[b];f.add_trace(go.Scatter(x=[x,u],y=[y,v],mode="lines",line=dict(color="#94a3b8"),showlegend=False));f.add_annotation(x=(x+u)/2,y=(y+v)/2,text=r,showarrow=False,font=dict(size=9))
 for n,l in NODES:
  x,y=pos[n];f.add_trace(go.Scatter(x=[x],y=[y],mode="markers+text",text=[n],textposition="top center",marker=dict(size=28),name=l))
 f.update_layout(title="In-memory graph: 6 nodes, 8 relationships",height=450,xaxis=dict(visible=False),yaxis=dict(visible=False));return f
def report(name,roll,trials,score,notes):
 return f"{TITLE}\n\nStudent: {name}\nRoll: {roll}\nDate: {datetime.now().date()}\n\nRecorded Trials\n"+("No trials recorded." if trials.empty else "\n".join(f"{x['Trial #']}. {x['Query']} - {x['Rows']} rows" for _,x in trials.iterrows()))+f"\n\nQuiz Score: {score}/{len(QUIZ)}\n\nObservations\n{notes}"
def pdf_report(name,roll,trials,score,notes):
 p=FPDF();p.set_auto_page_break(auto=True,margin=15);p.add_page()
 p.set_font("Helvetica","B",16);p.cell(0,10,TITLE,new_x="LMARGIN",new_y="NEXT")
 p.set_font("Helvetica","",10);p.cell(0,7,f"Student: {name or 'N/A'} | Roll: {roll or 'N/A'} | Date: {datetime.now().date()}",new_x="LMARGIN",new_y="NEXT")
 for heading,body in [("Learning Objectives","- Retrieve nodes and properties.\n- Retrieve relationships.\n- Explore one-hop and multi-hop paths."),("Recorded Query Trials","No trials recorded." if trials.empty else "\n".join(f"{x['Trial #']}. {x['Query']} - {x['Rows']} rows" for _,x in trials.iterrows())),("Assessment and Observations",f"Quiz score: {score}/{len(QUIZ)}\n\n{notes}")]:
  p.ln(4);p.set_font("Helvetica","B",12);p.cell(0,8,heading,new_x="LMARGIN",new_y="NEXT");p.set_font("Helvetica","",9);p.multi_cell(0,5,body)
 return bytes(p.output())
def theory():
 st.header("Theory");st.markdown("Knowledge graphs represent entities as nodes and facts as typed relationships. Cypher is a declarative query language: describe the desired pattern with MATCH, then select fields with RETURN. This lab uses a small graph featuring Aarush, Harshita, Nidhish, goat, Jass, and Yahya, so Neo4j is not expected.")
 st.subheader("Objectives")
 for item in ["Retrieve nodes and properties.","Retrieve relationships.","Explore one-hop connections.","Discover multi-hop paths."]:
  st.write("- "+item)
 st.subheader("Procedure")
 for index,item in enumerate(["Inspect the graph.","Run each Cypher pattern.","Record at least three trials.","Take the quiz and export the report."],1):
  st.write(f"{index}. {item}")
def simulation():
 st.header("Interactive Cypher Query Sandbox");st.info("Cypher queries are evaluated against the built-in graph; no database server is needed.");st.plotly_chart(visual(),use_container_width=True);q=st.selectbox("Choose a query",list(QUERIES));code,why,kind=QUERIES[q];st.caption(why);st.code(code,language="cypher")
 if st.button("Run Query",type="primary"):st.session_state.active=q
 active=st.session_state.get("active",q);data=run(QUERIES[active][2]);st.metric("Rows returned",len(data));st.dataframe(data,use_container_width=True,hide_index=True)
 if st.button("Record Current Trial"):st.session_state.trials.append({"Trial #":len(st.session_state.trials)+1,"Query":active,"Rows":len(data)});st.success("Trial recorded.")
 if st.session_state.trials:st.dataframe(pd.DataFrame(st.session_state.trials),hide_index=True)
def quiz():
 st.header("Quiz")
 with st.form("quiz"):ans=[st.radio(q,o,key=str(i)) for i,(q,o,a) in enumerate(QUIZ)];done=st.form_submit_button("Grade quiz",type="primary")
 if done:st.session_state.score=sum(x==o[a] for x,(_,o,a) in zip(ans,QUIZ));st.success(f"Score: {st.session_state.score}/{len(QUIZ)}")
def reports():
 st.header("Report Generation");a,b=st.columns(2);name=a.text_input("Student Name");roll=b.text_input("Roll Number",value="46");notes=st.text_area("Observations","Cypher queries successfully retrieved nodes, relationships, and multi-hop graph connections.");trials=pd.DataFrame(st.session_state.trials)
 st.write(f"**Quiz score:** {st.session_state.score}/{len(QUIZ)}")
 if PDF_READY: st.download_button("Download lab report (PDF)",pdf_report(name,roll,trials,st.session_state.score,notes),"cypher_knowledge_graph_report.pdf","application/pdf",type="primary")
 else:
  st.warning("PDF export needs fpdf2. Run: pip install fpdf2")
  st.download_button("Download text report meanwhile",report(name,roll,trials,st.session_state.score,notes),"cypher_knowledge_graph_report.txt","text/plain")
def main():
 st.set_page_config(page_title=TITLE,layout="wide");st.title(TITLE)
 if "trials" not in st.session_state:st.session_state.trials=[]
 if "score" not in st.session_state:st.session_state.score=0
 page=st.sidebar.radio("Lab Navigator",["Theory","Simulation","Quiz","Report Generation"]);{"Theory":theory,"Simulation":simulation,"Quiz":quiz,"Report Generation":reports}[page]()
if __name__=="__main__":main()
