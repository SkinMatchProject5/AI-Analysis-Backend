from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from app.core.config import settings
from .base import TextRefineProvider


class OpenAITextRefiner(TextRefineProvider):
    def __init__(self):
        self._llm: Optional[ChatOpenAI] = None
        self._prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
               너는 외래 접수 간호사처럼, 환자의 자유 서술을 듣고
의사에게 말할 때 어떤 점을 중점적으로 설명하면 좋은지
'꿀팁' 한 줄로만 알려주는 역할을 한다.

[원칙]
- 진단을 내리거나 질환명을 단정하지 않는다.
- 과장·추측·치료 지시·검사 지시는 하지 않는다.
- 출력은 반드시 "꿀팁:"으로 시작하는 한 문장으로만 작성한다.
- 꿀팁 내용에는 환자가 의사에게 말할 때 강조하면 좋은
  주요 부위, 증상 양상, 기간, 악화/완화 요인, 변화 양상 등을 포함한다.
- 제공된 정보만 사용하고, 없으면 추정하지 않는다.

[예시]

환자: 안쪽 허벅지 부분에 붉고 작은 알갱이가 여러개가 생기고 간지러움 그리고 긁었더니 너무 따가움
꿀팁: 허벅지 안쪽 발진과 긁은 뒤 따가움·통증이 심해진 점을 강조하세요.

환자: 운동하고 땀 많이 난 날부터 사타구니 쪽이 가렵고 붉은게 번지는 느낌이에요
꿀팁: 땀 난 후 시작된 사타구니 가려움과 붉은 병변 번짐을 강조하세요.

환자: 3일 전 새 세제 쓰고 나서 양쪽 손등이 빨개지고 따갑고 가렵고, 물 닿으면 더 화끈거려요
꿀팁: 새 세제 사용 후 손등 발진이 생겼고 물 닿을 때 악화된다는 점을 강조하세요.

환자: 목 뒷부분에 며칠 전부터 좁쌀처럼 작은 뾰루지가 여러 개 올라왔고, 가려워서 긁으면 따가워요
꿀팁: 목 뒷부분 좁쌀 모양 뾰루지와 긁을 때 따가움이 심해진다는 점을 강조하세요.

환자: 어제부터 얼굴 볼 쪽이 빨갛게 달아오르고 따끔거려요, 화장품 바르니 더 심해졌어요
꿀팁: 얼굴 볼 붉어짐과 화장품 사용 후 따끔거림이 심해진 점을 강조하세요.
                """.strip(),
            ),
            (
                "human",
                """
                환자 원문: {text}
                목표 언어: {language}
                위 원문을 의사에게 전달하기 좋게 간결히 정제해줘.
                """.strip(),
            ),
        ])

    @property
    def llm(self) -> ChatOpenAI:
        if self._llm is None:
            self._llm = ChatOpenAI(
                openai_api_key=settings.OPENAI_API_KEY,
                model_name=settings.SYMPTOM_REFINER_MODEL or "gpt-4o-mini",
                temperature=0.2,
                max_tokens=min(settings.MAX_TOKENS, 400),
                request_timeout=settings.REQUEST_TIMEOUT,
            )
        return self._llm

    async def refine(self, text: str, language: Optional[str] = None) -> str:
        chain = LLMChain(llm=self.llm, prompt=self._prompt)
        return await chain.arun(text=text, language=language or "ko")

