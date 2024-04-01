import os
from flask import Flask, request, jsonify
from googlesearch import search
from bs4 import BeautifulSoup as bs
import requests
from PIL import Image
from io import BytesIO
import google.generativeai as genai
import base64

app = Flask(__name__)

# Function to perform Google Image Search for the bird
def google_image_search(bird_name):
    params = {
        "q": f"{bird_name} bird",
        "tbm": "isch",
    }

    html = requests.get("https://www.google.com/search", params=params, timeout=30)
    soup = bs(html.content, 'html.parser')

    images = soup.select('div img')
    if len(images) > 1:
        return images[1]['src']
    else:
        return None

# Function to get information using Gemini
def get_gemini_info(query):
    # Replace 'YOUR_API_KEY' with your actual Google API key
    genai.configure(api_key="AIzaSyCDB2nPeHI_Csv9lmsfSH6UK91l-jVXQMc")

    # Initialize a GenerativeModel instance with 'gemini-pro' model
    model = genai.GenerativeModel('gemini-pro')

    # Generate content using Gemini
    response = model.generate_content(f"Summary of it in 150 words ,if the name is bird then only give the response otherwise don't respond back  {query}")

    # Limit the response to approximately 150 words
    limited_response = ' '.join(response.text.split()[:150])

    return {'summary': limited_response}  # Assuming Gemini does not return image URLs

# Define a route for handling bird information
@app.route('/bird_info', methods=['POST'])
def get_bird_info():
    input_bird_name = request.json.get('bird_name')

    # Check if the input is a bird name using Gemini
    gemini_info = get_gemini_info(input_bird_name)
    if "bird" not in gemini_info['summary'].lower():
        return jsonify({'message': 'Only enter the name of the bird'}), 400

    # Perform Google Image Search for the bird
    bird_image_url = google_image_search(input_bird_name)
    print(f"Image URL: {bird_image_url}")

    if bird_image_url:
        # Download the image
        response = requests.get(bird_image_url)
        img = Image.open(BytesIO(response.content))

        # Convert image to base64
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return jsonify({'bird_name': input_bird_name, 'summary': gemini_info['summary'], 'image': img_str}), 200
    else:
        return jsonify({'message': 'No image found for the given bird name'}), 404

if __name__ == '__main__':
    app.run(debug=False, port=8080)  # Run the app on port 8080