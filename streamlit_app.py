

# ensure required libraries are installed and recorded
import pkg_resources, subprocess, sys, os

def ensure_requirements(packages):
    # install missing packages and append to requirements.txt
    path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    # read existing requirements
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
        try:
            pkg_resources.get_distribution(pkg)
        except pkg_resources.DistributionNotFound:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# list the packages that the app relies on
ensure_requirements(["streamlit", "matplotlib", "streamlit-plotly-events"])

import streamlit as st
# switch to plotly for interactivity
from streamlit_plotly_events import plotly_events
import plotly.graph_objects as go


st.title("2x2 Process Maturity Grid")

# initialize project list storage
if 'projects' not in st.session_state:
    st.session_state['projects'] = []

# sidebar form for adding a single project
with st.sidebar.form("add_project_form", clear_on_submit=True):
    st.header("Add Project to Grid")
    name = st.text_input("Project Name")
    method = st.selectbox("Method", ["Manual", "Auto + AI"])
    location = st.selectbox("Location", ["Offshore", "Onshore"])
    submitted = st.form_submit_button("Submit")
    if submitted and name:
        st.session_state['projects'].append({
            "name": name,
            # x=0 for Manual, 1 for Auto+AI
            "x": 0 if method == "Manual" else 1,
            # y=0 for Offshore, 1 for Onshore
            "y": 0 if location == "Offshore" else 1
        })

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
    xaxis=dict(range=[0, 1], tickmode='array', tickvals=[0, 1], ticktext=['Manual', 'AI'],
               title='Process Maturity →'),
    yaxis=dict(range=[0, 1], tickmode='array', tickvals=[0, 1], ticktext=['Offshore', 'Onshore'],
               title='Complexity Handled →'),
    width=600, height=600
)
# arrow representing y = -x within unit square
fig.add_shape(type='line', x0=0, y0=1, x1=1, y1=0,
              line=dict(color='red', width=2))
fig.add_annotation(x=1, y=0, ax=0, ay=1,
                   xref='x', yref='y', axref='x', ayref='y',
                   showarrow=True, arrowhead=2, arrowcolor='red')

# add project points
if projects:
    xs = [p['x'] for p in projects]
    ys = [p['y'] for p in projects]
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
        with st.sidebar.expander(f"Edit '{proj['name']}'"):
            new_name = st.text_input("Project Name", value=proj['name'], key=f"edit_name_{idx}")
            new_method = st.selectbox("Method", ["Manual", "Auto + AI"],
                                      index=0 if proj['x'] == 0 else 1, key=f"edit_method_{idx}")
            new_location = st.selectbox("Location", ["Offshore", "Onshore"],
                                        index=0 if proj['y'] == 0 else 1, key=f"edit_loc_{idx}")
            if st.button("Save", key=f"save_{idx}"):
                proj['name'] = new_name
                proj['x'] = 0 if new_method == "Manual" else 1
                proj['y'] = 0 if new_location == "Offshore" else 1
                st.session_state['projects'][idx] = proj
                st.experimental_rerun()
            if st.button("Delete", key=f"delete_{idx}"):
                st.session_state['projects'].pop(idx)
                st.experimental_rerun()

# finally display the figure with modern width parameter
st.plotly_chart(fig, width='stretch')
