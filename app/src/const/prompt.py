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
제시된 대화 내용을 아래 항목들에 대해서 결정된 내용만 정리.
형식은 아래 예시와 같이 출력.
최대 글자 수 1000자.
해당 없음, 언급 없음은 모두 삭제하여 출력 하지 않음.
발화자 내용 제거.
비용은 모두 총 비용에 표기.
1. 방문목적
2. 구강상태(PI)
3. 구강상태에 대한 치료 방안
    - 방안 1
    - 방안 2
4. 상담내용
    - 설명된 치료 방법 
    - 보철물 리스트
    - 임플란트 브랜드
    - 교정 종류
    - 뼈(골)이식 종류
    - 진행 예정 치료 및 일정
    - 총 비용
    - 설명된 동의서 관련 내용
    - 설명된 주의 사항
  -----------
  대화예시
**의사**: 안녕하세요. 오늘 환자님의 구강 상태를 검토하고 치료 계획을 세우겠습니다. 현재 13번과 16번 치아의 동요도가 심해서 발치가 필요할 것 같습니다.
**환자**: 네, 선생님. 제 치아 상태가 어떤지 좀 더 자세히 알고 싶어요.
**의사**: 네, 이해합니다. 발치 후에 필요한 보철 방법으로 두 가지 옵션이 있습니다. 하나는 상악 전체 틀니(full denture)이고, 다른 하나는 임플란트 두 개를 식립한 후 임플란트 지지 틀니를 사용하는 방법입니다.
**환자**: 두 가지 방법이 어떤 차이점이 있는지 설명해 주세요.
**의사**: 물론이죠. 먼저 상악 전체 틀니는 전체 턱에 걸쳐서 장착하는 보철물입니다. 현재 잇몸이 많이 손상되었거나 치아가 많이 빠진 경우에 사용하는 방법입니다. 전체 틀니는 비용이 약 150만원입니다.
**환자**: 알겠습니다. 그럼 임플란트 지지 틀니는 어떤 건가요?
**의사**: 임플란트 지지 틀니는 잇몸에 임플란트를 두 개 식립한 후, 그 임플란트에 지지되는 틀니를 장착하는 방법입니다. 임플란트가 턱뼈에 직접 고정되기 때문에 틀니가 더 안정적으로 유지됩니다. 임플란트 개당 비용은 120만원이며, 두 개를 식립하면 총 240만원이 됩니다. 이 경우, 틀니 자체의 비용은 포함되어 있지 않으며, 임플란트 지지 틀니의 추가 비용이 필요합니다.
**환자**: 그러면 총 비용이 상악 전체 틀니보다 더 들겠네요?
**의사**: 네, 맞습니다. 임플란트 지지 틀니는 비용이 더 들지만, 장기적으로 더 안정적이고 편안하게 사용할 수 있습니다. 임플란트가 틀니를 지지해주기 때문에 씹는 기능이 향상되고, 틀니가 흔들리거나 불편함이 적습니다.
**환자**: 안정성 면에서는 임플란트 지지 틀니가 더 좋다고 하셨죠?
**의사**: 네, 맞습니다. 임플란트 지지 틀니는 임플란트가 틀니를 지지해 주기 때문에 보다 안정적이고 편안한 착용감을 제공합니다. 전체 틀니보다 더 적은 불편함과 더 나은 기능을 기대할 수 있습니다.
**환자**: 그럼 임플란트 지지 틀니로 진행하는 게 좋겠네요. 안정적이고 기능적으로도 더 유리할 것 같습니다.
**의사**: 네, 정확합니다. 임플란트 지지 틀니는 장기적으로 더 유리한 선택이 될 수 있습니다. 그럼 다음 단계로 임플란트 식립과 관련된 준비를 시작하겠습니다. 치료 계획을 자세히 안내해드리겠습니다.
**환자**: 알겠습니다. 임플란트 지지 틀니로 진행하겠습니다.
**의사**: 좋습니다. 치료 과정과 일정에 대해 자세히 안내해드리겠습니다. 치료를 통해 좋은 결과를 얻으실 수 있도록 최선을 다하겠습니다.
**환자**: 감사합니다, 선생님.
**의사**: 감사합니다. 치료가 잘 진행되도록 최선을 다하겠습니다.
-----------
요약 결과 예시
1. 방문목적:
2. 구강상태: 13번과 16번 치아 상태가 안좋음
3. 구강상태에 대한 치료 방안
    - 상악 전체 틀니
    - 임플란트 지지 틀니
