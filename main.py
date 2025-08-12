from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from fastapi.staticfiles import StaticFiles
from database import router as db_router

# Load environment variables
load_dotenv()

app = FastAPI()
app.include_router(db_router, tags=["database"])

# Will try to deploy this server on on https://render.com as given by https://chatgpt.com/c/689b137e-49c8-8324-8d2d-f7d2bb675c5a
# use https://dashboard.render.com/register to deploy the python app free

# pip install -r requirements.txt
# uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class EmailSchema(BaseModel):
    to_email: str
    subject: str
    body: str

@app.get("/")
def read_root():
    return {"message": "Hello, World! The REST server is running."}

@app.post("/send-email")
async def send_email(email: EmailSchema):
    try:
        # Get email credentials from environment variables
        sender_email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        if not all([sender_email, password, smtp_server]):
            raise HTTPException(status_code=500, detail="Email configuration is incomplete")

        # Create the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email.to_email
        message["Subject"] = email.subject

        # Add body to email
        message.attach(MIMEText(email.body, "plain"))

        # Create SMTP session
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(message)

        return {"message": "Email sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
