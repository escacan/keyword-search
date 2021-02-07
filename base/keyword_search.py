import requests
import sys
import csv
import time

_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpbklkIjoiaG9uZ19vd25lcjpuYXZlciIsInJvbGUiOjAsImNsaWVudElkIjoibmF2ZXItY29va2llIiwiaXNBcGkiOmZhbHNlLCJ1c2VySWQiOjIzNTU4NjIsInVzZXJLZXkiOiI3YzEyYmFjOC0xZjg5LTRkODQtODZiOC0zNGMwMGY5ZjljNmQiLCJjbGllbnRDdXN0b21lcklkIjoyMTA1NTE0LCJpc3N1ZVR5cGUiOiJ1c2VyIiwibmJmIjoxNjEyNjQ1MDA0LCJpZHAiOiJ1c2VyLWV4dC1hdXRoIiwiY3VzdG9tZXJJZCI6MjEwNTUxNCwiZXhwIjoxNjEyNjQ1NjY0LCJpYXQiOjE2MTI2NDUwNjQsImp0aSI6ImY4NjVhNGJhLTY5ZjMtNDQ5ZS04YWY3LTM2MGMwNjczZTdhMiJ9.0bVrfgS6AA5gEN--ZTbp6vHAdU4JhLO7mg_hoSPjKPI'
_clientId = '-XfwsIC9THj27j7OVClGw'
_keywordSet = set()

def getClientId():
    clientId = input("ClientId 입력 : ")
    return clientId

def getBearerToken():
    global _token
    _token = input("베어러 토큰 입력 : ")

def readCsv(filename):
    f = open(filename, 'r')
    rdr = csv.reader(f)
    for line in rdr:
        product_name = line[0]
        rel_keywords = line[1]
        rel_keyword_list = rel_keywords.split(',')

        print('Product : ', product_name)

        keywords_cnt = len(rel_keyword_list)
        keyword_grp = keywords_cnt // 5 + 1

        ff = open('{}.csv'.format(product_name),'w',encoding= 'utf-8-sig', newline='')
        wr = csv.writer(ff)
        wr.writerow(['상품명','카테고리','검색수','상품수','경쟁률'])
        ff.close()

        for group_num in range(keyword_grp):
            if group_num*5 + 5 < keywords_cnt:
                keyword_list_part = rel_keyword_list[group_num*5:group_num*5+5]
            else:
                keyword_list_part = rel_keyword_list[group_num*5:keywords_cnt]
            keyword_str = ','.join(keyword_list_part)
            sendRequestToNaverKeywordTool(product_name, keyword_str)
            print("---{}% done---".format((group_num + 1) * 100 // keyword_grp ))

    f.close()

def filterKeywords(productName, keywordList):
    f = open('{}.csv'.format(productName),'a',encoding= 'utf-8-sig', newline='')
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

            parsedKeywordList = []
            for keyword in keywordList:
                if keyword['relKeyword'] in _keywordSet:
                    continue
                _keywordSet.add(keyword['relKeyword'])

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
    
    itemCategory = ''
    totalItemCount = 0

    try:
        resp = requests.get(url= url, params= params)

        products = resp.json().get('pageProps').get('initialState').get('products')
        # pageProps -> initialState -> products -> total

        totalItemCount = products.get('total', 0)
    
        # pageProps -> initialState -> products -> list -> 0 -> item -> [category1Name, category1Name, category1Name, category1Name]
        if totalItemCount > 0:
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

    except Exception as e:
        print("sendRequestToNaverShopping:: ", str(e))
    finally:
        return {'itemCategory': itemCategory, 'totalItemCount': totalItemCount}

start_time = time.time()

readCsv('상품조사.csv')

print("---Total time : {}---".format(time.time() - start_time))