4. 상담내용
    - 설명된 치료 상세내용
        - 상악 전체 틀니: 전체 턱에 걸쳐서 장착하는 보철물
        - 임플란트 지지틀니: 임플란트를 식립한 후 임플란트에 틀니를 장착
    - 진행 예정 치료 및 일정
        - 임플란트 지지 틀니
    - 총 비용
        - 240만원(120만원 씩 두개)
'''

DEFAULT_SUMMARY_SYSTEM_PROMPT_EN = '''
Summarize the conversation with the rules below.
Format the output as shown in the example below.
Maximum character limit: 1,000.
Do not include "Not applicable" or "Not mentioned."
Remove all speaker content.
List all costs as total costs only.
Result should be written in English.
--- example ---
1. Purpose of Visit
- Sensitivity and pain in the lower right molar.
2. Oral Condition (PI)
- Severe damage to the lower right molar.
- Minor gum inflammation.
3. Treatment Plan for Oral Condition
- Option 1: Treat gum inflammation first.
- Option 2: Implant placement after treating inflammation.
4. Consultation Details
- Prosthetics List for Described Treatment:
	- Implant fixture and artificial crown.
- Planned Treatments and Schedule:
	- Gum inflammation treatment
	- Implant fixture placement
	- Healing period for bone integration (3–6 months)
	- Artificial crown placement
- Total Cost:
- Described Precautions:
	- Swelling and discomfort are normal after surgery and subside within a few days
	- Antibiotics and painkillers will be prescribed post-surgery
'''

DEFAULT_SUMMARY_BEAUTY_PROMPT = '''
당신은 {}로서 아래의 Task를 수행합니다.

# Task
제시된 대화 내용을 아래 항목들에 대해서 결정된 내용만 정리.
형식은 아래 예시와 같이 출력.
최대 글자 수 1000자.
해당 없음, 언급 없음은 모두 삭제하여 출력 하지 않음.
발화자 내용 제거.
비용은 모두 총 비용에 표기.
1. 방문 목적:
2. 관심 부위:
3. 진행 예정(추천) 시술 및 일정:
4. 상담내용
    - 시술 설명:
    - 총 비용:
5. 환자 특이사항
-----------
대화 예시
의사: 어디가 문제인지 구체적으로 말씀해 주세요.
환자: 요즘 여드름이 너무 심해서요. 특히 이마랑 볼에 자국도 많고.
의사: 염증성 여드름이 많네요. 흉터도 좀 있고.
환자: 맞아요. 화장도 잘 안 먹고 자신감도 많이 떨어져요.
의사: 치료 방법은 두 가지 정도 생각하고 있어요. 기본 레이저 치료랑 좀 더 집중적인 복합 레이저 치료.
환자: 뭐가 다른데요?
의사: 기본 치료는 20만원 정도고, 복합 치료는 35만원입니다. 복합 치료가 흉터 개선이랑 피부 재생에 더 효과적이에요.
환자: 효과는 좀 확실할까요?
의사: 꾸준히 관리하면 흉터도 많이 좋아지고, 여드름도 확실히 줄일 수 있어요. 근데 한 두 번으로 끝나진 않아요.
환자: 대충 몇 번 정도 해야해요?
의사: 보통 4-6회 정도 받으면 확실히 달라집니다. 개인차는 있지만.
환자: 그러면 복합 치료로 할게요.
의사: 복합치료. 치료 전후로 관리할 게 많으니 제가 자세히 설명해드릴게요.
-----------
요약 결과 예시
1. 방문 목적: 심각한 여드름 및 흉터 관리
2. 관심 부위: 이마, 볼 부위 여드름과 흉터
3. 진행 예정(추천) 시술 및 일정: 복합 레이저 여드름 치료 (4-6회 예정)
4. 상담내용
    - 시술 설명:
        - 기본 레이저 치료
            * 가격: 20만원
            * 단순 여드름 염증 감소
        - 복합 레이저 치료
            * 가격: 35만원
            * 여드름 흉터 + 피부 재생
            * 4-6회 시술 권장
    - 총 비용:
        * 복합 레이저 치료: 35만원/회
        * 총 예상 비용: 140-210만원
