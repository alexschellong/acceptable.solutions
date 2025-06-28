import os 
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()

load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")