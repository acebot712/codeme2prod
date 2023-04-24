from email_testing import send_verification_email
from fastapi import FastAPI, Request, Form, BackgroundTasks, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from models.completion import Completion
from models.turbo import AzureChatGPTAPI
from models.prompt import Prompt
from pydantic import EmailStr
import secrets
import sqlite3
import uuid
import os
import re

STATIC_DIR = "static"
DASHBOARD = os.path.join(STATIC_DIR, "dashboard.html")
INDEX = os.path.join(STATIC_DIR, "index.html")
LOGIN = os.path.join(STATIC_DIR, "login.html")
LOGIN_ERROR = os.path.join(STATIC_DIR, "login_error.html")
REGISTER = os.path.join(STATIC_DIR, "register.html")
REGISTER_ERROR = os.path.join(STATIC_DIR, "register_error.html")
WELCOME = os.path.join(STATIC_DIR, "welcome.html")

def code_only(response):
    code_pattern = re.compile(r'```.*?```', re.DOTALL)
    code_blocks = re.findall(code_pattern, response)
    for block in code_blocks:
        return block.strip('`')


def get_html_from_file(filename):
    with open(filename) as f:
        file_contents = f.read()
    return file_contents


# Helper function to generate a unique session token
def generate_session_token():
    return str(uuid.uuid4())


def delete_session_token(request, session_token):
    session_token = request.cookies.get(session_token)
    if session_token:
        conn = sqlite3.connect(os.environ.get("DB_NAME"))
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET session_token = NULL where session_token = ?",
                (session_token,),
            )
            conn.commit()


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user(request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    # retrieve user's authentication status using the session token
    conn = sqlite3.connect(os.environ.get("DB_NAME"))
    with conn:
        cursor = conn.cursor()
        # execute the SQL query to retrieve the user's authentication status
        cursor.execute("SELECT * FROM users WHERE session_token = ?", (session_token,))
        user = cursor.fetchone()
        if not user:
            return None
        return user

@app.get("/")
def index(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    # user is authenticated, return the dashboard page
    return HTMLResponse(get_html_from_file(DASHBOARD))

@app.get("/login")
def login_get(request: Request):
    delete_session_token(request, "session_token")
    return HTMLResponse(get_html_from_file(LOGIN))


@app.post("/login")
async def login_post(
    request: Request, email: str = Form(...), password: str = Form(...)
):
    # connect to the SQLite database
    conn = sqlite3.connect(os.environ.get("DB_NAME"))
    with conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # check if the email and password are valid
        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?", (email, password)
        )
        user = cursor.fetchone()
        if user:
            if user["verified"]:
                # generate a session token and store it in the database
                session_token = secrets.token_hex(16)
                cursor.execute(
                    "UPDATE users SET session_token=? WHERE id=?",
                    (session_token, user["id"]),
                )
                conn.commit()

                # set cookie and redirect to dashboard
                response = RedirectResponse(
                    url="/", status_code=status.HTTP_303_SEE_OTHER
                )
                response.set_cookie(key="session_token", value=session_token)
            else:
                response = HTMLResponse(get_html_from_file(LOGIN_ERROR))
        else:
            response = HTMLResponse(get_html_from_file(LOGIN_ERROR))

    return response


@app.get("/register", response_class=HTMLResponse)
def register_get():
    return get_html_from_file(REGISTER)


@app.post("/register")
async def register_post(
    request: Request,
    background_tasks: BackgroundTasks,
    email: EmailStr = Form(...),
    password: str = Form(...),
):
    # check if the email is already registered
    conn = sqlite3.connect(os.environ.get("DB_NAME"))
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if user:
            # if the email is already registered, return an error message
            return HTMLResponse(get_html_from_file(REGISTER_ERROR))

        token = generate_session_token()

        # insert the new user into the database
        cursor.execute(
            "INSERT INTO users (email, password, verified, verification_token) VALUES (?, ?, ?, ?)",
            (email, password, 0, token),
        )
        conn.commit()

        # send a verification email to the new user
        background_tasks.add_task(send_verification_email, email, token)

    # redirect the user to the welcome page
    delete_session_token(request, "session_token")
    return HTMLResponse(get_html_from_file(WELCOME))


@app.get("/verify/{token}")
async def verify(request: Request, token: str):
    # retrieve the user from the database using the session token
    conn = sqlite3.connect(os.environ.get("DB_NAME"))
    conn.row_factory = sqlite3.Row
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE verification_token=?", (token,))
        user = cursor.fetchone()

        if not user:
            # if the session token is not valid, return an error message
            return HTMLResponse("Invalid verification link")

        # update the user's verification status in the database
        cursor.execute("UPDATE users SET verified=? WHERE id=?", (1, user["id"]))
        conn.commit()

    # redirect the user to the login page
    delete_session_token(request, "session_token")
    return RedirectResponse(url="/login")


@app.get("/logout")
async def logout(request: Request):
    delete_session_token(request, "session_token")
    return RedirectResponse(url="/login")

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