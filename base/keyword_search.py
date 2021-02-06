import requests
import sys
import csv
import time

_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpbklkIjoiaG9uZ19vd25lcjpuYXZlciIsInJvbGUiOjAsImNsaWVudElkIjoibmF2ZXItY29va2llIiwiaXNBcGkiOmZhbHNlLCJ1c2VySWQiOjIzNTU4NjIsInVzZXJLZXkiOiI3YzEyYmFjOC0xZjg5LTRkODQtODZiOC0zNGMwMGY5ZjljNmQiLCJjbGllbnRDdXN0b21lcklkIjoyMTA1NTE0LCJpc3N1ZVR5cGUiOiJ1c2VyIiwibmJmIjoxNjEyNjM5NTkzLCJpZHAiOiJ1c2VyLWV4dC1hdXRoIiwiY3VzdG9tZXJJZCI6MjEwNTUxNCwiZXhwIjoxNjEyNjQwMjUzLCJpYXQiOjE2MTI2Mzk2NTMsImp0aSI6ImU0OWE0Njg3LTA4MmEtNDdmMS05NTI4LTY1ZjA2NTU3ZjMyZCJ9.GO0JjJ6VlYAv7AmHycwDYFwU6Y7PVAX80jsOjEsr4Kk'
_clientId = '-XfwsIC9THj27j7OVClGw'

def getClientId():
    clientId = input("ClientId 입력 : ")
    return clientId

def getBearerToken():
    global _token
    _token = input("베어러 토큰 입력 : ")

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

def filterKeywords(productName, keywordList):
    f = open('{}.csv'.format(productName),'a', newline='')
    wr = csv.writer(f)

    for keywordObj in keywordList:
        keyword, searchCount = keywordObj['keyword'], keywordObj['searchCount']
        
        if searchCount >= 1000:
            shoppingData = sendRequestToNaverShopping(keyword)
            finalKeywordObj = {
                'searchCount': searchCount,
                'itemCategory': shoppingData['itemCategory'],
                'totalItemCount': shoppingData['totalItemCount'],
                'ratio': float(shoppingData['totalItemCount']) / searchCount
            }
            wr.writerow([keyword,finalKeywordObj['itemCategory'],finalKeywordObj['searchCount'],finalKeywordObj['totalItemCount'],finalKeywordObj['ratio']])

    f.close()

def sendRequestToNaverKeywordTool(productName= '', keywords=''):
    keywordSet = set()

    bearerToken = 'Bearer ' + _token
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
            getBearerToken()
            sendRequestToNaverKeywordTool(productName, keywords)
        else:
            if resp.status_code != 200:
                print("StatusCode가 이상하다. 확인필요")
                return

            keywordList = resp.json().get('keywordList')

            print("검색된 단어 개수 : {}".format(len(keywordList)))

            parsedKeywordList = []
            for keyword in keywordList:
                if keyword['relKeyword'] in keywordSet:
                    continue
                keywordSet.add(keyword['relKeyword'])

                if keyword['monthlyPcQcCnt'] == '< 10' :
                    keyword['monthlyPcQcCnt'] = 0
                if keyword['monthlyMobileQcCnt'] == '< 10':
                    keyword['monthlyMobileQcCnt'] = 0
                parsedKeywordList.append({'keyword': keyword['relKeyword'], 'searchCount': keyword['monthlyPcQcCnt'] + keyword['monthlyMobileQcCnt']})

            filterKeywords(productName, parsedKeywordList)

    except Exception as e:
        print("Exception On sendRequestToNaverKeywordTool:: ", str(e))

def sendRequestToNaverShopping(keyword):
    url = 'https://search.shopping.naver.com/_next/data/{}/search/all.json'.format(_clientId)
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


start_time = time.time()

sendRequestToNaverKeywordTool("예쁜탁자", "탁자,1인용탁자")
sendRequestToNaverKeywordTool("예쁜탁자2", "탁자,1인용탁자")
sendRequestToNaverKeywordTool("예쁜탁자3", "탁자,1인용탁자")
sendRequestToNaverKeywordTool("예쁜탁자4", "탁자,1인용탁자")

print("---Total time : {}---".format(time.time() - start_time))