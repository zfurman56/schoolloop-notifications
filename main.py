import requests
import Cookie
import pickle
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import time
import emailer


# parse command line arguments
args = sys.argv[1:]
if len(args) != 7:
    sys.exit("Usage: python main.py <schoolloop school prefix> <schoolloop username> <schoolloop password> <destination address> <sender address> <sender password> <smtp address> <time between updates>")

if len(args) == 8:
    update_time = int(args[7])
else:
    update_time = int(60)
    
def main():
    """Main program loop."""

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
        teacher_name = str(row.find("td", {"class": "teacher co-teacher"}).a.text).strip().split(", ")[1] + " " + str(row.find("td", {"class": "teacher co-teacher"}).a.text).strip().split(", ")[0]
        new_data.append([course_name, grade, teacher_name])


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
        emailer.send(emailer.format(new_data, old_data), args[3], args[4], args[5], args[6])

try:
    while True:
        main()
        time.sleep(update_time)
except KeyboardInterrupt:
    print "User terminated the program, shutting down..."
