import sqlite3
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import EmailStr
import uuid
import secrets
from email_testing import send_verification_email

app = FastAPI()

def get_html_from_file(filename):
    with open(filename) as f:
        file_contents = f.read()
    return file_contents

# Helper function to generate a unique session token
def generate_session_token():
    return str(uuid.uuid4())

@app.get("/", response_class=HTMLResponse)
def index():
    return get_html_from_file("./login.html")

@app.get("/register", response_class=HTMLResponse)
def register_page():
    return get_html_from_file("./register.html")

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    # connect to the SQLite database
    conn = sqlite3.connect("codeme.db")
    cursor = conn.cursor()

    # check if the email and password are valid
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    if user:
        # generate a session token and store it in the database
        session_token = secrets.token_hex(16)
        cursor.execute("UPDATE users SET session_token=? WHERE email=?", (session_token, email))
        conn.commit()

        # set cookie and redirect to dashboard
        response = RedirectResponse(url="/dashboard")
        response.set_cookie(key="session_token", value=session_token)
    else:
        response = HTMLResponse(get_html_from_file("./login_error.html"))

    # close the database connection
    conn.close()

    return response

@app.post("/register")
async def register(request: Request, background_tasks: BackgroundTasks, email: EmailStr = Form(...), password: str = Form(...)):
    # check if the email is already registered
    conn = sqlite3.connect("codeme.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()

    if user:
        # if the email is already registered, return an error message
        return HTMLResponse("Email already registered")
    
    token = generate_session_token()

    # insert the new user into the database
    cursor.execute("INSERT INTO users (email, password, verified, verification_token) VALUES (?, ?, ?, ?)",
                   (email, password, 0, token))
    conn.commit()

    # send a verification email to the new user
    background_tasks.add_task(send_verification_email, email, token)

    # redirect the user to the welcome page
    return HTMLResponse(get_html_from_file("./welcome.html"))

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard(request: Request):
    if request.method == "GET":
        return HTMLResponse(get_html_from_file("./login_error.html"))

    # check for session token in cookie
    session_token = request.cookies.get("session_token")
    if not session_token:
        # if session token is not present, redirect to login
        return RedirectResponse(url="/")

    # retrieve user's authentication status using the session token
    conn = sqlite3.connect("codeme.db")
    cursor = conn.cursor()

    # execute the SQL query to retrieve the user's authentication status
    cursor.execute("SELECT * FROM users WHERE session_token = ?", (session_token,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        # if the session token is invalid, redirect to login
        return RedirectResponse(url="/")

    # user is authenticated, return the dashboard page
    return HTMLResponse(get_html_from_file("./dashboard.html"))

@app.get("/verify/{token}")
async def verify(request: Request, token: str):
    # retrieve the user from the database using the session token
    conn = sqlite3.connect("codeme.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE verification_token=?", (token,))
    user = cursor.fetchone()

    if not user:
        # if the session token is not valid, return an error message
        return HTMLResponse("Invalid session token")

    # update the user's verification status in the database
    cursor.execute("UPDATE users SET verified=? WHERE id=?", (1, user[0]))
    conn.commit()
    conn.close()

    # redirect the user to the login page
    return RedirectResponse(url="/")

