# dotenv til at læste env filer
from dotenv import load_dotenv
# Miljøvariabler
import os
# OpenAI client til embeddings
from openai import OpenAI

# Load variabler fra .env
load_dotenv()
# Init OpenAI client med API key
client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))