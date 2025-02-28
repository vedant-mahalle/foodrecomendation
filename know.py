from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

# Load and preprocess data
data = pd.read_csv("meal_dataset.csv")
features = data[['calories', 'protein', 'fat', 'carbs']]
scaler = StandardScaler()
normalized_features = scaler.fit_transform(features)

knn = NearestNeighbors(n_neighbors=5, metric='euclidean')
knn.fit(normalized_features)

# Function to calculate BMI
def calculate_bmi(weight, height):
    height = height / 100  
    return weight / (height ** 2)

# Function to recommend meals
def recommend_meal(user_bmi, user_region, user_diet, user_allergies):
    user_allergies = [allergy.lower() for allergy in user_allergies]

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

    # Define target nutrient profile based on BMI
    if user_bmi < 18.5:
        query = [500, 40, 20, 60]
    elif 18.5 <= user_bmi < 25:
        query = [400, 30, 15, 50]
    elif 25 <= user_bmi < 30:
        query = [300, 25, 10, 40]
    else:
        query = [250, 20, 8, 30]

    query_df = pd.DataFrame([query], columns=['calories', 'protein', 'fat', 'carbs'])

    # Standardize query using the same scaler
    scaler.fit(filtered_data[['calories', 'protein', 'fat', 'carbs']])
    query_norm = scaler.transform(query_df)

    knn.fit(scaler.transform(filtered_data[['calories', 'protein', 'fat', 'carbs']]))
    distances, indices = knn.kneighbors(query_norm)

    return filtered_data.iloc[indices[0]].to_dict(orient='records')

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        request_data = request.get_json()

        if not request_data:
            return jsonify({"error": "Invalid JSON received"}), 400

        weight = float(request_data.get('weight', 0))
        height = float(request_data.get('height', 0))
        region = request_data.get('region', "").strip()
        diet = request_data.get('diet', "none").strip().lower()
        allergies = request_data.get('allergies', [])

        if weight <= 0 or height <= 0:
            return jsonify({"error": "Weight and height must be positive numbers"}), 400

        bmi = round(calculate_bmi(weight, height), 2)

        # Get meal recommendations
        recommended_meals = recommend_meal(bmi, region, diet, allergies)

        return jsonify({"bmi": bmi, "meals": recommended_meals})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
