from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import random
import json
import pandas as pd
from markupsafe import Markup
from sklearn.neural_network import MLPClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from playwright.sync_api import sync_playwright
import secrets
from datetime import timedelta



app = Flask(__name__, static_url_path='/static', static_folder='static')
# Define a secret key for session management
app.secret_key = secrets.token_hex(16)

# Load the CSV file into a DataFrame
csv_file_path = "machine_password.csv"
df = pd.read_csv(csv_file_path)

# Drop rows with missing values
df = df.dropna(axis=0, how='any')

# Preprocess the data
texts = df['Machine'] + ' ' + df['Purpose']
labels = df['Target Variable']

# Convert text to numeric representation using TF-IDF vectorizer
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)
y = labels

# Build and train the Artificial Neural Network (MLP classifier)
mlp_classifier = MLPClassifier(hidden_layer_sizes=(100,), max_iter=300, random_state=42)
mlp_classifier.fit(X, y)

# Define ERP login details (replace with your actual details)
ERP_USERNAME = "your_username"
ERP_PASSWORD = "your_password"

RASA_API_ENDPOINT = "http://localhost:5005/model/parse"

@app.route("/")
def home():
    if 'username' in session:
        return redirect(url_for("calculate_realization_page"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember")  # Check if the "Remember Me" checkbox is checked

        if check_erp_credentials(username, password):
            session['username'] = username  # Store the username in the session

            # Set a cookie or use session to remember login information if "Remember Me" is checked
            if remember == "on":
                # Set a cookie or use session to remember login information
                # Example using session:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=7)  # Adjust as needed

            return redirect(url_for("calculate_realization_page"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html", error=None)

def check_erp_credentials(username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the ERP login page
        print("Navigating to the ERP login page...")
        page.goto("https://erp.electrolabgroup.com/login#login")

        # Fill in the login credentials
        print(f"Filling in the username: {username}")
        email_input = page.wait_for_selector('//*[@id="login_email"]', timeout=10000)
        email_input.type(username)

        print("Filling in the password...")
        password_input = page.wait_for_selector('//*[@id="login_password"]', timeout=10000)
        password_input.type(password)

        # Find the login button and click it
        print("Clicking the login button...")
        login_button = page.wait_for_selector('//*[@id="page-login"]/div/main/div[2]/div/section[1]/div[1]/form/div[2]/button', timeout=10000)
        login_button.click()

        # Wait for navigation or load state to ensure the login process is completed
        print("Waiting for the login process to complete...")
        page.wait_for_load_state("load")

        # Wait for an additional 20 seconds (adjust as needed)
        print("Waiting for an additional 20 seconds...")
        page.wait_for_timeout(20000)  # 20,000 milliseconds = 20 seconds

        # Check the current URL after login
        current_url = page.url

        # Check if the URL matches the expected one
        is_logged_in = current_url.startswith("https://erp.electrolabgroup.com/app")

        if is_logged_in:
            print("Login successful!")
        else:
            print("Login failed.")

        # Close the browser
        context.close()
        browser.close()

        return is_logged_in

@app.route("/calculate_realization_page")
def calculate_realization_page():
    if 'username' not in session:
        return redirect(url_for("login"))
    return render_template("calculate_realization_page.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_message = request.form["user_message"]
    response = interpret_message(user_message)
    return jsonify(response)

def interpret_message(message):
    payload = {"text": message}
    try:
        response = requests.post(RASA_API_ENDPOINT, json=payload)

        if response.status_code == 200:
            result = response.json()
            intent = result.get("intent", {}).get("name", "No intent detected")
            entities = result.get("entities", [])
            print(f"Intent: {intent}")
            print(f"Entities: {entities}")

            response_text = generate_response(intent, entities, message)

            return response_text
        else:
            return "Error in parsing message"
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Rasa server: {e}")
        return "Error connecting to Rasa server"


def generate_response(intent, entities, message):
    if intent == "get_password":
        # Take the whole question asked by the user
        user_question = request.form["user_message"]

        # Convert the user's question to the same numeric representation used during training
        user_vector = vectorizer.transform([user_question])

        # Make a prediction using the trained MLP classifier
        predicted_label = mlp_classifier.predict(user_vector)

        # Get the confidence of the prediction
        confidence = mlp_classifier.predict_proba(user_vector).max() * 100

        if confidence >= 25:
            # Customize the response based on the predicted password
            response_text = f"{predicted_label[0]} Confidence: {confidence:.2f}%"
        else:
            response_text = "No password for the provided input."



    elif intent == "access_serial_no":
        # Take the whole question asked by the user
        user_question = request.form["user_message"]

        # Convert the user's question to the same numeric representation used during training
        user_vector = vectorizer.transform([user_question])

        # Make a prediction using the trained MLP classifier
        predicted_label = mlp_classifier.predict(user_vector)

        # Get the confidence of the prediction
        confidence = mlp_classifier.predict_proba(user_vector).max() * 100

        if confidence >= 25:
            # Customize the response based on the predicted password
            response_text = f"{predicted_label[0]} Confidence: {confidence:.2f}%"
        else:
            response_text = "No password for the provided input."




    elif intent == 'access_username':

        # Take the whole question asked by the user
        user_question = request.form["user_message"]

        # Convert the user's question to the same numeric representation used during training
        user_vector = vectorizer.transform([user_question])

        # Make a prediction using the trained MLP classifier
        predicted_label = mlp_classifier.predict(user_vector)

        # Get the confidence of the prediction
        confidence = mlp_classifier.predict_proba(user_vector).max() * 100

        if confidence >= 25:
            # Customize the response based on the predicted password
            response_text = f"{predicted_label[0]} Confidence: {confidence:.2f}%"
        else:
            response_text = "No password for the provided input."


    elif intent == 'change_serial_no':
        # Take the whole question asked by the user
        user_question = request.form["user_message"]

        # Convert the user's question to the same numeric representation used during training
        user_vector = vectorizer.transform([user_question])

        # Make a prediction using the trained MLP classifier
        predicted_label = mlp_classifier.predict(user_vector)

        # Get the confidence of the prediction
        confidence = mlp_classifier.predict_proba(user_vector).max() * 100

        if confidence >= 25:
            # Customize the response based on the predicted password
            response_text = f"{predicted_label[0]} Confidence: {confidence:.2f}%"
        else:
            response_text = "No password for the provided input."



    elif intent == 'password_reset_procedure':
        # Take the whole question asked by the user
        user_question = request.form["user_message"]

        # Convert the user's question to the same numeric representation used during training
        user_vector = vectorizer.transform([user_question])

        # Make a prediction using the trained MLP classifier
        predicted_label = mlp_classifier.predict(user_vector)

        # Get the confidence of the prediction
        confidence = mlp_classifier.predict_proba(user_vector).max() * 100

        if confidence >= 25:
            # Customize the response based on the predicted password
            response_text = f"{predicted_label[0]} Confidence: {confidence:.2f}%"
        else:
            response_text = "No password for the provided input."



    elif intent == 'factory_setting_access':
        # Take the whole question asked by the user
        user_question = request.form["user_message"]

        # Convert the user's question to the same numeric representation used during training
        user_vector = vectorizer.transform([user_question])

        # Make a prediction using the trained MLP classifier
        predicted_label = mlp_classifier.predict(user_vector)

        # Get the confidence of the prediction
        confidence = mlp_classifier.predict_proba(user_vector).max() * 100

        if confidence >= 25:
            # Customize the response based on the predicted password
            response_text = f"{predicted_label[0]} Confidence: {confidence:.2f}%"
        else:
            response_text = "No password for the provided input."



    elif intent == 'get_instrument_id':
        # Take the whole question asked by the user
        user_question = request.form["user_message"]

        # Convert the user's question to the same numeric representation used during training
        user_vector = vectorizer.transform([user_question])

        # Make a prediction using the trained MLP classifier
        predicted_label = mlp_classifier.predict(user_vector)

        # Get the confidence of the prediction
        confidence = mlp_classifier.predict_proba(user_vector).max() * 100

        if confidence >= 25:
            # Customize the response based on the predicted password
            response_text = f"{predicted_label[0]} Confidence: {confidence:.2f}%"
        else:
            response_text = "No password for the provided input."





    elif intent == "calculate_realization":

        # Provide a message with a link to the new page for the calculation


        response_text = "Sure! Let's calculate the realization. \n"

        response_text += f'<a class = link-button href={url_for("calculate_realization_page")}>Click here to proceed.</a>'




    elif intent == "greet":
        greetings = [
            "Hello! How can I assist you today?",
            "Hi there! What can I do for you?",
            "Hey! How can I help?",
            "Greetings! Is there something I can help you with?",
            "Good day! What brings you here?",
        ]
        response_text = random.choice(greetings)

    elif intent == 'goodbye':
        goodbye = [
            "It was my pleasure to assist you. Goodbye!",
            "Goodbye! Have a Nice Day."
        ]
        response_text = random.choice(goodbye)

    else:
        response_text = "I'm not sure how to respond to that."




        # Replace '\n' with '<br>'
    response_text = response_text.replace('\n', '<br>')

        # Use Markup to render HTML tags
    response_text = Markup(response_text)

    return response_text






if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
