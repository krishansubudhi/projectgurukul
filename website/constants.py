import dotenv
dotenv.load_dotenv(".env")
import os

SITE_BASE_URL=os.environ["SITE_BASE_URL"] if "SITE_BASE_URL" in os.environ else "https://gurukul.streamlit.app"