# import libraries
import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os, subprocess, smtplib
import urllib
from twilio.rest import Client
import time

now =str( datetime.datetime.now())
working_path = "/".join(os.path.realpath(__file__).split("/")[:-1])+"/"
debug = False

def send_email(content):
    print("\nFound:")
    for i in content:	
        print(i)

    sender_email = "xxxx"
    sender_login = "xxxx"
    sender_pass = "xxxx"
    sender_server = "xxxx"
    receiver_email = "xxxx"


    mail_head = "From: "+sender_email+"\nTo: "+receiver_email+"\nSubject: New adverts!\n\n\n"
    mail_body =  "Here you go:\n\n" + '\n'.join(map(str, content))
    msg = mail_head + mail_body

    server = smtplib.SMTP_SSL('sender_server', 465)
    server.login(sender_login, sender_pass) 
    server.sendmail(sender_email, receiver_email, msg)
    server.quit()
    print(now +  " - Email sent ")

def send_sms(content):
    msg_body =  '\n      '.join(map(str, content))
    account_sid = 'xxxxxxxxxx'
    auth_token = 'xxxxxxxxxxx'
    client = Client(account_sid, auth_token)
    msg = "\nNew:" + msg_body 


    message = client.messages \
	                .create(
	                     body=msg,
	                     from_='+xxxxx', #phone number obtained from twilo 
	                     to='+xxxxx' #your phone number
	                 )

    print(now +  " - SMS sent " + message.sid)


def clean_entries(result_list):
    result_list_copy = list(result_list)
    forbidden_words = ["4gb"] #if script will find any word from this list in advert url, then url will be omitted
    for entry in result_list:
        for word in forbidden_words:
            if word in entry :
                if entry in result_list_copy:
                    result_list_copy.remove(entry)
    return result_list_copy

def get_diff(name, content):
    list_from_file = []
    for line in open(working_path +name, 'r'):
        list_from_file.append(line.strip())
    diff = list (set(content) - set(list_from_file))
    to_save = list(set(content) | set (list_from_file) )
    with open( working_path + name, 'w') as f:
        for item in to_save:
            f.write("%s\n" % item)
    return diff

def handle_olx(given_url_list):
    url_list = []
    for link in given_url_list:
        if debug:
            print (now + " processing "+ link)
        i=0
        while(True):
            i= i+1
            url = link+"&page="+str(i)
            req = urllib.request.Request(
            url, 
            data=None, 
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
            page = urlopen(req)
            soup = BeautifulSoup(page, "html.parser")
            pager = soup.find("div", attrs={"class": "pager rel clr"})
            if pager:    
                pager = pager.text
                pages_number = ( max([int(s) for s in pager.split() if s.isdigit()])   )
            else:
                if debug:
                    print("No pager!")
                pages_number = i 
                no_results = soup.find("h1", attrs={"class": "c41 lheight24"})
                if no_results:
                    if debug:
                        print(link + " gave no results! ")
                    break
            table = soup.find_all("a", attrs={"class": "marginright5 link linkWithHash detailsLink"})      
            for entry in table:
                url_list.append(entry.get("href").split('?')[0].split('#')[0])
            if pages_number == i:
                break

    cleaned = clean_entries(url_list)
    diff = get_diff("olx", cleaned )    
    if diff:
        return diff  
    else:
        print(now + " OLX -  Nothing new")
        return []

def handle_gumtree(given_url_list):
    url_list = []
    for link in given_url_list:
        time.sleep(3)
        i= 1
        while(True):        
            if i == 1:
                url = link
            else:
                splited = link.split("/")
                url = "/".join(splited[:-1])+"/page-"+str(i)+"/"+splited[-1]
            if debug:
                print(url)    
            req = urllib.request.Request(
            url, 
            data=None, 
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
            page = urlopen(req)
            if page == "":
                print(now + link + "something's wrong")
            soup = BeautifulSoup(page, "html.parser")

            pages_number = (soup.find("a", attrs={"class": "last follows"}) )
            if pages_number:
           	    pages_number= int(pages_number.get("href").split("page-")[1].split("/")[0])
            else:
                pages_number = 1

            adverts = soup.find_all("a", attrs={"class": "href-link"})
            for entry in adverts:
                url_list.append("https://www.gumtree.pl" +entry.get("href"))    
            if i ==  pages_number:
                break
            break
    cleaned = clean_entries(url_list)
    diff = get_diff("gumtree", cleaned )    
    if diff:
        return diff
    else:
        print(now + " Gumtree - Nothing new")
        return []


#provide urls to monitor in every website

url_olx = [
"https://www.olx.pl/warszawa/q-google-pixel/?search%5Bfilter_float_price%3Ato%5D=800",
]

url_gumtree = ["https://www.gumtree.pl/s-mieszkania-i-domy-sprzedam-i-kupie/bielany/v1c9073l3200011p1?pr=150000,275000&sort=dt&order=desc",
]

new_links = []

new_links = new_links + handle_olx(url_olx)
new_links = new_links + handle_gumtree(url_gumtree)


if new_links:
	send_email(new_links)
	send_sms(new_links)

