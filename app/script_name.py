import os

# Generate a random SECRET_KEY securely
SECRET_KEY = os.urandom(24).hex()
print(f"Generated SECRET_KEY: {SECRET_KEY}")
