from flask import Flask, request, jsonify
from googlesearch import search
from bs4 import BeautifulSoup
import requests
import google.generativeai as genai

app = Flask(__name__)


# Function to perform Google Search
def google_search(query):
    try:
        # Include both common and scientific names in the search query
        search_query = f"{query} bird {query.split()[0]}"
        search_results = list(search(search_query, num=1, stop=1))

        if search_results:
            first_result = search_results[0]
            title = first_result
            link = first_result
            return [{'title': title, 'link': link}]
        else:
            return []
    except Exception as e:
        print(f"Error in Google Search: {e}")
        return []

def get_wikipedia_info(bird_name):
    try:
        # Perform a Google search to find the Wikipedia page for the bird
        google_results = google_search(bird_name)
        wiki_link = google_results[0]['link'] if google_results else None

        if wiki_link:
            response = requests.get(wiki_link)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract image URL
            img_tag = soup.find('meta', {'property': 'og:image'})
            image_url = img_tag['content'] if img_tag else None

            return {'image_url': image_url}
        else:
            return {'image_url': None}
    except Exception as e:
        print(f"Error getting Wikipedia information: {e}")
        return {'image_url': None}

    
# Function to perform Google Image Search for the bird
def get_gemini_info(query):
    # Replace 'YOUR_API_KEY' with your actual Google API key
    genai.configure(api_key="AIzaSyCDB2nPeHI_Csv9lmsfSH6UK91l-jVXQMc")

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
    bird_image_url = get_wikipedia_info(input_bird_name)
    print(f"Image URL: {bird_image_url}")

    if bird_image_url:
        return jsonify({'bird_name': input_bird_name, 'summary': gemini_info['summary'], 'image_url': bird_image_url}), 200

    else:
        return jsonify({'message': 'No HD image found for the given bird name'}), 404

if __name__ == '__main__':
    app.run(debug=False, port=8080)  # Run the app on port 8080
