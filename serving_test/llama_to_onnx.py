import time
import torch
import os
import onnx
import numpy as np

import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType
from optimum.onnxruntime import ORTModelForCausalLM

from optimum.intel import OVModelForCausalLM
import openvino as ov

from transformers import GenerationConfig, TextStreamer,  AutoTokenizer
from transformers import pipeline
from src.depend import get_model


os.environ['TRANSFORMERS_CACHE'] = './nas/conan/hf/'
os.environ['HF_HOME'] = './nas/conan/hf/'
os.environ['HF_DATASETS_CACHE'] = './nas/conan/hf/datasets/'
os.environ["OMP_NUM_THREADS"] = "24"

def inference_timer(fun):
    def wrapper(*args, **kwargs):
        start = time.time()
        print("inference testing start")
        fun(*args, **kwargs)
        end = time.time()
        print("inference testing end")
        print(f"Time: {end-start}")
    return wrapper



model, tokenizer = get_model(model_path="HuggingFaceH4/zephyr-7b-alpha",
                             adapter_path=None)
tokenizer.pad_token = tokenizer.eos_token if tokenizer.pad_token is None else tokenizer.pad_token
tokenizer.pad_token_id = tokenizer.eos_token_id
print(tokenizer.pad_token_id, tokenizer.eos_token_id)
target = '''
id1: 여러분 안녕하십니까 &company-name1& &name1&입니다. id1: 북아메리카에서는 살인 개미라고 불리워진다는 붉은불개미. id1: 지난 이천십칠 년 부산항을 시작으로 뭐 재작년 작년 계속 발견이 됐는데 올봄 앞두고 올봄에도 또다시 발견되고 혹시 한반도에 창궐하는 건 아닌지 좀 걱정이 됩니다. id1: 그래서 오늘 국내 최고의 개미 전문가 무려 사십 년 동안 개미를 연구하신 분을 초대했습니다. id1: 원광대학교의 &name2& 명예교수님이십니다. id1: 교수님 어서 오세요. id2: 예 반갑습니다. id1: 개미들도 겨울잠을 자죠? id2: 네 개 개미들도 겨울잠 잡니다. id1: 지금 현재는 잠자고 있죠 아직은? id2: 삼월 초니까 지금 지금은 한참 잠 잠을 자고 있을 땝니다. id1: 언제쯤 나와요 보통? id2: 뭐 삼월 말에서 사월 초 정도면 나오게 됩니다. id1: 그래요. id1: 붉은불개미 이게 북아메리카에서 왜 살인 개미라고 불리워 졌습니까? id2: 이 붉은불개미가 원래는 남미 아르헨티나 쪽에서 살고 있었는 개민데 원산지가. id2: 근데 이제 그 북미 쪽으로 그 배를 타고 또는 그 저 목재래든가 또 화물에 의해서 운반되어 가지고 남 미국에 미국 쪽으로 지금 에 들어가게 된 거죠. id2: 그래가지고 미국에서 아주 발생이 잘 돼서 그런 천적들이 별로 없어가지고. id1: 천적이 없다? id2: 네 네. id2: 천적이 없어서 미국 전역을 장악을 해서 피해를 많이 끼친 그런 개미기 때문에 그 개미들을 그 수입된 개미다 그래서 원래 이렇게 명칭을 붙였는데 id1: 수입된 불개미 예 예. id2: 제가 얘기했던 옛날에 에 수입된 적색불개미라고 있었습니다 왜냐면 불개미라고 하는 개미가 또 따로 있어요. id1: 그냥 불개미가 따로 있고? id2: 불그스름한 개미 여기에선 맞지 않습니다 여기서는 파이어 앤트니까. id2: 이제 쏘이면은 불에 데인 것같이 아퍼서 어 그럼 파인트 앤트 그러니까 불개미라 그랬는데 에 우리나라 현재 용어가 조금 적합치는 않습니다. id1: 근데 암튼 파이어가 붙은 거는 개미한테 물리거나 쏘이면 불에 덴 것처럼 아프다? id2: 그렇죠. id1: 그래서 목숨을 잃기도 해요 사람이? id2: 목숨을 잃기도 하죠. id2: 에 인제 그 목숨을 잃는 경우가 아 그렇게 많은 게 아니라 보통 한 쏘인 사람들의 영 점 육에서 에 한 육 퍼센트 정도 거의 id2: 이 사람들한테는 인제 애 그 알러지 과민반응이 일어납니다. id1: 그분들은 좀 특이 체질인가요? id2: 에 인제 그 그렇죠 알러지에 과민하게 반응하는 반응하는 사람들이 영 점 육에서 한 육 퍼센트 정도니까. id2: 그 사람들의 경우는 으 아주 심해서 어 그 호흡곤란도 일어나고 어 빈사상태에 빠지고 그래서 죽는 수도 있습니다. id1: 뭐 미국 북미 지역에서만 한 해 평균 한 팔만 명 이상이 이 개미에 쏘인다 그러고 지금까지 백 명이 목숨을 잃었다 맞습니까? id2: 맞습니다. id2: 통계는 아주 정확하지 않은데 백여 명 정도는 인제. id1: 근데 그동안에는 이 붉은불개미가 우리 한반도에는 전혀 없었어요? id2: 없었죠. id1: 어 처음 발견된 게 이천십칠 년 맞습니까? id2: 이천십칠 년이 맞습니다. id2: 이천십칠 년 에 구월 id1: 아마도 배를 타고 목재에 이렇게 옮겨왔겠죠? id2: 그 목재에 옮겨왔을 가능성도 있고 또 다른 화물 뭐 곡식이나 그런 컨테이너에 컨테이너 밑에다가 에 개미집을 지었는데 컨테이너를 옮길 때 따라올 수도 있고 그렇습니다. id2: 그니까 하여튼 선박에 의해서 오게 된 겁니다. id2: 개미가 지가 온 것이 아니고 가져온 거죠. id1: 바다 건너서 못 오죠 개미 {laughing} 혼자서는 그 그 크기가 좀 커요? id2: 삼 미리에서 한 육 미리 작죠 그러니까. id1: 삼에서 육 미리 id2: 적갈 색을 띄우고 어 침을 가지고 있고 에 크기는 한 삼 내지 육 미리 됩니다. id1: 근데 이 개미가 이천십칠 년에 부산항에서 발견됐고 일명 살인 개미라 그래서 인제 국민들이 놀랬단 말이에요. id1: 그리고 많은 뭐 방제 전문가들이 가가지고 박멸을 했다고 했거든요. id1: 근데 아니라고 하셨죠? id1: 아닐 거라고 하셨죠? id2: 예 예. id2: 근데 그 박멸이래는 말이 상당히 비과학적인 얘기거든요. id2: 왜냐믄 내 앞에 보이는 그 개미들을 없앴다 그래서 박멸이 아니잖아요. id1: 그러니까 눈에 보이는 개미가 없어졌다고 완전 없어진 게 아닌 거죠? id2: 왜냐면 왜냐면 개미 특성은 그 여왕개미가 있고 에 일개미가 있고 수개미가 있고 그래서 이제 번식을 여왕개미는 알만 낳고 수개미는 교미만 하고 일개미는 일만 합니다. id2: 그러니까 이 개 이 개미들이 번식을 할래면 여왕개미가 인제 공주개미를 낳죠. id2: 공주개미를 낳아가지고 공주개미가 인제 하늘로 올라가서 신혼비행을 해 가지고 에 수개미들하고 교미하면 그 그 개미들이 결혼 결혼을 해 가지고 내려와서 땅에 내려오죠. id2: 땅에서 인제 알을 낳아 가지고 번식하거든요. id2: 그러니까 인제 그 개미가 현재 없다고 그랬을 때 이 공주개미가 비상 비상해서 다른 지역에 가서 바람을 타고 올라가 가지고 어 그들이 발생할 가능성이 높기 때문에. id1: 어느 위치엔가 땅속에 지금 알을 낳고 있을 수도 있는데 그땐 안 보이는 거죠? id2: 그렇죠 그 감만 부두에서 그 개미집을 놔두고 일 메타 아 일 키로메타 반경으로 해가 조사를 해 가지고 그 속에서 여왕개미를 발견하지는 못했다 인제 그렇게 됐기 때문에 개미는 에 박멸되었다 이렇게 얘기를 해는데 그 뭐 저도 상당히 좀 그런 논박을 하기 힘들었습니다 왜냐면 에 그분들이 곤란해지니까. id2: 그런데도 불구하고 제가 이건 아니다. id2: 왜냐면 개미의 그 생태 습성을 사 키로 오 키로도 날아갈 수가 있거든요. id2: 에 그리고 그들이 인제 운동장 같은 데 떨어져서 개미집을 지으면 쉽게 알아보지만 수풀이거든요. id2: 우리나라에서 개미집을 발견하기가 엄청 어려워요. id2: 왜냐면 우리나라는 그냥 초원이 있는 것이 아니라 그냥 잡풀들이 막 우거지고 나무가 있고 등등 하면서 개미들은 충분히 자기 영역을 넓혀 갈 수가 있거든요. id1: 어딘가 숨어서 사람 눈엔. id2: 개미를 박멸했다고 표현하는 것은 문제가 있다 그런 얘길 했죠. id1: 교수님 말씀이 맞았어요. id1: 이천십팔 년에 또 나왔고? id2: 나왔죠 부산에서 또 나왔죠. id1: 이천십구 년에 또 나왔고 그죠? id2: 예 그다음에 또 어디서 나왔는가 하면 평택항에서 나왔어요. id2: 예 그다음에 인천항에서 나왔고. id1: 부산 평택 인천? id2: 그렇죠 이 이러한 개미들이 이 옮겨온 것이 아니라 항구에서 발견된 거로 봐서 중국 화물선에 의해서 온 것으로 저는 그렇게 추정을 했었어요. id1: 따로따로 온 거네요? id2: 그럴 가능성이 높죠 왜냐면 고 일이 년 사이에 그렇게 그 많은 그 영역을 점유하면서 초토화 시킬 수가 없습니다. id1: 부산에서 평택까지 일 년 사이에는 못 간다? id2: 절대 못 하죠. id2: 그다음에 또 인제 뭐 무엇이 발견됐는가 하면 대구의 아파트 공사장에서 거기서 또 개미가 발견되는데 그것은 정원석. id2: 정원석에서 발견된 거예요. id2: 그거는 상당히 문제점이 많았습니다 왜냐면 중국에서 우리가 그 아파트에서 쓰는 정원석 싸니까 그것을 많이 수입을 하거든요. id2: 그 수입 흙에 묻어서 온 거예요. id2: 그런 것은 뭐 완전히 개미집을 갖다 옮겨놓은 거나 마찬가지거든요. id1: 그러면 이게 아르헨티나 그쪽이 첫 번짼데 북미에서 창궐하고 이미 중국은 뭐 널리 퍼져 있다 이 말이군요? id2: 그것은 뭐 제가 그 이천사 년도에 저 칼럼을 쓴 적이 있었습니다. id2: 그래서 그 과학으로 세상보기라는 칼럼에 거기서 인제 제가 개미를 연구하니까 개미에 대한 여러 가지 인제 얘기를 많이 해서 독자들이 많이 좋아했었는데 그때에 바로 이 적색불개미를 우리가 에 조심해야 된다 그런 얘기 썼습니다. id2: 왜냐면 남미에서 얘들이 북미로 가고 북미는 거의 뭐 초토화시켰고 그 후 후로이에서부터 시작해서 저 미국의 북부 지역까지 거의 다 장악해 가지고 그 완전히 뭐 그 지역에 있는 농작물에서부터 가축들서부터 다 막 눈이 멀고 막 죽게 만들고 사람들도 많이 쏘여가지고 막 졸도하고 그래서 사람들 죽고 그런 일이 천구백삼십 년서부터 있었어요. id2: 그니까 거의 한 뭐 칠십 년 뭐 이상 에 미국을 교란을 시켰죠.
'''
target = '''
id1: 오늘 두 분 박사님이 약간 인삼 패션을 하고 오신 것 같아요. id2: 인삼이시고 약간 흑삼이시고 id1: 그러니까 id3: 백삼에 가깝습니다. id2: 백삼 id4: 하여간 며칠 고민 끝에 또는 테마가 인삼인 만큼 조금 준비 좀 했습니다. id1: 저희 오늘 기대해 보겠습니다. id1: 인삼 예로부터 좀 약재로 많이 사용을 해 왔죠. id1: 최근 들어서 코로나 일구때문에 인삼이랑 또 홍삼의 소비량이 많이 늘었다고 하는데 아마 두 분 이거는 모르실걸요? id2: 뭘요? id1: 네. id1: 인삼이 한류의 원조라고 합니다. id2: 한류 한류 저희가 아는 그 한류요? id1: 네. id2: 한류라고 하면 적어도 &name1& 아니면 제가 특별히 애정하는 우리 &name2& 정도는 돼야만 한류라고 할 수 있지 않을까요? id5: 김 과장님 저는 듣자마자 느낌이 딱 오는데요. id5: 아니 생각해보세요. id5: 인삼 앞에 보통 어떤 말이 붙죠? id2: 고려 고려 id5: 고려인삼 id5: 자 이름만 들으면 딱 알 수 있듯이 고려인삼 고려 시대부터 우리가 그 인삼이 위세를 떨쳤다는 거니까 인삼이 한류의 원조 맞지 않습니까? id2: 듣고 보니까 설득력이 있기는 한데 어떻게 맞는 건가요? id2: 박사님 어떻습니까? id4: 네 우리 박 대리님이 약간 공부가 약간 부족은 했습니다. id1: 어 id4: 사실은 고려 시대 이전의 삼국시대부터 해외로부터 많은 인기가 있었고 대표적인 교역품 중의 하나였습니다. id4: 이러고 나서 고려 시대로 넘어오면서 그때 이제 그 당시에는 고려삼 지금은 아마 고려인삼이 그 당시의 고려삼이 되었고 고려시대도 주변 국가와의 어떤 수교품이라든지 교역품으로서 많이 애용이 되었고요. id4: 그 뒤에 조선 시대로 넘어오면서 우리 인삼에 대한 위상과 명성이 아주 극치에 달했던 거죠. id4: 모니터를 잠깐 봐 주실래요? id2: 아 저거요? id4: 네 네. id4: 무엇인지 한 번 알아맞혀 보세요. id1: 저게 모양이 약간 짚신을 조금 눌러 놓은게 아닌가 id2: 저는 감이 왔는데 약간 네일아트 약간 조선 시대 스타일로 네일아트 색깔이 조선 스타일로 딱 해가지고 id4: 정답하고 점점 멀어지는 것 같구요. id2: 점점 멀어진다고요? id4: 저것은 사실은 일본에서 우리나라 인삼만을 수입하기 위해서 특수하게 제작한 화폐입니다. id1: 화폐요? id4: 일명 이름이 인삼대왕고은이라고 해서 현재는 일본 동경에 있는 화폐박물관에 소장되어 있습니다만 인삼대왕고은의 크기는 약 십 센치고 무게가 한 이백십 그램 정도 id1: 오 id4: 그런데 순도 팔십 퍼센트 짜리 은으로 제작된 것입니다. id2: 오 id4: 인삼대왕고은 백이십 개를 모아 와야지 인삼 한 근을 살 수 있을 정도로 우리 나라 인삼의 가치가 그리고 인기가 대단했던 것입니다. id2: 음 id4: 여기서 한 가지 재미있는 일화를 하나 말씀드리면요. id1: 네. id4: 결국은 일본에서 우리나라 인삼을 많이 수입하기 위해서 거꾸로 자국 내에는 은을 많이 유출을 해야될 부분이 생겼거든요 인삼을 사는 만큼. id4: 그러다보니까 일본 상인들이 약간 꼼수를 부렸던 것입니다. id4: 순도 팔십 퍼센트가 아닌 순도를 조금 낮춘 id5: 아 id4: 육십사 퍼센트 짜리 화폐를 만들었던 거죠. id1: 어머 어머 id4: 하지만 우리나라 상인들이 가만히 있을 건 아니구요. id4: 그러한 사실들을 알아내고 id5: 네. id4: 뭐~ 화가 잔뜩 난 거죠. id4: 그래서 이렇게 일본에서 순도가 낮춘 것으로 유통을 하면 우리는 절대 일본에게는 인삼을 수출하지 않겠다. id1: 아 id4: 언플을 내다 보니까 일본도 두 손 들고 순도 팔십 퍼센트 짜리 조금 전에 보여드렸던 인삼대왕고은을 천칠백십 년에 만들었던 것이죠. id1: 그런데 조선 시대 우리나라 인삼의 명성이 동아시아를 넘어서 유럽까지 진출했다면서요? id4: 예. id4: 우리가 실크로드라는 이야기를 많이 들었을 겁니다. id4: 중국의 비단의 어떤 서남아시아에서 유럽까지 가는 하나의 교역로가 실크로드인데요. id4: 사실 그 당시에 이미 우리나라는 중국 일본 우리나라로 이어지는 인삼로드가 있었습니다. id1: 오 id4: 그런 인삼로드를 통해서 동남아시아는 물론 유럽까지 우리나라 인삼이 드디어 진출을 하게 된 거죠. id4: 그러다가 이제 유럽 사람이 우리나라 인삼에 대해서 맛도 보고 효능을 보니까 유럽에선 이거야말로 정말 천하에 효능이 가장 좋은 약효가 아주 뛰어난 하나의 식품이라고 할 수도 있고 약재라고 할 수 있는데 그 정도로 유럽내에서 우리나라 인삼이나 가치들이 점점점 높아왔습니다. id4: 어쩌면 오늘 한류 이야기가 조금 나왔습니다만 id1: 네. id4: 무려 십칠 세기에 이미 유럽에선 우리 인삼 때문에 한류의 붐이 일어났다고 볼 수가 있고요. id1: 그런데요 인삼을 많은 분들이 즐겨 드시기는 하지만 인삼에 대해서는 정작 잘 모르는 것 같아요. id1: 인삼이 어렴풋이 귀한 약재로 쓰인다 또 뿌리를 주로 먹는다 요런거 정도만 알고 있지 않나요? id2: 맞아요. id5: 그래서 제가 인삼의 신상 정보를 간단히 털어왔습니다. id1: 오 id5: 오늘의 브리핑 한 번 시작해볼까요? id2: 좋아요. id5: 네. id5: 인삼 두릅나무과 여러해살이풀로 재배 가능한 온도나 생육 조건이 매우 까다로워 북위 삼십팔 도에서 사십팔 도 사이에서만 자란다고 합니다. id5: 인삼의 구조는 머리에 해당하는 뇌두 몸체에 해당하는 동체 다리에 해당하는 지근으로 이루어져 있다고 합니다. id1: 예 . id1: 아 역시 우리 박대리 오늘도 기대를 저버리지 않습니다. id5: 감사합니다. id1: 그러니까요. id2: 아 과장으로 승진할 것 같아요. id1: 자 우리 박사님들이 어떻게 박 대리 브리핑 마음에 드시나요? id3: 알기가 쉽지 않았을 텐데 대단하시네요. id1: 네. id1: 어 그런데요 인삼이 북위 삼십팔 도에서 사십팔 도 사이에서 자란다고 했거든요. id1: 어떤 특별한 이유가 있나요? id3: 어~ 저희가 인삼이 가장 활발하게 광합성을 할 수 있는 온도가 이십오 도로 알려져 있습니다. id3: 그래서 일반적으로 인삼이 연평균 영 도에서 십 도 사이에서 가장 잘 자라고 여름철에는 삼십오 도 이상이 넘어서게 되면 인삼 생육 장애를 얻게 돼서 잘 자라지 못하거나 뿌리 썩음병이 발생하게 됩니다. id3: 또 하나는 이런 온도와 더불어서 강수량이라든지 혹은 토양이라든지 이런 부분이 굉장히 영향을 많이 받는 게 바로 인삼입니다. id3: 이러한 다양한 기후 조건들을 충족하는 곳 이 지역이 바로 우리나라의 대한민국 이 대한민국이 인삼의 최적의 재배지 최적지라고 할 수 있습니다. id1: 그렇군요. id1: 어우 우리 박대리 덕분에 아주 좋은 정보 유익한 정보를 얻었어요. id5: 그럼 저 조만간 만년 대리에서 벗어날 수 있는 건가요? id2: 아니요 이게 좀 약해 왜냐하면 솔직히 요거 요거 세 치 혀로 이렇게 이렇게 나불댄 거야 쉽지. id2: 저처럼 이렇게 현장에 나가서 직접 발로 뛰어야지 되는 거 아니겠습니까? id5: 네 네. id2: 보세요 보세요 아 id2: 인삼에 숨겨진 과학의 비밀을 제가 좀 찾아야 되는데 id2: 심봤다 우아 id1: 이번에는 어~ 우리나라에서 언제부터 인삼을 키우기 시작했는지 재배농법에 대해서 좀 알아보도록 할까요? id1: 처음 언제 재배하기 시작했나요? id3: 삼국시대에서부터 문헌에 기록되기 시작했다고 보고가 되고 있습니다. id3: 그때에 인삼이라고 하면 대부분은 산속에서 자생하고 있는 지금 여러분들이 알고 있는 산삼 id2: 오 id3: 근데 이 산삼이 굉장히 귀한 약재로 인제 가치가 인정을 받기 시작을 하면서 이~ 각 지방에서는 나라에다가 조공으로 정해져서 보내야 되는 물량이 정해지기 시작을 한 거예요. id1: 음 id3: 그러다 보니까 백성들은 이 고갈되어 있는 산삼을 계속 바쳐야 되는데 id1: 어우 id3: 물량은 적고 할 수는 없으니 id1: 네네. id3: 그러면 백성들은 야반도주를 하게 되는 거예요. id3: 어떻게 하면 이제 우리는 일상생활 속에 묻게 올 수 있을까 함께 할 수 있을까 id3: 조선 시대로 거슬러 올라가게 되면 산에서 자생하고 있는 산삼의 씨앗을 따서 id5: 네. id3: 산 속에다 다시 고대로 뿌려서 자라나게 하는 요렇게 해서 키우기 시작했다는 보고가 있습니다. id5: 산삼을 인공적으로 키우는 게 정말 쉽지만은 않았을 것 같아요? id1: 그러게요. id4: 예. id4: 당연히 쉽지 않습니다. id5: 네. id4: 지금 토양이나 빛이나 온도 이러한 지형적 기후적 아니면 토양적 영향을 많이 받습니다. id4: 아주 예민한 식물이고요. id4: 또 재배기간이 사 년에서 육 년 정도로 깁니다. id4: 또 그 긴 사이에 병충해에도 좀 약해요. id4: 그러다보니까 이것은 누구나 쉽게 접근할 수 있는 작물이 아니고 많은 기술과 경험이 필요로 하죠. id4: 사실은 인제 인공 재배가 된 이후에 아마 대량생산이 우리나라 되었을 텐데요. id4: 조금 전에 제가 말씀드렸던 그런 대량 생산된 인삼을 인삼로드를 통해서 아마 동남아시아뿐만 아니라 전 세계적으로 우리 인삼이 아마 홍보가 되고 진출을 했던 걸로 제가 기억을 하고 있고요. id4: 아마 인삼 재배 역사상 id5: 네. id4: 인삼을 인공적으로 재배했다는 그 자체는 아마 가장 큰 인삼 재배 역사 중에서 가장 혁신적인 기술이지 않을까 저는 그렇게 생각합니다. id1: 만약에 그때 인공 재배에 성공을 하지 못했다면 우리가 지금처럼 이렇게 편하게 인삼을 먹을 수 없었겠어요? id5: 그렇네요. id4: 중요한 것은 그러한 전통적인 방식에 의해서 대량 생산되었던 것이 지금 이 시기에도 지금 현시점에도 그러한 방식이 그대로 계승되고 있다는 점이 주목할 필요가 있는 거거든요. id1: 그러니까 전통 그 재배 방식이 지금도 계속 이어져 오고 있다구요? id4: 네 네. id2: 자 그렇다면 여기서 한번 짚고 넘어가야겠죠. id2: 대체 우리 선조들은 어떻게 이 대량 생산에 성공을 해서 인삼을 재배해 왔는지 그 비밀을 지금부터 낱낱이 파헤쳐 보겠습니다. id2: 인삼의 숨겨진 비밀을 밝히기 위해서 찾은 이곳 전국에서 인삼이 가장 많이 모인다는 여기 바로바로 인삼의 성지 금산수삼센터입니다. id2: 제철을 맞아 때깔 좋은 인삼 id2: 아 도대체 전국적으로 인삼 생산량이 얼마나 되는 거예요? id6: 한 해에 전국 생산량은 한 이만 톤 이상이고요. id2: 우와 그렇게나 많이요? id2: 전국에서 생산되는 인삼의 칠십 퍼센트가 이곳 금산으로 모인다고 합니다. id2: 인삼 대량 생산의 비밀을 찾기 위해 제대로 온 것 같죠? id2: 어머니 혹시 그 인삼이 왜 이렇게 재배가 잘되고 유명한지 좀 비밀을 혹시 아시나요? id7: 그건 인삼밭으로 가서 물어보시고 id8: 네. id8: 벼 맞습니다. id2: 그쵸? id2: 그래 이거 누가 봐도 벼네. id2: 잠깐 깜짝이야. id2: 어이 누 누 누구 누구십니까? id8: 아 저는 인삼약초연구소 &name3&입니다. id8: 반갑습니다. id2: 인삼의 비밀 세 가지가 있다고 들었는데 고 비밀을 캐내는 게 저희 오늘 미션입니다. id2: 첫 번째 비밀 지금 시간이 없습니다. id2: 빨리 알려주세요. id8: 첫번째 비밀은? id2: 궁금하시죠? id1: 아우 빨리 알려주세요. id8: 순환농법입니다. id2: 어 순환농법 id2: 이름하야 순환식 이동농법 id2: 인삼을 한 번 재배한 땅에 인삼을 바로 다시 심지 않구요. id2: 다른 작물을 재배한 다음에 땅을 잠시 쉬게 두는 순환과정을 거치는 건데요. id2: 땅 스스로 지력을 회복해서 새로운 인삼을 심을 수 있도록 만드는 자연친화적인 농법입니다. id2: 아니 그냥 인삼만 그냥 쭉 심고 또 심고 심고 심고 이렇게 하면 안 되는 거예요? id8: 예. id8: 저도 그렇게 하고 싶은데 인삼을 수확하고 나면 인삼의 이병 잔재물도 있고 뿌리썩음병이라는 균이 생깁니다. id2: 뿌리썩음병은 땅 속에 오래 남아서 인삼을 공격하는데요. id2: 치료제가 따로 없는 무서운 병입니다. id2: 건강하게 자란 인삼들이 수확을 기다리고 있는데요. id2: 자 여기서 퀴즈 id2: 인삼은 수확 시기를 어떻게 할까요? id1: 글쎄요 인삼이 땅 위에서는 안 보여서 id8: 인삼은 가을이 되고 이 끝에 빨갛게 단풍이 들기 시작하면 수확을 할 수가 있습니다. id2: 귀하게 자란 인삼 실물 영접해 보실래요? id2: 어 그런데 박사님 제가 아까 그 수삼센터에서 봤던 삼에 비하면 좀 작은데 요거 몇 년생이에요? id8: 현재 이건 삼 년생 인삼이 되겠습니다. id8: 요 상태에서 한 일 년이면 더 키워가지고 사 년생 오 년생 육 년생 되면 수확을 합니다. id2: 그러면 예를 들어서 한 십 년생 뭐~ 이십 년생 이러면 굉장히 좋아지는 건가요? id8: 육 년생 이상이 되면 삼이 크면 병이 생깁니다. id8: 그래가지고 이제 더 이상 놔두면 썩어서 많이 없어져 가지고 보통 사 년생에서 사 년생이나 육 년생에서 수확을 하는 이유가 거기에 있습니다. id2: 자 그러면은 두 번째 비밀이 뭔지도 빨리 알려주시죠. id8: 예 두 번째 비밀은 바로 두 번째 비밀은 바로 요 종자에 있습니다. id2: 요 씨앗이 두 번째 비밀이라고요? id2: 오 자 박사님 저희가 있는 이곳이 어디인가요 박사님? id8: 여기는 인삼종자를 개갑시키는 개갑장입니다. id8: 아까 이 종자를 보셨죠? id2: 예. id8: 과육을 제거를 하면 요렇게 종자가 드러나게 됩니다. id2: 개갑이란 단어 생소하시죠? id2: 인삼 농가에서 오래전부터 전해 내려오는 비법인데요. id2: 인삼 종자의 발아율을 높이기 위해서 미리 종자의 껍질을 벌어지게 하는 과정입니다. id2: 백 일 정도 개갑과정을 거치게 되면 이렇게 껍질이 벌어집니다. id2: 이거 어떻게 사람이 또 일일이 그 관리를 할 수 있는 건가요? id8: 지금 다 자동화시설 돼서 자동으로 물을 주고 온도를 관리하는 그런 이제 시설로 가고 있습니다. id8: 온도는 십오 도에서 이십 도 수분은 십 프로에서 십오 프로 정도 필요하고요. id8: 고걸 이제 유지하기 위해서 아침저녁으로 물을 줘야 됩니다. id2: 자동화 시설이 돼 있지만 사람의 손길이 꼭 필요한 때가 있습니다. id2: 이 과정이 왜 필요한 겁니까? id8: 종자가 잘 있나 확인도 하고 위아래를 뒤집어줌으로써 위나 아래나 온도 그리고 수분을 다시 고르게 맞추기 위해서 이렇게 뒤집기 작업을 하는겁니다. id2: 박사님 덕분에 이 두 번째 비밀까지 이제 딱 알아냈는데 중요한 건 마지막 세 번째 비밀 요거 알아내야지 제가 이제 칼퇴할 수 있거든요 예. id2: 세 번째 비밀 뭔가요? id8: &name4&씨는 뜨거운 햇볕에 있으면 햇볕을 피하기 위해서 어떻게 하죠? id2: 선글라스를 끼거나 아니면 모자를 눌러 쓰거나 아니면 양산을 딱 펴서 햇볕을 피하죠. id8: 인삼도 마찬가지입니다. id8: 인삼도 그와 같은 방법이 있습니다. id2: 인삼밭 하면 떠오르는 저 검은 물결 인삼 대량 생산의 세 번째 비밀이 여기에 숨겨져 있다고 하는데요. id2: 과학적 사고를 하는 저 김 과장도 잘 모르겠더라고요. id2: 과연 이 검은 해가림막에는 어떤 과학적 원리가 숨겨져 있을까요? id2: 여러분도 궁금하지 않으세요? id1: 인삼밭 하면 가장 먼저 떠오르는 풍경 정말 검은 해 가림막이거든요. id1: 흔히 보던 풍경인데 이게 어떤 역할을 하는지는 사실 생각을 안 해봤던 것 같아요. id4: 해 가림막에는 여러가지 비밀이 숨겨져 있습니다. id4: 우리가 원래 인삼이라고 하면은 야생에서 산 속에서 자라던 산삼을 떠올릴 수가 있는데요. id2: 네. id4: 산삼은 자연스럽게 나뭇가지나 다른 나무들에 의해서 자연 차광이 됩니다. id1: 네 네. id4: 그러면 어떻게 이러한 자연 상태의 차광을 만들어 낼 수 있을까라고 고민 끝에 선인들은 나뭇가지나 볏짚 등을 이용해서 자연 소재죠? id1: 아 id4: 자연 소재를 이용해서 차광막 시설을 만들었던 겁니다. id1: 어 id4: 하지만 지금은 다른 제품으로 화학 제품으로 많이 바꼈긴 했습니다마는 사실상 차광막 시설의 해 가림막 시설의 구조 좀 높이나 아니면 그 각도는 옛날이나 지금이나 변함이 없습니다. id2: 오 id4: 즉 해 가림막 시설도 몇 백 년 동안 우리가 계승해 왔던 아주 중요한 과학적 원리라고 볼 수가 있겠습니다. id5: 그런데 자세히 보면 해 가림막이 살짝 비스듬하게 돼 있잖아요. id1: 맞아요 맞아요. id5: 이 모든 해 가림막이 일정한 각도로 열을 딱딱 맞춰서 세워져 있던데 거기에는 혹시 또 다른 비밀이 있는 건가요? id4: 네 숨겨져 있죠. id4: 아마 그 각도를 보시면 약간의 지형적이나 지역을 따라서 조금씩 다릅니다마는 대략 한 이십오 도 정도 됩니다. id4: 사실은 해 가림 시설을 두는 곳이 인삼 재배지에 당연히 두게 되잖아요. id5: 네. id4: 그믄 과연 인삼 재배는 어느 지역에 가장 잘될까가 중요합니다. id5: 네. id4: 거기에서의 원리는 또 향이라는 원리가 있습니다. id1: 향? id4: 예. id4: 방향 id1: 방향 id4: 예. id4: 인삼은 사실은 이제 반음지성 식물이기 때문에 요리 직사광성도 좋아하지 않고 아주 뜨거운 햇볕도 좋아하지 않습니다. id4: 햇볕이 덜 받던 북향이나 또 오후에 뜨거운 햇볕을 덜 받게 하는 동향으로 id1: 네. id4: 그래서 인삼밭은 북향이나 동향에 많이 설치를 하게 됩니다. id4: 거기에 이제 각도가 이십오 도 이렇게 설명이 되어 있는데요. id4: 그거 역시 그런 광선 햇볕하고 많은 연관성이 있습니다. id4: 아침에 부드럽고 선선한 바람을 많이 받게 하고 한낮에 뜨거운 직사광선을 피하게 만드는 부분이 있고요. id4: 또 한 가지는 뭐~ 당연한 일입니다마는 비가 내렸을 때 비가 인삼밭에 바로 떨어지지 않고 인삼 가에 떨어지게끔 각도를 정해놨는데요. id4: 이 각도 역시 몇 백 년 이상 지켜 왔던 우리 인삼 농업에 있어서는 지금도 그렇지만 후세에도 넘겨줄 만한 아주 훌륭한 유산이기도 합니다. id5: 그러니까 정리하자면 각도를 너무 크지도 작지도 않게 설계해서 인삼 재배에 필요한 만큼의 빛만을 공급해 줄려는거죠? id4: 그렇죠 그렇죠. id2: 아이 저 날 제가 사실 금요일이여가지고 불금 보낼려고 칼퇴 욕심이 딱 발동을 해 가지고 시간만 좀 더 있었으면 제가 각도 해 가림막 각도도 제대로 좀 보고 시간에 따라서 들어오는 빛의 양이 어떻게 바뀔지 이런 것도 좀 살펴봤어야 되는데 아 이것 좀 아쉽네요. id3: 그런데 여기서 저희가 놓치는 부분들이 또 있어요 과학적 그거가 id3: 이 해 가림막에 아까 이제 박사님께서 말씀해주신 것처럼 그 방향이라든지 빛을 차광하는 고런 기능 외에 바로 바람이 순환될 수 있는 구조라는 거예요. id5: 바람이요? id3: 네 특히 여름철에는 낮에 이 바람이 이 골짜기에서부터 쭉 올라가기 시작해서 정상 쪽으로 불게 됩니다. id5: 네. id3: 그렇게 되면 당연히 얘네들이 바람이 계속 순환되지 않고 멈춰 있는 형태가 돼요. id3: 이럴 때 해 가림 내부에는 이 넓은 쪽 아까 이십오 도라고 하셨으니까 넓은 쪽으로 바람이 들어와서 나갈 때는 좁은 쪽으로 출구 쪽으로 나가게 되는 거예요. id3: 그러면 얘는 저기 앞에 있는 거에서 저 끝에 있는 데까지 계속 바람에 통풍이 되는 겁니다. id1: 와아 id3: 이런 식으로 순환이 되다 보니까 해가림 시설 안에 있는 자체 온도가 계속 상승되는 것을 억제시켜줄 수 있는 효과를 가지게 되는 게 이 해가림막의 또 다른 하나의 과학적인 숨겨진 비밀로 id1: 오 백년간 이어져 온 이런 인삼 전통 재배 방식이 세계적으로 가치를 인정받았다고 해요. id1: 예. id4: 세계의 농업 유산 이야기를 하시는 것 같은데요. id4: 저는 세계 농업 유산 이야기를 들으면 기쁜 마음이 나오긴 하지만 또 한 번의 실패를 했던 기억도 있기 때문에요. id4: 좀 아쉬운 감도 있습니다만 결국은 세계 농업 유산으로 우리나라 금산 지역에 인삼 농업이 지정이 되었습니다. id4: 당시 이천십육 년에 처음 도전장을 냈을 때는 id5: 네. id4: 세계 농업 유산에도 여러 가지 기준들이 있는데요. id4: 그런 기준들에 좀 부합하지 못했고 어떤 부분에서는 많이 미흡했기 때문에 어~ 심사위원들 전원 일치 불합격 판단을 해서 id5: 아이고 id4: 뭐~ 탈락이라는 id1: 음 id4: 아주 쓰다쓴 고배를 마신 적도 있습니다. id4: 그런데 그 당시 저뿐만 아니라 금산군에 계시는 분들 농림축산식품부에 계시는 분들이 너무 안타까워했죠. id1: 그쵸 id4: 우리 나라의 자존심 하면 고려인삼인데 id5: 그렇죠. id4: 이것이 세계 농업 유산이 안되면 무엇이 뭐가 되냐라는 해서 다시 한 번 재도전하는 것으로 가닥을 잡고 다시 한 번 준비를 했습니다. id4: 사실은 실패했던 이유는 여러 가지는 있었습니다마는 아무래도 세계 농업 유산의 심사를 하시는 분들은 일곱 명이신데 다 외국분이십니다. id4: 이해하기 좀 어려운 부분이 있죠. id1: 네. id4: 그래서 두 번째 도전할 때는 저를 포함해서 몇 분이 직접 외국에 계시는 심사위원들을 찾아 뵙고 설명을 드리고요. id4: 일부 심사위원분들은 직접 우리나라에 와서 인삼밭에 같이 가면서 현장에서 이런 것들이 수 백 년 동안 내려왔던 가치였고 수 백 년 동안 내려왔던 전통적인 과학이었습니다라고 그렇게 어느 정도 이해를 시킨 끝에 이천십팔 년 칠월에 만장일치로 id5: 오 id4: 금산 인삼을 세계농업유산으로 등재를 시켰는데요. id1: 예. id4: 저는 무엇보다도 세계 심사위원분들에게 id2: 네. id4: 우리가 전통적으로 내려왔던 여러 가지 지식 체계들 id5: 네. id4: 전통적인 방식들 전통적인 과학들을 그분들이 이해를 하시고 그것을 세계농업유산으로 인정해줬다는 부분에 가장 뿌듯한 생각이 듭니다. id1: 네 우리의 인삼이 인삼로드를 거쳐서 실크로드로 이어지고 또 동아시아를 넘어서 유럽까지 진출할 수 있게 된데에 어떤 기술이 바탕이 됐다라고 했죠 두 분? id5: 인공 재배 기술을 통한 대량 생산 이게 중요하죠. id1: 맞습니다 맞아요. id1: 독창적인 재배 기술 말고도 한 가지 비결이 더 있다고 해요. id1: 뭘까요? id2: 아무래도 당연히 그 인삼을 기르는 이 농부들의 사랑과 관심과 애정과 보살핌 뭐 이런 것 아닐까요? id1: 우리 박대리는요? id5: 산삼이 몸에 좋고 또 아픈 사람들도 치유하고 또 나라에서 대대적으로 홍보하고 이런 문화적인 홍보가 잘되지 않았습니까? id2: 그 당시에 바이럴마케팅 id5: 네 이렇게 자 털어 id1: 저 박사님 두 분의 의견 중에서 정답이 있나요? id4: 두 분 말씀에 정답이 감춰져 있기도 하고 또 약간은 그런 맥락에서 또 벗어나긴 한데요. id2: 빨리 알려 주세요. id4: 그 하나의 비법은 홍삼입니다. id2: 홍삼? id4: 홍삼에도 우리나라의 전통적인 지혜와 지식 그리고 과학적 원리가 숨겨져 있습니다. id2: 에 아니 그 옛날에도 홍삼이 있었다는 얘긴가요? id4: 홍삼의 제조 역사가 얼마 안 됐다고 생각하시는 분들 많이 계실텐데요. id4: 의외로 홍삼의 역사는 천 년 가까이 긴 역사를 가지고 있습니다. id4: 우리가 홍삼이라는 이야기가 처음 나온 것이 고려 인종 때 천백이십삼 년에 고려의 생활상을 적어놓은 고려도경이라는 사료가 있는데요. id4: 그 사료 속에 홍삼의 제조법이 등장을 합니다. id4: 물론 고려 시대 때는 홍삼이라는 표현을 쓰지 않고 익히다라는 숙 자를 써서 숙삼이라고 표현을 했고요. id4: 홍삼이라는 것은 조선 시대 넘어와서 홍삼이라고 표현된 걸로 알고 있습니다. id4: 그럼 왜 우리나라가 홍삼을 만들었느냐는 그 이유는 역시 수삼 상태로서는 상온에 두었을 때 변질되거나 부패되기 쉽습니다. id4: 그래서 아주 오랜 기간 인삼이 가지고 있는 고유한 성분을 유지한 채 오랜 기간 보관 할 수 있는 방법이 없을까 그런 궁리 끝에 우리 선조들이 만든 것이 수삼을 찌고 건조하는 과정 속에서 홍삼이라는 것이 탄생하게 됩니다. id4: 사실상 홍삼은 지금 현재 어떻게 보면 이십 년 정도 길게 보관이 될 수 있을 정도로 어떻게 보면 인삼 가공의 백미라고 할 수 있습니다. id4: 사실 홍삼에 대해서 홍삼을 제조하는 과정은 수삼을 찌고 건조하는 과정을 되풀이 하는데요. id4: 그러면서 색깔이 갈변화가 됩니다. id4: 갈변화된다는 의미는 갈색으로 변해서 우리가 흔히 홍삼을 갈색 좀 더 진한 갈색으로 이렇게 표현을 하고 있고요. id4: 사실 홍삼은 그러한 찌고 건조하는 과정을 통하면 생물학적 미생물학적으로 볼 때 불활성화된다고 합니다. id4: 불활성화가 인삼을 오랜 기간 보존할 수 있는 기본적인 원리가 된다고 볼 수가 있고요. id4: 흔히 수삼과 홍삼을 비교했을 때 홍삼이 덜 쓰다라는 표현을 많이 해주시는데요. id4: 그건 과학적으로 맞는 말씀입니다. id4: 수삼을 찌고 건조하는 과정을 통하면 그 속에 포함되어 있던 전분이 그러한 당분들이 당하가 되는데요. id4: 그러면 약간 단맛이 나는 감미 성분이 나타납니다. id4: 그리고 또 구수한 맛을 내는 성분도 새롭게 나타나는데요. id4: 그래서 우리가 홍삼에는 특이한 맛과 향이 있다고들 합니다. id4: 그리고 마지막 하나의 특징은 사실은 인삼에는 뿌리에도 사포닌 성분이 많이 있습니다만 껍질에 많이 포함되어 있습니다. id4: 사실 홍삼을 만들 때에는 수삼을 껍질을 벗기지 않은 채 통채로 우리가 그것을 찌고 건조하는 과정을 하는데요. id4: 그렇다보니까 인삼이 가지고 있는 좋은 성분들이 가히 안정화 상태로 오랜기간 보관할수 있는 것이죠. id4: 아마 그러한 오랫동안 보관할수 있는 선조들의 기술 아니면 그러한 지식들이 아마 오늘날까지 전승되고 있다는 점은 매우 유익한 과학적 정보가 아닐까 싶습니다. id4: 사실은 이러한 우리나라 고려인삼의 어떤 명성이 높게 된 이유는 홍삼이라는 가공품을 만들어서 오랜 기간 보관했던 점이라고 생각합니다. id4: 이런 것들이 선인들이 만들어냈던 지혜의 산물이지 않을까 생각합니다. id1: 홍삼이 그렇게 오랜 역사를 가졌다니까 참 놀랍기도 한데요. id1: 홍삼 얘기가 나와서 말인데 인삼에도 종류가 여러 가지가 있잖아요. id5: 그렇죠. id5: 언뜻 떠오르는 것만 해도 생삼 그리고 방금 말씀하신 홍삼 그리고 흑삼이라고 검은 빛깔을 띠는 인삼도 있더라고요. id2: 오늘 의상도 딱 흑삼이잖아 id5: {laughing} id3: 저희가 인삼은 그 가공 방법에 따라서 여러 가지로 구분이 됩니다. id5: 네. id3: 특히 이제 열을 가하거나 증숙하는 과정에 있어서의 수분의 함량이 얼마나 있느냐 없느냐에 따라서 지금 보시는 것처럼 얘가 이제 수삼이라고 합니다. id2: 아 수삼 id3: 수삼인데 보시면 연질이 조직이 되게 말랑말랑해 보이죠 그죠? id1: 네. id3: 보시면 인삼에 수분의 함량이 칠십 프로 이상을 포함하고 있는 게 이 수삼이라고 보시면 됩니다. id3: 이 증숙을 하지 않고 껍질만 벗겨 직접 말리는 거 약간 (()) 나타내죠. id3: 얘는 백삼이라고 합니다. id1: 백삼 id3: 저희가 무역을 하는 데 있어서 저장에 관련되어 있어서 그 방법을 찾았던 게 바로 이 가공 방법입니다. id3: 수분을 십오 프로 이내로 낮춰주는 가공이 바로 백삼 홍삼 흑삼이 되겠는데요. id3: 여러분들이 제일 잘 아시는 홍삼 약간 붉은 빛을 띄면서 굉장히 예쁘게 (()) id3: 여러분들이 가장 접하기 쉬운 거 id2: 그렇죠. id3: 대신에 홍삼이 몸에 좋다 흑삼이 뭐가 더 몸에 좋다라고 표현은 못 하는데 여러분들이 드시기에 약간 더 달고 쓴 맛의 양이 좀 적고 하는 게 바로 이제 이런 홍삼류로 대체를 할 수가 있고요. id3: 최근의 연구에 따르면 이렇게 거의 좀 까매요. id3: 완전히 흑갈색의 형태를 나타내는데 홍삼은 찌고 말리고 한 번 정도 한다라고 하면 흑삼은 적어도 세 번 이상의 반복을 하게 됩니다. id3: 네. id3: 그런데 이제 거의 아홉 번 찌고 말린다고 해서 구증구포 많이 들어보셨죠? id3: 그러다보면 어~ 태우니까 몸에 안 좋은 거 아니야 이런 걱정이 많이 되는 거죠. id1: 네. id3: 그런데 저희가 만들어 낸 이 가공식품 즉 가공 인삼에는 이런 유해 성분이 없는 안전하게 가공을 하고 있는 것으로 나타나고 있어서 여러분들이 편하게 이용을 하시면 될 것 같아요. id2: 궁금한 게 이제 성분 가공 방법에 따라서 성분도 좀 바뀌거나 달라지거나 추가되거나 없어지거나 이런 게 있는지 id3: 저희가 수삼 형태에 있는 성분을 그대로 인삼에 수삼의 향이라든지 성분이 몸에 좋은 성분들이 그대로 가지고 있는 형태라고 하면 열을 가하거나 찌거나 수증기를 찌게 되면 수삼에 있는 성분이 일부 다른 성분으로 변하게 돼요. id3: 이 성분들이 특히 백삼에서는 말로닐 진세노사이드라고 하고요. id3: 흑삼 홍삼에는 알지쓰리가 그 다음에 흑삼에서는 알케이원이라고 하는 특이 성분들이 서로 생성되거나 다시 증가가 됩니다. id3: 여기에 각각의 진세노사이드 즉 인삼의 사포닌이 진세노사이드라고 하는데 진세노사이드들이 각각의 약리 작용을 나타내는 거예요. id3: 그래서 인제 저희가 건강 식품으로 먹는 데 아주 유용하게 부담 없이 드실 수 있는 것들이 인삼가공제품이라고 할 수 있어요. id1: 네. id1: 과학으로 보는 세상 씨 시청자 여러분의 영상메세지가 도착했습니다. id1: 평소에 인삼에 관해 궁금했던 점들을 좀 보내주셨거든요. id1: 뭐가 궁금하세요? id10: 인삼 고를 때 크고 통통한 인삼을 사는 편인데 좋은 인삼 고르는 방법 좀 알려주세요. id9: 제가 몸이 허할 때마다 삼계탕을 자주 해먹는데 문득 그런 생각이 들더라고요. id9: 왜 삼계탕에는 인삼이 들어갈까요? id1: 네 자 첫 번째 질문부터 한 번 풀어보도록 하죠. id1: 인삼은 크고 통통한 게 좋다. id1: 좋은가요라고 물어봐 주셨습니다. id1: 어떤가요? id4: 사실 인삼은 버릴 게 없습니다. id4: 작고 크고 간에 약리적인 효과는 똑같고요. id5: 네. id4: 하지만 그래도 그중에서 좋은 인삼을 고르신다고 하면 제가 한 가지 가지고 나왔는데요. id4: 인삼은 크게 세 가지 부분으로 구별이 됩니다. id5: 네. id4: 머리 부분이라고 하는 뇌두 부분이 있고요. id4: 몸통 부분이 있고 뿌리 부분이 있습니다. id4: 그래서 요 세 개의 부분이 명확하게 구별이 되는 것이 좋다고 하고요. id1: 아 id4: 물론 현재 이제 수삼 같은 경우는 수분이 있기 때문에 아주 딱딱하지는 않습니다마는 그래도 이렇게 만져보셨을 때 약간 재질이 단단한 부분이 좋습니다. id4: 하나 더 귀중한 우리가 인삼으로 생각하는 것이 인삼의 사람 인 자처럼 요 아래 뿌리 부분이 요렇게 다리 두 개를 양다리를 벌려서 사람 모양처럼 생긴 인삼은 더욱 더 비싸게 팔리고 많은 소비자들이 선호하는 부분입니다. id1: 네. id2: 이 지금 들고 계신 인삼도 그렇고 제 것도 그렇고 보면 잔뿌리들이 많죠. id5: 네 그러네요. id2: 그런데 이게 잔뿌리들이 많은 게 좋은건지 아니면 없는 게 좋은 건지 요것도 좀 알려주시죠. id4: 당연히 뭐든지 많은 게 좋 id2: 다다익선 id4: 예 당연히 잔뿌리도 중요한 역할을 합니다. id4: 오히려 인삼의 중요한 성분 중에 하나가 사포닌인데요. id4: 인삼의 사포닌은 사실은 그리스어로 거품을 낸다. id4: 비누의 어원입니다. id1: 어 id4: 그래서 화학 구조적으로 얘기하면 이제 비단 부분에 포도당이나 과당 등 이러한 당질들이 결합된 배당체라고 하는데요. id4: 사실은 인삼 외에도 더덕이나 도라지 그 외 한 칠백여 종의 식물에도 사포닌 성분이 들어 있습니다. id4: 하지만 왜 인삼 사포닌이 우리 인간 몸에 더 좋을까라는 부분은 그 인삼에 들어있는 사포닌은 저 어독성이라든지 어떤 그~ 적혈구를 파괴시키는 그것을 이제 용혈 독성이라고 표현하는데요. id4: 그런 용혈 독성이 포함되어 있지 않습니다. id5: 아 id4: 전혀 여기에는 포함되지 않기 때문에 우리 사람 인체에 아무런 해가 없는 거죠. id1: 예. id4: 그렇기 때문에 인삼 고르실 때는 오히려 뿌리가 잔뿌리가 많은 것이 사포닌 함량이 많다. id4: 그래서 반드시 그 부분을 좀 확인해서 구입하셨으면 좋겠습니다. id1: 두 번째 질문인데요. id1: 이런 생각을 좀 안 해봤어요. id1: 삼계탕에는 왜 인삼이 들어가나요? id3: 천구백사십 년대 넘어서기 시작을 하면서 인제 그래도 경제가 조금씩 살아나면서 시장이 형성되면서 시장에서 삼과 닭을 넣은 탕 그래서 삼계탕이 아니라 계삼탕 id5: 계삼탕 id3: 네. id3: 닭의 닭백숙에 삼발을 넣었어요. id3: 그래서 계삼탕으로 불려졌고요. id3: 천구백육십 년대를 넘어서기 시작을 하면서 육이오가 끝나고 경제가 조금 부흥이 되면서 가전제품 즉 냉장고가 보급이 되기 시작을 하면서 인삼을 보관할 수 있는 기간이 늘어나기 시작을 하는 거예요. id3: 그러다 보니까 닭백숙이라고 하는 닭고기에 삼을 통째로 넣기 시작하는거죠. id1: 음 id3: 이제는 계삼탕 왠지 삼이 닭한테 지는 느낌 그런데 경제적으로 더욱 귀한 약재로 사용되고 삼이잖아요 인삼이잖아요? id1: 네. id3: 그래서 삼계탕 인삼의 귀한 인지도를 늘리자. id3: 삼계탕으로 불려지게 됐고요. id3: 특히 삼계탕에 삼을 넣으면 저는 언제부터 넣었을까보다는 왜 넣었을까? id1: 네. id3: 응 왜 닭에다가 삼을 넣었을까? id5: 그렇죠. id3: 예. id3: 많이 있을 텐데 id1: 네. id3: 아마도 얘는 인삼의 특유의 향이 닭에서 날 수 있는 누린내를 이렇게 억제해 줄 수 있다라고도 하고요. id3: 또 하나는 인삼과 고단백질인 닭고기를 같이 섭취하게 되면 신진대사가 촉진이 되고 아까 말씀하신 기력 회복 원기 회복이 돼서 여름철 보양식인 대표 음식으로 지금 현재 삼계탕이 되어 있지 않았나 그렇게 이렇게 생각하고 있습니다. id1: 네. id1: 천오백 년 전부터 국내는 물론이고 세계 곳곳에서도 인정을 받아 온 우리 인삼 그런데 최근에 이 인삼이 위기를 겪고 있다고 하더라구요. id4: 인삼 농가의 위기라고 할까요? id4: 기후 변화입니다. id4: 그~ 농촌진흥청에서 발표한 자료를 보면 이천이십 년 기준으로 우리나라 전국 면적의 국토 면적의 약 칠십팔 퍼센트는 인삼 재배가 가능하다. id1: 아 id4: 하지만 이천육십 년에는 이십삼 퍼센트로 급감을 할 거라고 예측을 하고 있고요 id4: 또 이천구십 년이 되면은 채 오 퍼센트만 가능할 것이다. id4: 물론 그 사이에 어떤 기술 변화가 일어날지는 모르겠습니다마는 지금처럼 지구온난화 기후 변화가 지속된다고 하면 우리 다음 다다음 세대에서 인삼밭을 찾기는 어쩌면 어려워질 수도 있는 위기에 봉착한 것은 사실입니다. id5: 우리가 위기에 강한 대한민국 아닙니까? id5: 당연히 가만히 지켜보지만은 않겠죠. id5: 이십일 세기 신 인삼로드를 열기 위한 움직임이 있겠죠? id3: 네. id3: 있습니다. id3: 전세계적으로 보면 음~ 소리 없는 전쟁 우리 농업 쪽에서는 즉 종자 전쟁이라고 표현을 하는데요. id3: 인삼도 마찬가지예요. id3: 어떠한 우수한 품종을 육성을 해내서 계량을 하고 얘를 산업화시킬 수 있는 데 노력을 해줘야 하는데 현재 개발되어 있는 게 이십여 종의 품종이 있고 이에 대응해서 앞으로는 어떠한 병충해에 강한 저항성을 가지고 있는 품종이 id3: 또 하나는 어떠한 고온이라든지 고광이라든지 염분이 버텨낼 수 있는 내인성이 강한 품종이라든지 또 하나는 한 재배 면적당 많은 품종이 많은 수량이 나올수 있는 그런 품종 또 하나 형태학적으로 사람인 모양을 닮은 아주 퀄리티는 있는 정말 우리나라가 (()) 인삼이라고 하는 이 형태를 가지고 있는 품종 이러한 다양한 연구들이 있고 꼭 개발되고 연구가 진행되어야 된다고 생각되고 있습니다. id4: 추가적으로 한 가지 더 말씀드리고 싶은 것은 보통 다른 작물처럼 벌써 유리온실에 스마트팜에 사 차 산업혁명의 여러가지 기술들이 도입된 작물들이 많이 있지만 id1: 네. id4: 인삼은 사실 기술력이 부족하다기보다는 인삼 재배 특수성 때문에 조금은 다른 작물의 못 미치는 건 사실입니다. id4: 하지만 한 가지 대표적으로 요즘의 좀 변화는 그 해 가림 시설은 사실은 많은 노동력이 요합니다. id2: 그렇죠. id4: 그러다보니까 지금 일부 이제 개발이 됐고 보급되고 있는 것이 긴 터널형으로 우리 하우스의 긴 터널형을 아마 상상해 보시면 될 텐데요. id4: 그 안에 이제 인삼을 재배하는 겁니다. id4: 그러면서 이제 다른 차광막 시설도 약간의 청색 계열의 또 다른 신소재로 만들어주고 있고요. id4: 물을 줄 수 있는 간수 시설까지 그 안에 포함되어 있는 것들이 이제 터널형 인삼 재배 방식으로 보급되고 있는데요. id1: 네. id4: 그래도 인삼만이 지켜왔던 수 백 년 동안의 어떤 전통적인 과학 이런 원리도 현대적인 과학과 좀 맞물려서 서로 공존해 나갔으면 하는 바람이 있습니다. id1: 네.
'''
target = """
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
# token_test = tokenizer(target, return_tensors="pt")
# print([tokenizer.decode(t) for t in token_test[:100] ])
# print(token_test["input_ids"].shape)

# if os.path.exists("/nas/conan/quantized_model.onnx"):
#     print("Exsisting Model found")
# else:
#     print("Generate onnx Model")
#     with torch.no_grad():
#         torch.onnx.export(
#             model=model,
#             args=tuple(token_test.values()),
#             f="/nas/conan/quantized_model.onnx",
#             input_names=["input_ids", 
#                         #  "attention_mask"
#                          ],
#             output_names=["logits"],
#             dynamic_axes={'input_ids': {0: 'batch_size', 1: 'sequence'}, 
#                         #   'attention_mask': {0: 'batch_size', 1: 'sequence'}, 
#                           'logits': {0: 'batch_size', 1: 'sequence'}}, 
#             do_constant_folding=True, 
#             opset_version=16,
#         )
#     if not os.path.exists("/nas/conan/int8_quantized_model.onnx"):
#         print("Model Quantize")
#         quantized_model =  quantize_dynamic(
#             model_input="/nas/conan/quantized_model.onnx", 
#             model_output="/nas/conan/int8_quantized_model.onnx",
#             weight_type=onnx.TensorProto.INT8, 
#             use_external_data_format=True)

user_message ={
    "role": "user",
    "content": f"{target}"
}

# print(tokenizer.apply_chat_template([user_message], tokenize=False, return_tensors="pt"))

# q_session = ort.InferenceSession("/nas/conan/int8_quantized_model.onnx", 
#                                  providers=["CPUExecutionProvider"])
# q_model = ORTModelForCausalLM(model=q_session, config=model.config, use_io_binding=False, use_cache=False)

# core = ov.Core()
# ov_model = core.read_model("/nas/conan/quantized_model.onnx")
# ov_model.reshape({model_input.any_name: ov.PartialShape([1, '?']) for model_input in ov_model.inputs})
# ov_model = OVModelForCausalLM(model=ov_model, config=model.config, use_io_binding=False, use_cache=False)

q_model = ORTModelForCausalLM.from_pretrained("WiseIntelligence/open_llama_3b_v2-Optimum-ONNX", 
                                              cache_dir=os.getenv("HF_HOME"), 
                                              use_cache=False, use_io_binding=False)
q_tokenizer = AutoTokenizer.from_pretrained("WiseIntelligence/open_llama_3b_v2-Optimum-ONNX", 
                                            cache_dir=os.getenv("HF_HOME"))
q_tokenizer.pad_token=q_tokenizer.eos_token if q_tokenizer.pad_token is None else q_tokenizer.pad_token
q_tokenizer.pad_token_id = q_tokenizer.encode(q_tokenizer.pad_token,)[0]

ov_model = OVModelForCausalLM.from_pretrained("OpenVINO/open_llama_3b_v2-int8-ov", 
                                              cache_dir=os.getenv("HF_HOME"))
ov_tokenizer = AutoTokenizer.from_pretrained("OpenVINO/open_llama_3b_v2-int8-ov", 
                                             cache_dir=os.getenv("HF_HOME"))
ov_tokenizer.pad_token=ov_tokenizer.eos_token if ov_tokenizer.pad_token is None else ov_tokenizer.pad_token
ov_tokenizer.pad_token_id = ov_tokenizer.encode(ov_tokenizer.pad_token,)[0]


@inference_timer
def test_inference(model, tokenizer, input_text):
    # llm_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
    user_message = {
        "role": "user",
        "content": input_text
        }
    tokenizer.pad_token_id = tokenizer.encode(tokenizer.pad_token,)[0]
    template = tokenizer.apply_chat_template(
            [user_message],
            return_tensors="pt",
            tokenize=True, )
    # tokenized = tokenizer(
    #         template,
    #         return_tensors="pt",
    #         max_length=2538,
    #         padding="max_length",
    #         truncation=True)
    return model.generate(
        # streamer=TextStreamer(tokenizer=tokenizer),
        generation_config=GenerationConfig(max_new_tokens=50,
                                           use_cache=True,),
        inputs=template)
    # return llm_pipeline(template)

# print(test_inference(model, tokenizer, user_message["content"]))
print(test_inference(q_model, q_tokenizer, user_message["content"]))
print(test_inference(ov_model, ov_tokenizer, user_message["content"]))
