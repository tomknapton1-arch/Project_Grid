import streamlit as st
import plotly.graph_objects as go
import random

# Set the page layout to wide
st.set_page_config(layout="wide", page_title="Process Maturity Grid")

# Initialize project list storage
if 'projects' not in st.session_state:
    st.session_state['projects'] = []

# Define options
AI_OPTIONS = [
    "No further tasks can be done with AI", 
    "Some tasks can be done with AI", 
    "Many tasks could be done with AI"
]

# Updated quadrant names to perfectly match the plot labels
QUADRANT_OPTIONS = [
    "Onshore",
    "Onshore + Offshore + Nearshore",
    "Onshore + Automation",
    "Onshore + AI"
]

def get_dot_size(ai_potential_answer):
    if ai_potential_answer == AI_OPTIONS[1]:
        return 24  
    elif ai_potential_answer == AI_OPTIONS[2]:
        return 34  
    return 14      

def get_xy_from_quadrant(quadrant_str):
    if quadrant_str == "Onshore": return 0, 1
    if quadrant_str == "onshore+offshore+nearshore": return 0, 0
    if quadrant_str == "Onshore + Automation": return 1, 0
    if quadrant_str == "Onshore + AI": return 1, 1
    return 0, 0

def get_quadrant_from_xy(x, y):
    if x == 0 and y == 1: return "Onshore"
    if x == 0 and y == 0: return "onshore+offshore+nearshore"
    if x == 1 and y == 0: return "Onshore + Automation"
    if x == 1 and y == 1: return "Onshore + AI"
    return "Onshore"

# ==========================================
# POP-UP DIALOG FUNCTIONS
# ==========================================

@st.dialog("Add New Submission")
def add_submission_dialog():
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Project Name")
        
        quadrant = st.selectbox("Select Quadrant", QUADRANT_OPTIONS)
        ai_potential = st.selectbox("Potential for further AI tasks", AI_OPTIONS)
        
        col1, col2 = st.columns(2)
        submitted = col1.form_submit_button("Submit", type="primary")
        cleared = col2.form_submit_button("Clear")
        
        if submitted:
            if name:
                jx = random.uniform(-0.15, 0.15)
                jy = random.uniform(-0.15, 0.15)
                x, y = get_xy_from_quadrant(quadrant)
                
                st.session_state['projects'].append({
                    "name": name,
                    "x": x,
                    "y": y,
                    "ai_potential": ai_potential,
                    "jx": jx,
                    "jy": jy,
                })
                st.rerun()
            else:
                st.error("Please enter a project name before submitting.")

@st.dialog("Edit Submission")
def edit_submission_dialog(preselected_idx=0):
    if not st.session_state['projects']:
        st.info("No projects available to edit. Please add a submission first.")
        return
        
    project_names = [p['name'] for p in st.session_state['projects']]
    
    if preselected_idx >= len(project_names):
        preselected_idx = 0
        
    selected_name = st.selectbox("Select Project to Edit", project_names, index=preselected_idx)
    idx = project_names.index(selected_name)
    proj = st.session_state['projects'][idx]
    
    st.divider()
    
    new_name = st.text_input("Project Name", value=proj['name'])
    
    current_quadrant = get_quadrant_from_xy(proj['x'], proj['y'])
    new_quadrant = st.selectbox("Select Quadrant", QUADRANT_OPTIONS, index=QUADRANT_OPTIONS.index(current_quadrant))
    
    current_ai_potential = proj.get('ai_potential', AI_OPTIONS[0])
    new_ai_potential = st.selectbox("Potential for further AI tasks", AI_OPTIONS, index=AI_OPTIONS.index(current_ai_potential))
    
    col1, col2 = st.columns(2)
    if col1.button("Save Changes", type="primary", use_container_width=True):
        new_x, new_y = get_xy_from_quadrant(new_quadrant)
        proj['name'] = new_name
        proj['x'] = new_x
        proj['y'] = new_y
        proj['ai_potential'] = new_ai_potential 
        st.session_state['projects'][idx] = proj
        st.rerun()
        
    if col2.button("Delete Project", use_container_width=True):
        st.session_state['projects'].pop(idx)
        st.rerun()

# ==========================================
# MAIN PAGE LAYOUT
# ==========================================

col_title, col_empty, col_add, col_edit = st.columns([5, 1, 1.5, 1.5])

with col_title:
    st.title("2x2 Process Maturity Grid")

with col_add:
    st.write("") 
    st.write("")
    if st.button("➕ Add Submission", use_container_width=True):
        add_submission_dialog()

with col_edit:
    st.write("") 
    st.write("")
    if st.button("✏️ Edit Submission", use_container_width=True):
        edit_submission_dialog()

projects = st.session_state['projects']

# ==========================================
# PLOTLY GRID GENERATION
# ==========================================

fig = go.Figure()

fig.update_layout(
    shapes=[
        dict(type='line', x0=0.5, x1=0.5, y0=0, y1=1, line=dict(color='gray')),
        dict(type='line', x0=0, x1=1, y0=0.5, y1=0.5, line=dict(color='gray'))
    ],
    xaxis=dict(range=[0, 1], showticklabels=False, title=''),
    yaxis=dict(range=[0, 1], showticklabels=False, title=''),
    height=1000, 
    margin=dict(t=80, b=80, l=40, r=40) 
)

# Custom large labels placed specifically above and below the quadrants
fig.update_layout(
    annotations=[
        # The Red Arrow
        dict(x=1, y=0, ax=0, ay=1, xref='x', yref='y', axref='x', ayref='y', showarrow=True, arrowhead=2, arrowcolor='red'),
        
        # Top Left Label
        dict(x=0.25, y=1.0, text="<b>Onshore</b>", showarrow=False, font=dict(size=22), xanchor='center', yanchor='bottom', xref='x', yref='y'),
        
        # Top Right Label
        dict(x=0.75, y=1.0, text="<b>Onshore + AI</b>", showarrow=False, font=dict(size=22), xanchor='center', yanchor='bottom', xref='x', yref='y'),
        
        # Bottom Left Label
        dict(x=0.25, y=0.0, text="<b>onshore+offshore+nearshore</b>", showarrow=False, font=dict(size=22), xanchor='center', yanchor='top', xref='x', yref='y'),
        
        # Bottom Right Label
        dict(x=0.75, y=0.0, text="<b>Onshore + Automation</b>", showarrow=False, font=dict(size=22), xanchor='center', yanchor='top', xref='x', yref='y')
    ]
)

if projects:
    xs = [0.25 + 0.5 * p['x'] + p.get('jx', 0) for p in projects]
    ys = [0.25 + 0.5 * p['y'] + p.get('jy', 0) for p in projects]
    names = [p['name'] for p in projects]
    
    dot_sizes = [get_dot_size(p.get('ai_potential', AI_OPTIONS[0])) for p in projects]
    
    fig.add_trace(go.Scatter(
        x=xs, y=ys, 
        mode='markers+text',         
        text=names,                  
        textposition='top center',   
        marker=dict(
            size=dot_sizes, 
            line=dict(width=1, color='DarkSlateGrey') 
        ),        
        customdata=list(range(len(projects))),
        hoverinfo='text',
        hovertext=[f"{p['name']}<br>AI Potential: {p.get('ai_potential', AI_OPTIONS[0])}" for p in projects] 
    ))

event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")

if "selection" in event and "points" in event["selection"] and len(event["selection"]["points"]) > 0:
    clicked_idx = event["selection"]["points"][0]["customdata"]
    edit_submission_dialog(preselected_idx=clicked_idx)
