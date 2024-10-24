from locust import HttpUser, task, between

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


class TestingUser(HttpUser):
    wait_time = between(1, 5)  # Wait time between requests

    @task
    def summary_testing(self):
        headers = {'Content-Type': 'application/json'}
        payload = {'input_text': input_text}
        response = self.client.post(url="http://localhost:8000/",
                                    headers=headers,
                                    json=payload)  # Replace with your actual endpoint
        # response = self.client.post(url="http://localhost:8555/summarize",
        #                             headers=headers,
        #                             json=payload)  # Replace with your actual endpoint
        # Add assertions or other logic here to validate the response if needed