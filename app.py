import streamlit as st
from chatbot import load_dataset, initialize_index, generate_response, extract_mood
import pandas as pd
import os

st.set_page_config(page_title="Recipe Buddy", page_icon="🍴", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Background and Font */
    body {
        background-color: #f5f5f5;
        font-family: 'Arial', sans-serif;
    }
    .main {
        background: linear-gradient(to right, #fff5e6, #ffe4cc);
        padding: 20px;
        border-radius: 15px;
    }
    /* Header Styling */
    h1 {
        color: #ff6347;
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 0;
    }
    h2 {
        color: #444;
        font-size: 1.5em;
        border-bottom: 2px solid #ff6347;
        padding-bottom: 5px;
    }
    /* Recipe Card Styling */
    .recipe-card {
        background: #fff;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .recipe-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .recipe-card h3 {
        color: #ff6347;
        margin-bottom: 8px;
        font-size: 1.3em;
    }
    .recipe-card h4 {
        color: #333;
        margin-top: 10px;
        margin-bottom: 5px;
        font-size: 1.1em;
        border-bottom: 1px solid #ddd;
        padding-bottom: 3px;
    }
    .recipe-card p {
        color: #555;
        margin: 5px 0;
        line-height: 1.5;
    }
    /* Buttons */
    .stButton>button {
        background-color: #ff6347;
        color: white;
        border-radius: 5px;
        padding: 8px 15px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #e5533d;
    }
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #fff5e6;
        padding: 15px;
    }
    /* Footer */
    .footer {
        text-align: center;
        color: #777;
        margin-top: 20px;
        font-size: 0.9em;
    }
    .footer a {
        color: #ff6347;
        text-decoration: none;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Recipe Filters")
    cuisine_filter = st.selectbox("Cuisine", ["All", "South Indian", "North Indian", "East Indian", "West Indian"])
    diet_filter = st.selectbox("Diet", ["All", "Vegetarian", "Non-Vegetarian"])
    st.markdown("---")
    st.markdown("Use these filters to narrow down your recipe suggestions!")

@st.cache_resource
def initialize():
    try:
        df = load_dataset()
        model, index = initialize_index(df)
        return df, model, index
    except Exception as e:
        st.error(f"Initialization failed: {str(e)}")
        raise e

if 'query' not in st.session_state:
    st.session_state.query = ""
if 'response' not in st.session_state:
    st.session_state.response = ""

try:
    df, model, index = initialize()
except Exception as e:
    st.error(f"Failed to initialize the app: {str(e)}. Please check the dataset file, dependencies, and ensure the Groq model is supported.")
    st.stop()

# Apply filters to the dataset
filtered_df = df
if cuisine_filter != "All":
    filtered_df = filtered_df[filtered_df['Cuisine'].str.contains(cuisine_filter, case=False, na=False)]
if diet_filter != "All":
    filtered_df = filtered_df[filtered_df['Diet'].str.contains(diet_filter, case=False, na=False)]

query = st.session_state.query
if query:
    mood = extract_mood(query)
    if mood:
        st.title(f"🍴 Recipe Buddy - {mood.capitalize()} Vibes")
    else:
        st.title("🍴 Recipe Buddy")
else:
    st.title("🍴 Recipe Buddy")
st.markdown("Ask for a recipe, tell me what ingredients you have, or share your mood (e.g., 'festive', 'comfort') to get delicious Indian dishes!")

# User input
with st.form(key="query_form"):
    query = st.text_input("What recipe, ingredients, or mood are you thinking of?", value=st.session_state.query, placeholder="e.g., 'chicken curry', 'tomatoes and rice', or 'I’m feeling festive'")
    submit_button = st.form_submit_button(label="Get Recipes")

if submit_button and query:
    st.session_state.query = query
    with st.spinner("Cooking up some delicious ideas... 🍳"):
        try:
            # Use filtered_df if it has entries, otherwise fall back to original df
            response = generate_response(query, filtered_df if not filtered_df.empty else df, model, index)
            st.session_state.response = response if response else "No response received from the server. Please try a different query."
        except Exception as e:
            st.session_state.response = f"Error processing query: {str(e)}. Please try again with a different query."


if st.session_state.response:
    st.subheader("Recipe Suggestions")
    
    if not st.session_state.response.strip() or "Error" in st.session_state.response:
        st.warning("Oops! I couldn’t find or generate a recipe for your query. Try something like 'chicken curry' or 'what can I make with tomatoes?'")
    else:
        try:
            lines = st.session_state.response.split("\n")
            current_card = []
            in_recipe = False
            in_ingredients = False
            in_method = False

            for line in lines:
                line = line.strip()
                if not line:
                    continue

              
                if line.startswith("**Name**"):
                    if current_card:  
                        recipe_content = "".join(current_card)
                        with st.container():
                            st.markdown('<div class="recipe-card">' + recipe_content + '</div>', unsafe_allow_html=True)
                            if st.button("Copy Recipe", key=f"copy_{len(current_card)}"):
                                st.code(recipe_content.replace('<h3>', '').replace('</h3>', '').replace('<h4>', '').replace('</h4>', '').replace('<p>', '').replace('</p>', ''), language="text")
                    current_card = []
                    in_recipe = True
                    current_card.append(f"<h3>{line}</h3>")
                # Ingredients section
                elif line.startswith("**Ingredients**"):
                    in_ingredients = True
                    in_method = False
                    current_card.append(f"<h4>{line}</h4>")
                # Method section
                elif line.startswith("**Method**"):
                    in_ingredients = False
                    in_method = True
                    current_card.append(f"<h4>{line}</h4>")
                # End of recipe (
                elif line.startswith("**Acknowledgment**") or line.startswith("**Closing Note**"):
                    in_recipe = False
                    in_ingredients = False
                    in_method = False
                    current_card.append(f"<p>{line}</p>")
                elif in_recipe:
                    if in_ingredients or in_method:
                        current_card.append(f"<p>{line}</p>")
                    else:
                        current_card.append(f"<p>{line}</p>")
                else:
                    current_card.append(f"<p>{line}</p>")

            if current_card:
                recipe_content = "".join(current_card)
                with st.container():
                    st.markdown('<div class="recipe-card">' + recipe_content + '</div>', unsafe_allow_html=True)
                    if st.button("Copy Recipe", key=f"copy_{len(current_card)}"):
                        st.code(recipe_content.replace('<h3>', '').replace('</h3>', '').replace('<h4>', '').replace('</h4>', '').replace('<p>', '').replace('</p>', ''), language="text")
        except Exception as e:
            st.error(f"Error rendering response: {str(e)}. Please try a different query.")

    if st.button("Clear"):
        st.session_state.query = ""
        st.session_state.response = ""
        st.rerun()

