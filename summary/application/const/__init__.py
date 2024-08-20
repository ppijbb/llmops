DEFAULT_SUMMARY_FEW_SHOT = [
    ("user", 
'''---
[대화]
참석자_1: 가족력에 대해 조금 말씀해 주세요.
참석자_2: 아버지와 할아버지 모두 제2형 당뇨병을 앓으셨어요. 제 아들은 현재 1형 당뇨병으로 고생하고 있습니다. 
참석자_1: 유감입니다. 가족 중에 심장 질환이 있는 분이 있나요? 
참석자_2: 아뇨. 
참석자_1: 암은 어떻습니까? 
참석자_2: 사촌 중 두 명이 유방암에 걸렸습니다.
---
[요약]
'''), 
    ("assistant", 
'''* 심장병에 관해서는 가족 중에 아무도 없음
* 암에 관해서는 사촌 두 명이 유방암 보유
* 당뇨병에 관해서는 아버지와 할아버지가 제 2 형 당뇨병 유병자
* 아들은 제1형 당뇨병을 앓고 있으며 현재 투병 중
---'''),
    ("user", 
'''---
[대화]
참석자_2: 의사 선생님, 저를 무엇으로 진단하실 건가요?
참석자_1: 주삿바늘에 의한 이차적인 혈액 매개 병원체 노출을 살펴보고 있습니다.
참석자_2: 네, 저도 오염에 대해 생각하고 있었습니다.
---
[요약]
'''),
    ("assistant",
'''* 오염 된 바늘에 이차적으로 혈액 매개 병원체 노출
---'''),
]

DEFAULT_SUMMARY_SYSTEM_PROMPT = '''
대화 내용은 요약하는 업무를 수행합니다.
대화 내용을 읽고 핵심 정보만 추출하여 요약합니다.
요약은 3 문장으로 합니다.
아래의 형식을 따라 요약합니다.
---
[대화]
사용자 1: ...
사용자 2: ...
---
[요약]
* 대화 요약 ...
* ...
---
'''