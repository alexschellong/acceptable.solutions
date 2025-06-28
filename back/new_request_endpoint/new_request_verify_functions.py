from fastapi import HTTPException
from sqlite3 import Error as sqlite3_Error


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

        cursor.close()
        db.commit()
    
    except sqlite3_Error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {sqlite3_Error}")
        

    return True