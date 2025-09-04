import openpyxl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
# Load the workbook
workbook = openpyxl.load_workbook('uploads/Now.xlsx')

# Select a sheet
sheet = workbook.active  # Or workbook['SheetName']
e_list=[]

# Read data from a specific cell
cell_value = sheet['A1'].value
print(f"Value of A1: {cell_value}")

# Iterate through rows and print values
for row in sheet.iter_rows():
    for cell in row:
      e_list.append(cell.value)
e_list.pop(0)
print(e_list)
names_list = [email.split('@')[0].split('.')[0] for email in e_list]
print(names_list)
names_list_title_case = [name.title() for name in names_list]
print(names_list_title_case)
names_list_title_case = [name.title() for name in names_list]
print(names_list_title_case)
e_list_lower = [email.lower() for email in e_list]
print(e_list_lower)
import re

cleaned_names_list = []
for name in names_list:
    # Remove numbers and symbols using regex
    cleaned_name = re.sub(r'[^a-zA-Z\s]', '', name)
    cleaned_names_list.append(cleaned_name)
filtered_names_list = cleaned_names_list
print(filtered_names_list)

# Define your email address and password
sender_email = "yadlapallis050@gmail.com"  # Replace with your email
sender_password = "wcae jlkw mnry npup   "  # Replace with your password

# Define SMTP server details (example for Gmail)
smtp_server = "smtp.gmail.com"
smtp_port = 587  # For TLS

print("Email environment configured.")
resume_path = "uploads/Yadlapalli_Sainath_Senior_Data_Analyst_Resume.docx"

# Open the file in read-binary mode
with open(resume_path, 'rb') as attachment:
    # Create a MIMEBase object
    part = MIMEBase("application", "octet-stream")

    # Set the payload to the content of the attachment
    part.set_payload(attachment.read())

# Encode the payload using Base64
encoders.encode_base64(part)

# Set the Content-Disposition header
part.add_header(
    "Content-Disposition",
    f"attachment; filename= {resume_path}",
)
subject = "Resume for Data Analyst Position"

# Connect to the SMTP server
try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Secure the connection
    server.login(sender_email, sender_password)

    # Iterate through the lists and send emails
    for recipient_email, recipient_name in zip(e_list_lower, filtered_names_list):
        # Create the email message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = "subject"

        # Replace the placeholder in the body with the recipient's name
        personalized_body = body = f"Hi {recipient_name},\n\nI hope this mail finds you well.\n\nPlease find attached my updated resume for your consideration for the Data Analyst position.\nWith [6 years] of experience in developing interactive dashboards, data visualization, SQL, and BI solutions.\nI am confident that my skills align well with the requirements of the role.\n\nI look forward to the opportunity to contribute my expertise and discuss how I can add value to your team.\n\nThanks & Regards,\nSainath.\nph.no :8309632859"
        # Attach the body to the email
        msg.attach(MIMEText(personalized_body, "plain"))

        # Attach the resume file
        msg.attach(part)

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Email sent to {recipient_email}")

except Exception as e:
    print(f"Error: {e}")

finally:
    # Close the connection
    if 'server' in locals() and server:
        server.quit()