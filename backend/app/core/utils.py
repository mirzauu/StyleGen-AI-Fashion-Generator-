def hash_password(password: str) -> str:
    # from passlib.context import CryptContext

    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return password

def verify_password(plain_password: str, hashed_password: str) -> bool:
   
    
    return plain_password

def generate_jwt_token(data: dict, secret: str, expires_delta: int = 3600) -> str:
    from datetime import datetime, timedelta
    from jose import JWTError, jwt

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret, algorithm="HS256")
    return encoded_jwt

def decode_jwt_token(token: str, secret: str) -> dict:
    from jose import JWTError, jwt

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except JWTError:
        return None