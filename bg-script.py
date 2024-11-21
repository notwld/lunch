from app.models import db, Order
from app import create_app
from datetime import datetime, timedelta

app = create_app()

def check_near_deadline_orders():
    with app.app_context():
        now = datetime.utcnow()
        reminder_time = now + timedelta(days=1)

        near_deadline_orders = Order.query.filter(
            Order.deadline >= now,
            # Order.deadline < reminder_time,
            Order.status == "Pending"
        ).all()

        for order in near_deadline_orders:
            send_reminder_email(order.parent.email, order.id, order.total_cost, order.deadline)

        db.session.commit()

        print(f"{len(near_deadline_orders)} reminder emails sent for orders nearing deadlines.")
        
email_address="mwfarrukh@gmail.com"
email_password="qnknnvvnvcgexoun"

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to, subject, body):
    try:
        if to is None:
            raise ValueError("Recipient email address is None")
        message = MIMEMultipart()
        message["From"] = email_address
        message["To"] = to
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Use TLS (Transport Layer Security)
            server.login(email_address, email_password)

            # Send the email
            server.sendmail(email_address, to, message.as_string())

        print(f"Email sent to {to} successfully.")
        return True
    except Exception as e:
        print(f"Error sending email to {to}: {e}")
        return False
def send_reminder_email(email, order_id, total_cost, deadline):
    print(f"Reminder email sent to {email} for Order {order_id}. Total: ${total_cost:.2f}, Deadline: {deadline}")
    send_email(email, "Order Reminder", f"Your order is due soon! Total: ${total_cost:.2f}, Deadline: {deadline}")


if __name__ == "__main__":
    check_near_deadline_orders()