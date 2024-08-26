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
    ("user", 
'''---
[대화]
참석자_1: 오늘은 무슨 일로 오셨나요? 
참석자_2: I've had a terrible toothache.(치통이 너무 심해서요.)
참석자_2: I can't stand the pain anymore.(더 이상 통증을 참을 수 없습니다.)
참석자_2: I have never experienced this pain in fifty eight years.(58년 동안 이런 통증은 처음입니다.)
참석자_1: 어디가 가장 아프신가요? 
참석자_1: 그리고 이 통증은 언제부터 시작되었나요? 
참석자_2: It started about three weeks ago.(약 3주 전에 시작되었습니다.)
참석자_2: It's mostly on the left side of my mouth(주로 입 왼쪽에 통증이 있습니다.)
참석자_2: Kind of on the lower end.(아래쪽 끝부분에요.)
참석자_2: It goes from my jaw all the way up to my left ear.(턱에서 왼쪽 귀까지 통증이 느껴집니다.)
참석자_1: 조금도 불편하지 않네요. 
참석자_1: 기분 좀 나아지게 해드릴게요. 
참석자_1: 치아와 관련이 있다고 생각하세요? 
참석자_2: No, I don't think so.(아니요, 그런 것 같지 않아요.)
참석자_2: I'm pretty good at making my dentist appointments, although I haven't been in since this new pain started.(이 새로운 통증이 시작된 이후로 치과에 간 적은 없지만 치과 예약을 꽤 잘 지키고 있습니다.)
참석자_1: 그렇군요. 마지막으로 치과를 방문하신 게 언제였나요? 
참석자_2: About two months ago for a routine clean.(약 두 달 전에 정기적인 스케일링을 위해 방문했습니다.)
참석자_1: 이 모든 일이 시작된 이후로 얼굴이 부은 것을 느끼셨나요? 
참석자_2: No, no swelling.(아니요, 붓기는 없습니다.)
참석자_1: 두통, 목 부종, 인후통, 삼키거나 씹는 데 어려움은 없었나요? 
참석자_2: No.(아니요.)
참석자_1: 목 통증, 림프절 부종, 오한, 발열 또는 기타 증상은 어떻습니까? 
참석자_2: No, thank goodness.(아니요, 다행히도 없습니다.)
---
[요약]
'''),
    ("assistant",
'''* 58세 남성
* 처음에는 입 아래 왼쪽에서 치통이 시작되어 지금은 턱과 왼쪽 귀 쪽으로 퍼지고 있음
* 다른 문제, 통증 또는 불편 부위 없음
---'''),
    ("user", 
'''---
[대화]
참석자_1: Hello, miss.(안녕하세요, 아가씨.)
참석자_1: Could you verify your age, please?(나이를 확인해 주시겠습니까?)
참석자_2: 저는 쉰다섯 살입니다. 
참석자_1: Great. What is the reason for your visit today? (그렇군요. 오늘 방문하신 이유는 무엇입니까? )
참석자_2: 최근에 문제가 많이 생겨서 선생님께 진찰을 받으러 왔습니다. 
참석자_1: I see. What kind of problems are you experiencing? (그렇군요. 어떤 문제가 있으신가요?)
참석자_2: 아, 목록이 길어요.
참석자_2: 여기 있습니다. 
참석자_1: Thank you. Let me take a look. (감사합니다. 한번 살펴볼게요.)
참석자_1: Looks like you have some general allergies and food allergies, loss of taste, problems with your G I tract, asthma, G E R D, and dry mouth or xerostomia. Patient: Yeah, that sounds about right. I think I forgot to add it, but I also have bad allergies during the spring time.(일반적인 알레르기와 음식 알레르기, 미각 상실, 위장관 문제, 천식, G E R D, 구강 건조증 또는 구강 건조증이 있는 것 같네요.)
참석자_2: 네, 맞는 것 같네요. 
참석자_2: 제가 깜빡하고 추가하지 못한 것 같은데 봄철에 알레르기가 심해요. 
참석자_1: Oh, I see. I would describe that as environmental inhalant allergies.(아, 그렇군요. 환경 흡입성 알레르기로 설명할 수 있겠네요.)
---
[요약]
'''),
    ("assistant",
'''* 55세 여성
* 평가 및 치료 가능성 의뢰
* 항목: 알레르기, 미각 저하, 구강 건조증, 위식도 역류 질환, 음식 알레르기 가능성, 만성 위장관 과민성, 천식 및 환경 흡입제 알레르기 
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