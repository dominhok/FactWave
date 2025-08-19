/* global chrome */

console.log("FactWave Service Worker initializing...");

// ========================================
// 설치 시 컨텍스트 메뉴 생성
// ========================================
chrome.runtime.onInstalled.addListener(() => {
  console.log("FactWave Extension installed/updated");
  
  // 사이드 패널 기본 동작 설정
  chrome.sidePanel
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch((error) => console.error("Failed to set panel behavior:", error));
  
  // 컨텍스트 메뉴 생성
  chrome.contextMenus.create({
    id: "factwave-check",
    title: "FactWave에서 팩트체크하기",
    contexts: ["selection"]
  }, () => {
    if (chrome.runtime.lastError) {
      console.error("Context menu creation error:", chrome.runtime.lastError);
    } else {
      console.log("Context menu created successfully");
    }
  });
});

// ========================================
// 컨텍스트 메뉴 클릭 이벤트 처리
// ========================================
chrome.contextMenus.onClicked.addListener((info, tab) => {
  console.log("Context menu clicked!", info.menuItemId, info.selectionText);
  
  if (info.menuItemId === "factwave-check" && info.selectionText) {
    console.log("FactWave menu selected with text:", info.selectionText);
    
    // 선택된 텍스트를 storage에 저장
    chrome.storage.local.set({ 
      pendingFactCheck: info.selectionText,
      timestamp: Date.now()
    }, () => {
      if (chrome.runtime.lastError) {
        console.error("Storage save error:", chrome.runtime.lastError);
        return;
      }
      console.log("Text saved to storage:", info.selectionText);
      
      // 사이드 패널 열기
      chrome.sidePanel.open({ windowId: tab.windowId })
        .then(() => {
          console.log("Side panel opened successfully!");
          
          // 사이드 패널이 열린 후 메시지 전송 시도
          setTimeout(() => {
            console.log("Attempting to send message to side panel...");
            chrome.runtime.sendMessage({
              type: 'FACT_CHECK_REQUEST',
              text: info.selectionText
            }).catch((error) => {
              console.log("Message sending failed (expected if panel is loading):", error);
            });
          }, 1500);
        })
        .catch(error => {
          console.error("Failed to open side panel:", error);
        });
    });
  }
});

// ========================================
// 메시지 리스너 (사이드 패널과 통신용)
// ========================================
chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
  console.log("Message received in background:", request.type);
  
  if (request.type === 'GET_PENDING_FACT_CHECK') {
    // 저장된 팩트체크 텍스트 가져오기
    chrome.storage.local.get(['pendingFactCheck', 'timestamp'], (result) => {
      if (result.pendingFactCheck) {
        // 5분 이내의 데이터만 유효
        const isRecent = (Date.now() - result.timestamp) < 5 * 60 * 1000;
        if (isRecent) {
          console.log("Returning pending fact check text:", result.pendingFactCheck);
          sendResponse({ text: result.pendingFactCheck });
          // 사용 후 삭제
          chrome.storage.local.remove(['pendingFactCheck', 'timestamp']);
        } else {
          console.log("Pending fact check expired");
          sendResponse({ text: null });
        }
      } else {
        console.log("No pending fact check found");
        sendResponse({ text: null });
      }
    });
    return true; // 비동기 응답을 위해 true 반환
  }
});

// ========================================
// 확장 프로그램 아이콘 클릭 시 사이드 패널 열기
// ========================================
chrome.action.onClicked.addListener((tab) => {
  console.log("Extension icon clicked!");
  chrome.sidePanel.open({ windowId: tab.windowId })
    .catch(error => console.error("Failed to open side panel:", error));
});

console.log("FactWave Service Worker initialized successfully");