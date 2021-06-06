# -*- coding: utf-8 -*-

import requests
import sys
import csv
import time
import ast
from bs4 import BeautifulSoup

_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpbklkIjoiaG9uZ19vd25lcjpuYXZlciIsInJvbGUiOjAsImNsaWVudElkIjoibmF2ZXItY29va2llIiwiaXNBcGkiOmZhbHNlLCJ1c2VySWQiOjIzNTU4NjIsInVzZXJLZXkiOiIzMzNkYzliOC0wMjMzLTRmNDQtYTA2OS01MDgxZGFmZWMyNDQiLCJjbGllbnRDdXN0b21lcklkIjoyMTA1NTE0LCJpc3N1ZVR5cGUiOiJ1c2VyIiwibmJmIjoxNjIyMjAwMTY5LCJpZHAiOiJ1c2VyLWV4dC1hdXRoIiwiY3VzdG9tZXJJZCI6MjEwNTUxNCwiZXhwIjoxNjIyMjAwODI5LCJpYXQiOjE2MjIyMDAyMjksImp0aSI6IjNkZmMzMDA3LTgwNTktNDFjMS05MTdkLWMxMDc3ZGRiZmE1ZSJ9.2idIploM0jWhKz9l17Xzyw8wVZBHgQskiXodiZKA1OY'
_keywordSet = set()
_cashFile = 'keywordCash.csv'

def getClientId():
    clientId = input("ClientId 입력 : ")
    return clientId.strip()

def getBearerToken():
    global _token
    _token = input("베어러 토큰 입력 : ")
    if "Bearer " in _token:
        _token = _token.split("Bearer ")[1]
    _token.strip()
    print(_token)

def readCsv(filename, useKeywordCash = False):
    if not useKeywordCash:
        # global totalProductKeywordListDict
        totalProductKeywordListDict = {}

        f = open(filename, 'r')
        rdr = csv.reader(f)
        for line in rdr:
            product_name = line[0].strip()
            totalProductKeywordListDict[product_name] = []
            keywordSet = set()
            rel_keywords = line[1]
            temp_list = rel_keywords.split(',')
            rel_keyword_list = []
            for keyword in temp_list:
                rel_keyword_list.append(keyword.strip())

            print('Product : ', product_name)

            keywords_cnt = len(rel_keyword_list)
            keyword_grp = keywords_cnt // 5 + 1

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

        ff = open(_cashFile,'w',encoding= 'utf-8-sig', newline='')
        wr = csv.writer(ff)
        for productName, parsedKeywordList in totalProductKeywordListDict.items():
            wr.writerow([productName, parsedKeywordList])
        ff.close()    

    # keywordCash를 순회하면서 filter 작업 수행하기!
    print('### Filter Keyword ###')
    f = open(_cashFile, 'r', encoding= 'utf-8-sig')
    rdr = csv.reader(f)
    for line in rdr:
        productName = line[0]
        keywordList = ast.literal_eval(line[1])
        filterKeywords(productName, keywordList)
    f.close()

def filterKeywords(productName, keywordList):
    print('Product : {}, KeywordSize : {}'.format(productName, len(keywordList)))
    f = open('./item/{}.csv'.format(productName),'w',encoding= 'utf-8-sig', newline='')
    wr = csv.writer(f)
    wr.writerow(['상품명', '카테고리', '검색수', '상품수', '경쟁률'])

    totalSize = len(keywordList)
    curIndex = 0
    prevC = 10

    for keywordObj in keywordList:
        curIndex = curIndex + 1
        keyword, searchCount = keywordObj['keyword'], keywordObj['searchCount']

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
            print(shoppingData)
        
        curProgress = (curIndex * 100) // totalSize
        
        if curProgress >= prevC:
            print("---{}% done---".format(prevC))
            prevC = prevC + 10

        time.sleep(1)
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
        print(resp.text)
        return []

def sendRequestToNaverShopping(keyword):
    url = 'https://search.shopping.naver.com/search/all?query={}&frm=NVSHATC'.format(keyword)

    itemCategory = ''
    totalItemCount = 0

    try:
        resp = requests.get(url= url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        totalItemCount = soup.select(".subFilter_num__2x0jq")[0].getText()
        totalItemCount = int(totalItemCount.replace(",",""))
        itemCategory = soup.select(".basicList_depth__2QIie")[0].getText()

    except Exception as e:
        print("sendRequestToNaverShopping:: ", str(e))
        # print(resp.text)
    finally:
        return {'itemCategory': itemCategory, 'totalItemCount': totalItemCount}

start_time = time.time()

readCsv('상품조사.csv', False)

print("---Total time : {}---".format(time.time() - start_time))
