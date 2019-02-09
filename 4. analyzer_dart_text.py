import pandas as pd
from pandas import Series, DataFrame
import sys
import datetime
import re
from nltk.tokenize import sent_tokenize
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from konlpy.tag import Twitter
tagger = Twitter() # Twitter 태깅 함수

##  프로그레스바
import sys
def progressBar(value, endvalue, bar_length=20):
    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()


## 데이터 받기
data = pd.read_excel("dart_text_half.xlsx", encoding = 'UTF-8')
data.head()
# 텍스트만
text = data["텍스트"]
# 텍스트 확인 - 길 수 있음
text[0]


#### 불필요한 html 소스 제거(텍스트 전처리)
processed_text = []  # 전처리한 데이터 저장할 빈 리스트
start = datetime.datetime.now()
for tmp in text:
    sent_text = sent_tokenize(tmp)  # 문장단위 토큰화
    for text_idx in range(0, len(sent_text)):
        if '이사의 경영진단 및 분석의견' in sent_text[text_idx]:  # 토큰화했을 때 '이사의 경영진단 및 분석의견'이 포함된 텍스트 이후로 가져옴
            sent_text = sent_text[text_idx + 1:]
            break
    ## 텍스트 전처리
    # 올바르게 단어수를 세기 위해 가능한 숫자와 의미있는 영어문자는 제거하지 않음
    # 한글만, 혹은 빠른 전처리를 원한다면 아래 ***까지 실행하고 아래 sent_text = [~] 부분은 지움
    sent_text = [re.sub("\r", ' ', text) for text in sent_text]
    sent_text = [re.sub("\n", ' ', text) for text in sent_text]
    # *** sent_text = [re.sub("-[가-힣]+"," ", text) for text in sent_text]
    sent_text = [re.sub("<.{1,}>", ' ', text) for text in sent_text]
    sent_text = [re.sub(" .\.", ' ', text) for text in sent_text]
    sent_text = [re.sub("\d+[\.\,]\d*[\.\,]*\d*", '숫자 ', text) for text in sent_text]
    ## 특수문자 혹은 한글이 아닌 것 텍스트 제거 전 의미있는 텍스트들을 가져오기(예: R&D는 의미있을 수 있음)
    sent_text = [re.sub("&amp;", '앤', text) for text in sent_text]  # &가 &amp; 로 읽힘
    sent_text = [re.sub("&nbsp;", ' ', text) for text in sent_text]  # 공백이 &nbsp; 로 읽힘
    ## 아래부터 특수문자 제거
    sent_text = [re.sub("\.", ' ', text) for text in sent_text]
    sent_text = [re.sub('[ⅢXI,;\(\)%\'\"」』『:\“\”ㆍ-]', ' ', text) for text in sent_text]
    sent_text = [re.sub("  +", ' ', text) for text in sent_text]
    sent_text = [' '.join(sent_text)]  # 토큰화된 텍스트들의 리스트를 다 붙임(대신 문장 구분이 없어짐)
    processed_text.append(sent_text)  # 각 사업보고서들의 텍스트를 리스트로 받아서 넣음

    progressBar(len(processed_text), len(text))

end = datetime.datetime.now()
print("\n걸린시간 : ", end - start)

len(processed_text) # 전처리한 텍스트의 수 = 총 사업보고서 수

# sample 사업보고서 텍스트 - 길 수 있음
processed_text[1]


#### 1. 단어 수 구하기
# 아래 반복문을 돌리기 전 예시
tmp = processed_text[0]
## word_tokenize는 space, punctuation기준으로 나눔, 위에서 구두점을 제거하였으므로 공백 기준으로 나눔 즉, 단어들로 나눔
text_token = [word_tokenize(text) for text in tmp] # 단어들로 나눈다
text_token[0]  # 단어들 리스트
len(text_token[0]) # 단어 수

## 단어수 구하기 루프 ### 약 10분
word_cnt, txt_token = [], [] # 데이터 저장 빈 텍스트
start = datetime.datetime.now()

for tmp in processed_text:
    text_token = [word_tokenize(text) for text in tmp]
    # text_token = [y for x in text_token for y in x]
    txt_token.append(text_token[0])
    word_cnt.append(len(text_token[0]))  # 단어들로 나뉜 토큰들의 길이 즉, 단어수

    progressBar(len(word_cnt), len(processed_text))

end = datetime.datetime.now()
print("\n걸린시간 : ", end - start)

# 데이터 확인해보기
print(len(word_cnt))
word_cnt[:5] # 단어수
text_token[0] # 단어들


#### 2. 긍부정 단어 수 구하기
# 긍정단어 목록 받기
# knu의 긍정 사전이나, 필요할 시 다른 사전을 가져와도 무방
f = open("pos_pol_word.txt", 'r', encoding = 'UTF-8')
pos = f.read()
f.close()
# 부정단어 목록 받기
f = open("neg_pol_word.txt", 'r', encoding = 'UTF-8')
neg = f.read()
f.close()

# 긍정단어 목록(사전)을 단어들의 리스트로 만듦
pos_dic = pos.split('\n') # 사전을 단어들의 리스트로 만듦
pos_dic[0] = re.sub("\ufeff",'',pos_dic[0]) # 인코딩 오류
print(pos_dic[:10]) # 긍정단어 목록 확인

# 부정단어 리스트
neg_dic = neg.split('\n')
neg_dic[0] = re.sub("\ufeff",'',neg_dic[0])
neg_dic[:10]

