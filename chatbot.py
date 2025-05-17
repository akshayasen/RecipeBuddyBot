import os
import pandas as pd
import faiss
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from groq import Groq
import re

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

try:
    client = Groq(api_key=groq_api_key)
except Exception as e:
    raise Exception(f"Failed to initialize Groq client: {e}")

def load_dataset(df="C:\\Users\\akshaya\\Desktop\\chatbot\\indianfood_dataset.xlsx"):
    try:
        if not os.path.exists(df):
            raise FileNotFoundError(f"Dataset file '{df}' not found in the current directory")
        
        df = pd.read_excel(df)
        required_columns = ['RecipeName', 'Ingredients', 'Instructions', 'Cuisine', 'Diet']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Dataset missing required columns: {missing_columns}")
        
        df.fillna("", inplace=True)
        df['combined'] = df.apply( 
            lambda row: f"Recipe: {row['RecipeName']}\nIngredients: {row['Ingredients']}\nInstructions: {row['Instructions']}\nCuisine: {row['Cuisine']}, Diet: {row['Diet']}",
            axis=1
        )
        print(f"Dataset loaded successfully. Total recipes: {len(df)}")
        return df
    except Exception as e:
        print(f"Failed to load dataset: {str(e)}")
        raise Exception(f"Failed to load dataset: {str(e)}")

# Initialize embeddings and FAISS index
def initialize_index(df):
    try:
        if 'combined' not in df.columns:
            raise ValueError("DataFrame missing 'combined' column. Ensure load_dataset ran successfully.")
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(df['combined'].tolist(), show_progress_bar=True)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        print(f"FAISS index initialized successfully. Dimension: {dimension}")
        return model, index
    except Exception as e:
        print(f"Failed to initialize FAISS index: {str(e)}")
        raise Exception(f"Failed to initialize FAISS index: {str(e)}")

def extract_ingredients(query):
    synonyms = {
        "tomato": ["tomatoes", "tomatoe"],
        "chicken": ["chiken"],
        "rice": ["basmati", "white rice"],
        "onion": ["onions"],
    }
    
    ingredient_keywords = re.findall(r'\b[\w\s]+(?:\s+\([\w\s]+\))?\b', query.lower())
    ingredients = [kw.strip() for kw in ingredient_keywords if len(kw) > 2]
    
    expanded_ingredients = set()
    for ing in ingredients:
        expanded_ingredients.add(ing)
        for key, syn_list in synonyms.items():
            if ing == key or ing in syn_list:
                expanded_ingredients.add(key)
                expanded_ingredients.update(syn_list)
    
    print(f"Extracted ingredients from query '{query}': {ingredients}")
    return list(expanded_ingredients)

# Extract mood from query 
def extract_mood(query):
    mood_map = {
        "festive": ["festive", "celebration", "party"],
        "comfort": ["comfort", "cozy", "relaxing"],
        "quick": ["quick", "fast", "easy"],
        "healthy": ["healthy", "light", "fresh"],
    }
    query_lower = query.lower()
    for mood, keywords in mood_map.items():
        if any(keyword in query_lower for keyword in keywords):
            print(f" Detected mood: {mood}")
            return mood
    print("No mood detected")
    return None

