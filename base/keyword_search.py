import requests
import sys
import csv
import urllib
import urllib.parse 

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
    bearerToken = 'Bearer ' + token
    url = 'https://manage.searchad.naver.com/keywordstool'
    print(url)
    headers = {'Authorization': bearerToken}
    params = {
        'format': 'json',
        'hintKeywords': keywords
    }

    try:
        resp = requests.get(url= url, headers= headers, params= params)
        print(resp.json())

        # print(len(keywords))
    except urllib.error.HTTPError as e:
        if e.getcode() == 401:
            print('Bearer토큰 유효시간 민료')
            newToken = getBearerToken()
            sendRequests(newToken, keywords)
        else:
            return


token = getBearerToken()
sendRequests(token, "탁자,1인용탁자")