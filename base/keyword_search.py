import threading
import requests
import sys
import csv

clientId = ''

def getClientId():
    clientId = input("ClientId 입력 : ")
    return clientId

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

def filterKeywords(keywordList):
    print("필터링 시작")
    # 총 검색횟수 1000회 이상인 키워드 필터링
    filterKeywordsDict = {}
    print("입력된 키워드 개수 : {}".format(len(keywordList)))

    ii = 1

    for keywordObj in keywordList:
        ii = ii + 1
        if ii == 10:
            break
            # print("Cur II : {}".format(ii))
        keyword, searchCount = keywordObj['keyword'], keywordObj['searchCount']
        print("Keyword : {},  cnt : {}".format(keyword, searchCount))
        if searchCount >= 1000:
            shoppingData = sendRequestToNaverShopping(keyword)
            filterKeywordsDict[keyword] = {
                'searchCount': searchCount,
                'itemCategory': shoppingData['itemCategory'],
                'totalItemCount': shoppingData['totalItemCount'],
                'ratio': float(shoppingData['totalItemCount']) / searchCount
            }
            print(filterKeywordsDict[keyword])

    print("검색수 1000이상인 키워드 개수 : ", len(filterKeywordsDict))
    print(filterKeywordsDict)


def sendRequestToNaverKeywordTool(token, keywords=''):
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
            sendRequestToNaverKeywordTool(newToken, keywords)        
        else:
            if resp.status_code != 200:
                print("StatusCode가 이상하다. 확인필요")
                return

            keywordList = resp.json().get('keywordList')

            print("검색된 단어 개수 : {}".format(len(keywordList)))

            parsedKeywordList = []
            for keyword in keywordList:
                if keyword['monthlyPcQcCnt'] == '< 10' :
                    keyword['monthlyPcQcCnt'] = 0
                if keyword['monthlyMobileQcCnt'] == '< 10':
                    keyword['monthlyMobileQcCnt'] = 0
                parsedKeywordList.append({'keyword': keyword['relKeyword'], 'searchCount': keyword['monthlyPcQcCnt'] + keyword['monthlyMobileQcCnt']})

            filterKeywords(parsedKeywordList)

    except Exception as e:
        print("Exception On sendRequestToNaverKeywordTool:: ", str(e))

def sendRequestToNaverShopping(keyword):
    url = 'https://search.shopping.naver.com/_next/data/{}/search/all.json'.format(clientId)
    params = {
        'query': keyword
    }

    try:
        resp = requests.get(url= url, params= params)

        products = resp.json().get('pageProps').get('initialState').get('products')
        # pageProps -> initialState -> products -> total
        totalItemCount = products.get('total')

        # pageProps -> initialState -> products -> list -> 0 -> item -> [category1Name, category1Name, category1Name, category1Name]
        itemCategory = ''

        productList = products.get('list')

        categoryBase = productList[0].get('item')
        if 'category1Name' in categoryBase:
            itemCategory = itemCategory + categoryBase['category1Name'] 
            if 'category2Name' in categoryBase:
                itemCategory = itemCategory + categoryBase['category2Name']
                if 'category3Name' in categoryBase:
                    itemCategory = itemCategory + categoryBase['category3Name']
                    if 'category4Name' in categoryBase:
                        itemCategory = itemCategory + categoryBase['category4Name']
                        if 'category5Name' in categoryBase:
                            itemCategory = itemCategory + categoryBase['category5Name']
        return {'itemCategory': itemCategory, 'totalItemCount': totalItemCount}

    except Exception as e:
        print("sendRequestToNaverShopping:: ", str(e))

# token = getBearerToken()
# clientId = getClientId()

token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpbklkIjoiaG9uZ19vd25lcjpuYXZlciIsInJvbGUiOjAsImNsaWVudElkIjoibmF2ZXItY29va2llIiwiaXNBcGkiOmZhbHNlLCJ1c2VySWQiOjIzNTU4NjIsInVzZXJLZXkiOiI3YzEyYmFjOC0xZjg5LTRkODQtODZiOC0zNGMwMGY5ZjljNmQiLCJjbGllbnRDdXN0b21lcklkIjoyMTA1NTE0LCJpc3N1ZVR5cGUiOiJ1c2VyIiwibmJmIjoxNjEyNjI5MTgzLCJpZHAiOiJ1c2VyLWV4dC1hdXRoIiwiY3VzdG9tZXJJZCI6MjEwNTUxNCwiZXhwIjoxNjEyNjI5ODQzLCJpYXQiOjE2MTI2MjkyNDMsImp0aSI6ImRlZjliOTU4LTRiODUtNDZjZC1iNGJjLTBiY2VkMDAyZTE1NSJ9.Dm1md_2aUe1UvdXFbQdo8TYrzoCzb4qb0W-6cWWZ6tY'
clientId = '-XfwsIC9THj27j7OVClGw'

sendRequestToNaverKeywordTool(token, "탁자,1인용탁자")