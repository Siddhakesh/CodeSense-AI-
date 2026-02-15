from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "password123"
print(f"Password: {password}")

try:
    hash = pwd_context.hash(password)
    print(f"Hash: {hash}")
    
    verify = pwd_context.verify(password, hash)
    print(f"Verify: {verify}")
    
    long_password = "a" * 80
    print(f"Long Password length: {len(long_password)}")
    hash_long = pwd_context.hash(long_password)
    print(f"Hash Long: {hash_long}")
    
except Exception as e:
    print(f"Error: {e}")
