import requests
import sys
import csv

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

def filterKeywords(keywordDict):
    # 총 검색횟수 1000회 이상인 키워드 필터링
    filterKeywordsDict = {}
    for keyword, cnt in keywordDict.items():
        if cnt >= 1000:
            filterKeywordsDict[keyword] = cnt

    print("검색수 1000이상인 키워드 개수 : ", len(filterKeywordsDict))

def sendRequests(token, keywords=''):
    bearerToken = 'Bearer ' + token
    url = 'https://manage.searchad.naver.com/keywordstool'

    headers = {'Authorization': bearerToken}
    params = {
        'format': 'json',
        'hintKeywords': keywords
    }

    try:
        resp = requests.get(url= url, headers= headers, params= params)

        if resp.status_code == 401:
            print('Bearer토큰 유효시간 민료')
            newToken = getBearerToken()
            sendRequests(newToken, keywords)        
        else:
            if resp.status_code != 200:
                print("StatusCode가 이상하다. 확인필요")
                return

            keywordList = resp.json().get('keywordList')

            print("검색된 단어 개수 : {}".format(len(keywordList)))

            tempKeyword = keywordList[0]

            print(tempKeyword)

            print(type(tempKeyword['monthlyPcQcCnt']))

            print(type(tempKeyword['monthlyMobileQcCnt']))

            print(tempKeyword['monthlyPcQcCnt'] + tempKeyword['monthlyMobileQcCnt'])

            parsedKeywordDict = {}
            i = 0
            try:
                for keyword in keywordList:
                    if keyword['monthlyPcQcCnt'] == '< 10' or keyword['monthlyMobileQcCnt'] == '< 10':
                        i = i+1
                        continue;

                    parsedKeywordDict[keyword['relKeyword']] = keyword['monthlyPcQcCnt'] + keyword['monthlyMobileQcCnt']                
                    i = i + 1
            except Exception as e:
                print(str(e))
                print("Error on {}".format(i))
                print(keywordList[i])

            filterKeywords(parsedKeywordDict)

    except Exception as e:
        print(str(e))

token = getBearerToken()
sendRequests(token, "탁자,1인용탁자")