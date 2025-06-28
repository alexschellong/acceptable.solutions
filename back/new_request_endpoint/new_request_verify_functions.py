import jwt
import sqlite3
from datetime import timedelta, timezone, datetime
from fastapi import HTTPException
import config

SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"

def generate_jwt_token(data: dict, expires_in: int) -> str:
    
    to_encode = data.copy()
    expire = datetime(timezone.utc) + timedelta(minutes=expires_in)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def look_up_request(customer_email: str, id: int, db):
    
    cursor = db.cursor()
    look_up_request = """SELECT COUNT(*) FROM customer_requests_auth
                                 WHERE customer_email = ?
                                  AND id = ?"""
    
    cursor.execute(look_up_request, (customer_email, id))

    result = cursor.fetchone()
    cursor.close()

    if result == 1:
        return True
    else:
        return False
    

def move_verified_request_to_customer_requests_table(customer_email: str, id: int, db):
    
    try:
        cursor = db.cursor()
        insert_into_customer_requests_and_delete_from_auth_table = """
        BEGIN TRANSACTION;

        INSERT INTO customer_requests
            SELECT * FROM customer_requests_auth
                                    WHERE customer_email = ?
                                    AND id = ?;

        DELETE FROM customer_requests_auth
                                    WHERE customer_email = ?
                                        AND id = ?;
                                    
        COMMIT;
        """
                                    
        cursor.execute(insert_into_customer_requests_and_delete_from_auth_table
                    , (customer_email, id))

        result = cursor.fetchone()
        cursor.close()
        db.commit()
    
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
        

    if result == 1:
        return True
    else:
        return False