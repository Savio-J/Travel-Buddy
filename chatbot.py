from flask import request, jsonify
from openai import OpenAI
from github_fetch import fetch_github_file

# Mistral API Setup (Using Together AI as the provider)
MISTRAL_API_KEY = "*********************************"
client = OpenAI(api_key=MISTRAL_API_KEY, base_url="https://api.mistral.ai/v1")

# Mapping user queries to relevant HTML files
FILE_MAP = {
    "achievements": "templates/achievements.html",
    "base layout": "templates/base.html",
    "dashboard": "templates/dashboard.html",
    "home": "templates/home.html",
    "homepage": "templates/index.html",
    "leaderboard": "templates/leaderboard.html",
    "map page": "templates/map.html",
    "login": "templates/login.html",
    "recommendations": "templates/recommendations.html",
}

def determine_relevant_file(user_query):
    """Decides which file to fetch based on the query."""
    for keyword, file_path in FILE_MAP.items():
        if keyword in user_query.lower():
            return file_path

    # If query is about navigation or menu, return index.html
    if "menu" in user_query.lower() or "navigation" in user_query.lower():
        return "templates/index.html"

    return "app.py"  # Default to app.py if no match is found

def chatbot():
    user_query = request.json.get('message')
    file_path = determine_relevant_file(user_query)
    code_content = fetch_github_file(file_path)

    system_message = (
        "You are an AI assistant for a Kerala Tourism website that encourages people to travel more."
        "Your goal is to guide users through the website’s features, which include interactive maps, location validation, "
        "trip recommendations, and a leaderboard system. Help users navigate efficiently and provide friendly responses. "
        "Do not mention the code or technical aspects; just offer clear explanations about the website and its sections."
        "Keep the responses really concise and small(under 50 words) yet informative"
        "Do not create buttons or names yourself. Only use existing names and words in the webpage"
        "The manubar tabs are:Home, Recommendations, Map, Leaderboard, Account, AI Assistant, Logout"
    )

    if "Error" not in code_content:
        try:
            response = client.chat.completions.create(
                model="open-mistral-7b",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"User Query: {user_query}\n\nWebsite section:\n{file_path}"}
                ],
                stream=False
            )
            return jsonify({"response": response.choices[0].message.content.strip()})
        
        except Exception as e:
            return jsonify({"response": "Sorry, something went wrong. Try again later!"})

    # If no relevant file is found, fallback to a general response
    try:
        response = client.chat.completions.create(
            model="open-mistral-7b",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_query}
            ],
            stream=False
        )
        return jsonify({"response": response.choices[0].message.content.strip()})
    except Exception as e:
        return jsonify({"response": "Sorry, I couldn’t process that request right now."})
