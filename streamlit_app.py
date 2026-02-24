import streamlit as st
import plotly.graph_objects as go
import random

# Set the page layout to wide
st.set_page_config(layout="wide", page_title="Process Maturity Grid")

# Initialize project list storage
if 'projects' not in st.session_state:
    st.session_state['projects'] = []

# Define the AI potential options and their corresponding dot sizes
AI_OPTIONS = [
    "No further tasks can be done with AI", 
    "Some tasks can be done with AI", 
    "Many tasks could be done with AI"
]

def get_dot_size(ai_potential_answer):
    if ai_potential_answer == AI_OPTIONS[1]:
        return 24  # Slightly larger dot
    elif ai_potential_answer == AI_OPTIONS[2]:
        return 34  # Largest dot
    return 14      # Current size (default)

# ==========================================
# POP-UP DIALOG FUNCTIONS
# ==========================================

@st.dialog("Add New Submission")
def add_submission_dialog():
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Project Name")
        method = st.selectbox("Method", ["Manual", "AI"])
        location = st.selectbox("Location", ["Onshore", "Offshore"])
        
        # New question for dot size
        ai_potential = st.selectbox("Potential for further AI tasks", AI_OPTIONS)
        
        col1, col2 = st.columns(2)
        submitted = col1.form_submit_button("Submit", type="primary")
        cleared = col2.form_submit_button("Clear")
        
        if submitted:
            if name:
                jx = random.uniform(-0.15, 0.15)
                jy = random.uniform(-0.15, 0.15)
                st.session_state['projects'].append({
                    "name": name,
                    "x": 0 if method == "Manual" else 1,
                    "y": 0 if location == "Onshore" else 1,
                    "ai_potential": ai_potential, # Save the new answer
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
    new_method = st.selectbox("Method", ["Manual", "AI"], index=0 if proj['x'] == 0 else 1)
    new_location = st.selectbox("Location", ["Onshore", "Offshore"], index=0 if proj['y'] == 0 else 1)
    
    # Safely get current AI potential (defaults to the first option if it's an older submission)
    current_ai_potential = proj.get('ai_potential', AI_OPTIONS[0])
    current_ai_index = AI_OPTIONS.index(current_ai_potential)
    
    # New question for dot size in the edit menu
    new_ai_potential = st.selectbox("Potential for further AI tasks", AI_OPTIONS, index=current_ai_index)
    
    col1, col2 = st.columns(2)
    if col1.button("Save Changes", type="primary", use_container_width=True):
        proj['name'] = new_name
        proj['x'] = 0 if new_method == "Manual" else 1
        proj['y'] = 0 if new_location == "Onshore" else 1
        proj['ai_potential'] = new_ai_potential # Update the answer
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
    xaxis=dict(range=[0, 1], tickmode='array', tickvals=[0.25, 0.75], ticktext=['Manual', 'AI'],
               title='Process Maturity →'),
    yaxis=dict(range=[0, 1], tickmode='array', tickvals=[0.25, 0.75], ticktext=['Onshore', 'Offshore'],
               title='Complexity Handled →'),
    height=1000 
)

fig.add_shape(type='line', x0=0, y0=1, x1=1, y1=0, line=dict(color='red', width=2))
fig.add_annotation(x=1, y=0, ax=0, ay=1, xref='x', yref='y', axref='x', ayref='y',
                   showarrow=True, arrowhead=2, arrowcolor='red')

if projects:
    xs = [0.25 + 0.5 * p['x'] + p.get('jx', 0) for p in projects]
    ys = [0.25 + 0.5 * p['y'] + p.get('jy', 0) for p in projects]
    names = [p['name'] for p in projects]
    
    # Calculate the size for each project dot based on their AI potential answer
    dot_sizes = [get_dot_size(p.get('ai_potential', AI_OPTIONS[0])) for p in projects]
    
    fig.add_trace(go.Scatter(
        x=xs, y=ys, 
        mode='markers+text',         
        text=names,                  
        textposition='top center',   
        marker=dict(
            size=dot_sizes, # Apply the dynamic sizes here
            line=dict(width=1, color='DarkSlateGrey') # Added a subtle border so overlapping dots are distinct
        ),        
        customdata=list(range(len(projects))),
        hoverinfo='text',
        hovertext=[f"{p['name']}<br>AI Potential: {p.get('ai_potential', AI_OPTIONS[0])}" for p in projects] # Shows the AI potential on hover
    ))

event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")

if "selection" in event and "points" in event["selection"] and len(event["selection"]["points"]) > 0:
    clicked_idx = event["selection"]["points"][0]["customdata"]
    edit_submission_dialog(preselected_idx=clicked_idx)
