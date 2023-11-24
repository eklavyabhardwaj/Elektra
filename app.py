from flask import Flask, render_template, request, jsonify,url_for
import requests
import random
import json
import pandas as pd
from markupsafe import Markup
from sklearn.neural_network import MLPClassifier
from sklearn.feature_extraction.text import TfidfVectorizer


# Load the CSV file into a DataFrame
csv_file_path = "machine_password.csv"
df = pd.read_csv(csv_file_path)

# Drop rows with missing values
df = df.dropna(axis=0, how='any')
# df = df.fillna(axis=0, how='any')

# Preprocess the data
texts = df['Machine'] + ' ' + df['Purpose']
labels = df['Target Variable']

# Convert text to numeric representation using TF-IDF vectorizer
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)
y = labels

# Build and train the Random Forest classifier
# Build and train the Artificial Neural Network (MLP classifier)
mlp_classifier = MLPClassifier(hidden_layer_sizes=(100,), max_iter=300, random_state=42)
mlp_classifier.fit(X, y)


app = Flask(__name__, static_url_path='/static', static_folder='static')


RASA_API_ENDPOINT = "http://localhost:5005/model/parse"  # Default Rasa API endpoint
#JSON_DATA_FILE = "C:/Users/Eklavyab/ElectrolabChatBOT/data/passworddata.json"  # Update with the actual path to your JSON file

# Load the JSON data
# with open(JSON_DATA_FILE, 'r') as json_file:
    # machine_data = json.load(json_file)

@app.route("/")
def home():
    return render_template("index.html")

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

            # Pass the user's message to generate_response
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


        response_text = "Sure! Let's calculate the realization. "

        response_text += f'<a href={url_for("calculate_realization_page")}>Click here to proceed.</a>'




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


@app.route("/calculate_realization_page")
def calculate_realization_page():
    # Render the template for the new page where the user can input details for the calculation
    return render_template("calculate_realization_page.html")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
