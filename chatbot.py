from openai import OpenAI  # Using Together AI's OpenAI-compatible API
from github_fetch import fetch_github_file  # Ensure this file exists and works correctly

# Mistral API Setup (Using Together AI as the provider)
MISTRAL_API_KEY = "j4RNjKWz0bjaPjJMkXQXZpkPuFffWM7R"
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

def chatbot_response(user_query):
    """Processes user queries and fetches GitHub files if needed, following the defined rules."""
    
    file_path = determine_relevant_file(user_query)
    code_content = fetch_github_file(file_path)

    if "Error" not in code_content:
        # Send both the user query and the fetched code to Mistral for context, without making it sound like code analysis
        try:
            response = client.chat.completions.create(
                model="open-mistral-7b",
                messages=[
                    {"role": "system", "content": (
                        "You are an AI assistant familiar with the website's structure and design. "
                        "Guide users in a friendly and concise manner without mentioning the code. "
                        "If they ask about a feature, show them where to find it on the website. "
                        "Avoid phrases like 'I found this in the code'—just provide clear, natural responses."
                    )},
                    {"role": "user", "content": f"User Query: {user_query}\n\nWebsite section:\n{file_path}"}
                ],
                stream=False
            )
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return "Sorry, something went wrong. Try again later!"

    # If no relevant file is found, fallback to a general response
    try:
        response = client.chat.completions.create(
            model="open-mistral-7b",
            messages=[
                {"role": "system", "content": (
                    "You are an AI assistant familiar with the website's structure and design. "
                    "Guide users in a friendly and concise manner without mentioning the code. "
                    "If they ask about a feature, show them where to find it on the website."
                )},
                {"role": "user", "content": user_query}
            ],
            stream=False
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return "Sorry, I couldn’t process that request right now."

# Example Usage
if __name__ == "__main__":
    while True:
        user_input = input("Ask something: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print(chatbot_response(user_input))
