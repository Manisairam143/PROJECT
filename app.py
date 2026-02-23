
import streamlit as st
import os
from google import genai
from PIL import Image
from dotenv import load_dotenv

st.set_page_config(
    page_title="Civil Engineering Insight Studio",
    layout="centered"
)

theme_option = st.sidebar.radio(
    "Select Theme",
    ["Dark", "Light"],
    index=0
)

if theme_option == "Dark":
    st.markdown(
        """
        <style>
            /* Main background */
            .stApp { background-color: #000000; }
            html, body, [class*="css"] { color: #FFFFFF !important; }
            h1,h2,h3,h4,h5,h6,p,label,div,span { color: #FFFFFF !important; }

            /* Sidebar */
            section[data-testid="stSidebar"] { background-color: #111111 !important; }
            section[data-testid="stSidebar"] * { color: #FFFFFF !important; }

            /* Input fields */
            input, textarea { background-color: #222222 !important; color: #FFFFFF !important; }
            input::placeholder, textarea::placeholder { color: #AAAAAA !important; }

            /* File uploader */
            div[data-testid="stFileUploader"] { 
                background-color: #000000 !important; 
                border: 2px solid #444444 !important; 
                border-radius: 12px !important; 
                padding: 10px !important;
            }
            div[data-testid="stFileUploader"] > div { 
                background-color: #000000 !important; 
                border: 2px dashed #555555 !important; 
                border-radius: 10px !important; 
            }
            div[data-testid="stFileUploader"] div[role="button"] { color: #CCCCCC !important; }
            div[data-testid="stFileUploader"] button { 
                background-color: #222222 !important; color: #FFFFFF !important; 
                border: 1px solid #555555 !important; transition: none !important;
            }
            div[data-testid="stFileUploader"] button:hover { background-color: #222222 !important; }

            /* Buttons */
            .stButton > button {
                background-color: #333333 !important;
                color: #FFFFFF !important;
                border: 1px solid #555555 !important;
                border-radius: 8px !important;
                padding: 0.5rem 1rem !important;
            }
            .stButton > button:hover { background-color: #555555 !important; }
        </style>
        """, unsafe_allow_html=True
    )
else:  # Light theme
    st.markdown(
        """
        <style>
            /* Main background */
            .stApp { background-color: #FFFFFF; }
            html, body, [class*="css"] { color: #000000 !important; }
            h1,h2,h3,h4,h5,h6,p,label,div,span { color: #000000 !important; }

            /* Sidebar */
            section[data-testid="stSidebar"] { background-color: #F0F0F0 !important; }
            section[data-testid="stSidebar"] * { color: #000000 !important; }

            /* Input fields */
            input, textarea { background-color: #FFFFFF !important; color: #000000 !important; }
            input::placeholder, textarea::placeholder { color: #666666 !important; }

            /* File uploader */
            div[data-testid="stFileUploader"] { 
                background-color: #FFFFFF !important; 
                border: 2px solid #CCCCCC !important; 
                border-radius: 12px !important; 
                padding: 10px !important;
            }
            div[data-testid="stFileUploader"] > div { 
                background-color: #FFFFFF !important; 
                border: 2px dashed #AAAAAA !important; 
                border-radius: 10px !important; 
            }
            div[data-testid="stFileUploader"] div[role="button"] { color: #555555 !important; }
            div[data-testid="stFileUploader"] button { 
                background-color: #EEEEEE !important; color: #000000 !important; 
                border: 1px solid #CCCCCC !important; transition: none !important;
            }
            div[data-testid="stFileUploader"] button:hover { background-color: #DDDDDD !important; }

            /* Buttons */
            .stButton > button {
                background-color: #EEEEEE !important;
                color: #000000 !important;
                border: 1px solid #CCCCCC !important;
                border-radius: 8px !important;
                padding: 0.5rem 1rem !important;
            }
            .stButton > button:hover { background-color: #DDDDDD !important; }
        </style>
        """, unsafe_allow_html=True
    )

# -----------------------------------
# Load Environment Variables
# -----------------------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("Missing GOOGLE_API_KEY. Please check your .env file.")
    st.stop()

# -----------------------------------
# Create Gemini Client
# -----------------------------------
client = genai.Client(api_key=api_key)

# -----------------------------------
# Get Available Gemini Models
# -----------------------------------
available_models = []
try:
    models = client.models.list()
    for m in models:
        if "gemini" in m.name.lower():
            available_models.append(m.name)
except Exception as e:
    st.sidebar.error(f"Error listing models: {e}")

# -----------------------------------
# Sidebar Model Selection
# -----------------------------------
st.sidebar.header("⚙️ Configuration")
selected_model_name = st.sidebar.selectbox(
    "Select Model",
    available_models,
    index=0 if available_models else None
)

# -----------------------------------
# Gemini Response Function
# -----------------------------------
def get_gemini_response(user_text, uploaded_file, system_prompt, model_name):
    try:
        image = Image.open(uploaded_file)
        response = client.models.generate_content(
            model=model_name,
            contents=[system_prompt, image, user_text if user_text else "Provide full structural analysis."]
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"

# -----------------------------------
# Main UI
# -----------------------------------
st.header("🏗️ Civil Engineering Insight Studio")
st.write("Upload a structure image for professional engineering analysis.")

input_text = st.text_input(
    "Additional Context (Optional):",
    placeholder="e.g., focus on structural integrity or load distribution"
)

uploaded_file = st.file_uploader(
    "Upload Structure Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Target Structure", use_container_width=True)

analyze_button = st.button("Analyze Structure")

# -----------------------------------
# Engineering Prompt
# -----------------------------------
system_prompt = """
You are an expert civil engineer.

Analyze the uploaded structure image and provide a professional engineering report including:

1. Type of structure
2. Materials likely used
3. Estimated dimensions
4. Construction techniques
5. Structural integrity observations
6. Possible engineering challenges
7. Safety recommendations

Be technical, structured, and professional.
"""

# -----------------------------------
# Run Analysis
# -----------------------------------
if analyze_button:
    if uploaded_file is not None:
        if not selected_model_name:
            st.error("No model available for selection.")
        else:
            with st.spinner("Analyzing structural data..."):
                result = get_gemini_response(
                    input_text, uploaded_file, system_prompt, selected_model_name
                )
            st.subheader("📋 Engineering Report")
            st.write(result)
    else:
        st.warning("Please upload an image before analysis.")