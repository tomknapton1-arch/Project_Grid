

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


st.title("2x2 Process Maturity Grid")

# Streamlit input for projects
st.sidebar.header("Add Projects to Grid")
num_projects = st.sidebar.number_input("Number of Projects", min_value=1, max_value=10, value=1)
projects = []
for i in range(num_projects):
    name = st.sidebar.text_input(f"Project {i+1} Name", key=f"name_{i}")
    # X: Method (0=Manual, 1=Auto+AI), Y: Location (0=Onshore, 1=Offshore)
    x = st.sidebar.selectbox(f"{name or 'Project'} Method", ["Manual", "Auto + AI"], key=f"x_{i}")
    y = st.sidebar.selectbox(f"{name or 'Project'} Location", ["Onshore", "Offshore"], key=f"y_{i}")
    if name:
        projects.append({
            "name": name,
            "x": 0 if x == "Manual" else 1,
            "y": 0 if y == "Onshore" else 1
        })


# Create a simple 1×1 square divided into four quadrants
fig, ax = plt.subplots(figsize=(6, 6))
# show only positive quadrant from 0 to 1 in both axes
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
# ticks at extremes (and optionally midpoint)
ax.set_xticks([0, 0.5, 1])
ax.set_yticks([0, 0.5, 1])
ax.set_xticklabels(["0", "", "1"])
ax.set_yticklabels(["0", "", "1"])
# thin background grid just for reference
ax.grid(False)
# draw dividing lines to form four equal squares
ax.axhline(0.5, color='gray', linewidth=1)
ax.axvline(0.5, color='gray', linewidth=1)

# Draw arrow corresponding to y = -x (within the unit square)
# start at (0,1) and end at (1,0)
ax.annotate('', xy=(1, 0), xytext=(0, 1),
            arrowprops=dict(facecolor='red', edgecolor='red', arrowstyle='->', lw=2))

# Add updated axis labels for the requested metrics
ax.set_xlabel('Process Maturity →')
ax.set_ylabel('Complexity Handled →')
ax.xaxis.set_label_coords(0.5, -0.08)
ax.yaxis.set_label_coords(-0.08, 0.5)

# remove old Pro Maturity text if any (not needed for now)


# Plot projects as points with labels
for proj in projects:
    ax.plot(proj["x"], proj["y"], 'o', markersize=10, label=proj["name"])
    ax.text(proj["x"]+0.05, proj["y"]+0.05, proj["name"], fontsize=10, color='black')

# Remove top/right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

st.pyplot(fig)
