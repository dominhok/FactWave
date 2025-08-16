/* global chrome */

// 기본 API 확인 함수
function isAPIAvailable(api) {
  return typeof chrome !== 'undefined' && chrome[api];
}

// API 메서드 확인 함수
function isMethodAvailable(api, method) {
  return isAPIAvailable(api) && typeof chrome[api][method] === 'function';
}

// 설치 시 알림 및 초기 설정
if (isMethodAvailable('runtime', 'onInstalled')) {
  chrome.runtime.onInstalled.addListener(() => {
    console.log("FactWave Extension installed successfully!");
    
    // 사이드 패널 기본 동작 설정 (안전하게)
    if (isMethodAvailable('sidePanel', 'setPanelBehavior')) {
      try {
        chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
      } catch (error) {
        console.error("Side panel setup error:", error);
      }
    }
  });
}

// 확장 프로그램 아이콘 클릭 시 사이드 패널 열기
if (isMethodAvailable('action', 'onClicked')) {
  chrome.action.onClicked.addListener((tab) => {
    console.log("FactWave extension clicked!");
    if (isMethodAvailable('sidePanel', 'open')) {
      try {
        chrome.sidePanel.open({ windowId: tab.windowId });
      } catch (error) {
        console.error("Side panel open error:", error);
      }
    }
  });
}

// 사이드 패널 초기 설정 (안전하게)
if (isMethodAvailable('sidePanel', 'setPanelBehavior')) {
  try {
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  } catch (error) {
    console.error("Side panel behavior error:", error);
  }
}