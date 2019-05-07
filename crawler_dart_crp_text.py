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

import nltk
from nltk.tokenize import sent_tokenize

# 프로그레스 바
def progressBar(value, endvalue, bar_length=20):
    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()

# 텍스트 전처리
def word_preprocess(textdata):
    join_text = ' '.join(textdata)
    sent_text = sent_tokenize(join_text)
    sent_text = [re.sub("\n|\r",'',text) for text in sent_text]
    sent_text = [re.sub("[^가-힣]",' ',text) for text in sent_text[2:]] # 한글빼고 다 제거
    sent_text = [re.sub(" {2,}",' ',text) for text in sent_text]
    process_text = ' '.join(sent_text)
    return process_text

## 1. 상장법인목록에 있는 기업들의 사업보고서 목록 크롤링
# 예시 url: http://dart.fss.or.kr/api/search.xml?auth=__your_api_key__&start_dt=20140101&bsn_tp=A001
# -- 검색 시작 날짜 (예시 : 20140101)
# -- 검색 종료 날짜
def crawler_dart_crp_list(start_date, end_date):
    
    print("---사업보고서 리스트 가져오기---")
    crp_list = pd.read_excel('C:/Users/user/Documents/euphoria/proj/DSC/dart/crp_list.xlsx')
    crp_cd_list = crp_list["itemcode"]
    df = pd.DataFrame(columns=["crp_nm", "crp_cd", "rcp_dt", "rpt_nm", "rcp_no"]) # 결과 데이터 저장
    
    start = datetime.datetime.now()
    
    for com_idx in range(0, len(crp_list)):
        url = "http://dart.fss.or.kr/api/search.xml?auth=" + auth_key + "&crp_cd=" + str(crp_cd_list.iloc[
            com_idx]) + "&start_dt=" + str(start_date) + "&end_dt=" + str(end_date) +  "&bsn_tp=A001"
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
    
        progressBar(com_idx+1, len(crp_list))
    
    end = datetime.datetime.now()
    print("\n걸린시간 : ", end - start)
    
    return df

## 2. 텍스트 크롤링에 필요한 함수 정의
# 2-1. 접수번호(rcp_no)에 해당하는 모든 하위 보고서 URL을 추출하여 리스트로 반환하는 함수
# 예시 url: http://dart.fss.or.kr/dsaf001/main.do?rcpNo=20181228000183\
# 예시 doc_url_tmpl :view-source:http://dart.fss.or.kr/report/viewer.do?rcpNo=20181228000183&dcmNo=6431765&eleId=19&offset=402114&length=10395&dtd=dart3.xsd
def get_sub_report_urls(rcp_no):
    doc_urls = []
    url = "http://dart.fss.or.kr/dsaf001/main.do?rcpNo=%s" % (rcp_no)
    r = requests.get(url)
    reg = re.compile('viewDoc\((.*)\);')
    params = []
    matches = reg.findall(r.text)
    for m in matches:
        params.append(m.replace("'", "").replace(" ", "").split(","))

    doc_url_tmpl = "http://dart.fss.or.kr/report/viewer.do?rcpNo=%s&dcmNo=%s&eleId=%s&offset=%s&length=%s&dtd=%s"

    for p in params:
        if rcp_no == p[0]:
            doc_urls.append(doc_url_tmpl % tuple(p))

    return doc_urls

# 2-2. 해당 url에서 텍스트를 가져오는 함수
def get_text_urls(rcp_no):
    url = get_sub_report_urls(rcp_no)
    html_text = []
    
    for url_idx in url:
        html_text.append(requests.get(url_idx).text)
            
    return html_text

## 3. 사업보고서 리스트로 텍스트를 가져오는 함수
def crawler_dart_text(crp_lists):
    print("---사업보고서 텍스트 가져오기---")    
    crp_lists_tolist = crp_lists[['crp_nm','crp_cd','rcp_dt','rpt_nm','rcp_no']].values.tolist()
    
    df = pd.DataFrame(columns=["회사명", "회사코드", "접수날짜", "보고서 명", "접수번호", "text"])
    start = datetime.datetime.now()
    
    for idx in range(0, len(crp_lists_tolist)):
        crp = crp_lists_tolist[idx] # idx번째 사업보고서의 변수 리스트(회사명 등, crp[4]는 접수번호)
        html_txt = get_text_urls(str(crp[4]))
        
        # len(html_txt)이 빈 칸이면 저장하지 않는다.
        try:
            le = len(html_txt)
        except:
            le = 0
            
        if le < 1:
            continue
        # html_txt를 전처리
        process_txt = word_preprocess(html_txt)
        
        # 해당 사업보고서의 회사명, 회사코드, ... , 접수번호, 텍스트를 리스트로 저장하여 붙여넣기
        record_rpt = pd.Series([crp[0], crp[1], crp[2], crp[3], crp[4], process_txt],
                               index=["회사명", "회사코드", "접수날짜", "보고서 명", "접수번호", "text"])
        df = df.append(record_rpt, ignore_index=True)
    
        progressBar(idx, len(crp_lists_tolist))
    
    end = datetime.datetime.now()
    print("\n걸린시간 : ", end - start)

    return df

if __name__ == "__main__":
        
    ## API key
    # 자신의 API key가 적혀있는 텍스트 파일 이름(확장자 포함)
    with open(input("your api key file.txt"),'r') as f:
        auth_key = f.read()
    
    ## 결과를 저장할 파일 이름(확장자 포함)
    filename = input("My result file name.xlsx: ")
    
    # 사업보고서를 찾을 날짜
    start_date_input = int(input("start date(20150101): "))
    end_date_input = int(input("end date(20190501): "))
    
    crp_lists = crawler_dart_crp_list(start_date_input, end_date_input)
    dart_text = crawler_dart_text(crp_lists)
    
    # 데이터(사업보고서 텍스트) 엑셀로 저장
    writer = pd.ExcelWriter(filename)
    dart_text.to_excel(writer, 'Sheet1')
    writer.save()

    
