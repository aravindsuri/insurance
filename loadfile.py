import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define the storage bucket name
BUCKET_NAME = 'InsuranceBot'  # Replace with your actual bucket name


file_path = "C:/Users/aravi/dev/web_apis/sec-edgar-filings/AAPL/10-K/0000320193-23-000106/AAPL_10k_latest.pdf"
with open(file_path, 'rb') as file_content:
    # Define just the file name for Supabase storage, without any path
    file_name_in_storage = "AAPL_10k_latest.pdf"  # Only the file name, no directory path

    response = supabase.storage.from_(BUCKET_NAME).upload(file_name_in_storage, file_content)