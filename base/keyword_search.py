import requests
import sys
import csv
import urllib
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

def sendRequests(token, keywords=''):
    print(keywords)
    bearerToken = 'Bearer ' + token
    url = 'https://manage.searchad.naver.com/keywordstool'
    values = {'format': 'json',
            'hintKeywords': '탁자,1인용탁자,2인용탁자,3인용탁자,4인용탁자'}
    headers = {'Authorization': bearerToken}
    data = urllib.parse.urlencode(values).encode('utf-8')
    # print(data)
    req = urllib.request.Request(url, data, headers, method='GET')

    try:
        f = urllib.request.urlopen(req)
        print(f.read())
        print(f.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.getcode() == 401:
            print('Bearer토큰 유효시간 민료')
            newToken = getBearerToken()
            sendRequests(newToken, keywords)
        else:
            return

def encodeKeyword(keywords):
    url = parse.urlparse('https://manage.searchad.naver.com/keywordstool?format=json&hintKeywords=' + keywords)

    print(url.geturl())

    # query = parse.parse_qs(url.query)
    # result = parse.urlencode(query, doseq=True)

    # print(query)
    # print(result)

token = getBearerToken()
sendRequests(token, "1,2,3")