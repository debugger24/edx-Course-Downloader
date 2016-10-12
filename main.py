import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import re
import os

COURSE  = input("Enter course URL (Example : https://courses.edx.org/courses/course-v1:GeorgetownX+GUIX-501-03x+3T2016/courseware/) : ")
EMAIL = input("Enter Email ID : ")
PASSWORD = input("Enter Password : ")
COURSENAME = input("Enter Course Name : ")

with requests.Session() as r:

    def getTopicList(page_data):
        mainCoursePage = BeautifulSoup(page_data.text, 'html.parser')
        courseNavList = mainCoursePage.find('nav', {"class" : "course-navigation"})
        TopicList = courseNavList.find_all('a', {"class" : "button-chapter"})
        SubTopicList = courseNavList.find_all('div', {"class" : "chapter-content-container"})
        topicList = []
        for i in range(len(TopicList)):
            subTopicList = []
            for subTopic in SubTopicList[i].find_all('a', {"class" : "accordion-nav"}):
                subTopicDict = {"Title" : (subTopic.find('p').text.lstrip().rstrip()), "Link" : ("https://courses.edx.org" + subTopic.get('href'))}
                subTopicList.append(subTopicDict)
            topicDict = {"Title" : (TopicList[i].find('span', {"class" : "group-heading"}).contents[2].lstrip().rstrip()), "Sup Topic List" : subTopicList}
            topicList.append(topicDict)
        return topicList

    def downloadVideo(directory, videoTitle, videoLink):
        os.system("aria2c " + videoLink + " --dir='" + directory + "' --out='" + videoTitle + ".mp4'")

    def getVideoLinks(directory, pageURL):
        page_data = r.get(pageURL)
        soup = BeautifulSoup(page_data.text, 'html.parser')
        div = soup.find('div', {"class" : "sequence"})
        div_seq = div.find_all('div', {"class" : "seq_contents"})
        for each_seq in div_seq:
            soup = BeautifulSoup(each_seq.string, 'html.parser')
            titleElement = soup.find('h3', {"class" : "hd hd-2"})
            videoElement = soup.find('a', {"class" : "video-download-button"})
            if(videoElement is None):
                continue
            else:
                videoTitle = (titleElement.string)
                videoLink = (videoElement.get('href'));
                downloadVideo (directory, videoTitle, videoLink)

    r.get("https://courses.edx.org/login")
    csrfToken = r.cookies['csrftoken']
    login_data = {"email" : EMAIL, "password" : PASSWORD, "remember":"false"}
    cookies = {"csrftoken" : csrfToken}
    headers = {'X-CSRFToken':csrfToken, 'Referer':'https://courses.edx.org/login'}
    page_data = r.post("https://courses.edx.org/user_api/v1/account/login_session/", data=login_data, cookies = cookies, headers = headers)
    page_data = r.get(COURSE)

    topicList = getTopicList(page_data)

    directory = COURSENAME
    try:
        os.stat(directory)
    except:
        os.system('mkdir "' + directory + '"')

    for topic in topicList:
        print ("-" + topic['Title'] + "-")
        directory = COURSENAME + '/' + topic['Title']
        try:
            os.stat(directory)
        except:
            os.system('mkdir "' + directory + '"')
        for subTopic in topic['Sup Topic List']:
            print ("     -" + subTopic['Title'] + "-")
            directory = COURSENAME + '/' + str(topic['Title']) + '/' + str(subTopic['Title'])
            try:
                os.stat(directory)
            except:
                os.system('mkdir "' + directory + '"')
            getVideoLinks(directory, subTopic['Link'])
