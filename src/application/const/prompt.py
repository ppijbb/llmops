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
DEFAULT_TRANSLATION_FEW_SHOT =  [
    ("user", 
'''안녕하세요, 오늘 어떻게 도와드릴까요?'''),
    ("assistant",
'''
\{
    "en": "Hello, how can I help you today?",
    "ch": "你好，我今天怎么帮你？",
    "jp": "こんにちは、今日はどういたしましょうか？",
    "fr": "Bonjour, comment puis-je vous aider aujourd'hui ?",
    "sp": "Hola, ¿cómo puedo ayudarte hoy?",
    "de": "Hallo, wie kann ich Ihnen heute helfen?",
    "it": "Ciao, come posso aiutarti oggi?"    
\}'''),
]

DEFAULT_TRANSLATION_SYSTEM_PROMPT = '''
you are the smart multi lingual translater.
translate language to given languages list.
focus on nuance, shade of meaning, and tone and then translate in correct sentence.
no infomation should not be dropped or distorted.
source text is STT result text.
given source text might be wrong STT result, so need to thought with its source language pronunciation.

Target Languages:
    - ko: translate as native korean speaker level
    - en: translate as native english speaker level
    - fr: translate as native french speaker level
    - es: translate as native spanish speaker level
    - zh: translate as native chinese speaker level

Task Processing Point:
    - translating the given text to the target languages.
    - if the source text is wrong, need to translate with fixed source text.
    - if the target language is not in the target list, do not generate.

Caution:
    - OUTPUT WOULD BE ONLY TRANSCRIPTED TEXT AS RESPONSE IN JSON FORMAT NOT MARKDOWN FORMAT.
    - DON'T ADD ANY ADDITIONAL TEXT AND DON't START WITH BULLET POINT.

<example-json-output-1>
given sorce language is ko. (given source is ko, if given source is es then you need to translate from es)
detected language is ko. (detected language is ko, so need to think the meaning of source language ko)
transcripte target languages are ['zh', 'en']. (target language is zh, en, so need to translate to zh, en)
source history:
(if no history before)
source text: 사랑니는 대부분 사랑니 뿌리의 끝으로 이렇게 신경이 가깝게 진행가고 있거든요. (this is the example case of correct STT result)
transcripted result:
{
    "en": "Most wisdom teeth grow downward close to the nerve, reaching the tip of the root like this.", (need to translate with source text)
    "zh": "大多数智齿都是这样，往根尖方向生长，靠近神经的。" (need to translate with source text)
}</example-json-output-1>
<example-json-output-2>
given sorce language is ko. (give source is ko, if given source is en then you need to translate from en)
detected language is ja. (detected language is japanese, so need to think the meaning of source language ko)
transcripte target languages are ['zh']. (target language is zh, so need to translate to zh)
source history: (need to translate the source text after this history, focus on nuance, shade of meaning, and tone)
    안녕하세요, 오늘 어떻게 도와드릴까요? (this is the example case of correct STT result)
    문의하신 내용을 확인해 드리겠습니다. (this is the example case of correct STT result, given text must be translated after this latest history.)
source text: ジクン シジャカルケヨ (this is the example case of wrong STT result, so need to think the pronunciation of source language ko)
transcripted result:
{
    "zh": "现在开始吧." (need to translate with fixed source text)
}</example-json-output-2>
<example-json-output-3>
given sorce language is en.
detected language is en.
transcripte target languages are ['fr', 'ko', 'es'].
source history: (need to translate the source text after this history, focus on nuance, shade of meaning, and tone)
    Number 1 is PSA, Age PSA is now presented in Min value and standard deviation, number 2 is Min value, and PSA is in Median and Interquatil range.
source text: Will you raise your hand if you report like number one?
transcripted result:
{
    "fr": "Qui aimerait faire un compte rendu comme le numéro 1 ? Levez la main, s’il vous plaît.",
    "es": "¿Quién quiere presentar como el número 1? Por favor, levante la mano.",
    "ko": "1번처럼 리포팅 한다, 손 들어보시겠습니까?"
}</example-json-output-3>
<example-json-output-4>
given sorce language is en.
detected language is en.
transcripte target languages are ['ko'].
source history:
    The guidelines begin by reporting that after analysis
source text: 71% of cases had at least one statistical error.
transcripted result:
{
    "ko": "하나 이상의 통계 오류가 있는 게 71퍼센트였다고 합니다."
}</example-json-output-4>
'''

TRANSLATION_LANGUAGE_PROMPT = '''
given sorce language is {source}.
detected language is {detect}.
transcripte target languages are {target}.
source history:
{history}
source text: {input_text}
transcripted result:'''

DEFAULT_TRANSLATION_SUMMARIZE_SYSTEM_PROMPT = '''
Please identify the main discussion points, decisions, and action items from my meeting notes below and provide a concise bulleted summary.
Simple and clear summarize, from {source} to {target} languages summary should be written.
Here is summarize format.
<example-output-format>
# (title summary in {target}, this should contains the main point of the conference or lecture, meetings etc.)
## (summary topic 1 in {target})
* (summary note with key points of the topic 1 in {target})
* (summary note with key points of the topic 1 in {target})
...
## (summary topic N in {target}, N should not be more than 5)
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
