from datetime import datetime
import os
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables (Supabase credentials)
load_dotenv()

app = FastAPI()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define the storage bucket name
BUCKET_NAME = 'InsuranceBot'  # Replace with your actual bucket name

# Endpoint to retrieve a list of files from a Supabase storage bucket
@app.get("/getfiles")
async def get_files():
    try:
        response = supabase.storage.from_(BUCKET_NAME).list()
        
        # Ensure response is a list of files
        if isinstance(response, list):
            #filtered_files = [file['name'] for file in response if file['name'] != '.emptyFolderPlaceholder']
            return {"files": response}
        else:
            raise HTTPException(status_code=500, detail="Failed to retrieve files.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to upload a file to a Supabase storage bucket
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read the file content and extract the filename
        file_content = await file.read()
        file_name = file.filename
        # file_name = "test" + datetime.now().strftime("%Y%m%d%H%M%S") + ".pdf"

        if file_name == "":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_extension = ".pdf"  # Default extension, modify as needed
            # file_name = f"uploaded_file_{timestamp}{default_extension}"
            file_name = file_name.strip()  # Remove extra spaces
        else:
            file_name = file_name.strip()  # Remove extra spaces

        # Ensure the file name is not empty or invalid
        if not file_name:
            raise HTTPException(status_code=400, detail="File name is invalid")
        
        # Ensure that the file name is valid (you can add more checks if necessary)
        file_name = file_name.strip()  # Remove extra spaces
        if len(file_name) == 0 or any(char in file_name for char in r'\/:*?"<>|'):
            raise HTTPException(status_code=400, detail="Invalid file name")

        # Upload the file to Supabase Storage
        response = supabase.storage.from_(BUCKET_NAME).upload(file_name, file_content)

        # Check if there is an error in the response
        if isinstance(response, dict) and 'error' in response:
            raise HTTPException(status_code=500, detail=response['error'])

        return {"status": "File uploaded successfully", "file_name": file_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
