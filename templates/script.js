document.getElementById("mealForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    // Get input values
    const weight = parseFloat(document.getElementById("weight").value.trim());
    const height = parseFloat(document.getElementById("height").value.trim());
    const region = document.getElementById("region").value.trim();
    const diet = document.getElementById("diet").value.trim();
    const allergies = document.getElementById("allergies").value.trim()
        ? document.getElementById("allergies").value.split(',').map(a => a.trim().toLowerCase())
        : [];

    // Validate required fields
    if (isNaN(weight) || isNaN(height) || region === "") {
        document.getElementById("results").innerHTML = `<p style="color:red;">Please enter valid values for weight, height, and region.</p>`;
        return;
    }

    // Prepare request data
    const requestData = { weight, height, region, diet, allergies };

    try {
        // Send request to backend
        const response = await fetch("/recommend", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`Server Error: ${response.status}`);
        }

        const data = await response.json();

        // Handle errors from backend
        if (data.error) {
            document.getElementById("results").innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
            return;
        }

        // Display results
        displayResults(data);
    } catch (error) {
        console.error("Error fetching data:", error);
        document.getElementById("results").innerHTML = `<p style="color:red;">Failed to fetch data. Please try again later.</p>`;
    }
});

function displayResults(data) {
    let resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = `<h3>Your BMI: ${data.bmi.toFixed(2)}</h3>`;

    if (!data.meals || data.meals.length === 0) {
        resultsDiv.innerHTML += "<p>No meals found for your preferences.</p>";
        return;
    }

    let mealsHTML = "<h3>Recommended Meals</h3><ul>";
    data.meals.forEach(meal => {
        mealsHTML += `
            <li>
                <strong>${meal["Food Name"] || "Unnamed Meal"}</strong> - 
                ${meal.calories} kcal, 
                ${meal.protein}g protein, 
                ${meal.fat}g fat, 
                ${meal.carbs}g carbs
            </li>`;
    });
    mealsHTML += "</ul>";

    resultsDiv.innerHTML += mealsHTML;
}
