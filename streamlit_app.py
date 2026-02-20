

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


# Create a 2x2 grid
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(["Manual", "Auto + AI"])
ax.set_yticklabels(["Onshore", "Offshore"])
ax.grid(True, which='both', color='gray', linestyle='-', linewidth=1)

# Draw the grid lines
for i in range(3):
    ax.axhline(i-0.5, color='gray', linewidth=1)
    ax.axvline(i-0.5, color='gray', linewidth=1)

# Draw diagonal arrow (from bottom-left to top-right)
ax.annotate('', xy=(1.15, 1.15), xytext=(0, 0),
            arrowprops=dict(facecolor='red', edgecolor='red', arrowstyle='->', lw=2))

# Add axis labels
ax.set_xlabel('Method →')
ax.set_ylabel('Location →')
ax.xaxis.set_label_coords(0.5, -0.08)
ax.yaxis.set_label_coords(-0.08, 0.5)

# Add 'Pro Maturity' note
ax.text(1.25, 0.5, 'Pro Maturity', fontsize=12, rotation=90, va='center', color='blue')

# Plot projects as points with labels
for proj in projects:
    ax.plot(proj["x"], proj["y"], 'o', markersize=10, label=proj["name"])
    ax.text(proj["x"]+0.05, proj["y"]+0.05, proj["name"], fontsize=10, color='black')

# Remove top/right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

st.pyplot(fig)
