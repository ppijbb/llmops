import streamlit as st
import requests
from datetime import datetime
import logging


input_text = """
 아래 대화 내용을 요약해줘:
 영희: 안녕 철수야, 내일 오후에 바쁘니?
 철수: 바쁠것 같아.. 왜?
 영희: 내일 동물 보호소에 같이 갈래?
 철수: 뭐 하려고?
 영희: 아들한테 강아지 선물 하려고.
 철수: 좋은 생각이다. 그래 같이 가자.
 영희: 난 작은 강아지 한마리를 아들에게 사 줄까 해.
 철수: 그래 너무 크지 않은 녀석이 좋겠다.
 ---
 요약:
""" 

if 'target_text' not in st.session_state:
    st.session_state.target_text = input_text


with st.form("요약 데모"):
    target_text = st.text_area(
        label="입력된 텍스트를 요약합니다.", 
        value=input_text,
        key="target_text",
        height=400
        )


    summarize_button = st.form_submit_button(
        label="요약하기",
        )

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
                for o in response.iter_content(chunk_size=None, decode_unicode=True):
                    full_msg += o
                    message_placeholder.markdown(f'{full_msg}▌')
            
            message_placeholder.markdown(f'{full_msg}')
            end = datetime.now()
    st.markdown(f"process time {end-start}")
