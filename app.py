from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from bmi_utils import calculate_bmi, get_bmi_category, get_health_tips  # Importing from bmi_utils

app = Flask(__name__)

# Load dataset
data = pd.read_csv("meal_dataset.csv")

# Initial KNN model setup (global)
features = data[['calories', 'protein', 'fat', 'carbs']]
scaler = StandardScaler()
normalized_features = scaler.fit_transform(features)

knn = NearestNeighbors(n_neighbors=5, metric='euclidean')
knn.fit(normalized_features)

# Meal recommendation function (same as before)
def recommend_meal(user_bmi, user_region, user_diet, user_allergies):
    filtered_data = data[data["region"].str.lower() == user_region.lower()]

    if user_diet.lower() != "none":
        filtered_data = filtered_data[filtered_data["diet_type"].str.lower() == user_diet.lower()]

    def contains_allergen(ingredients):
        if pd.isna(ingredients) or ingredients.lower() == "none":
            return False
        ingredients_list = [item.strip().lower() for item in ingredients.split(",")]
        return any(allergen in ingredients_list for allergen in user_allergies)

    filtered_data = filtered_data[~filtered_data["ingredients"].apply(contains_allergen)]

    if filtered_data.empty:
        return []

    feature_columns = ['calories', 'protein', 'fat', 'carbs']
    scaler.fit(filtered_data[feature_columns])

    if user_bmi < 18.5:
        query = [[500, 40, 20, 60]]  # Underweight
    elif user_bmi < 25:
        query = [[400, 30, 15, 50]]  # Normal weight
    elif user_bmi < 30:
        query = [[300, 25, 10, 40]]  # Overweight
    else:
        query = [[250, 20, 5, 30]]   # Obese

    query_norm = scaler.transform(pd.DataFrame(query, columns=feature_columns))

    knn.fit(scaler.transform(filtered_data[feature_columns]))
    distances, indices = knn.kneighbors(query_norm)

    recommended = filtered_data.iloc[indices[0]].copy()
    recommended["ingredients"] = recommended["ingredients"].replace(np.nan, "None")

    return recommended.to_dict(orient='records')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_data = request.get_json()
        print("Received User Data:", user_data)

        age = int(user_data.get('age', 0))
        gender = user_data.get('gender', "").strip().lower()
        height = float(user_data.get('height', 0))
        weight = float(user_data.get('weight', 0))
        region = user_data.get('region', "").strip()
        diet = user_data.get('preference', "none").strip().lower()
        allergies = [a.strip().lower() for a in user_data.get('allergies', [])]

        if height <= 0 or weight <= 0 or not region:
            return jsonify({"error": "Invalid height, weight, or region"}), 400

        bmi = calculate_bmi(weight, height)
        bmi_category = get_bmi_category(bmi)

        recommended_meals = recommend_meal(bmi, region, diet, allergies)

        health_insights = get_health_tips(age, gender, bmi_category)

        response = {
            "bmi": bmi,
            "bmi_category": bmi_category,
            "meals": recommended_meals,
            "health_tips": health_insights["health_tips"],
            "exercise_recommendations": health_insights["exercise_recommendations"]
        }

        print(f"User BMI: {bmi:.2f}, Category: {bmi_category}")
        print(f"Recommended Meals: {recommended_meals}")

        return jsonify(response)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
