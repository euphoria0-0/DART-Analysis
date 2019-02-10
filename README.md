## dart2
전자공시시스템(DART) text mining

# 1. 상장 기업 사업보고서 crawling

 ## API key는 비식별화
 
 ## web crawling 과정에서 호스트와 연결이 끊기는 오류 발생 -> 다른 IP로 접속
 
 ## 대안으로 다음과 같이 처리
 
 ### 1. 회사별 사업보고서의 존재(접수번호 기준) 리스트를 먼저 크롤링
 
      - 상장법인목록 기준 기업 2263개 -> 사업보고서 10064개
      
      - 이때 사업보고서는 제출된 사업보고서 외에 [기재정정]사업보고서 등의 형태도 존재한다. 이는 같은 해를 기준으로 최신 보고서를 가져왔다.
        즉, '사업보고서 (2017.12)' 와 '[기재정정]사업보고서 (2017.12)'이 존재하면 더 최신에 제출된 '[기재정정]사업보고서 (2017.12)'를 가져온다.
        그러나 여기에도 기존 형식에 일치하지 않은 사업보고서가 존재할 수 있다.
        
 ### 2. 먼저 받은 접수번호를 이용해 url에 접속
      (이를 for문 안에 같이 처리했었는데 나눴다.)
      (이 중에도 호스트와 연결이 끊기는 오류가 발생하였다.)
      
 ### 최종: 크롤링 함수를 재정의한 crawler.py
      
### 2. 사업보고서 텍스트 단어수 및 긍부정 사전 이용 단어수

    > 텍스트 단어 수는 전처리를 최대한 적게 하였다.
    
    > 긍부정 사전에 포함된 단어수를 세기 위해 한글 단어만 비교하였다.

### 3. 사업보고서 텍스트 복잡도(..)

## report


## 참고 ####
https://github.com/seoweon/dart_reports
http://quantkim.blogspot.com/2018/01/dart-api-with.html

