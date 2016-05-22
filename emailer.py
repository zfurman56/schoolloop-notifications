import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys

def send((html_text, regular_text), destination, sender, sender_pwd, smtp_address):
    """
    Send an email to yourself.

    Parameters:
    - html_text and regular_text are the email content, typically the output of format()
    - destination is the email address you would like to send updates to
    - sender is the email address you want to send updates from
    - sender_pwd is the password for the sender email account
    - smtp_address is the smtp server for sender, with port number (e.g. "smtp.gmail.com:587")
    """

    # create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Your grades have changed"
    msg['From'] = sender
    msg['To'] = destination

    # record MIME types
    part1 = MIMEText(regular_text, 'plain')
    part2 = MIMEText(html_text, 'html')

    # attach parts into message container.
    msg.attach(part1)
    msg.attach(part2)

    server = smtplib.SMTP(smtp_address)

    # start TLS
    server.ehlo()
    server.starttls()

    server.login(sender, sender_pwd)

    # send message
    server.sendmail(destination, sender, msg.as_string())
    server.quit()


def format(data, old):
    """Convert raw data to email format."""

    changed = []
    body = "<br><table align='center'>"

    # determine whether grades have changed, and if so which classes
    for index in xrange(0, len(data)):
        try:
            if (data[index][1] != old[index][1]) or (data[index][0] != old[index][0]):
                changed.append([data[index][0], data[index][1], (round(100*(data[index][1] - old[index][1]))/100)])
        # if classes are missing or changed, exit the program
        # everything will work normally the next time the program is run
        except IndexError, TypeError:
            sys.exit()
        body = body + "<tr><td style='padding: 0.3em 2em;'>" + data[index][0] + ":</td><td>" + str(data[index][1]) + "</td></tr>"

    body = body + "</table><br><br>"
    top = ""

    for course in changed:
        # grade increases are green, decreases are red
        if course[2] > 0:
            color = 'green'
        else:
            color = 'red'
        top = top + "<p style='text-align: center;'>" + course[0] + ": Net change of <b style='color:" + color + "'>" + str(course[2]) + "</b></p>"
        regular = course[0] + ": Net change of " + str(course[1])

    return ((top + body), regular)

