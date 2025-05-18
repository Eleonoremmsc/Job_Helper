import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

print(hash_password("abc123"))  # Run this to generate password hashes
