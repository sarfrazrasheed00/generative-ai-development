
# Lesson 01: Python for Generative AI

# 1. Variables
developer_name = "Sarfraz"
skills = ["HTML", "CSS", "JavaScript", "Vue.js", "Laravel", "Python"]

print("Developer:", developer_name)
print("Skills:", skills)


# 2. Dictionary (similar to PHP associative array)
developer = {
    "name": "Sarfraz",
    "role": "Full Stack Developer",
    "learning": "Generative AI",
    "experience": 3
}

print("Role:", developer["role"])


# 3. Functions
def generate_prompt(topic):
    return f"Explain {topic} in simple language with examples."


prompt = generate_prompt("Generative AI")
print("Prompt:", prompt)


# 4. List of AI models
ai_models = ["GPT", "Gemini", "Claude", "Llama"]

for model in ai_models:
    print("AI Model:", model)


# 5. JSON Conversion
import json

developer_json = json.dumps(developer, indent=4)
print("JSON Output:")
print(developer_json)


# 6. JSON Parsing
parsed_data = json.loads(developer_json)
print("Parsed Name:", parsed_data["name"])
