from email_testing import send_verification_email
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr
import secrets
import sqlite3
import uuid
import os

STATIC_DIR="static"
LOGIN_ERROR=os.path.join(STATIC_DIR,"login_error.html")
DASHBOARD=os.path.join(STATIC_DIR,"dashboard.html")
INDEX=os.path.join(STATIC_DIR,"index.html")
LOGIN=os.path.join(STATIC_DIR,"login.html")
REGISTER=os.path.join(STATIC_DIR,"register.html")
WELCOME=os.path.join(STATIC_DIR, "welcome.html")

def get_html_from_file(filename):
    with open(filename) as f:
        file_contents=f.read()
    return file_contents

# Helper function to generate a unique session token
def generate_session_token():
    return str(uuid.uuid4())

app=FastAPI()

origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index(request: Request):

    # check for session token in cookie
    session_token=request.cookies.get("session_token")
    if not session_token:
        # if session token is not present, redirect to login
        return RedirectResponse(url="/login")

    # retrieve user's authentication status using the session token
    conn=sqlite3.connect(os.environ.get("DB_NAME"))
    with conn:
        cursor =conn.cursor()

        # execute the SQL query to retrieve the user's authentication status
        cursor.execute("SELECT * FROM users WHERE session_token = ?", (session_token,))
        user=cursor.fetchone()
        if not user:
            # if the session token is invalid, redirect to login
            return RedirectResponse(url="/login")

    # user is authenticated, return the dashboard page
    return HTMLResponse(get_html_from_file(DASHBOARD))

@app.get("/login")
def index(request: Request):
    session_token = request.cookies.get('session_token')
    if session_token:
        conn = sqlite3.connect(os.environ.get("DB_NAME"))
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE session_token=?", (session_token,))
            cursor.commit()
    return HTMLResponse(get_html_from_file(LOGIN))

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    # connect to the SQLite database
    conn=sqlite3.connect(os.environ.get("DB_NAME"))
    with conn:
        conn.row_factory=sqlite3.Row
        cursor=conn.cursor()

        # check if the email and password are valid
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user=cursor.fetchone()
        if user:
            if user["verified"]:
                # generate a session token and store it in the database
                session_token=secrets.token_hex(16)
                cursor.execute("UPDATE users SET session_token=? WHERE id=?", (session_token, user["id"]))
                conn.commit()

                # set cookie and redirect to dashboard
                response=RedirectResponse(url="/")
                response.set_cookie(key="session_token", value=session_token)
            else:
                response=HTMLResponse(get_html_from_file(LOGIN_ERROR))
        else:
            response=HTMLResponse(get_html_from_file(LOGIN_ERROR))

    return response

@app.get("/register", response_class=HTMLResponse)
def register_page():
    return get_html_from_file(REGISTER)

@app.post("/register")
async def register(request: Request, background_tasks: BackgroundTasks, email: EmailStr = Form(...), password: str = Form(...)):
    # check if the email is already registered
    conn=sqlite3.connect(os.environ.get("DB_NAME"))
    with conn:
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user=cursor.fetchone()

        if user:
            # if the email is already registered, return an error message
            return HTMLResponse(get_html_from_file(REGISTER))
        
        token=generate_session_token()

        # insert the new user into the database
        cursor.execute("INSERT INTO users (email, password, verified, verification_token) VALUES (?, ?, ?, ?)",
                    (email, password, 0, token))
        conn.commit()

        # send a verification email to the new user
        background_tasks.add_task(send_verification_email, email, token)

    # redirect the user to the welcome page
    return HTMLResponse(get_html_from_file(WELCOME))

@app.get("/verify/{token}")
async def verify(request: Request, token: str):
    # retrieve the user from the database using the session token
    conn=sqlite3.connect(os.environ.get("DB_NAME"))
    with conn:
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE verification_token=?", (token,))
        user=cursor.fetchone()

        if not user:
            # if the session token is not valid, return an error message
            return HTMLResponse("Invalid verification link")

        # update the user's verification status in the database
        cursor.execute("UPDATE users SET verified=? WHERE id=?", (1, user["id"]))
        conn.commit()

    # redirect the user to the login page
    return RedirectResponse(url="/login")
