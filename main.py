import requests
import Cookie
import pickle
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# send an email to me, zach.furman1@gmail.com
# replace with your email, password, smtp info
def send_email((html_text, regular_text)):

    me = "zach.furman1@gmail.com"
    you = "zach.furman1@gmail.com"

    # create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Your grades have changed"
    msg['From'] = me
    msg['To'] = you


    # record MIME types
    part1 = MIMEText(regular_text, 'plain')
    part2 = MIMEText(html_text, 'html')

    # attach parts into message container.
    msg.attach(part1)
    msg.attach(part2)

    # start server
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()

    # login
    server.login("zach.furman1@gmail.com","******")

    # send message
    server.sendmail(me, you, msg.as_string())
    server.quit()


# convert data to email format
def format_to_email(data, old):

    changed = []
    body = "<br><table>"

    for index in xrange(0, len(data)):
        if (data[index][1] != old[index][1]) or (data[index][0] != old[index][0]):
            changed.append([data[index][0], data[index][1], (data[index][1] - old[index][1])])
        body = body + "<tr><td style='padding: 0.3em 2em;'>" + data[index][0] + ":</td><td>" + str(data[index][1]) + "</td></tr>"

    body = body + "</table><br><br>"
    top = ""

    for course in changed:
        if course[2] > 0:
            color = 'green'
        else:
            color = 'red'
        top = top + "<p style='text-align: center;'>" + course[0] + ": Net change of <b style='color:" + color + "'>" + str(course[2]) + "</b></p>"
        regular = course[0] + ": Net change of " + str(course[1])

    return ((top + body), regular)

# need to make two requests -
# the first to gather necessary login fields and cookies,
# the second to actually login

# make first request
request1 = requests.get('https://mahs-seq-ca.schoolloop.com/portal/guest_home?d=x') # replace with your school
soup1 = BeautifulSoup(request1.text)

# parse data, create data for next request
form_data_id = soup1.find("input", {"id" : "form_data_id"})['value']
cookie_sent = {'JSESSIONID': request1.cookies['JSESSIONID'], 'slid': request1.cookies['slid']}
payload = {'login_name' : '******', 'password' : '******', 'event_override' : 'login', 'form_data_id' : form_data_id}

# make second request
request2 = requests.post('https://mahs-seq-ca.schoolloop.com/portal/guest_home?etarget=login_form', cookies=cookie_sent, data=payload)
soup2 = BeautifulSoup(request2.text)

new_data = []


# find and loop through courses
for row in soup2.find_all("table", {"class" : "student_row"}):

    try:
        grade = float(row.find("div", {"class": "percent"}).text.replace('%', ''))
    except AttributeError:
        grade = 'None';

    course_name = str(row.find("td", {"class": "course"}).a.text)
    new_data.append([course_name, grade])


old_data = pickle.load(open('data.txt', 'rb'))
if new_data != old_data:
    pickle.dump(new_data, open('data.txt', 'wb'))
    send_email(format_to_email(new_data, old_data))


