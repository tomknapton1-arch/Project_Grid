import streamlit as st
import plotly.graph_objects as go
import random

# ADDED: Set the page layout to wide so it uses the whole screen
st.set_page_config(layout="wide", page_title="Process Maturity Grid")

st.title("2x2 Process Maturity Grid")

# initialize project list storage
if 'projects' not in st.session_state:
    st.session_state['projects'] = []

# sidebar inputs for adding a single project
st.sidebar.header("Add Project to Grid")
name = st.sidebar.text_input("Project Name", key='new_name')
method = st.sidebar.selectbox("Method", ["Manual", "AI"], key='new_method')
location = st.sidebar.selectbox("Location", ["Onshore", "Offshore"], key='new_location')

if st.sidebar.button("Submit"):
    if name:
        # Generate jitter to prevent text/dot overlap
        jx = random.uniform(-0.15, 0.15)
        jy = random.uniform(-0.15, 0.15)
        st.session_state['projects'].append({
            "name": name,
            "x": 0 if method == "Manual" else 1,
            "y": 0 if location == "Onshore" else 1,
            "jx": jx,
            "jy": jy,
        })
        st.success(f"Added project '{name}'")
        st.rerun() 
    else:
        st.sidebar.warning("Please enter a project name before submitting.")

projects = st.session_state['projects']

# build plotly figure for interactive grid
fig = go.Figure()

# quadrant dividing lines
fig.update_layout(
    shapes=[
        dict(type='line', x0=0.5, x1=0.5, y0=0, y1=1, line=dict(color='gray')),
        dict(type='line', x0=0, x1=1, y0=0.5, y1=0.5, line=dict(color='gray'))
    ],
    xaxis=dict(range=[0, 1], tickmode='array', tickvals=[0.25, 0.75], ticktext=['Manual', 'AI'],
               title='Process Maturity →'),
    yaxis=dict(range=[0, 1], tickmode='array', tickvals=[0.25, 0.75], ticktext=['Onshore', 'Offshore'],
               title='Complexity Handled →'),
    height=1000 # UPDATED: Increased height to 800 and removed hardcoded width
)

# arrow representing y = -x within unit square
fig.add_shape(type='line', x0=0, y0=1, x1=1, y1=0, line=dict(color='red', width=2))
fig.add_annotation(x=1, y=0, ax=0, ay=1, xref='x', yref='y', axref='x', ayref='y',
                   showarrow=True, arrowhead=2, arrowcolor='red')

# add project points 
if projects:
    xs = [0.25 + 0.5 * p['x'] + p.get('jx', 0) for p in projects]
    ys = [0.25 + 0.5 * p['y'] + p.get('jy', 0) for p in projects]
    names = [p['name'] for p in projects]
    
    fig.add_trace(go.Scatter(
        x=xs, y=ys, 
        mode='markers+text',         
        text=names,                  
        textposition='top center',   
        marker=dict(size=14),        # Slightly increased dot size for the larger grid
        customdata=list(range(len(projects))),
        hoverinfo='text',
        hovertext=names
    ))

# Render interactive plot natively
event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")

# If a point was clicked, show edit/delete UI
if "selection" in event and "points" in event["selection"] and len(event["selection"]["points"]) > 0:
    idx = event["selection"]["points"][0]["customdata"]
    
    if idx is not None and 0 <= idx < len(projects):
        proj = projects[idx]
        st.sidebar.divider()
        st.sidebar.subheader(f"Edit '{proj['name']}'")
        
        new_name = st.sidebar.text_input("Project Name", value=proj['name'], key=f"edit_name_{idx}")
        new_method = st.sidebar.selectbox("Method", ["Manual", "AI"],
                                          index=0 if proj['x'] == 0 else 1, key=f"edit_method_{idx}")
        new_location = st.sidebar.selectbox("Location", ["Onshore", "Offshore"],
                                            index=0 if proj['y'] == 0 else 1, key=f"edit_loc_{idx}")
        
        # Put Save and Delete buttons side-by-side
        col1, col2 = st.sidebar.columns(2)
        if col1.button("Save", key=f"save_{idx}", type="primary"):
            proj['name'] = new_name
            proj['x'] = 0 if new_method == "Manual" else 1
            proj['y'] = 0 if new_location == "Onshore" else 1
            st.session_state['projects'][idx] = proj
            st.rerun()
            
        if col2.button("Delete", key=f"delete_{idx}"):
            st.session_state['projects'].pop(idx)
            st.rerun()
