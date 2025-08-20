#!/usr/bin/env python3
"""
WebSocket 클라이언트 테스트 - FactWave 실시간 스트리밍 테스트
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

class FactWaveWebSocketClient:
    def __init__(self, uri="ws://localhost:8000/ws/test-session"):
        self.uri = uri
        self.websocket = None
        
    async def connect(self):
        """WebSocket 연결"""
        try:
            self.websocket = await websockets.connect(self.uri)
            print(f"✅ Connected to {self.uri}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def send_message(self, message):
        """메시지 전송"""
        if self.websocket:
            await self.websocket.send(json.dumps(message))
            print(f"📤 Sent: {message}")
    
    async def listen(self):
        """메시지 수신 대기"""
        if not self.websocket:
            return
        
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed")
        except Exception as e:
            print(f"❌ Error listening: {e}")
    
    async def handle_message(self, data):
        """수신된 메시지 처리"""
        msg_type = data.get("type", "unknown")
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n[{timestamp}] 📨 {msg_type.upper()}")
        
        if msg_type == "connection_established":
            print(f"🎉 연결 확립: {data.get('content', {}).get('session_id')}")
        
        elif msg_type == "fact_check_started":
            content = data.get("content", {})
            print(f"🚀 팩트체킹 시작: {content.get('statement')}")
        
        elif msg_type == "step_start":
            step = data.get("step", "")
            content = data.get("content", {})
            print(f"📋 {step} 단계 시작: {content.get('description')}")
        
        elif msg_type == "agent_start":
            agent = data.get("agent", "")
            step = data.get("step", "")
            content = data.get("content", {})
            print(f"🔍 [{step}] {agent} 에이전트 시작: {content.get('message')}")
        
        elif msg_type == "tool_call":
            agent = data.get("agent", "")
            tool = data.get("tool", "")
            step = data.get("step", "")
            content = data.get("content", {})
            tool_input = content.get("input", "")
            tool_output = content.get("output", "")
            
            print(f"🔧 [{step}] {agent} → {tool}")
            print(f"   📥 입력: {str(tool_input)[:100]}...")
            if tool_output and tool_output != "결과 처리 중...":
                print(f"   📤 결과: {str(tool_output)[:100]}...")
        
        elif msg_type == "agent_analysis":
            agent = data.get("agent", "")
            step = data.get("step", "")
            content = data.get("content", {})
            analysis = content.get("analysis", "")
            print(f"💭 [{step}] {agent} 분석:")
            print(f"   {analysis[:200]}...")
        
        elif msg_type == "agent_complete":
            agent = data.get("agent", "")
            step = data.get("step", "")
            content = data.get("content", {})
            result = content.get("result", {})
            print(f"✅ [{step}] {agent} 완료")
            if isinstance(result, dict):
                verdict = result.get("verdict", "")
                confidence = result.get("confidence", 0)
                print(f"   판정: {verdict} (신뢰도: {confidence:.2f})")
        
        elif msg_type == "step_complete":
            step = data.get("step", "")
            content = data.get("content", {})
            print(f"🎯 {step} 단계 완료")
            summary = content.get("summary", {})
            if summary:
                print(f"   요약: {len(summary)} 에이전트 완료")
        
        elif msg_type == "final_result":
            content = data.get("content", {})
            verdict = content.get("verdict", "")
            confidence = content.get("confidence", 0)
            analysis = content.get("analysis", {})
            
            print(f"🏆 최종 결과:")
            print(f"   판정: {verdict}")
            print(f"   신뢰도: {confidence:.2f}")
            if isinstance(analysis, dict):
                summary = analysis.get("summary", "")
                print(f"   요약: {summary[:200]}...")
        
        elif msg_type == "progress":
            step = data.get("step", "")
            content = data.get("content", {})
            progress = content.get("progress", 0)
            message = content.get("message", "")
            print(f"📊 [{step}] 진행: {progress:.1%} - {message}")
        
        elif msg_type == "error":
            content = data.get("content", {})
            error = content.get("error", "")
            print(f"❌ 오류: {error}")
        
        else:
            print(f"❓ 알 수 없는 메시지 타입: {data}")
    
    async def start_fact_check(self, statement):
        """팩트체킹 시작"""
        message = {
            "action": "start",
            "statement": statement
        }
        await self.send_message(message)
    
    async def ping(self):
        """연결 유지용 ping"""
        message = {"action": "ping"}
        await self.send_message(message)
    
    async def close(self):
        """연결 종료"""
        if self.websocket:
            await self.websocket.close()
            print("🔌 Connection closed")

async def main():
    """메인 테스트 함수"""
    if len(sys.argv) < 2:
        print("사용법: python test_websocket_client.py '팩트체킹할 문장'")
        print("예시: python test_websocket_client.py '한국의 최저임금은 계속 증가하고 있다'")
        return
    
    statement = sys.argv[1]
    
    client = FactWaveWebSocketClient()
    
    # 연결 시도
    if not await client.connect():
        return
    
    # 리스너 태스크 시작
    listen_task = asyncio.create_task(client.listen())
    
    # 잠시 대기 후 팩트체킹 시작
    await asyncio.sleep(1)
    print(f"\n🎯 팩트체킹 시작: '{statement}'")
    await client.start_fact_check(statement)
    
    try:
        # 리스너 대기 (팩트체킹 완료까지)
        await listen_task
    except KeyboardInterrupt:
        print("\n⏹️  사용자 중단")
    finally:
        await client.close()

if __name__ == "__main__":
    print("🤖 FactWave WebSocket 클라이언트 테스트")
    print("=" * 50)
    asyncio.run(main())