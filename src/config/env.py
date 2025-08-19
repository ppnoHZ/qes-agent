from load_dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv('MODEL_NAME'))