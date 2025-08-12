from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from fastapi.staticfiles import StaticFiles

# Load environment variables
load_dotenv()

app = FastAPI()

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
