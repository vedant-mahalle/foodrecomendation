from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

data = pd.read_csv("meal_dataset.csv")
features = data[['calories', 'protein', 'fat', 'carbs']]
scaler = StandardScaler()
normalized_features = scaler.fit_transform(features)

knn = NearestNeighbors(n_neighbors=5, metric='euclidean')
knn.fit(normalized_features)

def calculate_bmi(weight, height):
    height = height / 100  
    bmi = weight / (height ** 2)
    return bmi

import numpy as np  # Make sure to import numpy

def recommend_meal(user_bmi, user_region, user_diet, user_allergies):
    # Filtering meals based on user input
    filtered_data = data[data["region"].str.lower() == user_region.lower()]

    if user_diet.lower() != "none":
        filtered_data = filtered_data[filtered_data["diet_type"].str.lower() == user_diet.lower()]

    # Remove meals with allergens
    def contains_allergen(ingredients):
        if pd.isna(ingredients) or ingredients.lower() == "none":  
            return False
        ingredients_list = [item.strip().lower() for item in ingredients.split(",")]
        return any(allergen in ingredients_list for allergen in user_allergies)

    filtered_data = filtered_data[~filtered_data["ingredients"].apply(contains_allergen)]
    
    if filtered_data.empty:
        return []

    # Normalize and recommend meals
    feature_columns = ['calories', 'protein', 'fat', 'carbs']
    scaler.fit(filtered_data[feature_columns])
    
    query = [[500, 40, 20, 60] if user_bmi < 18.5 else [400, 30, 15, 50]]  
    query_norm = scaler.transform(pd.DataFrame(query, columns=feature_columns))
    
    knn.fit(scaler.transform(filtered_data[feature_columns]))
    distances, indices = knn.kneighbors(query_norm)

    recommended = filtered_data.iloc[indices[0]].copy()
    
    # ✅ Convert NaN values in "ingredients" column
    recommended["ingredients"] = recommended["ingredients"].replace(np.nan, "None")

    return recommended.to_dict(orient='records')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        print(data)

        if not data:
            return jsonify({"error": "Invalid JSON received"}), 400

        weight = float(data.get('weight', 0))
        height = float(data.get('height', 0))
        region = data.get('region', "").strip()
        diet = data.get('diet', "none").strip().lower()
        allergies = data.get('allergies', [])

        if weight <= 0 or height <= 0:
            return jsonify({"error": "Weight and height must be positive numbers"}), 400

        bmi = round(weight / ((height / 100) ** 2), 2)

        # Get recommended meals
        recommended_meals = recommend_meal(bmi, region, diet, allergies)  # Call the function
        print(recommended_meals)
        return jsonify({"bmi": bmi, "meals": recommended_meals}) # ✅ Proper JSON format


    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
