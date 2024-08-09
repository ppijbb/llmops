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



input_text = """---
[대화]
참석자_1: 부모님은 좀 어떠세요?
참석자_2: 의사 선생님, 지금 두 분 다 돌아가셨어요.
참석자_1: 정말 유감입니다, 선생님. 형제들은 어떠세요?
참석자_2: 감사합니다, 의사 선생님. 두 형제 모두 아주 잘 지내고 있습니다.
참석자_1: 몇 살인지 기억해 주시겠습니까?
참석자_2: 한 분은 예순 여덟이고 다른 한 분은 일흔일곱입니다. 저는 중간에 있습니다.
참석자_1: 잘됐네요. 가족 중에 지병이 있으신 분이 있나요?
참석자_2: 글쎄요, 포함되는지 잘 모르겠지만 저에게는 남매가 있었는데 쌍둥이였는데 태어날 때 사망했습니다.
참석자_1: 아, 말씀해 주셔서 감사합니다.
참석자_2: 네, 중요할 것 같아서요.
참석자_1: 자녀가 있으신가요, 선생님?
참석자_2: 네, 두 아들이 있는데 둘 다 아주 잘 지내고 있습니다.
참석자_1: 아들들은 몇 살입니까?
참석자_2: 한 명은 쉰네 살이고 다른 한 명은 쉰일곱 살입니다.
참석자_1: 신생아 사망 외에 제가 알아야 할 다른 질환이 있나요?
참석자_2: 네, 가족 중 많은 수가 당뇨병을 앓고 있고 심장마비를 겪은 사람도 많습니다.
---
[요약]
""" 

if 'target_text' not in st.session_state:
    st.session_state.target_text = input_text



input_col, output_col = st.columns(2)
with input_col:
    st.title("LLM 요약")
    with st.form("요약 데모"):
        target_text = st.text_area(
            label="입력된 텍스트를 요약합니다.", 
            value=input_text,
            key="target_text",
            height=400)
        summarize_button = st.form_submit_button(label="요약하기")

with output_col:
    st.title("요약 결과")
    with st.container(border=True):
        st.markdown("요약 결과가 여기에 표시됩니다.")
        if summarize_button:
            with st.spinner('Wait for it...'):
                start = datetime.now()
                response = requests.post(
                    url="http://localhost:8885/summarize_stream",
                    json={
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
                    for o in response.iter_content(chunk_size=256, decode_unicode=True):
                        for word in o:
                            full_msg += o
                            message_placeholder.markdown(f'{full_msg}▌')
                
                message_placeholder.markdown(f'{full_msg}')
                end = datetime.now()
            st.markdown(f"process time {end-start}")
