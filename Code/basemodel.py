import ollama

# Initialize Ollama client
client = ollama.Client()

# Take input from user
clause = input("\nEnter your clause or terms text:\n> ")

# Define the prompt
prompt = f"""
You are a legal safety assistant.

Given a clause from Terms and Conditions, analyze it and return ONLY in the following format:

Risk Level: Safe / Concerning / High Risk
Possible Violations: list law names (e.g., GDPR, CCPA, IT Act India)
Explanation: short explanation in simple language
Fix: one line suggestion to fix the issue

Clause:
\"\"\"{clause}\"\"\"
"""

# Call the Ollama model
response = client.generate(
    model="llama3.1",   # use your installed model
    prompt=prompt
)

# Print output
print("\n================ RESULT ================\n")
print(response["response"].strip())

