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


input_prompt = """
제시된 대화 내용을 아래 항목들에 대해서 결정된 내용만 정리.
형식은 아래 항목들과 순서가 똑같이 최대 글자 수 500자.
해당 없음, 언급 없음은 모두 삭제하여 출력 하지 않음.
발화자 내용 제거.
약 복용 법 언급 시 무조건 포함.
한글로만 출력.
1. 방문목적
2. 구강상태(PI)
3. 구강상태에 대한 치료 방안
4. 상담내용
- 설명된 치료 방법
- 보철물 종류(보철 진행 시)
- 임플란트 종류(임플란트 진행 시)
- 교정 종류(교정치료 진행 시)
- 뼈(골)이식 종류(뼈이식 진행 시)
- 치료 진행 유무 및 일정
- 결정된 치료 방법
- 총 비용
- 설명된 동의서 관련 내용(부작용 및 실패 가능성 설명 등등)
- 설명된 주의사항(복용약이 있을 시 표시)
"""

input_text = """---
참석자 1: 선생님 외에 다른 약속은 없어요. 그래서 잘 차분하게 준비해서 마무리 잘 하겠습니다.
참석자 1: 이쪽이 오른쪽이고 이쪽이 왼쪽입니다. 지금 오른쪽 위에 어금니 쪽은 치아가 없는 상태이시고 송곳니는 부러져 있고 그 앞에 작은 앞니도 부러져 있고요. 반대쪽도 지금 어금니는 없고 그 앞에 혼자 있는 요 작은 어금니는 이제 많이 흔들리고 그 앞에 송고니도 부러지고 염증이 있는 상태예요. 그래서 이제 위에는 이 대문니 두개를 제외하고는 좀 시야가 수명을 다한 상태라 오늘 이제 발치를 할 거고요. 밑에는 여기 사랑니가 하나 남아있고 또 송곳니와 그 뒤에 작은 어금니들 네 이거는 지금 상태가 괜찮습니다. 네 네 지금 손으로 짚고 계시는 고치아들 그리고 앞니가 밑에도 이제 4개가 있는데 그중에 2개는 빠진 상태고요. 네 맞습니다. 나머지 2개의 치아도 지금 뿌리 쪽에 염증 때문에 이가 꽤 흔들리는 
참석자 2: 네 프로그램은 완전히
참석자 1: 그래서 걔네들도 살려서 쓰기에는 조금 상태가 안 좋은 상태이기 때문에 이것들도 이제 같이 발치를 할 거고요. 요 부러진 치아 네 지금 위가 부러지고 노출된 신경 때문에 이제 감염이 일어나서 뿌리 쪽에 이렇게 염증이 있는데 이거는 이제 발치하고 염증 제거를 할 거고요. 그 사이에 그리고 이 오른쪽 아래도 이제 부러진 부러진 치아들 뿌리 조각들 이런 것들은 다 제거할 겁니다. 그래서 이렇게 뺄 거 빼고 정리하고 나면 이제 위에는 양쪽에 치아가 6개씩 비게 되거든요. 근데 그거를 이제 임플란트를 4개를 심어서 회복을 할 거고 6개 치아를 다 채우 지는 않고 요 맨 끝에 거는 이제 꼭 회복해야 되는 건 아니거든요. 그래서 그 부분은 이제 이 뒤에 치아를 조금 사이즈를 키우면서 그러니까 6개 같은 5개를 이제 만들게 될 겁니다. 그래서 대칭적인 형태로 이렇게 제작이 될 거고 이 위턱의 어금니 쪽 같은 경우는 광대뼈 안쪽에 상악동이라고 하는 공기주머니가 있어요. 
참석자 1: 이 공기주머니의 존재 때문에 임플란트를 하는데 대부분의 경우에 이 임플란트를 하려면 뼈가 폭과 높이가 돼야 되는데 높이가 부족한 경우가 많습니다. 그래서 이 양쪽 상악동 쪽에 뼈 이식을 좀 같이 하면서 진행을 하게 될 겁니다. 그래서 위에는 이렇게 정리가 될 거고요. 밑에는 남겨놓는 송금니와 작은 어금니 뒤쪽으로 치아가 2개가 피게 되고요. 이쪽도 이 작은 어금니 뒤쪽으로 어금니가 이제 2개가 피게 되는데 이 양쪽 두 개 비는 어금니 쪽에 임플란트를 2개씩 식립을 할 거고 요 앞니 빠진 자리와 이 중간에 이 뿌리 조각 제거한 자리는 이 양쪽 치아들 살리기로 이제 한 치아들을 연결해서 씌우는 브리지라고 하는 치료를 해서 이제 수복을 하게 될 거예요.
참석자 1: 지금 이제 말씀드린 발치 임플란트 뼈 이식 이런 과정들은 수면 상태에서 한 번에 다 진행을 하게 될 거고 오늘 그 임신 치아까지 다 해서 마무리를 할 겁니다. 전체적인 치료 기간은 이제 발치하고 뼈 이식하고 임플란트 심어놓은 것들이 이제 잇몸 뼈하고 좀 이렇게 단단하게 결합하는 데 시간이 필요하거든요. 그래서 한 3개월에서 4개월 정도 걸리게 될 거고 그 기간 동안은 조금 불편하시겠지만 임시 치아 상태로 지내시게 될 거예요. 오늘 잘 차분하게 준비해서 마무리 잘 하겠습니다.
오늘
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
""" 

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
