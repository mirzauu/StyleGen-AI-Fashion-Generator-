def hash_password(password: str) -> str:
    # In a production environment, we should use a secure password hashing library
    # like passlib with bcrypt. For now, we're returning the password as-is.
    # from passlib.context import CryptContext
    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # return pwd_context.hash(password)
    
    # Simple return (not secure for production)
    return password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # In a production environment, we should use a secure password hashing library
    # like passlib with bcrypt. For now, we're doing a simple comparison.
    # from passlib.context import CryptContext
    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # return pwd_context.verify(plain_password, hashed_password)
    
    # Simple comparison (not secure for production)
    return plain_password == hashed_password

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