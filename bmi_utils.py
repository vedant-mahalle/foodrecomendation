# bmi_utils.py

def calculate_bmi(weight, height):
    height = height / 100  # Convert cm to meters
    bmi = weight / (height ** 2)
    return bmi

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def get_health_tips(age, gender, bmi_category):
    tips = []
    exercises = []

    if age < 18:
        tips.append("Ensure a balanced diet rich in proteins and vitamins for healthy growth.")
        exercises.append("Focus on outdoor games, swimming, and cycling.")
    elif age < 40:
        tips.append("Maintain a balanced diet with lean proteins, whole grains, and vegetables.")
        exercises.append("Include cardio, strength training, and flexibility exercises.")
    elif age < 60:
        tips.append("Watch portion sizes and maintain good hydration.")
        exercises.append("Include brisk walking, light strength training, and yoga.")
    else:
        tips.append("Focus on fiber-rich foods and foods rich in calcium and vitamin D.")
        exercises.append("Walking, stretching, and light aerobics are recommended.")

    if gender == "female":
        tips.append("Ensure adequate calcium and iron intake.")
    elif gender == "male":
        tips.append("Focus on heart health with fiber-rich and low-fat foods.")

    if bmi_category == "Underweight":
        tips.append("Increase healthy calorie intake with nuts, avocados, and dairy.")
        exercises.append("Include light resistance training to build muscle.")
    elif bmi_category == "Overweight":
        tips.append("Reduce refined carbs and sugary drinks.")
        exercises.append("Prioritize cardio and HIIT workouts.")
    elif bmi_category == "Obese":
        tips.append("Consult a nutritionist for a personalized meal plan.")
        exercises.append("Start with low-impact exercises like swimming or walking.")

    return {"health_tips": tips, "exercise_recommendations": exercises}
