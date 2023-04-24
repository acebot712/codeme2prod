from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from models.completion import Completion
from models.turbo import AzureChatGPTAPI
from models.prompt import Prompt
import re
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/getInformation")
async def get_information(req : Request):
    IM_START_TOKEN = "<|im_start|>"
    IM_END_TOKEN = "<|im_end|>"
    req_body = await req.json()
    prompt = Prompt(
        text=req_body["prompt"],
        im_start_token=IM_START_TOKEN,
        im_end_token=IM_END_TOKEN,
        run_prompt_engine=True,
    ).get_text()
    print(prompt)

    session_cookie = req.cookies.get("new_cookie")  # Get the value of the session_cookie cookie
    
    print("session_cookie =", session_cookie)

    model = AzureChatGPTAPI(
        api_key=os.environ.get("FK_API_KEY", ""),
        endpoint=os.environ.get("FK_ENDPOINT", ""),
        im_start_token=IM_START_TOKEN,
        im_end_token=IM_END_TOKEN,
    )
    code_data = model.generate_code(prompt)
    print(code_data)

    return {
        "status" : "SUCCESS",
        "code" : code_data
    }

@app.post("/getInformations")
async def get_informations(req : Request):
    req_body = await req.json()

    session_cookie = req.headers.get("Cookie")
    if session_cookie:
        session_cookie = session_cookie.split("; ")[0].split("=")[1]
    print("session_cookie =", session_cookie)

    model = Completion(api_key=os.environ.get('API_KEY'))
    prompt = Prompt(
        text=req_body["prompt"],
    ).get_text()
    print(prompt)
    code_data = model.generate_code(prompt)
    return {
        "status" : "SUCCESS",
        "code" : code_data
    }
"""
curl -X POST -H "Content-Type: application/json" -d '{"prompt": "Write a function for dfs"}' -b "session_cookie=cookie_monster" http://localhost:8000/getInformation

"""