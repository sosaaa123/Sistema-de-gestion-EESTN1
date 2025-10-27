import bcrypt
from pydantic import BaseModel

class PasswordManager:
    def __init__(self):
        self.rounds = 12
    
    def hash_pwd(self, password):
        salt = bcrypt.gensalt(rounds=self.rounds)
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    def verify_pwd(self, password, hashed):
        return bcrypt.checkpw(password.encode(), hashed.encode())

class LoginRequest(BaseModel):
    email: str
    password: str
