from models.turbo import AzureChatGPTAPI
from .prompt import Prompt
import requests
import os
from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    req_body = {
        "Write a dfs function"
    }
    IM_START_TOKEN = "<|im_start|>"
    IM_END_TOKEN = "<|im_end|>"
    prompt_object = Prompt(
        text=req_body["prompt"],
        context=req_body["context"],
        im_start_token=IM_START_TOKEN,
        im_end_token=IM_END_TOKEN,
        run_prompt_engine=True,
    )
    model = AzureChatGPTAPI(
        api_key=os.environ.get("FK_API_KEY", ""),
        endpoint=os.environ.get("FK_ENDPOINT", ""),
        im_start_token=IM_START_TOKEN,
        im_end_token=IM_END_TOKEN,
    )

    print(model.generate_code(prompt_object))

