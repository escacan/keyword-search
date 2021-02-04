import requests
import sys
import csv
from urllib import parse

def getBearerToken():
    token = input("베어러 토큰 입력 : ")
    return token

def writeCsv():
    f = open('example.csv','w', newline='')
    wr = csv.writer(f)
    wr.writerow(['탁자', 'a,b,c,d,e,f,g'])
    wr.writerow(['탁자2', 'a,b,c,d,e,f,g'])
    wr.writerow(['탁자3', 'a,b,c,d,e,f,g'])

    f.close()

def readCsv():
    f = open('example.csv', 'r')
    rdr = csv.reader(f)
    for line in rdr:
        encodeKeyword(line[0])
        encodeKeyword(line[1])
    
    f.close()

def sendRequests(baseUrl, token, keywords):
    URL = baseUrl

    response = requests.get(URL) 
    print("% : %", response.status_code ,response.text)

def encodeKeyword(keywords):
    url = parse.urlparse('https://manage.searchad.naver.com/keywordstool?format=json&hintKeywords=' + keywords)

    print(url)

    query = parse.parse_qs(url.query)
    result = parse.urlencode(query, doseq=True)

    # print(query)
    # print(result)

writeCsv()
readCsv()