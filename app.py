from flask import Flask, request, jsonify
from googlesearch import search
from bs4 import BeautifulSoup as bs
import requests
import google.generativeai as genai

app = Flask(__name__)


# Function to extract image URL from Google search results
def extract_image_url(search_query):
    search_results = search(search_query, num=10, stop=10, pause=2)

    for url in search_results:
        html = requests.get(url, timeout=30)
        soup = bs(html.content, 'html.parser')
        img_tags = soup.find_all('img')
        for img_tag in img_tags:
            img_url = img_tag.get('src')
            if img_url and img_url.startswith('http'):
                return img_url
    return None


# Function to perform Google Image Search for the bird
def google_image_search(bird_name):
    search_query = f"{bird_name} bird HD"
    return extract_image_url(search_query)

# Function to get information using Gemini
def get_gemini_info(query):
    # Replace 'YOUR_API_KEY' with your actual Google API key
    genai.configure(api_key="AIzaSyCDB2nPeHI_Csv9lmsfSH6UK91l-jVXQMc    ")

    # Initialize a GenerativeModel instance with 'gemini-pro' model
    model = genai.GenerativeModel('gemini-pro')

    # Generate content using Gemini
    response = model.generate_content(f"Summary of {query} bird in 150 words.")

    # Limit the response to approximately 150 words
    limited_response = ' '.join(response.text.split()[:150])

    return {'summary': limited_response}  # Assuming Gemini does not return image URLs

# Define a route for handling bird information
@app.route('/bird_info', methods=['POST'])
def get_bird_info():
    input_bird_name = request.json.get('bird_name').capitalize()

    # Check if the input is a bird name using Gemini
    gemini_info = get_gemini_info(input_bird_name)
    if "bird" not in gemini_info['summary'].lower():
        return jsonify({'message': 'Only enter the name of the bird'}), 400

    # Perform Google Image Search for the bird
    bird_image_url = google_image_search(input_bird_name)
    print(f"Image URL: {bird_image_url}")

    if bird_image_url:
        return jsonify({'bird_name': input_bird_name, 'summary': gemini_info['summary'], 'image_url': bird_image_url}), 200

    else:
        return jsonify({'message': 'No HD image found for the given bird name'}), 404

if __name__ == '__main__':
    app.run(debug=False, port=8080)  # Run the app on port 8080
