from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=True,
)

def get_password_hash(password):
    if len(password.encode("utf-8"))>72:
        raise ValueError("password too long")

    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password)->bool:
    if len(plain_password.encode("utf-8"))>72:
        return False
    return pwd_context.verify(plain_password, hashed_password)