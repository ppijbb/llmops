import streamlit as st
import requests
from datetime import datetime
import logging


st.set_page_config(
    page_title="LLM Summary", 
    page_icon="📝", 
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None)
st.page_link(
    "pages/translation_test.py", label="translation test", icon="🔣"
)

input_prompt = """
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
    - 설명된 치료 방법 보철물 리스트
    - 임플란트 브랜드
    - 교정 종류
    - 뼈(골)이식 종류
    - 진행 예정 치료 및 일정
    - 총 비용
    - 설명된 동의서 관련 내용
    - 설명된 주의 사항
-----------
    대화예시
**의사**: 안녕하세요. 오늘 환자님의 구강 상태를 검토하고 치료 계획을 세우겠습니다. 현재 13번과 16번 치아의 동요도가 심해서 발치가 필요할 것 같습니다.\n
**환자**: 네, 선생님. 제 치아 상태가 어떤지 좀 더 자세히 알고 싶어요.\n
**의사**: 네, 이해합니다. 발치 후에 필요한 보철 방법으로 두 가지 옵션이 있습니다. 하나는 상악 전체 틀니(full denture)이고, 다른 하나는 임플란트 두 개를 식립한 후 임플란트 지지 틀니를 사용하는 방법입니다.\n
**환자**: 두 가지 방법이 어떤 차이점이 있는지 설명해 주세요.\n
**의사**: 물론이죠. 먼저 상악 전체 틀니는 전체 턱에 걸쳐서 장착하는 보철물입니다. 현재 잇몸이 많이 손상되었거나 치아가 많이 빠진 경우에 사용하는 방법입니다. 전체 틀니는 비용이 약 150만원입니다.\n
**환자**: 알겠습니다. 그럼 임플란트 지지 틀니는 어떤 건가요?\n
**의사**: 임플란트 지지 틀니는 잇몸에 임플란트를 두 개 식립한 후, 그 임플란트에 지지되는 틀니를 장착하는 방법입니다. 임플란트가 턱뼈에 직접 고정되기 때문에 틀니가 더 안정적으로 유지됩니다. 임플란트 개당 비용은 120만원이며, 두 개를 식립하면 총 240만원이 됩니다. 이 경우, 틀니 자체의 비용은 포함되어 있지 않으며, 임플란트 지지 틀니의 추가 비용이 필요합니다.\n
**환자**: 그러면 총 비용이 상악 전체 틀니보다 더 들겠네요?\n
**의사**: 네, 맞습니다. 임플란트 지지 틀니는 비용이 더 들지만, 장기적으로 더 안정적이고 편안하게 사용할 수 있습니다. 임플란트가 틀니를 지지해주기 때문에 씹는 기능이 향상되고, 틀니가 흔들리거나 불편함이 적습니다.\n
**환자**: 안정성 면에서는 임플란트 지지 틀니가 더 좋다고 하셨죠?\n
**의사**: 네, 맞습니다. 임플란트 지지 틀니는 임플란트가 틀니를 지지해 주기 때문에 보다 안정적이고 편안한 착용감을 제공합니다. 전체 틀니보다 더 적은 불편함과 더 나은 기능을 기대할 수 있습니다.\n
**환자**: 그럼 임플란트 지지 틀니로 진행하는 게 좋겠네요. 안정적이고 기능적으로도 더 유리할 것 같습니다.\n
**의사**: 네, 정확합니다. 임플란트 지지 틀니는 장기적으로 더 유리한 선택이 될 수 있습니다. 그럼 다음 단계로 임플란트 식립과 관련된 준비를 시작하겠습니다. 치료 계획을 자세히 안내해드리겠습니다.\n
**환자**: 알겠습니다. 임플란트 지지 틀니로 진행하겠습니다.\n
**의사**: 좋습니다. 치료 과정과 일정에 대해 자세히 안내해드리겠습니다. 치료를 통해 좋은 결과를 얻으실 수 있도록 최선을 다하겠습니다.\n
**환자**: 감사합니다, 선생님.\n
**의사**: 감사합니다. 치료가 잘 진행되도록 최선을 다하겠습니다.\n
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
""".strip()

