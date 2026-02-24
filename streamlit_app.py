

# ensure required libraries are installed and recorded without extra dependencies
import subprocess, sys, os, importlib.util

def ensure_requirements(packages):
    # install missing packages and append to requirements.txt
    path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(path):
        with open(path) as f:
            existing = {line.strip() for line in f if line.strip()}
    else:
        existing = set()
    for pkg in packages:
        if pkg not in existing:
            with open(path, "a") as f:
                f.write(pkg + "\n")
            existing.add(pkg)
        # if module not importable, install it
        if importlib.util.find_spec(pkg) is None:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# list the packages that the app relies on
ensure_requirements(["streamlit", "matplotlib", "streamlit-plotly-events"])

import streamlit as st
# switch to plotly for interactivity
from streamlit_plotly_events import plotly_events
import plotly.graph_objects as go
import random


st.title("2x2 Process Maturity Grid")

# initialize project list storage
if 'projects' not in st.session_state:
    st.session_state['projects'] = []

# sidebar inputs for adding a single project (no form to avoid confusion)
st.sidebar.header("Add Project to Grid")
# use session_state keys to preserve between reruns
name = st.sidebar.text_input("Project Name", key='new_name')
method = st.sidebar.selectbox("Method", ["Manual", "AI"], key='new_method')
location = st.sidebar.selectbox("Location", ["Onshore", "Offshore"], key='new_location')
if st.sidebar.button("Submit"):
    if name:
        # generate small jitter to reduce overlap
        jx = random.uniform(-0.1, 0.1)
        jy = random.uniform(-0.1, 0.1)
        st.session_state['projects'].append({
            "name": name,
            "x": 0 if method == "Manual" else 1,
            "y": 0 if location == "Onshore" else 1,
            "jx": jx,
            "jy": jy,
        })
        st.success(f"Added project '{name}'")
        st.experimental_rerun()
    else:
        st.sidebar.warning("Please enter a project name before submitting.")

# make a local reference to avoid repeated lookups
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
    width=600, height=600
)
# arrow representing y = -x within unit square
fig.add_shape(type='line', x0=0, y0=1, x1=1, y1=0,
              line=dict(color='red', width=2))
fig.add_annotation(x=1, y=0, ax=0, ay=1,
                   xref='x', yref='y', axref='x', ayref='y',
                   showarrow=True, arrowhead=2, arrowcolor='red')

# add project points (map 0/1 to quadrant centers with jitter)
if projects:
    xs = [0.25 + 0.5 * p['x'] + p.get('jx', 0) for p in projects]
    ys = [0.25 + 0.5 * p['y'] + p.get('jy', 0) for p in projects]
    names = [p['name'] for p in projects]
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode='markers', marker=dict(size=12),
        customdata=list(range(len(projects))),
        hovertext=names
    ))

# render interactive plot and capture clicks
clicked = plotly_events(fig, click_event=True, key='grid')

# if a point was clicked show edit/delete UI
if clicked and len(clicked) > 0:
    idx = clicked[0].get('customdata')
    if idx is not None and 0 <= idx < len(projects):
        proj = projects[idx]
        # display edit controls directly instead of expander
        st.sidebar.subheader(f"Edit '{proj['name']}'")
        new_name = st.sidebar.text_input("Project Name", value=proj['name'], key=f"edit_name_{idx}")
        new_method = st.sidebar.selectbox("Method", ["Manual", "AI"],
                                          index=0 if proj['x'] == 0 else 1, key=f"edit_method_{idx}")
        new_location = st.sidebar.selectbox("Location", ["Onshore", "Offshore"],
                                            index=0 if proj['y'] == 0 else 1, key=f"edit_loc_{idx}")
        if st.sidebar.button("Save", key=f"save_{idx}"):
            proj['name'] = new_name
            proj['x'] = 0 if new_method == "Manual" else 1
            proj['y'] = 0 if new_location == "Onshore" else 1
            st.session_state['projects'][idx] = proj
            st.experimental_rerun()
        if st.sidebar.button("Delete", key=f"delete_{idx}"):
            st.session_state['projects'].pop(idx)
            st.experimental_rerun()

# finally display the figure with modern width parameter
st.plotly_chart(fig, width='stretch')
