import streamlit as st
import os
import base64

st.set_page_config(page_title="Singularity Visual", layout="centered")

st.title("🌀 Crystalline Singularity Visualization")

# --- Image handling ---
root_dir = os.path.dirname(os.path.abspath(__file__))
local_image_path = os.path.join(root_dir, "singularity.png")

crystal_src = None

uploaded_file = st.file_uploader("Upload a different singularity image (optional):", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    data = uploaded_file.read()
    encoded = base64.b64encode(data).decode()
    crystal_src = f"data:image/png;base64,{encoded}"

elif os.path.exists(local_image_path):
    with open(local_image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    crystal_src = f"data:image/png;base64,{encoded}"

else:
    crystal_src = "https://placehold.co/600x600/1b0033/FFFFFF?text=Singularity"

# --- Display image ---
st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="{crystal_src}" alt="Crystalline Singularity"
             style="width:65%; border-radius:18px; box-shadow:0 0 40px rgba(150,0,255,0.6); margin-top:20px;">
    </div>
    """,
    unsafe_allow_html=True
)
