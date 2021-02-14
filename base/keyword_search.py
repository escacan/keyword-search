import requests
import sys
import csv
import time

_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpbklkIjoiaG9uZ19vd25lcjpuYXZlciIsInJvbGUiOjAsImNsaWVudElkIjoibmF2ZXItY29va2llIiwiaXNBcGkiOmZhbHNlLCJ1c2VySWQiOjIzNTU4NjIsInVzZXJLZXkiOiJkZTVlODdjMi1mMzEzLTQ2YWQtYTdlZC03ZTE1Zjk3ZmRkM2YiLCJjbGllbnRDdXN0b21lcklkIjoyMTA1NTE0LCJpc3N1ZVR5cGUiOiJ1c2VyIiwibmJmIjoxNjEzMzA4MTgyLCJpZHAiOiJ1c2VyLWV4dC1hdXRoIiwiY3VzdG9tZXJJZCI6MjEwNTUxNCwiZXhwIjoxNjEzMzA4ODQyLCJpYXQiOjE2MTMzMDgyNDIsImp0aSI6IjRhMDE4OGQ3LWRjOWEtNGVmMC05ODkzLWMyNzUwYzE0OTJlMyJ9.0Z_Vg0S86UfxR-bM5JDfJLWGvLOAGhlDSJQMG9N90n0'
_clientId = 'k5ZoItU4ij5tAH1wX-seU'
_keywordSet = set()

def getClientId():
    clientId = input("ClientId 입력 : ")
    return clientId

def getBearerToken():
    global _token
    _token = input("베어러 토큰 입력 : ")

def readCsv(filename):
    # global totalProductKeywordListDict
    totalProductKeywordListDict = {}

    f = open(filename, 'r')
    rdr = csv.reader(f)
    for line in rdr:
        product_name = line[0]
        totalProductKeywordListDict[product_name] = []
        keywordSet = set()
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
            time.sleep(1)
            if group_num*5 + 5 < keywords_cnt:
                keyword_list_part = rel_keyword_list[group_num*5:group_num*5+5]
            else:
                keyword_list_part = rel_keyword_list[group_num*5:keywords_cnt]
            keyword_str = ','.join(keyword_list_part)
            keywordList = sendRequestToNaverKeywordTool(product_name, keyword_str)

            if keywordList:
                for item in keywordList:
                    if item['keyword'] in keywordSet:
                        continue
                    else:
                        keywordSet.add(item['keyword'])
                        totalProductKeywordListDict[product_name].append(item)
            
            print("---{}% done---".format((group_num + 1) * 100 // keyword_grp ))
    f.close()

    for productName, parsedKeywordList in totalProductKeywordListDict.items():
        ff = open('keywordCash.csv','w',encoding= 'utf-8-sig', newline='')
        wr = csv.writer(ff)
        wr.writerow([productName, parsedKeywordList])
        ff.close()    

    # keywordCash를 순회하면서 filter 작업 수행하기!
    print('### Filter Keyword ###')
    f = open(filename, 'r')
    rdr = csv.reader(f)
    for line in rdr:
        productName = line[0]
        keywordList = line[1]
        filterKeywords(productName, parsedKeywordList)
    f.close()

def filterKeywords(productName, keywordList):
    print('Product : {}, KeywordSize : {}'.format(productName, len(keywordList)))
    f = open('{}.csv'.format(productName),'a',encoding= 'utf-8-sig', newline='')
    wr = csv.writer(f)

    totalSize = len(keywordList)
    curIndex = 0
    prevC = 10

    for keywordObj in keywordList:
        time.sleep(0.5)
        curIndex = curIndex + 1
        keyword, searchCount = keywordObj['keyword'], keywordObj['searchCount']
        
        if searchCount >= 1000:
            shoppingData = sendRequestToNaverShopping(keyword)
            try:
                finalKeywordObj = {
                    'searchCount': searchCount,
                    'itemCategory': shoppingData['itemCategory'],
                    'totalItemCount': shoppingData['totalItemCount'],
                    'ratio': float(shoppingData['totalItemCount']) / searchCount
                }
                wr.writerow([keyword,finalKeywordObj['itemCategory'],finalKeywordObj['searchCount'],finalKeywordObj['totalItemCount'],finalKeywordObj['ratio']])
            except Exception as e:
                print("Exception On filterKeywords:: ", str(e))
        
        curProgress = (curIndex * 100) // totalSize
        
        if curProgress >= prevC:
            print("---{}% done---".format(prevC))
            prevC = prevC + 10
    f.close()
    print("---100% done---")

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
            return sendRequestToNaverKeywordTool(productName, keywords)
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
                totalSearchCount = keyword['monthlyPcQcCnt'] + keyword['monthlyMobileQcCnt']

                if totalSearchCount > 1000:
                    parsedKeywordList.append({'keyword': keyword['relKeyword'], 'searchCount': totalSearchCount})
            return parsedKeywordList
    except Exception as e:
        print("Exception On sendRequestToNaverKeywordTool:: ", str(e))
        return []

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
