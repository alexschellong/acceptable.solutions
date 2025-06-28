import sqlite3
from fastapi import  HTTPException
from nltk.corpus import words
import re
import smtplib
from email.mime.text import MIMEText
import jwt
from datetime import timedelta, timezone, datetime
import config

SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"

def get_db(dbName):
    db = sqlite3.connect(dbName)
    try:
        yield db
    finally:
        db.close()

def check_if_request_has_real_words(customer_request: str) -> bool:
    english_words = set(words.words())

    word_list = customer_request.split()

    sum_of_real_words = sum(1 for word in word_list if word.lower() in english_words)
    
    if(sum_of_real_words > 20):
        return True
    else:
        return False


def check_if_email_is_valid(customer_email: str) -> bool:

    email_regex = r"^[A-Za-z0-9]+@[A-Za-z0-9]+(\.[A-Za-z0-9]+)*$"
    if re.match(email_regex, customer_email):
        return True
    else:
        return False
    

def get_count_of_pending_requests_and_id(customer_email: str, db) -> tuple[int, int | None]:

    cursor = db.cursor()

    get_number_of_pending_requests = """SELECT COUNT(*) FROM customer_requests
                                     WHERE customer_email = ?
                                        AND status = ?"""
    
    cursor.execute(get_number_of_pending_requests, (customer_email, 1))
    result = cursor.fetchone()

    if result > 2:
         raise HTTPException(status_code=429, detail="Too many currently pending requests")
    

    get_number_of_unauth_requests_and_id = """SELECT COUNT(*), MAX(id) FROM customer_requests_auth
                                     WHERE customer_email = ? """
    
    cursor.execute(get_number_of_unauth_requests_and_id, (customer_email))

    result = cursor.fetchone()
    cursor.close()

    if result[0] > 2:
        raise HTTPException(status_code=429, detail="Too many requests used over limit")
        

    return (result[0], result[1]) if result else (0, None)
    
   

def send_email(customer_email: str,sender_email: str, url: str, id: int) -> None:
        
    jwt_token = generate_jwt_token({"email": customer_email,"id": id}, 10)

    subject = "request authentication"

    body = f""""
    <html>
        <body>
            <p>Please click the link below to authenticate your request :) !</p>
            <a href="{url}/api/v1/customer_request/verify?token={jwt_token}">
                {url}/api/v1/customer_request/verify?token={jwt_token}
            </a>
        </body>
    </html>
    """
    
    html_message = MIMEText(body, "html")
    html_message["Subject"] = subject
    html_message["From"] = sender_email
    html_message["To"] = customer_email
    

    with smtplib.SMTP("smtp.gmail.com", 465) as server:
        server.starttls()
        server.login(sender_email, "rnws vueu pccr amkf")

        server.sendmail(sender_email, customer_email, html_message.as_string())


    
def generate_jwt_token(data: dict, expires_in: int) -> str:
    
    to_encode = data.copy()
    expire = datetime(timezone.utc) + timedelta(minutes=expires_in)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