# Retrieve similar recipes
def retrieve_similar_recipes(query, df, model, index, k=3):
    try:
        if not query.strip():
            print("Query is empty")
            return None, "Please provide a valid query."
        
        ingredients = extract_ingredients(query)
        if ingredients:
            print(f"Filtering recipes with ingredients: {ingredients}")
            filtered_df = df[df['Ingredients'].str.lower().apply(
                lambda x: any(ing in x.lower() for ing in ingredients)
            )]
            if filtered_df.empty:
                print("No recipes found with the provided ingredients")
                return None, "No recipes found with the provided ingredients in the dataset."
            
            filtered_indices = filtered_df.index.tolist()
            query_embedding = model.encode([query])
            embeddings = model.encode(filtered_df['combined'].tolist())
            temp_index = faiss.IndexFlatL2(embeddings.shape[1])
            temp_index.add(embeddings)
            D, I = temp_index.search(query_embedding, min(k, len(filtered_df)))
            print(f"Retrieved recipes (ingredient-based): {filtered_df.iloc[I[0]]['RecipeName'].tolist()}")
            return df.iloc[filtered_indices].iloc[I[0]], None
        else:
            print(" No ingredients found, performing semantic search")
            query_embedding = model.encode([query])
            D, I = index.search(query_embedding, k)
            retrieved_recipes = df.iloc[I[0]]
            print(f"Retrieved recipes (semantic search): {retrieved_recipes['RecipeName'].tolist()}")
            return retrieved_recipes, None
    except Exception as e:
        print(f" Error retrieving recipes: {str(e)}")
        return None, f"Error retrieving recipes: {str(e)}"

# Generate response using Groq API
def generate_response(query, df, model, index):
    try:
        print(f"Processing query: {query}")
        mood = extract_mood(query)
        mood_context = f"The user is in a {mood} mood, so suggest recipes that match this vibe. " if mood else ""

        context_df, error = retrieve_similar_recipes(query, df, model, index)
        
        if error:
            print(f" No recipes found in dataset, falling back to AI generation: {error}")
            prompt = f"""You are Recipe Buddy, a creative recipe assistant. A user asked: '{query}'.
{mood_context}Unfortunately, I couldn't find any recipes in my dataset that match your request.

Instead, please generate a recipe based on the user's query. Format the response as follows:
1. **Acknowledgment**: A friendly acknowledgment of the query.
2. **Recipe Details**:
   - **Name**: The name of the recipe.
   - **Cuisine**: The cuisine type (e.g., Indian).
   - **Diet**: The diet type (e.g., Vegetarian, Non-Vegetarian).
   - **Ingredients**: A list of key ingredients in bullet points.
   - **Method**: A list of preparation steps in bullet points.
3. **Closing Note**: A closing note encouraging the user to try the recipe or ask for more.

Use a warm, conversational tone."""
        else:
            context = "\n\n".join(context_df['combined'].tolist())
            print(f"Recipes found in dataset, using context: {context[:100]}...")
            prompt = f"""You are Recipe Buddy, a creative recipe assistant. A user asked: '{query}'.
{mood_context}Here are relevant recipes:

{context}

Provide a concise, engaging response in the following format:
1. **Acknowledgment**: A friendly acknowledgment of the query.
2. **Suggested Recipes**: A list of 2-3 recipes, each with:
   - **Name**: The name of the recipe.
   - **Cuisine**: The cuisine type (e.g., Indian).
   - **Diet**: The diet type (e.g., Vegetarian, Non-Vegetarian).
   - **Ingredients**: A list of key ingredients in bullet points.
   - **Method**: A list of preparation steps in bullet points.
3. **Closing Note**: A closing note encouraging the user to try the recipes or ask for more.

Use a warm, conversational tone."""

        print("Sending prompt to Groq API...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful recipe assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        response_content = response.choices[0].message.content
        print(f"Groq API response received: {response_content[:100]}...")
        return response_content
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        print(f"{error_msg}")
        return error_msg

def main():
    print("Welcome to Recipe Buddy! Ask for a recipe or provide ingredients.")
    print("You can also mention your mood (e.g., 'festive', 'comfort', 'quick') to get vibe-based suggestions!")
    print("Type 'exit' to quit.")
    
    try:
        df = load_dataset()
        model, index = initialize_index(df)
    except Exception as e:
        print(f"Initialization failed: {str(e)}")
        return
    
    while True:
        query = input("\nWhat recipe, ingredients, or mood? ")
        if query.lower() == 'exit':
            print("Happy cooking!")
            break
        
        response = generate_response(query, df, model, index)
        print("\n" + response)

if __name__ == "__main__":
    main()
