from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from models.completion import Completion
from models.turbo import AzureChatGPTAPI
from models.prompt import Prompt
import os
from dotenv import load_dotenv
import pandas as pd
import datetime

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

@app.post("/getcode/{model}")
async def get_information(req: Request, model: str):
    req_body = await req.json()
    session_cookie = req.headers.get("Cookie")
    if session_cookie:
        session_cookie = session_cookie.split("; ")[0].split("=")[1]
    print("session_cookie =", session_cookie)

    if model == "turbo":
        IM_START_TOKEN = "<|im_start|>"
        IM_END_TOKEN = "<|im_end|>"
        prompt = Prompt(
            text=req_body["prompt"],
            im_start_token=IM_START_TOKEN,
            im_end_token=IM_END_TOKEN,
            run_prompt_engine=True,
        ).get_text()
        model = AzureChatGPTAPI(
            api_key=os.environ.get("FK_API_KEY", ""),
            endpoint=os.environ.get("FK_ENDPOINT", ""),
            im_start_token=IM_START_TOKEN,
            im_end_token=IM_END_TOKEN,
        )
        
    elif model == "completions":

        model = Completion(api_key=os.environ.get('API_KEY'))
        prompt = Prompt(
            text=req_body["prompt"],
        ).get_text()

    else:
        return {
            "status" : "FAILURE",
            "code" : "Model not found"
        }
    
    code_data = model.generate_code(prompt)
    response = {
        "status" : "SUCCESS",
        "code" : code_data
    }

    # Create a DataFrame from the two lists
    data = req_body
    data["Response"] = response
    df = pd.DataFrame(data)

    current_date = datetime.date.today()
    date_string = "~/" + current_date.strftime("%Y-%m-%d") + "_server_logs.csv"

    # Check if output.csv exists, if not create a new file
    if not os.path.exists(os.path.expanduser(date_string)):
        df.to_csv(date_string, index=False)
    else:
        # Append to existing csv file
        df.to_csv(date_string, mode='a', header=False, index=False)
    return response
    """
    curl -X POST -H "Content-Type: application/json" -d '{"prompt": "Write a function for dfs"}' -b "session_cookie=cookie_monster" http://localhost:8000/getcode/turbo
    """