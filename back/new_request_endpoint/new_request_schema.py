from pydantic import BaseModel, Field

class CustomerRequest(BaseModel):
    customer_email: str = Field(min_length=3, max_length=1000)
    customer_request: str = Field(min_length=20, max_length=10000)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None