# 여기서 단어수를 확인해보자 ----- 토큰화하는 함수마다 달라서 확인 필요
print(len(tagger.nouns(processed_text[0][0])))  # 트위터 태깅함수는 335 위(최대한 덜 제거하려고 한 함수)는 342
tagger.nouns(processed_text[0][0])[0]

## 해당 사업보고서의 텍스트의 명사를 추출해냄 (긍부정 사전에서 추출된 명사와 비교하기 위함)
start = datetime.datetime.now()

text_tag = []
for tmp in processed_text:
    text_token = tagger.nouns(tmp[0]) # 트위터 태깅함수를 이용한 토큰 중 명사만 가져옴 -> 형용사는 어떻게?
    text_token = [text for text in text_token if len(text) >= 2] # 여기서 비교의 용이를 위해 2음절 이상의 단어만 가져옴
    text_tag.append(text_token)

    progressBar(len(text_tag), len(processed_text))

end = datetime.datetime.now()
print("\n걸린시간 : ", end - start)

## 트위터 태깅함수를 이용하여 추출된 사업보고서 텍스트의 명사들 목록 - 필수X
# f = open('text_tag_half.txt', 'w')
# for text_idx in text_tag:
#     f.write(' '.join(text_idx))
# f.close()

# nltk 모듈을 이용한 텍스트 단어들
text_list = []
for tmp in text_tag:
    tmp2 = nltk.Text(tmp)
    text_list.append(tmp2)
# 단어 확인(가장 많이 나오는 단어 순)
text_list[4000].vocab()

## 불용어 제거
text_vocab, text_ko = [], []
# 불용어 리스트 (본인의 판단에 따라 더 추가 가능) : 텍스트 분석에 필요가 없거나 사업보고서 특성상 당연히 많이 나와 분석에 의미 없는 단어들
stop_words = ['사항','제기','및','년','사업','관','그','등','것','및','부','수','위','나','대하']
for tmp in text_list:
    ko = [word for word in tmp if word not in stop_words] # 불용어 제거
    ko = nltk.Text(ko) # 텍스트의 단어들만 가져옴
    text_ko.append(ko)
    text_vocab.append(ko.vocab())

# 확인
text_vocab[:5]

# 문서의 단어들
doc_words = [list(ko) for ko in text_ko]
doc_words[:2] # 예측, 정보, 대한, 주의, 당사, 보고서 등


## 긍부정단어 목록에서 단어들 가져오기
# 긍정 사전
pos_words = [tagger.nouns(doc) for doc in pos_dic if len(tagger.nouns(doc))!=0] #긍정사전의 단어들로부터 명사 추출, 명사 없으면 스킵
pos_words = [re.findall(r'[가-힣]{2,10}', word) for y in pos_words for word in y] #추출된 명사들 중 2음절 이상인 명사만 추출
pos_words = [y for x in pos_words for y in x] #unlist
pos_words = set(pos_words) # 세트 형 구조로 만듦(중복되지 않게)
pos_words = [word for word in pos_words if word not in stop_words] # 불용어 없애고 리스트로 만듦
pos_words[:10] # 원동력, 기상, 애하, 가르침, 더없이 등

# 부정 사전
neg_words = [tagger.nouns(doc) for doc in neg_dic if len(tagger.nouns(doc))!=0]
neg_words = [re.findall(r'[가-힣]{2,10}', word) for y in neg_words for word in y]
neg_words = [y for x in neg_words for y in x]
neg_words = set(neg_words)
neg_words = [word for word in neg_words if word not in stop_words]
neg_words[:10] # 불량, 요사, 모순, 선천, 실행


## 긍정단어가 몇 개 포함되었는지 ## 꽤 걸림
start = datetime.datetime.now()

pos_words_cnt, cnt = [], 0
for ko in text_ko:
    cnt = sum([word in ko for word in pos_words])  # 각 긍정단어가 사업보고서 텍스트의 단어들에 있는지 논리값을 가져오고 개수 세기
    pos_words_cnt.append(cnt)

    progressBar(len(pos_words_cnt), len(text_ko))

end = datetime.datetime.now()
print("\n걸린시간 : ", end - start)

# 단어 수 확인
pos_words_cnt[:5]

## 부정단어가 몇 개 포함되었는지 ## 꽤 걸림
# 여기서 부정사전 내 단어수가 긍정사전보다 많으므로 부정단어의 수가 더 많을 수밖에 없다.
start = datetime.datetime.now()

neg_words_cnt, cnt = [], 0
for ko in text_ko:
    cnt = sum([word in ko for word in neg_words])
    neg_words_cnt.append(cnt)

    progressBar(len(neg_words_cnt), len(text_ko))

end = datetime.datetime.now()
print("\n걸린시간 : ", end - start)

# 단어 수 확인
neg_words_cnt[:5]


### 데이터 합치기
# 데이터프레임으로 합칠 데이터 형태
data2 = data[['회사명','회사코드','보고서 명','접수번호','접수날짜']]
proc_text = pd.Series(processed_text, name = '텍스트')
word_cnt = pd.Series(word_cnt, name = '단어수')
pos_words_cnt = pd.Series(pos_words_cnt, name = '긍정단어수')
neg_words_cnt = pd.Series(neg_words_cnt, name = '부정단어수')
data2 = pd.concat([data2, proc_text, word_cnt, pos_words_cnt, neg_words_cnt], axis=1)
data2.head()
data2.tail()

## 엑셀로 저장
writer = pd.ExcelWriter('./dart_text_wordcnt.xlsx')
data2.to_excel(writer,'Sheet1')
writer.save()