import streamlit as st
import requests
from datetime import datetime
import logging


input_text = """[Dialouge]
의사: 부모님은 좀 어떠세요?
환자: 의사 선생님, 지금 두 분 다 돌아가셨어요.
의사: 정말 유감입니다, 선생님. 형제들은 어떠세요?
환자: 감사합니다, 의사 선생님. 두 형제 모두 아주 잘 지내고 있습니다.
의사: 몇 살인지 기억해 주시겠습니까?
환자: 한 분은 예순 여덟이고 다른 한 분은 일흔일곱입니다. 저는 중간에 있습니다.
의사: 잘됐네요. 가족 중에 지병이 있으신 분이 있나요?
환자: 글쎄요, 포함되는지 잘 모르겠지만 저에게는 남매가 있었는데 쌍둥이였는데 태어날 때 사망했습니다.
의사: 아, 말씀해 주셔서 감사합니다.
환자: 네, 중요할 것 같아서요.
의사: 자녀가 있으신가요, 선생님?
환자: 네, 두 아들이 있는데 둘 다 아주 잘 지내고 있습니다.
의사: 아들들은 몇 살입니까?
환자: 한 명은 쉰네 살이고 다른 한 명은 쉰일곱 살입니다.
의사: 신생아 사망 외에 제가 알아야 할 다른 질환이 있나요?
환자: 네, 가족 중 많은 수가 당뇨병을 앓고 있고 심장마비를 겪은 사람도 많습니다.
 ---
 [Summary]
""" 

if 'target_text' not in st.session_state:
    st.session_state.target_text = input_text


with st.form("요약 데모"):
    target_text = st.text_area(
        label="입력된 텍스트를 요약합니다.", 
        value=input_text,
        key="target_text",
        height=400)


    summarize_button = st.form_submit_button(label="요약하기")

if summarize_button:
    with st.spinner('Wait for it...'):
        start = datetime.now()
        response = requests.post(
             url="http://localhost:8555/summarize_stream",
             json={
                 "text": st.session_state.target_text
                 },
             stream=True)
        # output = response.json()["text"]
        
        # logging.warn(output)
        # if "---" in output:
        #     output = output.split("---")[-1].replace("<|end_of_text|>", "")
    
        with st.container(border=True):
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_msg = ""
                for o in response.iter_content(chunk_size=256, decode_unicode=True):
                    full_msg += o
                    message_placeholder.markdown(f'{full_msg}▌')
            
            message_placeholder.markdown(f'{full_msg}')
            end = datetime.now()
    st.markdown(f"process time {end-start}")
