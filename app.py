from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import random
import pandas as pd
from markupsafe import Markup
from sklearn.neural_network import MLPClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from playwright.sync_api import sync_playwright
import secrets
from datetime import datetime, timedelta


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
        return render_template("index.html")
    return redirect(url_for("login"))

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

            return render_template("index.html")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html", error=None)

def check_erp_credentials(username, password):
    with sync_playwright() as p:
        #browser = p.chromium.launch(headless=False)
        browser = p.chromium.launch()
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
        print("Waiting for an additional 5 seconds...")
        page.wait_for_timeout(5000)  # 20,000 milliseconds = 20 seconds

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

    # Example: Determine the user_intent (you'll need to replace this with your actual logic)
    user_intent = "some_intent"  # Placeholder, replace with actual intent determination logic

    if 'machine_name' in session:
        # Updated to include user_intent
        response = handle_follow_up(user_intent, user_message, session['machine_name'])
        session.pop('machine_name', None)
    elif 'asked_for_machine_name' in session and session['asked_for_machine_name']:
        session['machine_name'] = user_message
        response = handle_machine_name_response(user_message)
        session['asked_for_machine_name'] = False
    else:
        response = interpret_message(user_message)
        # Handle setting 'asked_for_machine_name' as needed

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
    if intent == "machine_purpose":
        user_question = request.form["user_message"]
        user_vector = vectorizer.transform([user_question])
        predicted_label = mlp_classifier.predict(user_vector)
        confidence = mlp_classifier.predict_proba(user_vector).max() * 100

        if confidence >= 75:
            # Generate a dynamic response based on the predicted label
            response_text = predicted_label[0]
        else:  # confidence < 75, this is the only other option
            # Ask for the machine name if confidence is less than 75%
            response_text = "I'm not quite sure which machine you're referring to. Could you please tell me the machine name?"
            # Set a flag in the session to remember that we've asked for the machine name
            session['asked_for_machine_name'] = True





    elif intent == "thankmessage":

        greetings = [

            "Happy to help!",

            "You're welcome!",

            "Glad I could assist you!",

            "No problem, anytime!",

            "It was my pleasure!",

            "You got it! If you have more questions, feel free to ask.",

            "Always here to help!",

            "Anytime! If you need further assistance, just let me know.",

        ]

        response_text = random.choice(greetings)


    elif intent == "greet":

        current_time = datetime.now().time()

        hour = current_time.hour

        if 5 <= hour < 12:

            greeting = "Good morning!"

        elif 12 <= hour < 17:

            greeting = "Good afternoon!"

        elif 17 <= hour < 21:

            greeting = "Good evening!"

        else:

            greeting = "Hello!"

        random_responses = [

            "How can I assist you today?",

            "What can I do for you?",

            "How can I help?",

            "Is there something specific you're looking for?",

            "What brings you here?",

        ]

        response_text = f"{greeting} {random.choice(random_responses)}"



    elif intent == 'goodbye':

        current_time = datetime.now().time()

        hour = current_time.hour

        if 5 <= hour < 12:

            time_greeting = "Have a wonderful morning!"

        elif 12 <= hour < 17:

            time_greeting = "Enjoy your afternoon!"

        elif 17 <= hour < 21:

            time_greeting = "Wishing you a pleasant evening!"

        else:

            time_greeting = "Goodnight!"

        goodbye_responses = [

            "It was my pleasure to assist you. Goodbye!",

            "Goodbye! Have a Nice Day.",

            f"Take care! {time_greeting}",

            "Farewell! If you need further assistance, feel free to ask.",

            "Until next time! Stay safe and have a great day!",

        ]

        response_text = random.choice(goodbye_responses)

    else:
        response_text = "I'm not sure how to respond to that."




        # Replace '\n' with '<br>'
    response_text = response_text.replace('\\n', '<br>')

        # Use Markup to render HTML tags
    response_text = Markup(response_text)

    return response_text


def handle_machine_name_response(machine_name):
    response_text = f"Thank you for providing the machine name: {machine_name}. " \
                    "What specific information or action are you looking for regarding this machine?"
    return response_text


def handle_follow_up(user_intent, user_message, machine_name):
    # Combine the machine name with the user message to create a new query context
    combined_input = f"{machine_name} {user_message}"

    # Transform the combined input using the TF-IDF vectorizer
    combined_vector = vectorizer.transform([combined_input])

    # Use the MLP classifier to predict the label for the combined input
    predicted_label = mlp_classifier.predict(combined_vector)
    confidence = mlp_classifier.predict_proba(combined_vector).max() * 100

    # Generate a response based on the predicted label and confidence level
    if confidence >= 75:
        # If the confidence is high, generate a dynamic response based on the predicted label
        response_text = f"Based on your query about '{user_message}' for the machine '{machine_name}',  " \
                        f"{predicted_label[0]}"
    else:
        # If the confidence is low, ask for clarification or provide a generic response
        response_text = "I'm not quite sure about your request. Could you please provide more details or clarify your query?"

    # Use Markup to render HTML tags if needed and return the response
    response_text = Markup(response_text.replace('\n', '<br>'))
    return response_text




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