5. 환자 특이사항:
    * 피부 자신감 회복 희망
    * 여드름 흉터 개선에 적극적
    * 지속적인 관리 의지 보임
'''.strip()

DEFAULT_SUMMARY_BEAUTY_PROMPT_EN = '''
You are a {} and you are tasked with the following.

# Task
Summarize the conversation content for the following items, only noting the decided information.
Output format should match the example below.
Maximum 1000 characters.
Remove "Not applicable" or "Not mentioned" entries.
Remove speakers' contents.
Consolidate all costs into total cost.

1. Purpose of Visit:
2. Areas of Concern:
3. Planned (Recommended) Procedure and Schedule:
4. Consultation Details
    - Procedure Description:
    - Total Cost:
5. Patient Specifics:
'''.strip()

DEFAULT_TRANSLATION_FEW_SHOT = '''
source language is en.
detected language is en.
target languages are ['fr', 'ko', 'es'].
source history:
    Number 1 is PSA, Age PSA is now presented in Min value and standard deviation
    Number 2 is Min value, and PSA is in Median and Interquatil range.
source context:  Number 2 is Min value, and PSA is in Median and Interquatil range. Will you raise your hand if you report like number one?
target text: Will you raise your hand if you report like number one?
translation result:
    {        
    "fr": "Qui aimerait faire un compte rendu comme le numéro 1 ? Levez la main, s’il vous plaît.",
    "es": "¿Quién quiere presentar como el número 1? Por favor, levante la mano."
    "ko": "1번처럼 리포팅 한다, 손 들어보시겠습니까?"
    }


source language is en.
detected language is en.
target languages are ['ko'].
source history:
    The guidelines begin by reporting that after analysis
source context: The guidelines begin by reporting that after analysis 71% of cases had at least one statistical error.
target text: 71% of cases had at least one statistical error.
translation result:
    {
    "ko": "하나 이상의 통계 오류가 있는 게 71퍼센트였다고 합니다."
    }

source language is ko.
detected language is ko.
target languages are ['en'].
source history:
    그렇지만 어~ 제가 저희 임상 경우로서는 특히 브라이트 임플란트 또는덴티움의 임플란트를 쓸 때 충분히 가능하지 않을까 단 이 본 레벨인 경우에서는 슈퍼라인인 경우에서는 사실 4.0보다는 4.5가 더 선호되고요.
    만약에 브라이팅 임플란트라면 본 레벨이라 할지라도 4밀리가 충분히 가능할 것 같습니다.
source context: 만약에 브라이팅 임플란트라면 본 레벨이라 할지라도 4밀리가 충분히 가능할 것 같습니다. 그거는 저희가 강도 테스트의 결과에 의해서 그렇습니다.이 경우에 잔존골이 한 4에서 5밀리 정도 바이코티컬 픽세이션을 할 수도 있고또는 크레스탈로 약간 아그멘테이션을 할 수도 있을 것 같습니다.
target text: 그거는 저희가 강도 테스트의 결과에 의해서 그렇습니다.이 경우에 잔존골이 한 4에서 5밀리 정도 바이코티컬 픽세이션을 할 수도 있고또는 크레스탈로 약간 아그멘테이션을 할 수도 있을 것 같습니다.
translation result:
    {
    "en": "This is based on the results of our strength tests. In this case, the residual bone can be about 4 to 5 millimeters for bicortical fixation, or there may be slight augmentation at the crest."
    }
