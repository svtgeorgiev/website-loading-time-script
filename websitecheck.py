import urllib
from urllib import request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import os
import time
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import subprocess

# usernames, passwords, filenames, paths, etc.
email_username = "email which sends messages"
email_password = "email password"
# monitoring email sender
agile_username = "username"
agile_password = "password"
# password for agile
mail_from = "email which sends messages"
mail_to = [list of recipients]
# list of recipients
ok_file_name = "new_agileserver_site_status.html"
# html when all good
err_file_name = "new_agileserver_err_msg.html"
# html when site inaccessible or service need restart
file_path = r"C:\inetpub\wwwroot\.... path to IIS folder"
# path to IIS folder
ok_file_path_name = os.path.join(file_path, ok_file_name)
err_file_path_name = os.path.join(file_path, err_file_name)
powershell_exe_file_name = "powershell.exe"
powershell_exe_file_path = r"C:\path to powershell exe"
complete_powershell_exe_file_path_name = os.path.join(powershell_exe_file_path, powershell_exe_file_name)
powershell_script_file_name = "agileserverservicerestart.ps1"
powershell_script_file_path = r"C:powershell script path"
complete_powershell_script_file_path_name = os.path.join(powershell_script_file_path, powershell_script_file_name)
# powershell exe and script details
upper_limit_seconds_for_service_restart = 60
upper_limit_seconds_for_email_notification = 20
# warning and error limits
now = datetime.now()
# current date and time
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
wait = WebDriverWait(driver, 300)

# trying to open agileapp01
try:
    agile_url = "http://agile site"
    agileapp01_status_check = urllib.request.urlopen(agile_url)
    site_status = int(agileapp01_status_check.getcode())
    driver.get(agile_url)
    driver.find_element(By.ID, "j_username").send_keys(agile_username)
    driver.find_element(By.ID, "j_password").send_keys(agile_password)
    driver.find_element(By.ID, "login").click()
    start_time = time.time()  # start count time
    login_message = driver.find_element(By.CSS_SELECTOR, "#dms > p").text
    driver.get("http://agile Main Menu")
    wait.until(ec.presence_of_element_located(
        (By.CSS_SELECTOR, "#header_tab_wrapper > div.header_wrapper > div.column_one.layout > h2")))

    welcome = driver.find_element(By.CSS_SELECTOR,
                                  "#header_tab_wrapper > div.header_wrapper > div.column_one.layout > h2").text
    end_time = time.time()  # stop count time
    elapsed_time = end_time - start_time  # calculated difference between start and end time by epoch
    print(f"elapsed time is {elapsed_time}, type is {type(elapsed_time)}")
    if elapsed_time > upper_limit_seconds_for_service_restart:
        print(f"restart service {elapsed_time}")
        print("sending email that service will be restarted")
        mail_subject = f"Service restart: Agile loading time more than {upper_limit_seconds_for_service_restart} seconds"
        mail_body = f"""Agile loading time is {elapsed_time} seconds and is above the error limit of {upper_limit_seconds_for_service_restart} seconds.
        Agileservice service on Agileserver will be restarted. Check agile status on http://IIS site address/new_agileserver_err_msg.html
       
        NOC team"""

        mimemsg = MIMEMultipart()
        mimemsg['From'] = mail_from
        mimemsg['To'] = ";".join(mail_to)
        mimemsg['Subject'] = mail_subject
        mimemsg.attach(MIMEText(mail_body, 'plain'))
        connection = smtplib.SMTP(host='smtp.office365.com', port=587)
        connection.starttls()
        connection.login(email_username, email_password)
        connection.send_message(mimemsg)
        connection.quit()
        p = subprocess.Popen([complete_powershell_exe_file_path_name, complete_powershell_script_file_path_name])
        # powershell script waits 20 seconds before starting the service
        q = p.communicate()
        print(q)
        # removing html that prtg listens to
        os.remove(ok_file_path_name)
        # create error html file
        content = open(err_file_path_name, "w")
        message = f"""
                <html>
                    <head>
                        <title>agileserver site status</title>
                    </head>
                <body>
                <p>agileserver site is up. Code {site_status}</p>
                <p>But time between login and page loading is {elapsed_time} above the error limit of {upper_limit_seconds_for_service_restart} seconds</p>
                <p>Agileservice service on Agileserver restart</p>
                <p>Email notification to {mail_to} sent.</p>
                <p>Report created: {now}</p>
                </body>
                </html>
                """
        content.write(message)
        content.close()

    elif upper_limit_seconds_for_service_restart > elapsed_time >= upper_limit_seconds_for_email_notification:
        print("send warning email")
        mail_subject = f"Warning: Agile loading time more than {upper_limit_seconds_for_email_notification} seconds"
        mail_body = f"""Agile loading time is {elapsed_time} seconds and is above the warning limit of {upper_limit_seconds_for_email_notification} seconds.
        Check agile status on http://IIS site address/new_agileserver_site_status.html
        NOC team"""

        mimemsg = MIMEMultipart()
        mimemsg['From'] = mail_from
        mimemsg['To'] = ";".join(mail_to)
        mimemsg['Subject'] = mail_subject
        mimemsg.attach(MIMEText(mail_body, 'plain'))
        connection = smtplib.SMTP(host='smtp.office365.com', port=587)
        connection.starttls()
        connection.login(email_username, email_password)
        connection.send_message(mimemsg)
        connection.quit()
        content = open(ok_file_path_name, "w")
        message = f"""
                    <html>
                    <head>
                        <title>agileserver site status</title>
                    </head>
                <body>
                <p>agileserver site is up. Code {site_status}</p>
                <p>But time between login and page loading is {elapsed_time} above the error limit of {upper_limit_seconds_for_service_restart} seconds</p>
                <p>AgilePLMManaged1 service on Agileserver restart</p>
                <p>Email notification to {mail_to} sent.</p>
                <p>Report created: {now}</p>
                </body>
                </html>
                """
        content.write(message)
        content.close()
    else:
        print(f"all good {elapsed_time}")
        content = open(ok_file_path_name, "w")
        message = f"""
                <html>
                    <head>
                        <title>agileserver site status</title>
                    </head>
                <body>
                <p>agileserver site is up. Code {site_status}</p>
                <p>time between login and page loading is {elapsed_time} seconds</p>
                <p>Report created: {now}</p>
                </body>
                </html>
                """
        content.write(message)
        content.close()


except:
    os.remove(ok_file_path_name)
    print("agile is not accessible email")
    mail_subject = "Error: Agile site not accessible"
    mail_body = f"""Agile {agile_url} could not be reached.
            NOC team"""

    mimemsg = MIMEMultipart()
    mimemsg['From'] = mail_from
    mimemsg['To'] = mimemsg['To'] = ";".join(mail_to)
    mimemsg['Subject'] = mail_subject
    mimemsg.attach(MIMEText(mail_body, 'plain'))
    connection = smtplib.SMTP(host='smtp.office365.com', port=587)
    connection.starttls()
    connection.login(email_username, email_password)
    connection.send_message(mimemsg)
    connection.quit()
    content = open(err_file_path_name, "w")
    message = f"""
                         <html>
                             <head>
                                 <title>agileserver site status</title>
                             </head>
                         <body>
                         <p>agileserver is down.</p>
                         <p>Email notification to {mail_to} sent.</p>
                         <p>Report created: {now}</p>
                         </body>
                         </html>
                         """
    content.write(message)
    content.close()
