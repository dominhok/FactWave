# FactWave

Multi-Agent-Based Fact-check Solution

## 프로토타입 실행

간단한 팩트체크 프로토타입을 실행하려면:

```bash
python factwave_prototype.py
```

## 특징

- **5개 전문 에이전트**: Academic, News, Logic, Social, Super Agent
- **3단계 프로세스**: 초기 분석 → 토론 → 최종 종합
- **Solar-pro2 LLM** 기반
- **CrewAI 프레임워크** 활용

## 에이전트 역할

1. **Academic Agent (30%)**: 학술적 관점에서 분석
2. **News Agent (35%)**: 언론 보도 패턴 기반 검증
3. **Logic Agent (20%)**: 논리적 일관성 검증
4. **Social Agent (15%)**: 사회적 맥락 분석
5. **Super Agent**: 모든 분석 종합 및 최종 판단

## 사용 예시

```
🔍 FactWave Prototype
Multi-agent fact-checking system powered by Solar-pro2

Enter a statement to fact-check (or 'quit' to exit):
> 2024년 한국의 출산율이 0.7명이다
```

시스템이 각 에이전트의 분석을 거쳐 최종 팩트체크 결과를 제공합니다.