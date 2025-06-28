from fastapi import APIRouter, Depends, HTTPException
from new_request_schema import CustomerRequest
from new_request_functions import *
from new_request_verify_functions import *
import jwt
from jwt.exceptions import ExpiredSignatureError
import config


SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"

router = APIRouter()

SENDER_EMAIL = "alex.schellong@gmail.com"
URL = ""


@router.post("/api/v1/customer_request")
async def create_new_request(customer_request: CustomerRequest, db=Depends(get_db)):
    try:

        if(not check_if_request_has_real_words(customer_request.customer_request)):
            
            raise HTTPException(status_code=406, detail="Request contains less than 40 real words") 

        if(not check_if_email_is_valid(customer_request.customer_email)):
            
            raise HTTPException(status_code=406, detail="Invalid email address")

        (count_of_pending_requests, id) = get_count_of_pending_requests_and_id()

        if count_of_pending_requests > 2:
            raise HTTPException(status_code=429, detail="Email used over limit")
        
        try:
            send_email(customer_request.customer_email, SENDER_EMAIL, URL, id)
        except:
            raise HTTPException(status_code=500, detail="Failed to send email")

        return {"Verification link sent": True}

    except HTTPException:
        raise  
    except Exception:
        raise HTTPException(status_code=500) 
    



@router.get("/api/v1/customer_request/verify")
async def verify_request(token: str, db=Depends(get_db)):

    try:

        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        customer_email = payload.get("email")
        id = payload.get("id")
        if not customer_email or not id:
            raise HTTPException(status_code=404, detail="Token is invalid")

        look_up_request = look_up_request(customer_email, id, db)

        if not look_up_request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        move_verified_request_to_customer_requests_table(customer_email, id, db)

        return {"Request verified": True}



    except sqlite3.Error:
        raise 
    except ExpiredSignatureError:
        raise HTTPException(status_code=408, detail="Token expired") 
    except Exception:
        raise HTTPException(status_code=500) 
    
    