input_text = """---
참석자 1: 선생님 외에 다른 약속은 없어요. 그래서 잘 차분하게 준비해서 마무리 잘 하겠습니다.
참석자 1: 이쪽이 오른쪽이고 이쪽이 왼쪽입니다. 지금 오른쪽 위에 어금니 쪽은 치아가 없는 상태이시고 송곳니는 부러져 있고 그 앞에 작은 앞니도 부러져 있고요. 반대쪽도 지금 어금니는 없고 그 앞에 혼자 있는 요 작은 어금니는 이제 많이 흔들리고 그 앞에 송고니도 부러지고 염증이 있는 상태예요. 그래서 이제 위에는 이 대문니 두개를 제외하고는 좀 시야가 수명을 다한 상태라 오늘 이제 발치를 할 거고요. 밑에는 여기 사랑니가 하나 남아있고 또 송곳니와 그 뒤에 작은 어금니들 네 이거는 지금 상태가 괜찮습니다. 네 네 지금 손으로 짚고 계시는 고치아들 그리고 앞니가 밑에도 이제 4개가 있는데 그중에 2개는 빠진 상태고요. 네 맞습니다. 나머지 2개의 치아도 지금 뿌리 쪽에 염증 때문에 이가 꽤 흔들리는 
참석자 2: 네 프로그램은 완전히
참석자 1: 그래서 걔네들도 살려서 쓰기에는 조금 상태가 안 좋은 상태이기 때문에 이것들도 이제 같이 발치를 할 거고요. 요 부러진 치아 네 지금 위가 부러지고 노출된 신경 때문에 이제 감염이 일어나서 뿌리 쪽에 이렇게 염증이 있는데 이거는 이제 발치하고 염증 제거를 할 거고요. 그 사이에 그리고 이 오른쪽 아래도 이제 부러진 부러진 치아들 뿌리 조각들 이런 것들은 다 제거할 겁니다. 그래서 이렇게 뺄 거 빼고 정리하고 나면 이제 위에는 양쪽에 치아가 6개씩 비게 되거든요. 근데 그거를 이제 임플란트를 4개를 심어서 회복을 할 거고 6개 치아를 다 채우 지는 않고 요 맨 끝에 거는 이제 꼭 회복해야 되는 건 아니거든요. 그래서 그 부분은 이제 이 뒤에 치아를 조금 사이즈를 키우면서 그러니까 6개 같은 5개를 이제 만들게 될 겁니다. 그래서 대칭적인 형태로 이렇게 제작이 될 거고 이 위턱의 어금니 쪽 같은 경우는 광대뼈 안쪽에 상악동이라고 하는 공기주머니가 있어요. 
참석자 1: 이 공기주머니의 존재 때문에 임플란트를 하는데 대부분의 경우에 이 임플란트를 하려면 뼈가 폭과 높이가 돼야 되는데 높이가 부족한 경우가 많습니다. 그래서 이 양쪽 상악동 쪽에 뼈 이식을 좀 같이 하면서 진행을 하게 될 겁니다. 그래서 위에는 이렇게 정리가 될 거고요. 밑에는 남겨놓는 송금니와 작은 어금니 뒤쪽으로 치아가 2개가 피게 되고요. 이쪽도 이 작은 어금니 뒤쪽으로 어금니가 이제 2개가 피게 되는데 이 양쪽 두 개 비는 어금니 쪽에 임플란트를 2개씩 식립을 할 거고 요 앞니 빠진 자리와 이 중간에 이 뿌리 조각 제거한 자리는 이 양쪽 치아들 살리기로 이제 한 치아들을 연결해서 씌우는 브리지라고 하는 치료를 해서 이제 수복을 하게 될 거예요.
참석자 1: 지금 이제 말씀드린 발치 임플란트 뼈 이식 이런 과정들은 수면 상태에서 한 번에 다 진행을 하게 될 거고 오늘 그 임신 치아까지 다 해서 마무리를 할 겁니다. 전체적인 치료 기간은 이제 발치하고 뼈 이식하고 임플란트 심어놓은 것들이 이제 잇몸 뼈하고 좀 이렇게 단단하게 결합하는 데 시간이 필요하거든요. 그래서 한 3개월에서 4개월 정도 걸리게 될 거고 그 기간 동안은 조금 불편하시겠지만 임시 치아 상태로 지내시게 될 거예요. 오늘 잘 차분하게 준비해서 마무리 잘 하겠습니다. 오늘
참석자 2: 기술이 어디까지 진행이 됩니까?
참석자 1: 지금 말씀드린 발치 뼈이식 임플란트 이런 것들은 오늘 다 할 거예요. 그래요. 네네 임시 체아까지
참석자 2: 그러니까 인플루언트 식립하는 것까지 다
참석자 1: 네네네. 오늘 그러니까 위에 8개 아래 4개 12개 임플란트를 다 인공 뼈 안에 넣을 겁니다.
참석자 2: 지금 염증이 밑에 조금씩 있다고 그랬는데 염증이 있는 상태에서 이렇게 해도 괜찮아.
참석자 1: 그러니까 염증을 깨끗하게 제거를 다 하고 정리를 하고 그 자리에 임플란트를 이제 심을 거고 이제 염증을 이렇게 정 제거하고 나면 잇몸뼈에 움푹 패인 일종의 웅덩이처럼 생기는데 그 부분은 이제 뼈 이식을 해서 회복을 할 겁니다.
참석자 2: 하루에 이렇게 많이 이빨을 재 발치하는 사람들도 있어요.
참석자 1: 네 저희 거의 매일 하고 있습니다. 그래서 지금 뭐 특별히 전신적인 컨디션이나 이런 게 좀 떨어지시는 게 아니라면 그 시술 과정이라든지 시술 이후에 회복하는 데 크게 지장이 있지는 않고요.
참석자 2: 그다음에 이게 다 완치됐을 때 앞으로 3개월 후에 좀 이렇게 대외 활동할 때 좀 깨끗하게 보이고 그렇게 다가
참석자 1: 그러니까 나머지 치아들은 다 만들어서 이제 제작이 되기 때문에 어떤 형태라든지 색깔 이런 것들은 가능하면 이제 예쁘고 원하시는 형태로 제작을 할 수 있어요. 근데 이제 다만 그 위에 앞니 두 개는 남겨놓잖아요. 그래서 얘랑 너무 동떨어지는 색깔이나 이렇게 하면 티가 날 수 있기 때문에 걔하고 조금 밸런스를 맞춰서 자연스러워 보이는 선에서 제작을 하는 게 나을 것 같습니다. 추후에 임플란트가 뼈랑 단단하게 굳고서 치아를 모양을 만들 때 한번 다시 한 번 말씀해 주시면 저희가 그거는 반영해서 치료 계획에 반영을 할 수 있습니다. 선생님 외에 다른 약속은 없어요. 그래서 그 선생님에 집중해서 진료 진행하겠습니다. 너무 긴장하지 마시고요. 잘 하겠습니다.
""".strip()

