# RecipeBuddyBot

Hey there! I’m Akshaya KS, and I’m excited to share my project Recipe Buddy with you! This is a Recipe Buddy Bot, I built to help food enthusiasts like myself discover delicious Indian recipes. Whether you’re searching for a specific dish, have some ingredients on hand, or just want recipes that match your mood (like "festive" or "comfort"), Recipe Buddy has got you covered. I created this bot using Python, Streamlit, and some  AI tools to make recipe searching fun and interactive.

The bot features a sleek interface with styled recipe cards, sidebar filters for cuisine and diet, and a structured output that neatly separates the Ingredients and Method for each recipe. I’ve also added a "Copy Recipe" button to make it easy to save your favorites. Let’s dive into the details!

# Project Overview

I built Recipe Buddy to make finding Indian recipes quick and personalized. The app uses a combination of semantic search and generative AI (Retrieval-Augmented Generation, or RAG) to suggest recipes. It first searches a dataset of Indian recipes to find matches, and if none are found, it generates a new recipe using Groq AI. I’ve designed the bot to:

* Accept queries like dish names (e.g., "chicken curry"), ingredients (e.g., "tomatoes and rice"), or moods (e.g., "I’m feeling festive").
* Display recipes in a structured format with separate Ingredients and Method sections.
* Offer filters for cuisine (e.g., South Indian) and diet (e.g., Vegetarian).
* Provide a professional UI with recipe cards, a dynamic title, and error handling for vague queries.
* This project was a great learning experience for me, combining NLP, AI, and web development to create something practical and user-friendly.


# Dataset

For this project, I used a dataset called indianfood_dataset.xlsx, which contains a collection of Indian recipes. It includes columns like:

* RecipeName: The name of the recipe (e.g., "Chicken Curry").
* Ingredients: The list of ingredients needed.
* Instructions: The preparation steps.
* Cuisine: The type of Indian cuisine (e.g., South Indian, North Indian).
* Diet: The dietary category (e.g., Vegetarian, Non-Vegetarian).
* I preprocess the dataset by combining these fields into a single text string for each recipe, which helps with semantic search.


# Tech Stack
Here’s what I used to build Recipe Buddy:

* Python: The core programming language for the project.
* Streamlit: For creating the interactive web interface.
* Pandas: To load and process the dataset.
* Sentence Transformers (all-MiniLM-L6-v2): To generate embeddings for semantic search.
* FAISS: For efficient similarity search to find relevant recipes.
* Groq API (llama-3.3-70b-versatile): For generating creative recipe responses when needed.
* Python-dotenv: To manage API keys securely.

# How It Works
I designed Recipe Buddy to work in a few simple steps:

* Dataset Loading: I load the indianfood_dataset.xlsx file and convert the recipes into embeddings using the Sentence Transformer model.
* Semantic Search: When you enter a query, the app extracts ingredients and uses FAISS to find the most similar recipes in the dataset based on their embeddings.
* Mood Detection: I added a feature to detect your mood (e.g., "festive", "comfort") from the query, which personalizes the suggestions.
* Recipe Generation: If no matches are found in the dataset, the Groq API generates a new recipe. The response is structured with separate Ingredients and Method sections for clarity.
* Display: The Streamlit app shows the recipes in styled cards, with filters for cuisine and diet, a dynamic title (e.g., "🍴 Recipe Buddy - Festive Vibes"), and a "Copy Recipe" button.
* It’s a Retrieval-Augmented Generation (RAG) system, which means it combines retrieval (searching the dataset) with generation (creating new recipes) to give you the best of both worlds.


# Set Up the Groq API Key:
I used the Groq API for generating recipes. You’ll need to get your own API key from Groq. Once you have it, create a .env file in the project directory and add 
GROQ_API_KEY=your-api-key-here

# Features
I added  these features to Recipe Buddy:

* Structured Recipe Output: Each recipe is neatly formatted with Ingredients and Method sections.
* Mood-Based Suggestions: The app detects your mood (e.g., "festive", "comfort") and tailors the suggestions accordingly.
* UI: Styled recipe cards, a gradient background, sidebar filters, and a dynamic title make the app visually appealing.
* Error Handling: If you enter a vague query (e.g., "recipe and give"), the app shows a helpful warning instead of crashing.
* Copy Functionality: Easily copy recipes with a single click.
