import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import subprocess

# target URLs
main_url = "https://example.com"
popup_url = "https://popup.example.com"

# credentials
users = {
    "user1": "password1",
    "user2": "password1",
    "user3": "password1"
}

# datetimenow, time warning and error limits
main_url_upper_limit_seconds_for_service_restart = 180
popup_url_upper_limit_seconds_for_service_restart = 180
main_url_upper_limit_seconds_for_email_notification = 15
popup_url_upper_limit_seconds_for_email_notification = 15
main_loading_time_list = []
popup_loading_time_list = []
now = datetime.now()

# html filenames and paths
ok_file_name = "ok.html"
# html file that tells prtg all is good
err_file_name = "err.html"
# html file with description of the error
file_path = r"path to IIS folder"
ok_file_path_name = os.path.join(file_path, ok_file_name)
err_file_path_name = os.path.join(file_path, err_file_name)
html_path_name = ""

# email credentials
mail_from = "monitoring@email.com"
mail_to = ["my_email@email.com", "other_email@email.com"]
email_username = "monitoring@email.com"
email_password = "$uperStr0ngpassword!"

# powershell
powershell_exe_file_name = "powershell.exe"
powershell_exe_file_path = r"path to powershell exe\System32\WindowsPowerShell\v1.0"
complete_powershell_exe_file_path_name = os.path.join(powershell_exe_file_path, powershell_exe_file_name)
powershell_script_file_name = "servicerestart.ps1"
powershell_script_file_path = r"path tho script"
complete_powershell_script_file_path_name = os.path.join(powershell_script_file_path, powershell_script_file_name)

# function to check url accessibility


def website_status_code_check(url):
    try:
        status_code = urllib.request.urlopen(url).getcode()
        if status_code == 200:
            return True
        else:
            return False
    except (urllib.error.URLError, urllib.error.HTTPError):
        return False


# function login to website and measure loading times


def login_and_time_measure(username, password):
    # install chrome driver manager as service
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    # define wait
    wait = WebDriverWait(driver, 300)
    driver.get(main_url)
    # click on the link
    start_time_main = time.time()
    # start measuring time
    wait.until(ec.presence_of_element_located((By.ID, "login")))
    # wait until the element login button is present in the page
    username_field = driver.find_element(By.ID, "j_username")
    password_field = driver.find_element(By.ID, "j_password")
    login_button = driver.find_element(By.ID, "login")
    username_field.send_keys(username)
    # send username
    password_field.send_keys(password)
    # send password
    login_button.click()
    # click login button
    site_loading_time = time.time() - start_time_main
    # stop measuring main url loading time
    driver.get(popup_url)
    # pop up window open
    start_time_popup = time.time()
    # start measuring time
    wait.until(ec.presence_of_element_located(
        (By.CSS_SELECTOR, "#header_tab_wrapper > div.header_wrapper > div.column_one.layout > p > strong")))
    # wait until element is present in the page
    popup_site_loading_time = time.time() - start_time_popup
    # stop measuring pop up loading time
    driver.close()
    driver.quit()
    return site_loading_time, popup_site_loading_time
    # the function return main url loading time and popup window loading time


# create/update html


def create_update_html_file(html_path_name, html_message):
    content = open(html_path_name, "w")
    content.write(html_message)
    content.close()


# function send email


def email_send(mail_subject_arg, mail_body_arg):
    mail_subject = mail_subject_arg
    mail_body = mail_body_arg
    mimemsg = MIMEMultipart()
    mimemsg['From'] = mail_from
    mimemsg['To'] = ";".join(mail_to)
    mimemsg['Subject'] = mail_subject
    mimemsg.attach(MIMEText(mail_body, 'plain'))
    connection = smtplib.SMTP(host='smtp.email.com', port=587)
    connection.starttls()
    connection.login(email_username, email_password)
    connection.send_message(mimemsg)
    connection.quit()


# url accessibility check


if not website_status_code_check(main_url):
    # main url does not return code 200
    print("Site main url inaccessible. delete ok html, send email, create err html")
    # check if ok html exists and remove it
    if os.path.exists(ok_file_path_name):
        os.remove(ok_file_path_name)
    html_path_name = err_file_path_name
    html_message = f””html message”””
    create_update_html_file(html_path_name, html_message)
    mail_subject_arg = "Site main url is not accessible!"
    mail_body_arg = f"""email body """
    email_send(mail_subject_arg, mail_body_arg)


