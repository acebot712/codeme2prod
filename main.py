from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from model_old import codeme
import re

def code_only(response):
    code_pattern = re.compile(r'```.*?```', re.DOTALL)
    code_blocks = re.findall(code_pattern, response)
    for block in code_blocks:
        return block.strip('`')
    
# Define a function that responds to user inputs
def respond(input_text):
    response = ""
    if "hello" in input_text.lower():
        response = "Hello! How can I help you today?"
    elif "goodbye" in input_text.lower():
        response = "Goodbye! Have a great day!"
    elif "code" in input_text.lower():
        response = code_only(codeme(input_text.lower()))
    else:
        response = codeme(input_text.lower())
    return response

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/getInformation")
async def get_information(info : Request):
    req_info = await info.json()
    code_data = respond(req_info['api_request'])
    code_data = code_data.lstrip("python")
    return {
        "status" : "SUCCESS",
        "code" : code_data
    }