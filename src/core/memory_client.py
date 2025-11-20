import os
from dotenv import load_dotenv
from mem0 import AsyncMemoryClient

load_dotenv()

memory_client = AsyncMemoryClient(api_key=os.getenv("MEM0_API_KEY"))