elif not website_status_code_check(popup_url):
    # Site main url is  available but the popup window doesnt return code 200
    print("popup window inaccessible. delete ok html, send email, create err html")
    if os.path.exists(ok_file_path_name):
        os.remove(ok_file_path_name)
    html_path_name = err_file_path_name
    html_message = fhtml message"""
    create_update_html_file(html_path_name, html_message)
    mail_subject_arg = "Site popup url is not accessible!"
    mail_body_arg = f"""email body """
    email_send(mail_subject_arg, mail_body_arg)
else:
    # both urls are accessible
    print("Both urls are accessible start checking loading time")
    # iterate through users dictionary
    for username, password in users.items():
        loading_times = login_and_time_measure(username, password)
        main_url_loading_time = loading_times[0]
        popup_url_loading_time = loading_times[1]
        main_loading_time_list.append(main_url_loading_time)
        popup_loading_time_list.append(popup_url_loading_time)

    # take users as list of keys
    user_list = list(users.keys())
    print(f"list of users trying to login: {user_list}")
    print(f"main url loading times: {main_loading_time_list}")
    print(f"popup url loading times: {popup_loading_time_list}")

    # loading times and users as list of strings
    result = []
    # checking if ANY element of ANY list is above service restart error limit
    if (any(x >= main_url_upper_limit_seconds_for_service_restart for x in main_loading_time_list)) or \
            (any(x >= popup_url_upper_limit_seconds_for_service_restart for x in popup_loading_time_list)):
        print("Loading time above error limit, send email, delete ok html, create err html, service restart?")
        # start checking which user and which loading time is above error limit
        for i, user in enumerate(user_list):
            if main_loading_time_list[i] >= main_url_upper_limit_seconds_for_service_restart:
                title = "main url"
                result.append(f"User {user_list[i]}: main url loading time: {main_loading_time_list[i]}")
            if popup_loading_time_list[i] >= popup_url_upper_limit_seconds_for_service_restart:
                title = "popup url"
                result.append(f"User {user_list[i]}: popup url loading time: {popup_loading_time_list[i]}")
        print(result)
        if os.path.exists(ok_file_path_name):
            os.remove(ok_file_path_name)
        html_path_name = err_file_path_name
        html_message = f”””html message"""
        create_update_html_file(html_path_name, html_message)
        mail_subject_arg = f"Site {title} loading time is above service restart limit!"
        mail_body_arg = f"""email body """
        email_send(mail_subject_arg, mail_body_arg)
        p = subprocess.Popen([complete_powershell_exe_file_path_name, complete_powershell_script_file_path_name])
        # powershell script waits 20 seconds before starting the service
        q = p.communicate()
    # start checking if ANY element of ANY list is above email notification limit
    elif (any(x >= main_url_upper_limit_seconds_for_email_notification for x in main_loading_time_list)) or \
            (any(x >= popup_url_upper_limit_seconds_for_email_notification for x in popup_loading_time_list)):
        print("Loading time above warning limit, send email, update ok html")
        # start checking which user and which loading time is above error limit
        for i, user in enumerate(user_list):
            if main_loading_time_list[i] >= main_url_upper_limit_seconds_for_email_notification:
                title = "main url"
                result.append(f"User {user_list[i]}: main url loading time: {main_loading_time_list[i]}")
            if popup_loading_time_list[i] >= popup_url_upper_limit_seconds_for_email_notification:
                title = "popup url"
                result.append(f"User {user_list[i]}: popup url loading time: {popup_loading_time_list[i]}")
        print(result)
        html_path_name = ok_file_path_name
        html_message = f”””html message"""
        create_update_html_file(html_path_name, html_message)
        mail_subject_arg = f"Site {title} loading time is above warning limit!"
        mail_body_arg = f"""email body """
        email_send(mail_subject_arg, mail_body_arg)
    # else all is good
    else:
        print("Loading time is ok, update ok html")
        for i, user in enumerate(user_list):
            result.append(f"User {user_list[i]}: main url loading time: {main_loading_time_list[i]}")
            result.append(f"User {user_list[i]}: popup url loading time: {popup_loading_time_list[i]}")
        html_path_name = ok_file_path_name
        html_message = f"""html message"""
        create_update_html_file(html_path_name, html_message)
        print(*result, sep="\n")