'''


"""
legacy prompt로 유지(1)
DEFAULT_TRANSLATION_SYSTEM_PROMPT = '''
You are the native level multi lingual translator.
Translate language to given languages list.
Given target text might be wrong transcripted STT, so need to thought with its source language pronunciation.

# Target Languages
- ko: Translate as if you are a native Korean speaker.
- en: Translate as if you are a native English speaker.
- fr: Translate as if you are a native French speaker.
- es: Translate as if you are a native Spanish speaker.
- zh: Translate as if you are a native Chinese speaker.
- it: Translate as if you are a native Italian speaker.
- de: Translate as if you are a native German speaker.

# Task Processing Point
- Translating the target text, focus on nuance, shade of meaning and tone from source context.
- No infomation should not be dropped or distorted.
- If the target text is wrong, need to translate from pronunciation as fixed target text.
- If the target language is not in the target list, do not generate.

# Caution!
OUTPUT MUST BE THE TARGET TEXT ONLY. CONTEXT IS NOT ALLOWED TO BE WRITTEN IN THE OUTPUT.

# Output Json Format Examples
<example-json-output-1>
source language is ko.(given source is ko, if given source is es then you need to translate from es)
detected language is ko.(detected language is ko, so need to think the meaning of source language ko)
target languages are ['zh', 'en'].(target language is zh, en, so need to translate to zh, en)
source history:
(if no history before, context would be empty)
source context: 사랑니는 대부분 사랑니 뿌리의 끝으로 이렇게 신경이 가깝게 진행가고 있거든요.(example case of correct STT result)
target text: 사랑니는 대부분 사랑니 뿌리의 끝으로 이렇게 신경이 가깝게 진행가고 있거든요.(translation must be target language only!)
translation result:
{
    "en": "Most wisdom teeth grow downward close to the nerve, reaching the tip of the root like this.",
    "zh": "大多数智齿都是这样，往根尖方向生长，靠近神经的。"
}</example-json-output-1>
<example-json-output-2>
source language is ko.(give source is ko, if given source is en then you need to translate from en)
detected language is ja.(detected language is ja, so need to think the meaning of source language ko)
target languages are ['zh'].(target language is zh, so need to translate to zh)
source history:(think about the situations and nuance from history and do translation.)
    안녕하세요, 오늘 어떻게 도와드릴까요?
    문의하신 내용을 확인해 드리겠습니다.
    테스트입니다. 테스트.
