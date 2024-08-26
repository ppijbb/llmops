DEFAULT_SUMMARY_FEW_SHOT = [
    ("user", 
'''---
[대화]
참석자_1: 오늘은 어떤 문제로 방문하셨나요?
참석자_2: My dental implant has been feeling a bit loose recently. (임플란트가 최근에 약간 흔들리는 느낌이 듭니다.)
참석자_2: It was placed about two years ago, and it’s the first time I’ve noticed this. (약 2년 전에 임플란트를 했는데, 이런 건 처음이에요.)
참석자_1: 그 외에 불편한 점이나 통증이 있으신가요?
참석자_2: There’s no pain, but sometimes it feels a bit uncomfortable when I chew on that side. (통증은 없지만, 그쪽으로 씹을 때 약간 불편해요.)
참석자_1: 임플란트를 받은 후에 정기적인 검진은 받으셨나요?
참석자_2: Yes, I’ve been coming in every six months for check-ups. (네, 정기 검진을 위해 6개월마다 방문했습니다.)
참석자_1: 최근에 잇몸 염증이나 출혈이 있던 적이 있나요?
참석자_2: No, my gums have been healthy, and I haven't noticed any bleeding. (아니요, 잇몸은 건강했고 출혈도 없었습니다.)
참석자_1: 임플란트 주변에 음식물이 잘 끼거나 청소가 어려운 부분이 있었나요?
참석자_2: Sometimes food gets stuck, but I’ve been careful to clean it thoroughly. (가끔 음식물이 끼긴 하지만, 철저히 청소하고 있어요.)
참석자_1: 알겠습니다. 임플란트와 주변 조직을 정밀하게 검사해보고, 필요한 경우 치료 방법을 논의하겠습니다.
---
[요약]
'''), 
    ("assistant", 
'''* 2년 전 임플란트를 받은 환자, 최근 임플란트가 흔들리는 느낌을 호소
* 통증은 없으나 씹을 때 약간 불편함을 느끼고 있으며, 잇몸 상태는 건강함
* 임플란트 주변에 음식물이 끼긴 하나 철저한 청소를 유지하고 있음
---'''),
    ("user", 
'''---
[대화] 
참석자_1: 무슨 문제로 오셨나요? 
참석자_2: My tooth has been sensitive for a few days now. (며칠 전부터 이가 민감해졌어요.) 
참석자_2: It's getting worse every time I eat something cold or sweet. (차가운 것이나 단 것을 먹을 때마다 점점 더 아파요.) 
참석자_2: The pain is sharp and mostly on the upper right side. (통증이 날카롭고 주로 오른쪽 윗부분에 있습니다.) 
참석자_1: 언제부터 통증이 시작되었나요? 
참석자_2: It started about a week ago. (약 일주일 전에 시작되었어요.) 
참석자_2: At first, it was just a little discomfort, but now it's hard to chew on that side. (처음에는 약간 불편했는데, 이제는 그쪽으로 씹기가 힘들어요.) 
참석자_1: 다른 증상은 없나요? 예를 들어, 발열이나 잇몸 출혈 같은 증상요. 
참석자_2: No fever, but I noticed some slight bleeding when I brushed my teeth this morning. (열은 없지만, 오늘 아침에 양치할 때 약간 출혈이 있었습니다.) 
참석자_1: 마지막으로 치과에 가신 게 언제인가요? 
참석자_2: About six months ago, for a routine check-up. (6개월 전에 정기 검진을 위해 갔습니다.) 
참석자_1: 치아를 제외하고는 다른 신체 부위에 통증이나 불편함이 없으신가요? 
참석자_2: No, the pain is localized to the upper right tooth area. (아니요, 통증은 오른쪽 위쪽 치아 부위에 국한되어 있습니다.) 
참석자_1: 알겠습니다. 지금부터 이 부위를 검사해 보겠습니다.
---
[요약]
'''),
    ("assistant",
'''* 중년 남성, 오른쪽 윗부분 치아의 민감함과 통증 호소
* 통증은 약 일주일 전부터 시작되었으며, 차가운 음식과 단 음식에 반응함
* 발열은 없으나, 오늘 아침 양치 시 약간의 잇몸 출혈을 경험함
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