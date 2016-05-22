import requests
import Cookie
import pickle
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import time


# parse command line arguments
args = sys.argv[1:]
if len(args) != 7:
    print "usage: python main.py <schoolloop school prefix> <schoolloop username> <schoolloop password> <destination address> <sender address> <sender password> <smtp address>"
    sys.exit()

def send_email((html_text, regular_text), destination, sender, sender_pwd, smtp_address):
    """
    Send an email to yourself.

    Parameters:
    - html_text and regular_text are the email content, typically the output of format_to_email()
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


def format_to_email(data, old):
    """Convert raw data to email format."""

    changed = []
    body = "<br><table>"

    # determine whether grades have changed, and if so which classes
    for index in xrange(0, len(data)):
        try:
            if (data[index][1] != old[index][1]) or (data[index][0] != old[index][0]):
                changed.append([data[index][0], data[index][1], (data[index][1] - old[index][1])])
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

def main():
    """Main progam loop."""

    # need to make two requests -
    # the first to gather necessary login fields and cookies,
    # the second to actually login

    # make first request
    request1 = requests.get(('https://' + args[0] + '.schoolloop.com/portal/guest_home?d=x'))
    soup1 = BeautifulSoup(request1.text)

    # parse data, create data for next request
    form_data_id = soup1.find("input", {"id" : "form_data_id"})['value']
    cookie_sent = {'JSESSIONID': request1.cookies['JSESSIONID'], 'slid': request1.cookies['slid']}
    payload = {'login_name' : args[1], 'password' : args[2], 'event_override' : 'login', 'form_data_id' : form_data_id}

    # make second request
    request2 = requests.post(('https://' + args[0] + '.schoolloop.com/portal/guest_home?etarget=login_form'), cookies=cookie_sent, data=payload)
    soup2 = BeautifulSoup(request2.text)

    new_data = []

    # find and loop through courses
    for row in soup2.find_all("table", {"class" : "student_row"}):

        try:
            grade = float(row.find("div", {"class": "percent"}).text.replace('%', ''))
        # if class doesn't have a grade
        except AttributeError:
            grade = 'None'

        course_name = str(row.find("td", {"class": "course"}).a.text)
        new_data.append([course_name, grade])


    try:
        old_data = pickle.load(open('data.txt', 'rb'))
    # if data.txt is missing, load it from new_data and then quit
    # everything will work normally the next time the program is run
    except IOError, EOFError:
        pickle.dump(new_data, open('data.txt', 'wb'))
        pickle.dump(new_data, open('data.txt', 'wb'))
        sys.exit()

    if new_data != old_data:
        pickle.dump(new_data, open('data.txt', 'wb'))
        send_email(format_to_email(new_data, old_data), args[3], args[4], args[5], args[6])

while True:
    main()
    time.sleep(60)
