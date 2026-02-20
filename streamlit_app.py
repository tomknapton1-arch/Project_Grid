

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.title("4x4 Process Maturity Grid")

# Create a 4x4 grid
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xticks(np.arange(0, 4, 1))
ax.set_yticks(np.arange(0, 4, 1))
ax.set_xticklabels(["Manual", "Semi-Auto", "Auto", "Auto + AI"])
ax.set_yticklabels(["Onshore", "Offshore", "", ""])
ax.grid(True, which='both', color='gray', linestyle='-', linewidth=1)

# Draw the grid lines
for i in range(5):
    ax.axhline(i-0.5, color='gray', linewidth=1)
    ax.axvline(i-0.5, color='gray', linewidth=1)

# Draw diagonal arrow (from bottom-left to top-right)
ax.annotate('', xy=(3.2, 3.2), xytext=(0, 0),
            arrowprops=dict(facecolor='red', edgecolor='red', arrowstyle='->', lw=2))

# Add axis labels
ax.set_xlabel('Method →')
ax.set_ylabel('Location →')
ax.xaxis.set_label_coords(0.5, -0.08)
ax.yaxis.set_label_coords(-0.08, 0.5)

# Add 'Pro Maturity' note
ax.text(3.5, 2, 'Pro Maturity', fontsize=12, rotation=90, va='center', color='blue')

# Remove ticks for empty labels
ax.set_yticks([2, 3], labels=['', ''])

# Remove top/right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

st.pyplot(fig)
