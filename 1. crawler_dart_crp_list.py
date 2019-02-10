## 필요한 패키지 다운로드
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen
import webbrowser
import requests
import re
import datetime
import sys

# 프로그레스 바: 해당 함수가 얼마나 오래걸리나
def progressBar(value, endvalue, bar_length=20):
    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()



## 1. 상장법인목록에 있는 기업들의 사업보고서 목록 크롤링
    
# 예시 url: http://dart.fss.or.kr/api/search.xml?auth=a2f0104fc81d7dc05f8817768aae6c55169516a6&crp_cd=005930&start_dt=20140101&bsn_tp=A001

# -- 검색 시작 날짜 (예시 : 20140101)
# -- 검색 종료 날짜
# -- crp_name: 확인하고 싶은 회사 이름, 입력하지 않으면 상장법인목록에 있는 모든 회사
# -- crp_codes_file_name: 확인하고 싶은 상장법인목록 엑셀 파일 이름. 입력하지 않으면 그냥 '상장법인목록'
def crawler_dart_crp_list(start_date, end_date, crp_name=None, crp_codes_file_name=None):
    print("---사업보고서 리스트 가져오기---")
    
    if crp_codes_file_name is None:
        company_codes = pd.read_excel('상장법인목록.xlsx', \
                                  converters={'종목코드': str})[["회사명","종목코드"]]
    else:
        company_codes = pd.read_excel(crp_codes_file_name, \
                                  converters={'종목코드': str})[["회사명","종목코드"]]

    
    if crp_name is not None:
        company_codes = pd.DataFrame(company_codes.iloc[list(np.where(company_codes["회사명"]==crp_name)[0])])
    
    crp_cd_list = company_codes["종목코드"]
    df = pd.DataFrame(columns=["crp_nm", "crp_cd", "rcp_dt", "rpt_nm", "rcp_no"]) # 결과 데이터 저장
    
    start = datetime.datetime.now()
    
    for com_idx in range(0, len(company_codes)):
        url = "http://dart.fss.or.kr/api/search.xml?auth=" + auth_key + "&crp_cd=" + crp_cd_list.iloc[
            com_idx] + "&start_dt=" + str(start_date) + "&end_dt=" + str(end_date) +  "&bsn_tp=A001"
        # 여기서 A001은 사업보고서를 의미함
        # 현재 url의 XML의 response를 읽는다
        resultXML = urlopen(url)
        result = resultXML.read()
        xmlsoup = BeautifulSoup(result, 'html.parser')
        # 현재 url에서 존재하는 한 회사의 사업보고서 리스트
        data = pd.DataFrame() # 사업보고서 리스트를 넣을 데이터
        te = xmlsoup.findAll("list")
        if len(te) == 0: continue
        tmp = ''
        # 현재 페이지 소스에서 리스트 당 필요한 변수들 저장하기. 위의 <형태> 참고
        for t in te:
            if tmp == t.rpt_nm.string.split()[1]: continue
            temp = pd.DataFrame(([[t.crp_nm.string, t.crp_cd.string, t.rcp_dt.string, 
                                   t.rpt_nm.string, t.rcp_no.string]]),
                                columns=["crp_nm", "crp_cd", "rcp_dt", "rpt_nm", "rcp_no"])
            data = pd.concat([data, temp])
            tmp = t.rpt_nm.string.split()[1]
    
        data = data.reset_index(drop=True)
        df = pd.concat([df, data])
    
        progressBar(com_idx, len(company_codes))
    
    end = datetime.datetime.now()
    print("\n걸린시간 : ", end - start)
    
    return df

if __name__ == "__main__":
        
    ## API key
    # 자신의 API key가 적혀있는 텍스트 파일 이름(확장자 포함)
    with open(input("My txt file name for API key.txt : "),'r') as f:
        auth_key = f.read()
    
    ## 결과를 저장할 파일 이름(확장자 포함)
    filename = input("My result file name.xlsx: ")
    
    result = crawler_dart_crp_list(20150101,20181231,'LG전자') # 예시
    # result = crawler_dart_crp_list(20150101,20181231)
    # result = crawler_dart_crp_list(20150101,20181231,crp_codes_file_name='상장법인목록.xlsx')
        
    # 데이터(사업보고서 리스트) 엑셀로 저장
    writer = pd.ExcelWriter(filename)
    result.to_excel(writer, 'Sheet1')
    writer.save()
    