if 'target_text' not in st.session_state:
    st.session_state.target_text = input_text

if 'prompt_text' not in st.session_state:
    st.session_state.prompt_text = input_prompt


input_col, output_col = st.columns(2)
with input_col:
    st.title("LLM 요약")
    with st.form("요약 데모"):
        prompt_text = st.text_area(
            label="LLM prompt를 설정합니다", 
            value=input_prompt,
            key="prompt_text",
            height=400)
        target_text = st.text_area(
            label="입력된 텍스트를 요약합니다.", 
            value=input_text,
            key="target_text",
            height=400)
        summarize_button = st.form_submit_button(label="요약하기")
st.title("프롬프트 마크다운")
st.markdown(prompt_text,)
with output_col:
    st.title("요약 결과")
    with st.container(border=True):
        st.markdown("GPT 요약 결과가 여기에 표시됩니다.")
        if summarize_button:
            with st.spinner('Wait for it...'):
                start = datetime.now()
                response = requests.post(
                    url="http://localhost:8501/summarize",
                    json={
                        "prompt": st.session_state.prompt_text,
                        "text": st.session_state.target_text
                        },
                    stream=True)
                # output = response.json()["text"]
                
                # logging.warn(output)
                # if "---" in output:
                #     output = output.split("---")[-1].replace("<|end_of_text|>", "")

                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_msg = ""
                    output = response.json()["text"]
                    for o in output:
                        for word in o:
                            full_msg += word
                            message_placeholder.markdown(f'{full_msg}▌')
                
                message_placeholder.markdown(f'{full_msg}')
                end = datetime.now()
            st.markdown(f"process time {end-start}")
    
    # with st.container(border=True):
    #     st.markdown("Llama 요약 결과가 여기에 표시됩니다.")
    #     if summarize_button:
    #         with st.spinner('Wait for it...'):
    #             start = datetime.now()
    #             response = requests.post(
    #                 url="http://localhost:8501/summarize_stream",
    #                 json={
    #                     "prompt": st.session_state.prompt_text,
    #                     "text": st.session_state.target_text
    #                     },
    #                 stream=True)
    #             # output = response.json()["text"]
                
    #             # logging.warn(output)
    #             # if "---" in output:
    #             #     output = output.split("---")[-1].replace("<|end_of_text|>", "")

    #             with st.chat_message("assistant"):
    #                 message_placeholder = st.empty()
    #                 full_msg = ""
    #                 for o in response.iter_content(chunk_size=256, decode_unicode=True):
    #                     for word in o:
    #                         full_msg += word
    #                         message_placeholder.markdown(f'{full_msg}▌')
                
    #             message_placeholder.markdown(f'{full_msg}')
    #             end = datetime.now()
    #         st.markdown(f"process time {end-start}")
