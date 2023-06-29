from .model import Model
from .prompt import Prompt
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class AzureChatGPTAPI(Model):
    def __init__(self, api_key, endpoint, *args, **kwargs):
        super().__init__(api_key, endpoint)
        self.temperature = kwargs.get("temperature", 0.6)
        self.top_p = kwargs.get("top_p", 0.925)
        self.max_tokens = kwargs.get("max_tokens", 400)
        self.frequency_penalty = kwargs.get("frequency_penalty", 0)
        self.presence_penalty = kwargs.get("presence_penalty", 0)
        self.logit_bias = kwargs.get("logit_bias", {1640: 10, 361: 10, 7783: 5})
        self.im_start_token = kwargs.get("im_start_token", "<|im_start|>")
        self.im_end_token = kwargs.get("im_end_token", "<|im_end|>")
        self.stop = kwargs.get("stop", [f"{self.im_end_token}", "```"])

    def generate_code(self, prompt_object):
        prompt = prompt_object.get_text()
        url = self.endpoint
        headers = {"Content-Type": "application/json", "api-key": self.api_key}
        data = {
            "prompt": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "top_p": self.top_p,
            "logit_bias": self.logit_bias,
            "stop": ["<|im_end|>"],
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()["choices"][0]["text"]


if __name__ == "__main__":
    IM_START_TOKEN = "<|im_start|>"
    IM_END_TOKEN = "<|im_end|>"
    prompt = Prompt(
        text="write a dfs function",
        im_start_token=IM_START_TOKEN,
        im_end_token="<|im_end|>",
        run_prompt_engine=True,
    ).get_text()
    print(prompt)
    model = AzureChatGPTAPI(
        api_key=os.environ.get("FK_API_KEY", ""),
        endpoint=os.environ.get("FK_ENDPOINT", ""),
        im_start_token=IM_START_TOKEN,
        im_end_token=IM_END_TOKEN,
    )
    print(model.generate_code(prompt))
