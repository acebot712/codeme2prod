from model import Model
from prompt import Prompt
import openai
import os
from dotenv import load_dotenv
load_dotenv()


class Completion(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        openai.api_key = self.api_key
        self.model_name = kwargs.get("model_name", "gpt-3.5-turbo")
        self.messages = kwargs.get("messages", [
            {
                "role": "user",
                "content": "Please write a Python function that calculates the factorial of a given number.",
            },
            {
                "role": "assistant",
                "content": "Sure, here's a Python function that calculates the factorial of a number:",
            },
            {
                "role": "assistant",
                "content": "def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)",
            },
            {
                "role": "user",
                "content": "Can you modify the function to calculate the factorial using a loop instead of recursion?",
            },
            {
                "role": "assistant",
                "content": "Certainly, here's the modified function:",
            },
            {
                "role": "assistant",
                "content": "def factorial(n):\n    result = 1\n    for i in range(1, n+1):\n        result *= i\n    return result",
            }
        ])
        self.temperature = kwargs.get("temperature", 0.6)
        self.top_p = kwargs.get("top_p", 0.925)
        self.max_tokens = kwargs.get("max_tokens", 1500)
        self.presence_penalty = kwargs.get("presence_penalty", 0)
        self.logit_bias = kwargs.get("logit_bias", {1640: 10, 361: 10, 7783: 5})

    def generate_code(self, prompt):
        self.messages.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=self.messages,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            presence_penalty=self.presence_penalty,
            logit_bias=self.logit_bias,
        )
        return response["choices"][0]["message"]["content"]
    
if __name__ == "__main__":
    model = Completion(api_key=os.environ.get('API_KEY'))
    prompt = Prompt(
        text="write code for implementing a dfs function",
    ).get_text()
    print(model.generate_code(prompt))

