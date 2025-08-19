import { useState, useRef, useEffect } from 'react'

function Discussion({ onSaveResult, onSaveConversation, context, onClearContext }) {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasStarted, setHasStarted] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const wsRef = useRef(null)
  const sessionIdRef = useRef(null)
  const [currentQuestion, setCurrentQuestion] = useState('')
  const [agentResults, setAgentResults] = useState({})
  const [allResponses, setAllResponses] = useState([]) // 11개 모든 응답 저장
  const [responseCount, setResponseCount] = useState(0) // 응답 개수 추적
  const [expectedResponses] = useState(11) // 예상 응답 수
  const messageQueueRef = useRef([]) // 메시지 큐
  const processingRef = useRef(false) // 처리 중 플래그
  const [isViewingHistory, setIsViewingHistory] = useState(false) // 저장된 대화 보기 모드
  const [isInitialLoad, setIsInitialLoad] = useState(true) // 초기 로드 체크
  const messagesEndRef = useRef(null) // 스크롤 끝 참조

  const [activeAgents, setActiveAgents] = useState([
    { id: 'news', name: 'News', avatar: '📰', active: true },
    { id: 'academic', name: 'Academia', avatar: '🎓', active: true },
    { id: 'logic', name: 'Logic', avatar: '🤔', active: true },
    { id: 'social', name: 'Social', avatar: '👥', active: true },
    { id: 'statistics', name: 'Statistics', avatar: '📊', active: true }
  ])
  
  const [shouldAnimate, setShouldAnimate] = useState(false)
  const containerRef = useRef(null)

  // 에이전트 설정
  const agentConfig = {
    'academic': { name: 'Academia', avatar: '🎓' },
    'news': { name: 'News', avatar: '📰' },
    'statistics': { name: 'Statistics', avatar: '📊' },
    'logic': { name: 'Logic', avatar: '🤔' },
    'social': { name: 'Social', avatar: '👥' },
    'super': { name: 'Super Agent', avatar: '🔮' }
  }

  // 스크롤을 맨 아래로 이동하는 함수
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // 메시지가 업데이트될 때마다 스크롤 (라이브러리에서 불러온 경우 제외)
  useEffect(() => {
    // 저장된 대화를 보는 중이거나 라이브러리에서 막 불러온 경우는 스크롤하지 않음
    if (!isViewingHistory && hasStarted && !context?.isConversation) {
      scrollToBottom()
    }
  }, [messages])

  // 애니메이션 필요성 체크 함수
  const checkIfAnimationNeeded = () => {
    if (containerRef.current) {
      const containerWidth = containerRef.current.offsetWidth
      // 각 아이콘 너비(144px) + 간격(24px) = 168px, 5개 = 840px
      const requiredWidth = 5 * 168 - 24 // 마지막 간격 제외
      setShouldAnimate(containerWidth < requiredWidth)
    }
  }

  // 화면 크기 감지하여 애니메이션 필요성 판단
  useEffect(() => {
    checkIfAnimationNeeded()
    window.addEventListener('resize', checkIfAnimationNeeded)
    
    return () => window.removeEventListener('resize', checkIfAnimationNeeded)
  }, [])

  // 에이전트 선택 UI가 표시될 때 애니메이션 체크
  useEffect(() => {
    if (!hasStarted && !isViewingHistory && (!context || !context.isConversation)) {
      // 약간의 지연 후 체크 (DOM이 완전히 렌더링된 후)
      setTimeout(checkIfAnimationNeeded, 100)
    }
  }, [hasStarted, isViewingHistory, context])

  // 저장된 대화 불러오기
  useEffect(() => {
    if (context && context.isConversation && context.fullData) {
      console.log('저장된 대화 불러오기:', context.fullData)
      setIsInitialLoad(false) // 라이브러리에서 온 경우
      loadSavedConversation(context.fullData)
    } else if (!context && isInitialLoad) {
      // 초기 로드이고 context가 없으면 토론 시작 창
      setIsInitialLoad(false)
    }
  }, [context])

  // 컨텍스트 메뉴에서 선택된 텍스트 처리를 위한 상태
  const [pendingFactCheck, setPendingFactCheck] = useState(null)

  // 컨텍스트 메뉴에서 선택된 텍스트 처리
  useEffect(() => {
    console.log('[Discussion] Component mounted, checking for Chrome Extension API...')
    
    // Chrome Extension API 체크
    if (typeof chrome !== 'undefined' && chrome.runtime) {
      console.log('[Discussion] Chrome API available, checking for pending fact check...')
      
      // 컴포넌트 마운트 시 pending fact check 확인
      const checkPendingFactCheck = () => {
        try {
          chrome.runtime.sendMessage({ type: 'GET_PENDING_FACT_CHECK' }, (response) => {
            if (chrome.runtime.lastError) {
              console.log('[Discussion] Chrome runtime error:', chrome.runtime.lastError)
              return
            }
            console.log('[Discussion] Response from background:', response)
            if (response && response.text) {
              console.log('[Discussion] Found pending fact check text:', response.text)
              setPendingFactCheck(response.text)
            } else {
              console.log('[Discussion] No pending fact check found')
            }
          })
        } catch (error) {
          console.log('[Discussion] Failed to check pending fact check:', error)
        }
      }

      // 즉시 확인
      checkPendingFactCheck()
      
      // 1초 후에도 한 번 더 확인 (타이밍 이슈 대응)
      setTimeout(checkPendingFactCheck, 1000)

      // 메시지 리스너 추가
      const messageListener = (request, sender, sendResponse) => {
        console.log('[Discussion] Received message:', request)
        if (request.type === 'FACT_CHECK_REQUEST' && request.text) {
          console.log('[Discussion] Processing FACT_CHECK_REQUEST with text:', request.text)
          setPendingFactCheck(request.text)
          sendResponse({ received: true })
        }
      }

      chrome.runtime.onMessage.addListener(messageListener)
      console.log('[Discussion] Message listener added')

      // Cleanup
      return () => {
        if (chrome.runtime.onMessage.hasListener(messageListener)) {
          chrome.runtime.onMessage.removeListener(messageListener)
          console.log('[Discussion] Message listener removed')
        }
      }
    } else {
      console.log('[Discussion] Chrome API not available')
    }
  }, [])

  // pendingFactCheck가 설정되면 자동으로 팩트체크 시작
  useEffect(() => {
    console.log('[Discussion] pendingFactCheck changed:', pendingFactCheck, 'hasStarted:', hasStarted)
    if (pendingFactCheck && !hasStarted) {
      console.log('[Discussion] Auto-starting fact check with text:', pendingFactCheck)
      setInput(pendingFactCheck)
      // 약간의 지연 후 제출
      setTimeout(() => {
        console.log('[Discussion] Submitting fact check...')
        handleSubmit(pendingFactCheck)
        setPendingFactCheck(null) // 처리 후 초기화
      }, 500)
    }
  }, [pendingFactCheck, hasStarted])

  // WebSocket 연결 함수
  const connectWebSocket = (sessionId) => {
    if (wsRef.current) {
      wsRef.current.close()
    }

    // WebSocket URL 설정 (환경변수 또는 기본값 사용)
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
    const ws = new WebSocket(`${wsUrl}/ws/${sessionId}`)
    wsRef.current = ws
    sessionIdRef.current = sessionId
    setConnectionStatus('connecting')
    
    // WebSocket 버퍼 크기 로깅
    console.log('[WS] 연결 시작:', sessionId)

    ws.onopen = () => {
      console.log('WebSocket 연결 성공')
      setConnectionStatus('connected')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('[WS] 원시 메시지 수신:', data.type, data.agent, data.step)
        
        // 메시지를 큐에 추가
        messageQueueRef.current.push(data)
        
        // 큐 처리 시작
        processMessageQueue()
      } catch (error) {
        console.error('메시지 파싱 오류:', error, event.data)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket 오류:', error)
      setConnectionStatus('error')
      setIsLoading(false)
    }

    ws.onclose = (event) => {
      console.log('[WS] 연결 종료:', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean
      })
      setConnectionStatus('disconnected')
      
      // 메시지 큐에 남은 메시지 처리
      if (messageQueueRef.current.length > 0) {
        console.log(`[경고] 연결 종료 시 ${messageQueueRef.current.length}개의 미처리 메시지 존재`)
      }
    }

    return ws
  }

  // 배열 문자열 파싱 헬퍼 함수
  const parseArrayString = (str) => {
    if (!str) return [];
    try {
      // "item1", "item2" 형태의 문자열을 배열로 변환
      const items = str.match(/"([^"]+)"/g);
      return items ? items.map(item => item.replace(/"/g, '')) : [];
    } catch (e) {
      return [];
    }
  };

  // JSON 응답 파싱 함수 (개선된 버전)
  const parseAgentResponse = (responseText) => {
    if (!responseText) return null;
    
    try {
      // 이미 객체인 경우
      if (typeof responseText === 'object') {
        console.log('[JSON] 이미 객체 형태');
        return responseText;
      }
      
      let text = responseText.toString();
      
      // Markdown 코드 블록 제거
      text = text.replace(/```json\s*/gi, '').replace(/```\s*$/gi, '').replace(/```/g, '');
      
      // 백슬래시 이스케이프 처리
      text = text.replace(/\\\\/g, '\\');
      
      // 먼저 간단한 JSON 파싱 시도
      try {
        const directParsed = JSON.parse(text);
        console.log('[JSON] 직접 파싱 성공');
        return directParsed;
      } catch (e) {
        // 직접 파싱 실패시 전처리 진행
        console.log('[JSON] 직접 파싱 실패, 전처리 시작');
      }
      
      // JSON 내부의 실제 줄바꿈 처리
      let processedText = '';
      let inString = false;
      let escapeNext = false;
      
      for (let i = 0; i < text.length; i++) {
        const char = text[i];
        const nextChar = text[i + 1];
        
        if (escapeNext) {
          processedText += char;
          escapeNext = false;
          continue;
        }
        
        if (char === '\\' && nextChar !== 'n' && nextChar !== 'r' && nextChar !== 't') {
          escapeNext = true;
          processedText += char;
          continue;
        }
        
        if (char === '"' && !escapeNext) {
          inString = !inString;
          processedText += char;
          continue;
        }
        
        // 문자열 내부의 줄바꿈 처리
        if (inString && (char === '\n' || char === '\r')) {
          processedText += '\\n';
          if (char === '\r' && nextChar === '\n') {
            i++; // CRLF 건너뛰기
          }
        } else {
          processedText += char;
        }
      }
      
      // JSON 객체 추출 (중첩된 중괄호 처리)
      let braceCount = 0;
      let jsonStart = -1;
      let jsonEnd = -1;
      let isInsideString = false;
      
      for (let i = 0; i < processedText.length; i++) {
        const char = processedText[i];
        const prevChar = i > 0 ? processedText[i-1] : '';
        
        // 문자열 내부인지 확인 (이스케이프된 따옴표 제외)
        if (char === '"' && prevChar !== '\\') {
          isInsideString = !isInsideString;
        }
        
        // 문자열 내부가 아닐 때만 중괄호 카운트
        if (!isInsideString) {
          if (char === '{') {
            if (jsonStart === -1) jsonStart = i;
            braceCount++;
          } else if (char === '}') {
            braceCount--;
            if (braceCount === 0 && jsonStart !== -1) {
              jsonEnd = i + 1;
              break;
            }
          }
        }
      }
      
      if (jsonStart !== -1 && jsonEnd !== -1) {
        const jsonString = processedText.substring(jsonStart, jsonEnd);
        try {
          const parsed = JSON.parse(jsonString);
          console.log('[JSON] 추출 후 파싱 성공');
          return parsed;
        } catch (e) {
          console.warn('[JSON] 파싱 실패:', e.message);
          console.warn('[JSON] 실패한 문자열 길이:', jsonString.length);
          
          // 한 번 더 시도: 탭과 특수 공백 문자 제거
          try {
            const cleanedString = jsonString
              .replace(/\t/g, ' ')
              .replace(/\u00A0/g, ' ')
              .replace(/\u2028/g, '')
              .replace(/\u2029/g, '');
            const secondTry = JSON.parse(cleanedString);
            console.log('[JSON] 정리 후 파싱 성공');
            return secondTry;
          } catch (e2) {
            console.warn('[JSON] 정리 후에도 파싱 실패');
          }
        }
      }
      
      // 파싱 실패시 null 반환 (기본값은 호출자가 처리)
      return null;
    } catch (error) {
      console.error('[JSON] 파싱 오류:', error.message);
      return null;
    }
  }

  // 메시지 큐 처리 함수
  const processMessageQueue = async () => {
    // 이미 처리 중이면 대기
    if (processingRef.current) return
    
    processingRef.current = true
    
    while (messageQueueRef.current.length > 0) {
      const data = messageQueueRef.current.shift()
      try {
        await handleWebSocketMessage(data)
      } catch (error) {
        console.error('[메시지 처리 오류]', error, data)
        // 에러가 발생해도 다음 메시지 처리 계속
      }
      
      // 짧은 대기 시간을 두어 렌더링 완료 보장
      await new Promise(resolve => setTimeout(resolve, 10))
    }
    
    processingRef.current = false
  }

  // WebSocket 메시지 처리
  const handleWebSocketMessage = async (data) => {
    console.log(`[메시지 처리] 타입: ${data.type}, 에이전트: ${data.agent}, 단계: ${data.step}`)
    
    const content = data.content || {}
    const agent = data.agent
    const step = data.step

    switch (data.type) {
      case 'connection_established':
        console.log('WebSocket 연결 확인:', content.session_id)
        break

      case 'fact_check_started':
        console.log('팩트체킹 시작:', content.statement)
        break

      case 'task_completed':
        console.log(`[task_completed] Agent: ${agent}, Step: ${step}`)
        console.log('[task_completed] Raw content:', content)
        
        // JSON 응답 파싱 (실패해도 계속 진행)
        let parsedResponse = null;
        if (content.analysis || content.message) {
          const textToParse = content.analysis || content.message;
          parsedResponse = parseAgentResponse(textToParse);
          if (!parsedResponse) {
            console.warn(`[경고] ${agent} ${step} JSON 파싱 실패`);
            console.log(`[파싱 실패 원본] ${agent} ${step}:`, textToParse?.substring(0, 200));
            
            // Step2와 Step3에 대한 추가 시도
            if ((step === 'step2' || step === 'step3') && typeof textToParse === 'string') {
              // 텍스트에서 직접 필드 추출 시도
              const verdictMatch = textToParse.match(/"(?:final_)?verdict"\s*:\s*"([^"]+)"/);
              const agreementsMatch = textToParse.match(/"(?:key_)?agreements"\s*:\s*\[(.*?)\]/s);
              const disagreementsMatch = textToParse.match(/"(?:key_)?disagreements"\s*:\s*\[(.*?)\]/s);
              
              if (verdictMatch || agreementsMatch || disagreementsMatch) {
                parsedResponse = {
                  final_verdict: verdictMatch?.[1] || '정보부족',
                  agreements: agreementsMatch ? parseArrayString(agreementsMatch[1]) : [],
                  disagreements: disagreementsMatch ? parseArrayString(disagreementsMatch[1]) : [],
                  key_agreements: agreementsMatch ? parseArrayString(agreementsMatch[1]) : [],
                  key_disagreements: disagreementsMatch ? parseArrayString(disagreementsMatch[1]) : []
                };
                console.log(`[${step}] 정규식으로 추출 성공:`, parsedResponse);
              }
            }
          }
        }
        
        // 파싱된 응답 또는 원본 content 사용
        const responseToUse = parsedResponse || content;
        
        // Step별로 다른 필드 매핑 (백엔드 prompts.yaml 형식에 따라)
        let messageData = {
          id: `${agent}_task_complete_${Date.now()}`,
          type: 'response',
          agentId: agent,
          agentName: agentConfig[agent]?.name || agent,
          avatar: agentConfig[agent]?.avatar || '🤖',
          step: step,
          timestamp: new Date(data.timestamp || Date.now())
        };
        
        // Step1: 초기 분석 (verdict, key_findings, evidence_sources, reasoning)
        if (step === 'step1') {
          messageData = {
            ...messageData,
            verdict: responseToUse.verdict || content.verdict || '정보부족',
            keyFindings: responseToUse.key_findings || [],
            evidenceSources: responseToUse.evidence_sources || [],
            reasoning: responseToUse.reasoning || '',
            // Step2,3 필드는 비움
            agreements: [],
            disagreements: [],
            additionalPerspective: ''
          };
        }
        // Step2: 토론 (agreements, disagreements, additional_perspective, final_verdict)
        else if (step === 'step2') {
          // Step2는 다른 필드명을 사용하므로 특별 처리
          const step2Data = parsedResponse || {};
          
          // Step2 특별 로깅
          if (!parsedResponse) {
            console.warn(`[Step2] ${agent} JSON 파싱 실패, 원본 content 사용`);
            console.log('[Step2] 원본 content:', content);
          } else {
            console.log(`[Step2] ${agent} 파싱 성공:`, {
              agreements: step2Data.agreements?.length || 0,
              disagreements: step2Data.disagreements?.length || 0,
              final_verdict: step2Data.final_verdict
            });
          }
          
          messageData = {
            ...messageData,
            verdict: step2Data.final_verdict || content.verdict || '정보부족',
            keyFindings: [],
            evidenceSources: [],
            reasoning: step2Data.additional_perspective || content.message || '',
            agreements: step2Data.agreements || [],
            disagreements: step2Data.disagreements || [],
            additionalPerspective: step2Data.additional_perspective || ''
          };
        }
        // Step3: 최종 종합 (final_verdict, key_agreements, key_disagreements, verdict_reasoning, summary)
        else if (step === 'step3' && agent === 'super') {
          messageData = {
            ...messageData,
            verdict: responseToUse.final_verdict || content.verdict || '정보부족',
            keyFindings: responseToUse.key_agreements || [], // 합의점을 핵심발견으로 표시
            evidenceSources: [],
            reasoning: responseToUse.verdict_reasoning || responseToUse.summary || '',
            agreements: responseToUse.key_agreements || [],
            disagreements: responseToUse.key_disagreements || [],
            additionalPerspective: responseToUse.summary || ''
          };
        }
        
        const taskCompletedMessage = messageData
        
        console.log(`[메시지 추가] ${agent} ${step}:`, taskCompletedMessage.verdict);
        setMessages(prev => [...prev, taskCompletedMessage])
        
        // 모든 응답을 allResponses에 저장 (라이브러리용)
        const responseData = {
            id: `${agent}_${step}_${Date.now()}`,
            agent: agent,
            step: step,
            agentName: agentConfig[agent]?.name || agent,
            avatar: agentConfig[agent]?.avatar || '🤖',
            data: parsedResponse || { verdict: content.verdict || '정보부족' },
            timestamp: new Date(data.timestamp || Date.now())
          }
          
          setAllResponses(prev => {
            const updated = [...prev, responseData]
            console.log(`[응답 저장] 현재 ${updated.length}/${expectedResponses}개 수신`)
            return updated
          })
          setResponseCount(prev => {
            const newCount = prev + 1
            console.log(`[응답 카운트] ${newCount}/${expectedResponses}`)
            
            // 모든 응답을 받았는지 확인
            if (newCount === expectedResponses) {
              console.log('[알림] 모든 응답 수신 완료!')
            }
            
            return newCount
          })
          
        // Step 1 결과만 agentResults에 저장 (최종 결과 계산용)
        if (step === 'step1' && agent !== 'super') {
          // 백엔드 JSON에서 직접 데이터 추출 (prompts.yaml 형식에 따라)
          const verdict = responseToUse.verdict || content.verdict || '정보부족';
          // confidence는 백엔드가 직접 제공하지 않으므로 reasoning에서 추출하거나 verdict 기반 계산
          const confidence = extractConfidenceFromResponse(responseToUse) || extractConfidenceFromResponse(content) || 70;
          const reasoning = responseToUse.reasoning || '';
          const keyFindings = responseToUse.key_findings || [];
          const evidenceSources = responseToUse.evidence_sources || [];
          
          // agent 이름 정규화 (백엔드에서 오는 이름을 프론트엔드 키로 변환)
          const agentKey = agent.toLowerCase().replace('_agent', '').replace(' agent', '');
            
          console.log(`[Step1] ${agent} -> ${agentKey} 에이전트:`);
          console.log(`  - 판정: ${verdict}`);
          console.log(`  - 신뢰도: ${confidence}%`);
          console.log(`  - 핵심 발견: ${keyFindings.length}개`);
            
          setAgentResults(prev => {
            const updated = {
              ...prev,
              [agentKey]: {
                name: agentConfig[agentKey]?.name || agent,
                verdict: verdict,
                confidence: confidence,
                reasoning: reasoning,
                keyFindings: keyFindings,
                evidenceSources: evidenceSources,
                rawData: responseToUse  // 원본 JSON 데이터 보관
              }
            };
            console.log('[agentResults 업데이트]:', Object.keys(updated));
            return updated;
          })
        }
        
        // Super Agent의 최종 결과인 경우 (Step3)
        if (agent === 'super' && step === 'step3') {
            console.log('[Step3] Super Agent 완료 - 최종 결과 처리')
            console.log(`최종 응답 수: ${responseCount + 1}/${expectedResponses}`)
            setIsLoading(false) // 로딩 상태 해제
            
            // 백엔드 Step3 JSON 형식
            const superAgentData = responseToUse || {
              final_verdict: content.verdict || '정보부족',
              key_agreements: [],
              key_disagreements: [],
              verdict_reasoning: content.message || '',
              summary: ''
            };
            
            console.log('[Step3] Super Agent 데이터:');
            console.log(`  - 최종 판정: ${superAgentData.final_verdict}`);
            console.log(`  - 합의점: ${superAgentData.key_agreements?.length || 0}개`);
            console.log(`  - 불일치점: ${superAgentData.key_disagreements?.length || 0}개`);
            
            // 최종 결과 저장
            saveToResults(superAgentData)
            
            // 대화 전체를 라이브러리에 저장
            setTimeout(() => {
              console.log(`라이브러리 저장 시작... (총 ${allResponses.length + 1}개 응답)`)
              saveConversationToLibrary()
            }, 1000)
        }
        
        break

      case 'error':
        const errorMessage = {
          id: `error_${Date.now()}`,
          type: 'error',
          content: content.error || data.message || '오류가 발생했습니다',
          timestamp: new Date(data.timestamp || Date.now())
        }
        setMessages(prev => [...prev, errorMessage])
        setIsLoading(false)
        break

      case 'final_result':
        console.log('최종 결과 수신:', content)
        setIsLoading(false) // 로딩 상태 해제
        if (content.final_verdict) {
          // summary에서 JSON 파싱 시도
          let parsedSummary = null;
          if (content.summary) {
            parsedSummary = parseAgentResponse(content.summary);
            console.log('파싱된 summary:', parsedSummary);
          }
          
          // final_result는 이미 task_completed에서 처리했으므로 메시지 추가하지 않음
          // 단, 결과 저장만 처리
          console.log('[final_result] Super Agent 결과는 이미 task_completed에서 표시됨')
          
          // agent_verdicts가 비어있으면 agentResults 사용
          if (content.agent_verdicts && Object.keys(content.agent_verdicts).length === 0) {
            console.log('agent_verdicts가 비어있음, agentResults 사용');
            // 이미 수집된 agentResults를 유지
          }
          
          // final_result에서는 결과를 저장하지 않음 (이미 task_completed에서 저장됨)
          // 단, 필요한 경우 추가 처리만 수행
          console.log('[final_result] 결과는 이미 task_completed에서 저장됨');
        }
        setIsLoading(false)
        break

      default:
        console.log('처리되지 않은 메시지 타입:', data.type)
    }
  }

  // 신뢰도 추출 함수 (응답에서 백분율 추출)
  const extractConfidenceFromResponse = (response) => {
    if (!response) return 70;
    
    // confidence_score 필드가 있으면 우선 사용
    if (response.confidence_score) {
      return parseInt(response.confidence_score);
    }
    
    // confidence 필드가 있으면 사용
    if (response.confidence) {
      return parseInt(response.confidence);
    }
    
    // reasoning이나 analysis 텍스트에서 백분율 추출
    const text = response.reasoning || response.analysis || response.verdict_reasoning || '';
    const percentageMatches = text.match(/(\d+(?:\.\d+)?)%/g);
    
    if (percentageMatches && percentageMatches.length > 0) {
      // 여러 백분율이 있으면 가장 높은 값 사용 (보통 신뢰도를 나타냄)
      const percentages = percentageMatches.map(match => parseFloat(match.replace('%', '')));
      return Math.round(Math.max(...percentages));
    }
    
    // 판정에 따른 기본값
    const verdict = response.verdict || response.final_verdict;
    if (verdict) {
      if (verdict.includes('참') || verdict.includes('거짓')) {
        return verdict.includes('대체로') ? 75 : 85;
      } else if (verdict.includes('부분적')) {
        return 60;
      } else if (verdict.includes('불확실') || verdict.includes('정보부족')) {
        return 50;
      }
    }
    
    return 70; // 기본값
  }

  // 판정을 Results 컴포넌트 형식으로 변환
  const convertVerdictToResultFormat = (verdict) => {
    if (!verdict) return '중립적';
    
    // 백엔드에서 정의한 verdict_options 기반
    const verdictMap = {
      '참': '긍정적',
      '대체로_참': '긍정적',
      '부분적_참': '중립적',
      '불확실': '중립적',
      '정보부족': '중립적',
      '논란중': '중립적',
      '부분적_거짓': '중립적',
      '대체로_거짓': '부정적',
      '거짓': '부정적',
      '과장됨': '중립적',
      '오해소지': '중립적',
      '시대착오': '부정적'
    };
    return verdictMap[verdict] || '중립적';
  }

  // 전체 신뢰도 계산
  const calculateOverallConfidence = (agents) => {
    if (agents.length === 0) return 0;
    const totalConfidence = agents.reduce((sum, agent) => sum + agent.confidence, 0);
    return Math.round(totalConfidence / agents.length);
  }

  // 결과를 Results 컴포넌트 형식으로 저장 (순수 JSON 데이터만 사용)
  const saveToResults = (superAgentData) => {
    console.log('[결과 저장] Super Agent 데이터:', superAgentData);
    
    // 최신 상태를 직접 가져오기 위해 setState 콜백 사용
    setAgentResults(currentAgentResults => {
      setMessages(currentMessages => {
        setCurrentQuestion(currentQuestionState => {
          console.log('[결과 저장] 현재 agentResults:', currentAgentResults);
          console.log('[결과 저장] 현재 질문:', currentQuestionState);
          console.log('[결과 저장] 현재 메시지 수:', currentMessages.length);
          
          // 사용자 질문 가져오기
          let userQuestion = currentQuestionState;
          if (!userQuestion) {
            // messages에서 질문 찾기
            const questionMsg = currentMessages.find(msg => msg.type === 'question');
            if (questionMsg) {
              userQuestion = questionMsg.content;
              console.log('[결과 저장] 메시지에서 질문 찾음:', userQuestion);
            }
          }
          
          // Step1 에이전트 결과를 백엔드 JSON 형식 그대로 사용
          const agentOrder = ['news', 'academic', 'statistics', 'logic', 'social'];
          const agents = [];
          
          agentOrder.forEach(agentKey => {
            if (currentAgentResults[agentKey]) {
              // 백엔드 Step1 JSON 데이터 그대로 사용
              const agentData = currentAgentResults[agentKey];
              agents.push({
                name: agentData.name,
                confidence: agentData.confidence,
                verdict: agentData.verdict,  // 원본 verdict 그대로 사용
                // 추가 데이터 보관 (필요시 사용)
                reasoning: agentData.reasoning,
                keyFindings: agentData.keyFindings,
                evidenceSources: agentData.evidenceSources
              });
              console.log(`[저장] ${agentKey}: ${agentData.verdict} (${agentData.confidence}%)`);
            } else {
              console.log(`[경고] ${agentKey} 에이전트 결과 없음`);
            }
          });
          
          // 백엔드 Step3 Super Agent JSON 데이터 사용
          // Super Agent confidence 계산 (평균 또는 reasoning에서 추출)
          const superConfidence = agents.length > 0 
            ? Math.round(agents.reduce((sum, a) => sum + a.confidence, 0) / agents.length)
            : extractConfidenceFromResponse(superAgentData) || 70;
          
          const result = {
            id: Date.now(),
            question: userQuestion || '질문 없음',
            date: new Date().toISOString().split('T')[0],
            agents: agents,  // Step1 5개 에이전트 결과
            // Super Agent Step3 데이터
            overallVerdict: superAgentData.final_verdict,  // 원본 verdict 그대로 사용
            confidence: superConfidence,  // 계산된 또는 추출된 신뢰도
            keyAgreements: superAgentData.key_agreements || [],
            keyDisagreements: superAgentData.key_disagreements || [],
            verdictReasoning: superAgentData.verdict_reasoning || '',
            summary: superAgentData.summary || '',
            // 전체 데이터 보관
            fullAnalysis: {
              step1Results: currentAgentResults,
              step3Result: superAgentData
            }
          };

          console.log('[최종 결과]:', result);
          console.log(`  - 질문: ${result.question}`);
          console.log(`  - Step1 에이전트: ${result.agents.length}개`);
          console.log(`  - 최종 판정: ${result.overallVerdict}`);
          
          // 부모 컴포넌트에 결과 전달
          if (onSaveResult) {
            onSaveResult(result);
          }
          
          return currentQuestionState; // 상태 변경하지 않음
        });
        return currentMessages; // 상태 변경하지 않음
      });
      return currentAgentResults; // 상태 변경하지 않음
    });
  }

  // 대화 전체를 라이브러리에 저장
  const saveConversationToLibrary = () => {
    // 현재 상태를 직접 가져오기 위해 state 업데이트 함수 사용
    setCurrentQuestion(currentQuestionState => {
      setAllResponses(currentResponses => {
        setMessages(currentMessages => {
          console.log(`총 ${currentResponses.length}개의 응답 수집 완료`);
          console.log('현재 메시지 수:', currentMessages.length);
          console.log('저장할 질문:', currentQuestionState);
          
          const conversation = {
            id: Date.now(),
            question: currentQuestionState, // 최신 질문 상태 사용
            date: new Date().toISOString().split('T')[0],
            timestamp: new Date().toISOString(),
            totalResponses: currentResponses.length,
            responses: currentResponses, // 모든 응답
            messages: currentMessages, // UI 메시지들
            summary: {
              step1: currentResponses.filter(r => r.step === 'step1').length,
              step2: currentResponses.filter(r => r.step === 'step2').length,
              step3: currentResponses.filter(r => r.step === 'step3').length
            }
          };

          console.log('라이브러리에 저장할 대화:', conversation);
          
          // 부모 컴포넌트에 대화 전달
          if (onSaveConversation) {
            onSaveConversation(conversation);
          }
          
          return currentMessages; // 상태 변경하지 않음
        });
        return currentResponses; // 상태 변경하지 않음
      });
      return currentQuestionState; // 상태 변경하지 않음
    });
  }

  // 저장된 대화 불러오기 함수
  const loadSavedConversation = (conversationData) => {
    console.log('대화 데이터 복원 중:', conversationData)
    
    // 저장된 대화 보기 모드로 전환
    setIsViewingHistory(true)
    setHasStarted(true)
    setCurrentQuestion(conversationData.question)
    
    // 저장된 메시지들 복원
    if (conversationData.messages && conversationData.messages.length > 0) {
      setMessages(conversationData.messages)
    }
    
    // 저장된 응답들 복원
    if (conversationData.responses && conversationData.responses.length > 0) {
      setAllResponses(conversationData.responses)
      setResponseCount(conversationData.responses.length)
    }
    
    // Step 1 에이전트 결과 복원 (Results 호환용)
    const step1Responses = conversationData.responses?.filter(r => r.step === 'step1') || []
    const agentResultsData = {}
    
    step1Responses.forEach(response => {
      if (response.agent && response.data) {
        agentResultsData[response.agent] = {
          name: response.agentName,
          verdict: response.data.verdict || response.data.final_verdict,
          confidence: extractConfidenceFromResponse(response.data)
        }
      }
    })
    
    setAgentResults(agentResultsData)
    console.log('저장된 대화 복원 완료')
  }

  // 새 질문 시작 함수
  const startNewConversation = () => {
    setIsViewingHistory(false)
    setHasStarted(false)
    setMessages([])
    setAllResponses([])
    setResponseCount(0)
    setAgentResults({})
    setCurrentQuestion('')
    setInput('')
    setIsLoading(false)
    
    // context 클리어하여 에이전트 이모지가 표시되도록 함
    if (onClearContext) {
      onClearContext()
    }
  }

  const handleSubmit = (eOrText) => {
    // 문자열이 직접 전달된 경우 (컨텍스트 메뉴에서 호출)
    let question
    if (typeof eOrText === 'string') {
      question = eOrText
    } else {
      // 이벤트 객체인 경우 (폼 제출)
      eOrText.preventDefault()
      if (!input.trim()) return
      question = input.trim()
    }

    setCurrentQuestion(question) // 현재 질문 저장
    setInput('')
    setIsLoading(true)
    setHasStarted(true)
    setMessages([]) // 새로운 질문 시 이전 메시지 클리어
    setAgentResults({}) // 에이전트 결과 초기화
    setAllResponses([]) // 모든 응답 초기화
    setResponseCount(0) // 응답 개수 초기화
    messageQueueRef.current = [] // 메시지 큐 초기화
    
    console.log('[새 질문] 질문 시작:', question)
    console.log(`[예상] 총 ${expectedResponses}개의 응답 대기 중...`)
    console.log('[초기화] agentResults 초기화 완료')

    // 사용자 질문을 메시지에 추가
    const questionMessage = {
      id: Date.now(),
      type: 'question',
      content: question,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, questionMessage])

    // WebSocket을 통한 실시간 팩트체킹 요청
    const sessionId = `session_${Date.now()}`
    const ws = connectWebSocket(sessionId)

    const sendFactCheckRequest = () => {
      ws.send(JSON.stringify({
        action: 'start',
        statement: question
      }))
    }

    if (ws.readyState === WebSocket.OPEN) {
      sendFactCheckRequest()
    } else {
      const openHandler = () => {
        setTimeout(sendFactCheckRequest, 100)
      }
      ws.addEventListener('open', openHandler)
    }
  }

  const toggleAgent = (agentId) => {
    setActiveAgents(prev => prev.map(agent => 
      agent.id === agentId ? { ...agent, active: !agent.active } : agent
    ))
  }


  const copyText = (text) => {
    navigator.clipboard.writeText(text)
  }

  const exportText = (text) => {
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'factcheck-result.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  // 에이전트 선택 UI 표시 여부 결정
  // 토론 시작 창에서만 표시
  const showAgentSelection = !hasStarted && !isViewingHistory && (!context || !context.isConversation);

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Agent Selection - 토론 시작 창에서만 표시 */}
      {showAgentSelection && (
        <div ref={containerRef} className="border-b border-gray-200 py-4 overflow-hidden">
          <div className="relative h-32">
          {shouldAnimate ? (
            <div 
              className="flex gap-6 absolute whitespace-nowrap"
              style={{
                animation: 'slideRight 15s linear infinite',
                width: 'calc(200% + 24px)', // 더블 너비로 무한 루프
                height: '100%',
                alignItems: 'center'
              }}
            >
            {/* 첫 번째 세트 */}
            {activeAgents.map((agent) => (
              <div 
                key={`first-${agent.id}`}
                className="relative flex flex-col items-center flex-shrink-0 w-36"
              >
                {/* Agent 이미지 */}
                <div className="relative">
                  <img 
                    src={`/img/agent_icons/${agent.id}.png`}
                    alt={agent.name}
                    className={`object-cover rounded-full transition-all duration-200 cursor-pointer ${
                      !agent.active ? 'opacity-50' : ''
                    }`}
                    style={{ width: '120px', height: '120px' }}
                    onClick={() => !agent.active && toggleAgent(agent.id)}
                    onError={(e) => {
                      // 이미지 로드 실패시 아바타 이모지로 대체
                      e.target.style.display = 'none'
                      e.target.nextElementSibling.style.display = 'flex'
                    }}
                  />
                  {/* 대체 아바타 */}
                  <div 
                    className={`w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center text-3xl cursor-pointer transition-all duration-200 ${
                      !agent.active ? 'opacity-50' : ''
                    }`}
                    style={{ display: 'none' }}
                    onClick={() => !agent.active && toggleAgent(agent.id)}
                  >
                    {agent.avatar}
                  </div>
                  
                  {/* X 버튼 - 활성화된 Agent에만 표시 */}
                  {/* {agent.active && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleAgent(agent.id)
                      }}
                      className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full flex items-center justify-center text-xs transition-colors z-10 bg-black text-white hover:bg-gray-800"
                    >
                      ×
                    </button>
                  )} */}
                </div>
                
                {/* Agent 이름 */}
                <span className={`text-xs font-medium text-center mt-2 transition-all duration-200 ${
                  !agent.active ? 'opacity-50 text-gray-400' : 'text-gray-700'
                }`}>
                  {agent.name.toUpperCase()}
                </span>
              </div>
            ))}
            
            {/* 두 번째 세트 (무한 루프용 복제) */}
            {activeAgents.map((agent) => (
              <div 
                key={`second-${agent.id}`}
                className="relative flex flex-col items-center flex-shrink-0 w-36"
              >
                {/* Agent 이미지 */}
                <div className="relative">
                  <img 
                    src={`/img/agent_icons/${agent.id}.png`}
                    alt={agent.name}
                    className={`object-cover rounded-full transition-all duration-200 cursor-pointer ${
                      !agent.active ? 'opacity-50' : ''
                    }`}
                    style={{ width: '120px', height: '120px' }}
                    onClick={() => !agent.active && toggleAgent(agent.id)}
                    onError={(e) => {
                      // 이미지 로드 실패시 아바타 이모지로 대체
                      e.target.style.display = 'none'
                      e.target.nextElementSibling.style.display = 'flex'
                    }}
                  />
                  {/* 대체 아바타 */}
                  <div 
                    className={`w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center text-3xl cursor-pointer transition-all duration-200 ${
                      !agent.active ? 'opacity-50' : ''
                    }`}
                    style={{ display: 'none' }}
                    onClick={() => !agent.active && toggleAgent(agent.id)}
                  >
                    {agent.avatar}
                  </div>
                  
                  {/* X 버튼 - 활성화된 Agent에만 표시 */}
                  {/* {agent.active && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleAgent(agent.id)
                      }}
                      className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full flex items-center justify-center text-xs transition-colors z-10 bg-black text-white hover:bg-gray-800"
                    >
                      ×
                    </button>
                  )} */}
                </div>
                
                {/* Agent 이름 */}
                <span className={`text-xs font-medium text-center mt-2 transition-all duration-200 ${
                  !agent.active ? 'opacity-50 text-gray-400' : 'text-gray-700'
                }`}>
                  {agent.name.toUpperCase()}
                </span>
              </div>
            ))}
            </div>
          ) : (
            // 애니메이션 없는 정적 레이아웃
            <div className="flex gap-6 justify-center absolute h-full w-full"
                 style={{ alignItems: 'center' }}>
              {activeAgents.map((agent) => (
                <div 
                  key={agent.id}
                  className="relative flex flex-col items-center flex-shrink-0 w-36"
                >
                  {/* Agent 이미지 */}
                  <div className="relative">
                    <img 
                      src={`/img/agent_icons/${agent.id}.png`}
                      alt={agent.name}
                      className={`object-cover rounded-full transition-all duration-200 cursor-pointer ${
                        !agent.active ? 'opacity-50' : ''
                      }`}
                      style={{ width: '120px', height: '120px' }}
                      onClick={() => !agent.active && toggleAgent(agent.id)}
                      onError={(e) => {
                        // 이미지 로드 실패시 아바타 이모지로 대체
                        e.target.style.display = 'none'
                        e.target.nextElementSibling.style.display = 'flex'
                      }}
                    />
                    {/* 대체 아바타 */}
                    <div 
                      className={`rounded-full bg-gray-100 flex items-center justify-center cursor-pointer transition-all duration-200 ${
                        !agent.active ? 'opacity-50' : ''
                      }`}
                      style={{ width: '120px', height: '120px', fontSize: '48px', display: 'none' }}
                      onClick={() => !agent.active && toggleAgent(agent.id)}
                    >
                      {agent.avatar}
                    </div>
                    
                    {/* X 버튼 - 활성화된 Agent에만 표시 */}
                    {/* {agent.active && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          toggleAgent(agent.id)
                        }}
                        className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full flex items-center justify-center text-xs transition-colors z-10 bg-black text-white hover:bg-gray-800"
                      >
                        ×
                      </button>
                    )} */}
                  </div>
                  
                  {/* Agent 이름 */}
                  <span className={`text-xs font-medium text-center mt-2 transition-all duration-200 ${
                    !agent.active ? 'opacity-50 text-gray-400' : 'text-gray-700'
                  }`}>
                    {agent.name.toUpperCase()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      )}

      <style jsx>{`
        @keyframes slideRight {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
        
        .user-message {
          align-self: flex-end;
          background-color: #3b82f6;
          color: white;
          padding: 12px 16px;
          border-radius: 18px 18px 4px 18px;
          max-width: 80%;
          margin-left: auto;
          width: fit-content;
        }
        
        /* 판정 결과 색상 클래스 */
        .verdict-참 { background: #dcfce7; color: #16a34a; }
        .verdict-거짓 { background: #fee2e2; color: #dc2626; }
        .verdict-불확실 { background: #f3f4f6; color: #6b7280; }
        .verdict-정보부족 { background: #f3f4f6; color: #6b7280; }
        
        /* 커스텀 스크롤바 스타일 */
        .overflow-y-auto::-webkit-scrollbar {
          width: 12px;
        }
        
        .overflow-y-auto::-webkit-scrollbar-track {
          background: transparent;
        }
        
        .overflow-y-auto::-webkit-scrollbar-thumb {
          background-color: #d1d5db;
          border-radius: 3px;
          background-clip: padding-box;
          border: 3px solid transparent;
        }
        
        .overflow-y-auto::-webkit-scrollbar-thumb:hover {
          background-color: #9ca3af;
          background-clip: padding-box;
          border: 3px solid transparent;
        }
        
        /* Firefox 스크롤바 */
        .overflow-y-auto {
          scrollbar-width: thin;
          scrollbar-color: #d1d5db transparent;
        }
      `}</style>

      {!hasStarted ? (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
          <h2 className="text-gray-800 mb-6 text-3xl font-bold">You're about to use FactWave</h2>
          <p className="text-gray-600 leading-relaxed mb-6 text-base max-w-lg">
            FactWave는 AI 에이전트가 협력하여 정보의 진위를 분석하는 차세대 팩트체킹 플랫폼입니다. 
            뉴스, 학술, 논리, 소셜 미디어 전문 에이전트들이 다각도로 검증하여 신뢰할 수 있는 판단을 제공합니다.
          </p>
          <p className="text-gray-600 leading-relaxed text-base max-w-lg">
            AI 분석 결과는 참고용으로만 사용하세요. 
            중요한 의사결정 전에는 반드시 추가적인 검증과 전문가 자문을 받으시기 바랍니다.
            최종 판단과 그 결과에 대한 책임은 사용자에게 있습니다.
          </p>
        </div>
      ) : isViewingHistory ? (
        // 저장된 대화 보기 모드
        <div className="flex flex-col h-full">
          {/* 저장된 대화 헤더 */}
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-blue-800 font-semibold text-lg">📚 저장된 대화 보기</h3>
                <p className="text-blue-600 text-sm mt-1">
                  총 {responseCount}개의 응답 | {currentQuestion}
                </p>
              </div>
              <button
                onClick={startNewConversation}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                새 질문하기
              </button>
            </div>
          </div>
          
          {/* 저장된 메시지들 표시 */}
          <div className="flex-1 overflow-y-auto">
            {messages.map((message) => (
              <div key={message.id} className="mb-6">
                {message.type === 'question' ? (
                  <div className="user-message mb-5">
                    {message.content}
                  </div>
                ) : message.type === 'error' ? (
                  <div className="bg-red-50 p-4 rounded-xl mb-5 text-base leading-relaxed text-red-800 border-l-4 border-red-500">
                    ⚠️ {message.content}
                  </div>
                ) : (
                  <div className="bg-white rounded-xl p-5 shadow-lg border border-gray-200">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-4xl w-16 h-16 flex items-center justify-center bg-gray-100 rounded-full">
                        {message.avatar}
                      </span>
                      <div className="flex-1">
                        <span className="font-semibold text-base text-gray-800">{message.agentName}</span>
                        {message.verdict && (
                          <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                            message.verdict.includes('참') ? 'verdict-참' :
                            message.verdict.includes('거짓') || message.verdict.includes('과장') ? 'verdict-거짓' :
                            message.verdict.includes('불확실') || message.verdict.includes('논란') ? 'verdict-불확실' :
                            message.verdict.includes('정보부족') ? 'verdict-정보부족' :
                            'verdict-불확실'
                          }`}>
                            {message.verdict}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      {message.keyFindings && message.keyFindings.length > 0 && (
                        <div>
                          <strong className="text-sm text-gray-800">핵심 발견사항:</strong>
                          <ul className="mt-1 space-y-1 text-sm text-gray-700">
                            {message.keyFindings.map((finding, index) => (
                              <li key={index} className="ml-4">• {finding}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {message.evidenceSources && message.evidenceSources.length > 0 && (
                        <div>
                          <strong className="text-sm text-gray-800">근거 출처:</strong>
                          <ul className="mt-1 space-y-1 text-sm text-gray-700">
                            {message.evidenceSources.map((source, index) => (
                              <li key={index} className="ml-4">• {source}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {message.reasoning && (
                        <div>
                          <strong className="text-sm text-gray-800">판정 근거:</strong>
                          <p className="mt-1 text-sm text-gray-700 leading-relaxed">{message.reasoning}</p>
                        </div>
                      )}
                      
                      {message.agreements && message.agreements.length > 0 && (
                        <div>
                          <strong className="text-sm text-gray-800">동의점:</strong>
                          <ul className="mt-1 space-y-1 text-sm text-gray-700">
                            {message.agreements.map((agreement, index) => (
                              <li key={index} className="ml-4">• {agreement}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {message.disagreements && message.disagreements.length > 0 && (
                        <div>
                          <strong className="text-sm text-gray-800">이견/보완점:</strong>
                          <ul className="mt-1 space-y-1 text-sm text-gray-700">
                            {message.disagreements.map((disagreement, index) => (
                              <li key={index} className="ml-4">• {disagreement}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {message.additionalPerspective && (
                        <div>
                          <strong className="text-sm text-gray-800">추가 관점:</strong>
                          <p className="mt-1 text-sm text-gray-700 leading-relaxed">{message.additionalPerspective}</p>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex justify-between items-center pt-3 border-t border-gray-100 relative mt-4">
                      <div className="flex gap-2">
                        <button 
                          className="bg-none border-none cursor-pointer p-1.5 rounded-md text-base transition-colors hover:bg-gray-100"
                          onClick={() => copyText(message.reasoning || message.additionalPerspective || '내용')}
                          title="복사"
                        >
                          📋
                        </button>
                        <button 
                          className="bg-none border-none cursor-pointer p-1.5 rounded-md text-base transition-colors hover:bg-gray-100"
                          onClick={() => exportText(message.reasoning || message.additionalPerspective || '내용')}
                          title="내보내기"
                        >
                          📤
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          {messages.map((message) => (
            <div key={message.id} className="mb-6">
              {message.type === 'question' ? (
                <div className="user-message mb-5">
                  {message.content}
                </div>
              ) : message.type === 'error' ? (
                <div className="bg-red-50 p-4 rounded-xl mb-5 text-base leading-relaxed text-red-800 border-l-4 border-red-500">
                  ⚠️ {message.content}
                </div>
              ) : (
                <div className="bg-white rounded-xl p-5 shadow-lg border border-gray-200">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-4xl w-16 h-16 flex items-center justify-center bg-gray-100 rounded-full">
                      {message.avatar}
                    </span>
                    <div className="flex-1">
                      <span className="font-semibold text-base text-gray-800">{message.agentName}</span>
                      {message.verdict && (
                        <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                          message.verdict.includes('참') ? 'verdict-참' :
                          message.verdict.includes('거짓') || message.verdict.includes('과장') ? 'verdict-거짓' :
                          message.verdict.includes('불확실') || message.verdict.includes('논란') ? 'verdict-불확실' :
                          message.verdict.includes('정보부족') ? 'verdict-정보부족' :
                          'verdict-불확실'
                        }`}>
                          {message.verdict}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    {message.keyFindings && message.keyFindings.length > 0 && (
                      <div>
                        <strong className="text-sm text-gray-800">핵심 발견사항:</strong>
                        <ul className="mt-1 space-y-1 text-sm text-gray-700">
                          {message.keyFindings.map((finding, index) => (
                            <li key={index} className="ml-4">• {finding}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {message.evidenceSources && message.evidenceSources.length > 0 && (
                      <div>
                        <strong className="text-sm text-gray-800">근거 출처:</strong>
                        <ul className="mt-1 space-y-1 text-sm text-gray-700">
                          {message.evidenceSources.map((source, index) => (
                            <li key={index} className="ml-4">• {source}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {message.reasoning && (
                      <div>
                        <strong className="text-sm text-gray-800">판정 근거:</strong>
                        <p className="mt-1 text-sm text-gray-700 leading-relaxed">{message.reasoning}</p>
                      </div>
                    )}
                    
                    {message.agreements && message.agreements.length > 0 && (
                      <div>
                        <strong className="text-sm text-gray-800">동의점:</strong>
                        <ul className="mt-1 space-y-1 text-sm text-gray-700">
                          {message.agreements.map((agreement, index) => (
                            <li key={index} className="ml-4">• {agreement}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {message.disagreements && message.disagreements.length > 0 && (
                      <div>
                        <strong className="text-sm text-gray-800">이견/보완점:</strong>
                        <ul className="mt-1 space-y-1 text-sm text-gray-700">
                          {message.disagreements.map((disagreement, index) => (
                            <li key={index} className="ml-4">• {disagreement}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {message.additionalPerspective && (
                      <div>
                        <strong className="text-sm text-gray-800">추가 관점:</strong>
                        <p className="mt-1 text-sm text-gray-700 leading-relaxed">{message.additionalPerspective}</p>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex justify-between items-center pt-3 border-t border-gray-100 relative mt-4">
                    <div className="flex gap-2">
                      <button 
                        className="bg-none border-none cursor-pointer p-1.5 rounded-md text-base transition-colors hover:bg-gray-100"
                        onClick={() => copyText(message.reasoning || message.additionalPerspective || '내용')}
                        title="복사"
                      >
                        📋
                      </button>
                      <button 
                        className="bg-none border-none cursor-pointer p-1.5 rounded-md text-base transition-colors hover:bg-gray-100"
                        onClick={() => exportText(message.reasoning || message.additionalPerspective || '내용')}
                        title="내보내기"
                      >
                        📤
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="text-center py-10 text-gray-600 italic">
              분석 중...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      )}

      {!isViewingHistory && (
        <form onSubmit={handleSubmit} className="p-3 bg-white border-t border-gray-200 mt-auto">
        <div className="relative flex items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Write any opinion..."
            rows={1}
            className="w-full px-4 py-3 pr-16 bg-white border border-gray-300 rounded-2xl text-base outline-none transition-all duration-200 focus:border-gray-600 shadow-md text-black resize-none overflow-hidden"
            style={{ minHeight: '48px', maxHeight: '120px' }}
            onInput={(e) => {
              // 자동 높이 조절
              e.target.style.height = 'auto'
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSubmit(e)
              }
            }}
          />
          <button 
            type="submit" 
            className="absolute right-2 top-1/2 transform -translate-y-1/2 w-8 h-8 bg-gray-200 text-gray-800 rounded-full cursor-pointer text-lg flex items-center justify-center transition-colors hover:bg-gray-300 border-none"
          >
            ↑
          </button>
        </div>
        </form>
      )}
    </div>
  )
}

export default Discussion