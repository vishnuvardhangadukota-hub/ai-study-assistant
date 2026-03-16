import requests

API_URL = "https://api.quotable.io/random"

def study_agent(question):

    try:
        response = requests.get(API_URL)
        data = response.json()

        return "AI Agent: " + data["content"]

    except:
        return "AI Agent: Sorry, I couldn't fetch an answer."


while True:

    user_input = input("Ask a study question (type exit to stop): ")

    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    answer = study_agent(user_input)

    print(answer)