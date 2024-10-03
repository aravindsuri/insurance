from datetime import datetime
import os
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from supabase import create_client, Client
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables (Supabase credentials)
load_dotenv()

app = FastAPI()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define the storage bucket name
BUCKET_NAME = 'InsuranceBot'  # Replace with your actual bucket name

# Define the request model to receive the question
class QuestionRequest(BaseModel):
    prompt: str


    
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

def generate_answer(question: str):
    if "coverage" in question.lower():
        return {"answer": "Your coverage includes general liability, property insurance, and workers' compensatio."}
    elif "premium" in question.lower():
        return {"answer": "Your monthly premium is $500."}
    elif "deductible" in question.lower():
        return {"answer": "Your deductible is $1,000."}
    elif "chart" in question.lower():
        return {
            "answer": "Here is how your insurance premium increased over time.",
            "chart_data": {
                "labels": ["2020", "2021", "2022", "2023", "2024"],
                "values": [63, 63, 69, 69, 73]
            }
        }
    else:
        return {"answer": "Sorry, I don't have an answer to that question."}

# Define the FastAPI endpoint
@app.post("/getanswer")
async def get_answer(question: QuestionRequest):
    # Generate an answer based on the question
    answer = generate_answer(question.prompt)
    return answer  # Return the result directly