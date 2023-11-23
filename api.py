from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.completion import Completion
from models.turbo import AzureChatGPTAPI
from models.prompt import Prompt
from models.langchain_agent import CodeGenerator
import os
from dotenv import load_dotenv
from typing import Dict, Optional
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import uuid


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

@app.post("/generateSession/")
async def generate_session():
  session_id = uuid.uuid4() # Generate a random UUID
  return JSONResponse(status_code=200, content={"session_id": str(session_id)})

@app.post("/getcode/{model}")
async def get_information(req: Request, model: str):
    try:
        req_body = await req.json()
        session_cookie = req.headers.get("Cookie")
        if session_cookie:
            session_cookie = session_cookie.split("; ")[0].split("=")[1]

        if model == "turbo":
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
            
        elif model == "completions":

            model = Completion(api_key=os.environ.get('OPENAI_API_KEY'))
            prompt_object = Prompt(
                text=req_body["prompt"],
                context=req_body["context"]
            )
            print("prompt_object =", prompt_object)
            print("prompt_object.get_text() =", prompt_object.get_text())
            
        else:
            raise HTTPException(status_code=404, detail="Model not found")
        
        code_data = model.generate_code(prompt_object)
        response = {
            "status" : "SUCCESS",
            "code" : code_data
        }
        return JSONResponse(status_code=200, content=response)
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "FAILURE", "error": str(e)})
    
# New Agent Code

# dict to store different instances of CodeGenerator per client  
clients: Dict[str, CodeGenerator] = {}
class PromptModel(BaseModel):
    prompt: str
    context: str
    user_id: str
    login_id: str
    onPremise: bool
    deepScan: bool
    deepScanText: Optional[str] = None
    
@app.post("/getagentcode/{client_id}")
async def get_information_agent(client_id: str, prompt_model: PromptModel):
    print(f"{client_id=}")
    print(f"{prompt_model.prompt=}")
    print(f"{prompt_model.deepScan=}")

    # Check if the client is already in the clients dictionary
    if client_id not in clients:
        clients[client_id] = CodeGenerator()

    generator = clients[client_id]

    try:
        additional_params = {}
        if prompt_model.deepScan and prompt_model.deepScanText:
            additional_params['deep_scan_text'] = prompt_model.deepScanText

        code_data = generator.generate_code(
            prompt=prompt_model.prompt,
            on_premise=prompt_model.onPremise,
            deep_scan=prompt_model.deepScan,
            **additional_params  # Pass additional parameters if they exist
        )

        response = {
            "status": "SUCCESS",
            "code": code_data
        }
        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "FAILURE", "error": str(e)})
    
    # Create a DataFrame from the two lists
    # data = req_body
    # data["Response"] = [code_data]
    # # df = pd.DataFrame(data)[["prompt","user_id","login_id","Response"]]
    # df = pd.DataFrame(data)
    # # Select all columns except "context"
    # df = df.drop("context", axis=1)

    # current_date = datetime.date.today()
    # date_string = "~/" + current_date.strftime("%Y-%m-%d") + "_server_logs.csv"

    # # Check if output.csv exists, if not create a new file
    # if not os.path.exists(os.path.expanduser(date_string)):
    #     df.to_csv(date_string, index=False)
    # else:
    #     # Append to existing csv file
    #     df.to_csv(date_string, mode='a', header=False, index=False)
    """
    curl -X POST -H "Content-Type: application/json" -d '{"prompt": "Write a function for dfs"}' -b "session_cookie=cookie_monster" http://localhost:8000/getcode/turbo
    curl -X POST -H "Content-Type: application/json" -d '{"prompt": "Code for DFS function", "context": ""}' -b "session_cookie=cookie_monster" http://35.223.253.138:8000/getcode/turbo
    """