## 필요한 패키지 다운로드
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import webbrowser
import requests
import re
import datetime
import sys

# 프로그레스 바
def progressBar(value, endvalue, bar_length=20):
    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()



## 텍스트 크롤링에 필요한 함수 정의
# 접수번호(rcp_no)에 해당하는 모든 하위 보고서 URL을 추출하여 리스트로 반환하는 함수
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

# 해당 url에서 텍스트를 가져오는 함수
def get_text_urls(rcp_no):
    url = get_sub_report_urls(rcp_no)
    le = len(url)
    # 'V. 이사의 경영진단 및 분석의견' 텍스트를 포함한 글(get_sub_report_urls의 리스트 중 하나) 찾기
    # 보통의 형식에서는 idx=18에 있는데, 정정보고서 등은 이 양식을 지키지 않아 새롭게 찾아야함
    html_text = requests.get(url[18])
    
    if "V. 이사의 경영진단 및 분석의견" not in html_text:
        idx = 0
        while True:
            if le == 0 or idx == le:
                html_text = ''
                break
            url2 = url[idx]
            r = requests.get(url2)
            html_text = r.text  # 해당 url의 텍스트 저장
            # 이사의 경영진단 및 분석의견이 텍스트에 포함되지 않으면 글 다시 찾기
            if "V. 이사의 경영진단 및 분석의견" in html_text:
                break
            else:
                idx += 1
                
    return html_text

## 2. 사업보고서 리스트로 텍스트를 가져오는 함수
def crawler_dart_text(crp_lists):
    
    txt = pd.DataFrame(columns=["회사명", "회사코드", "접수날짜", "보고서 명", "접수번호", "text"])
    start = datetime.datetime.now()
    
    for idx in range(0, len(crp_lists)):
        crp = crp_lists[idx]        # idx번째 사업보고서의 변수 리스트(회사명 등, crp[4]는 접수번호)
        html_txt = get_text_urls(str(crp[4])) # 접수번호의 url에 접속하여 V. 이사회의 ~ 텍스트 가져오기
        # 해당 사업보고서의 회사명, 회사코드, ... , 접수번호, 텍스트를 리스트로 저장하여 붙여넣기
        # 이사의 경영진단~이 없는 사업보고서는 보지 않는다
        try:
            a = len(html_txt)
        except:
            a = 0
        if a < 1:
            continue
        
        txt2 = pd.Series([crp[0], crp[1], crp[2], crp[3], crp[4], html_txt],
                         index=["회사명", "회사코드", "접수날짜", "보고서 명", "접수번호", "text"])
        txt = txt.append(txt2, ignore_index=True)
    
        progressBar(idx, len(crp_lists))
    
    end = datetime.datetime.now()
    print("\n걸린시간 : ", end - start)

    return txt


if __name__ == "__main__":
    # 크롤링했던 회사들의 사업보고서 리스트(확장자포함입력) 가져오기
    crplist_filename = input("사업보고서 리스트(crp_list).xlsx : ")
    crp_lists = pd.read_excel(crplist_filename)
    crp_lists = crp_lists[['crp_nm','crp_cd','rcp_dt','rpt_nm','rcp_no']].values.tolist()
    
    ## 결과를 저장할 파일 이름(확장자 포함)
    filename = input("My result file name.xlsx: ")
    
    dart_text = crawler_dart_text(crp_lists)
    

    
    # 데이터(사업보고서 리스트) 엑셀로 저장
    writer = pd.ExcelWriter(filename)
    dart_text.to_excel(writer, 'Sheet1')
    writer.save()
    
    # 데이터 확인
    dart_text.head()
    
    
