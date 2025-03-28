import requests

# 🔹 Replace with your PythonAnywhere username
PA_USERNAME = "Brymax"

# 🔹 Replace with your API Token from Step 1
PA_API_TOKEN = "548a594ff938e66955bff3d30544ac8a463461b5"

# 🔹 Path to your ZIP file (Corrected)
FILE_PATH = r"D:\BRYMAX\brymaxtech.zip"

# 🔹 Upload URL
UPLOAD_URL = f"https://www.pythonanywhere.com/api/v0/user/{PA_USERNAME}/files/path/home/{PA_USERNAME}/brymaxtech.zip"

# 🔹 API Headers
HEADERS = {"Authorization": f"Token {PA_API_TOKEN}"}

# 🔹 Uploading the file
with open(FILE_PATH, "rb") as file:
    response = requests.post(UPLOAD_URL, headers=HEADERS, files={"file": file})

# 🔹 Check Response
if response.status_code == 201:
    print("✅ Upload successful!")
else:
    print(f"❌ Upload failed: {response.text}")