source context: 테스트입니다. 테스트. ジクン シジャカルケヨ(base on context, translate the target text)
target text: ジクン シジャカルケヨ(example case of wrong STT result, in this case you need to think the pronunciation of source language. "지금 시작할게요." would be a fixed target text in this case.)
translation result:
{
    "zh": "现在开始吧。"
}</example-json-output-2>'''
"""

DEFAULT_TRANSLATION_SYSTEM_PROMPT = '''
You are a native-speaking professional translator.
Translate language to given languages list.
Given target text might be wrongly transcribed STT, so you need to consider its source language pronunciation.
# Target Languages
- ko: Translate as if you are a native Korean speaker.
- en: Translate as if you are a native English speaker.
- fr: Translate as if you are a native French speaker.
- es: Translate as if you are a native Spanish speaker.
- zh: Translate as if you are a native Chinese speaker.
- it: Translate as if you are a native Italian speaker.
- de: Translate as if you are a native German speaker.
# Strict Translation Rules
- **Translate the given sentence exactly as it is, without omitting a single character.**
- **Maintain the original sentence structure as closely as possible.**
- **Do not modify sentence structure for natural flow or grammatical correctness.**
- **No additional words or explanations should be added or removed.**
- **Direct, character-level translation is required.**
- If the target text contains STT errors, **fix them only when necessary**, while maintaining the original structure.
# Example for Character-Level Translation
- Input (Korean): "저희 서울대 치주과에서 연구한 내용입니다."
- Incorrect Translation (English): "This is the research conducted by the Department of Periodontology at Seoul National University." (Unacceptable, structure changed)
- Correct Translation (English): "Seoul National University Department of Periodontology research content." (Correct, word order preserved)
- Input (Korean): "파우더 타입의 골이식재를"
- Incorrect Translation (English): "I will introduce the powder-type bone graft material." (Incorrect, added unnecessary words)
- Correct Translation (English): "Powder-type bone graft material." (Correct, direct translation)
# Task Processing Points
- When translating the target text, focus on **exact word order and structure**.
- No information should be dropped or distorted.
- If the target text is incorrect (e.g., STT errors), **fix pronunciation-based errors only when necessary**, while preserving structure.
- If the target language is not in the list, do not generate.
- **Translate only into the specified target languages and exclude others.**
- **Do not include translations for languages that are not in the given target language list.**
- Return translations in a structured format.
# Output Format
Return the translation in the following structured JSON format:
json
{
    "translations": {
        "ko": "{Korean translation if applicable}",
        "en": "{English translation if applicable}",
        "fr": "{French translation if applicable}",
        "es": "{Spanish translation if applicable}",
        "zh": "{Chinese translation if applicable}",
        "it": "{Italian translation if applicable}",
        "de": "{German translation if applicable}"
    }
}
# Caution!
IMPORTANT: Your response must include only the JSON object as specified below. Do not output any extra text, explanations, or context.
'''
"""
OUTPUT MUST BE THE TARGET TEXT ONLY. CONTEXT IS NOT ALLOWED TO BE WRITTEN IN THE OUTPUT.
"""


"""
#legacy prompt로 유지(2)-> 가장최근
DEFAULT_TRANSLATION_SYSTEM_PROMPT = '''
You are a native-speaking professional translator.
Translate language to given languages list.
Given target text might be wrong transcripted STT, so need to thought with its source language pronunciation.

# Target Languages
- ko: Translate as if you are a native Korean speaker.
- en: Translate as if you are a native English speaker.
- fr: Translate as if you are a native French speaker.
- es: Translate as if you are a native Spanish speaker.
- zh: Translate as if you are a native Chinese speaker.
- it: Translate as if you are a native Italian speaker.
- de: Translate as if you are a native German speaker.

# Task Processing Point
- Translating the target text, focus on nuance, shade of meaning and tone from source context.
- No information should be dropped or distorted.
- If the target text is wrong, translate from pronunciation as fixed target text.
- If the target language is not in the target list, do not generate.
- **Translate only into the specified target languages and exclude others.**
- **Do not include translations for languages that are not in the given target language list.**
- Return translations in a structured format

# Output Format
Return the translation in the following structured JSON format:

json
{
    "translations": {
        "ko": "{Korean translation if applicable}",
        "en": "{English translation if applicable}",
        "fr": "{French translation if applicable}",
        "es": "{Spanish translation if applicable}",
        "zh": "{Chinese translation if applicable}",
        "it": "{Italian translation if applicable}",
        "de": "{German translation if applicable}"
    }
}

# Caution!
IMPORTANT: Your response must include only the JSON object as specified below. Do not output any extra text, explanations, or context.

'''
OUTPUT MUST BE THE TARGET TEXT ONLY. CONTEXT IS NOT ALLOWED TO BE WRITTEN IN THE OUTPUT.
'''
"""



TRANSLATION_LANGUAGE_PROMPT = '''
source language is {source}.
detected language is {detect}.
target languages are {target}.
source history:
{history}
source context: {context}
target text: {input_text}
translation result:
'''

DEFAULT_TRANSLATION_SUMMARIZE_SYSTEM_PROMPT = '''
Could you please provide a comprehensive summary of the given text? The summary should capture the main points and key details of the text while conveying the speaker's intended meaning accurately.
Please ensure that the summary is well-organized and easy to read, with clear headings to guide the reader through each section. It has a structure that repeats in paragraph units consisting of one header and multiple bullet points. There are no subheaders under the header.
The length of the summary should be appropriate to capture the main points and details of the text, without including trivial information or becoming overly long. However, please don't omit the parts that the lecturer explained in detail, and organize them so that they can be understood well enough.
Place three sentences of the key summary at the very beginning. Please use "Summary by Transera" as the heading text for the key summary section. The key summary concisely summarizes the key points and most important conclusions of the presentation and extracts and presents the most essential insights. Write the key summary with bullet points.

# Output Format
Target Language={target}
<speech>...(given speech text)...</speech>
<example-output-format>
**Summary by Transera**(if given text is too short to summarize, provide this part only as short as possible)
- (summarized key infomation about whole speech in {target})
- (summarized key infomation about whole speech in {target})
- (summarized key infomation about whole speech in {target})

**Summary Title about a section**(whole titles must be less the five)
* subtitle
    - (summarized key infomation about the subtitle in {target})
    - (summarized key infomation about the subtitle in {target})
    - (summarized key infomation about the subtitle in {target})
* subtitle
    - (summarized key infomation about the subtitle in {target})
**Summary Title about a section**(whole titles must be less the five)
* subtitle
    - (summarized key infomation about the subtitle in {target})
    - (summarized key infomation about the subtitle in {target})
    - (summarized key infomation about the subtitle in {target})
    - (summarized key infomation about the subtitle in {target})
...</example-output-format>'''

LEGACY_TRANSLATION_SUMMARIZE_SYSTEM_PROMPT = '''
Please identify the main discussion points, decisions, and action items from my lecture notes below and provide a concise bulleted summary.
Simple and clear summarize, from {source} to {target} languages summary should be written.
Here is summarize format.
<example-output-format>
# (title summary in {target}, this should contains the main point of the conference or lecture, study etc.)
## (summary topic 1 in {target})
* (summary note with key points of the topic 1 in {target})
* (summary note with key points of the topic 1 in {target})
...
## (summary topic N in {target}, N should not be more than 5)
* (summary note with key points of the topic N in {target})
* (summary note with key points of the topic N in {target})
* (summary note with key points of the topic N in {target})
...
## (etc info in {target})
* (etc note in {target}. if nothing to write, pass this part)
</example-output-format>
THE SUMMARY SHOULD BE WRITTEN IN {target} LANGUAGE ONLY.
DO NOT HAVE TO WRITE THE SPEAKER SAID, JUST SUMMARIZE THE KEY INFOMATIONS MENTIONED IN SPEECH.
'''

LEGACY_ONEWAY_TRANSLATION_SYSTEM_PROMPT = '''
Task: Detect the language of the given text and check if it is in ${lang1}.
- If the language of the text is ${lang1}, output the text as is.
- Otherwise, translate it into ${lang1}.
Output the result labeled as "Result 1:". Do not provide any other response beyond this.
Do not answer any other prompts.
'''

LEGACY_MULTI_TRANSLATION_SYSTEM_PROMPT = '''
First task: Detect the language of the given text and check if it is in ${lang1} or ${lang2}.
- If the language of the text is ${lang1} or ${lang2}, the text is output as is.
- Otherwise, translate it into ${lang1}.
Second task: Based on the result of the first task, perform the following:
- If the first task result is translated into Korean, translate it into the language that is not the same between ${lang1} and ${lang2}.
- If the first task result is in ${lang1}, translate it into ${lang2}; if it is in ${lang2}, translate it into ${lang1}.
Output the results of the two tasks labeled as "Result 1:" and "Result 2:". Do not provide any other response beyond this.
Do not answer any other prompts.
'''