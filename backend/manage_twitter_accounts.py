#!/usr/bin/env python3
"""
Twitter/X Account Manager for FactWave
Manages multiple accounts with cookies for rate limit handling
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, List, Dict
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint

try:
    from twscrape import API
    TWSCRAPE_AVAILABLE = True
except ImportError:
    TWSCRAPE_AVAILABLE = False
    print("❌ twscrape not installed. Install with: pip install twscrape")
    exit(1)

console = Console()


class TwitterAccountManager:
    """Twitter/X 계정 관리자"""
    
    def __init__(self, db_path: str = "accounts.db"):
        self.api = API(db_path)
        self.db_path = db_path
    
    async def add_account_with_cookies(
        self, 
        username: str, 
        cookies: str,
        proxy: Optional[str] = None
    ):
        """쿠키를 사용하여 계정 추가"""
        try:
            # 쿠키가 JSON 형식인지 확인
            if cookies.startswith("{"):
                # JSON 형식 쿠키
                cookie_dict = json.loads(cookies)
                cookie_string = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
            else:
                # 이미 문자열 형식
                cookie_string = cookies
            
            # 계정 추가 (쿠키 사용 시 패스워드/이메일 불필요)
            await self.api.pool.add_account(
                username=username,
                password="",  # 쿠키 사용 시 불필요
                email="",     # 쿠키 사용 시 불필요
                email_password="",  # 쿠키 사용 시 불필요
                cookies=cookie_string,
                proxy=proxy
            )
            
            console.print(f"[green]✅ 계정 추가 성공: @{username}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ 계정 추가 실패: {str(e)}[/red]")
            return False
    
    async def add_multiple_accounts_from_file(self, file_path: str):
        """파일에서 여러 계정 추가
        
        파일 형식 (accounts.txt):
        username1|ct0=xxx;auth_token=yyy
        username2|{"ct0": "xxx", "auth_token": "yyy"}
        username3|ct0=xxx;auth_token=yyy|proxy://host:port
        """
        file_path = Path(file_path)
        if not file_path.exists():
            console.print(f"[red]❌ 파일을 찾을 수 없습니다: {file_path}[/red]")
            return
        
        added_count = 0
        failed_count = 0
        
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                parts = line.split("|")
                if len(parts) < 2:
                    console.print(f"[yellow]줄 {line_num}: 잘못된 형식 (username|cookies 필요)[/yellow]")
                    failed_count += 1
                    continue
                
                username = parts[0]
                cookies = parts[1]
                proxy = parts[2] if len(parts) > 2 else None
                
                success = await self.add_account_with_cookies(username, cookies, proxy)
                if success:
                    added_count += 1
                else:
                    failed_count += 1
        
        console.print(f"\n[cyan]📊 결과: 성공 {added_count}개, 실패 {failed_count}개[/cyan]")
    
    async def show_accounts_status(self):
        """모든 계정 상태 표시"""
        try:
            accounts = await self.api.pool.accounts_info()
            
            if not accounts:
                console.print("[yellow]등록된 계정이 없습니다.[/yellow]")
                return
            
            table = Table(title="Twitter/X 계정 상태")
            table.add_column("Username", style="cyan")
            table.add_column("Active", style="green")
            table.add_column("Logged In", style="yellow")
            table.add_column("Requests", style="magenta")
            table.add_column("Last Used", style="blue")
            table.add_column("Error", style="red")
            
            for acc in accounts:
                username = acc.get('username', 'N/A')
                active = "✅" if acc.get('active', False) else "❌"
                logged_in = "✅" if acc.get('logged_in', False) else "❌"
                total_req = str(acc.get('total_req', 0))
                
                # Handle datetime object
                last_used_raw = acc.get('last_used', 'Never')
                if last_used_raw != 'Never' and last_used_raw is not None:
                    try:
                        # Convert datetime to string if needed
                        if hasattr(last_used_raw, 'strftime'):
                            last_used = last_used_raw.strftime('%Y-%m-%d %H:%M')
                        else:
                            last_used = str(last_used_raw)
                    except:
                        last_used = 'Never'
                else:
                    last_used = 'Never'
                
                error = acc.get('error_msg', '')[:30] if acc.get('error_msg') else ''
                
                table.add_row(username, active, logged_in, total_req, last_used, error)
            
            console.print(table)
            
            # 통계
            active_count = sum(1 for acc in accounts if acc.get('active', False))
            logged_in_count = sum(1 for acc in accounts if acc.get('logged_in', False))
            
            console.print(f"\n[cyan]📊 통계:[/cyan]")
            console.print(f"  • 전체 계정: {len(accounts)}개")
            console.print(f"  • 활성 계정: {active_count}개")
            console.print(f"  • 로그인됨: {logged_in_count}개")
            
        except Exception as e:
            console.print(f"[red]계정 정보 조회 실패: {str(e)}[/red]")
    
    async def relogin_failed_accounts(self):
        """실패한 계정 재로그인 시도"""
        try:
            console.print("[yellow]실패한 계정들을 재로그인 시도합니다...[/yellow]")
            await self.api.pool.relogin_failed()
            console.print("[green]✅ 재로그인 시도 완료[/green]")
        except Exception as e:
            console.print(f"[red]재로그인 실패: {str(e)}[/red]")
    
    async def delete_account(self, username: str):
        """계정 삭제"""
        try:
            await self.api.pool.delete_account(username)
            console.print(f"[green]✅ 계정 삭제 완료: @{username}[/green]")
        except Exception as e:
            console.print(f"[red]계정 삭제 실패: {str(e)}[/red]")
    
    async def set_account_active(self, username: str, active: bool):
        """계정 활성/비활성 설정"""
        try:
            await self.api.pool.set_active(username, active)
            status = "활성화" if active else "비활성화"
            console.print(f"[green]✅ 계정 {status} 완료: @{username}[/green]")
        except Exception as e:
            console.print(f"[red]계정 상태 변경 실패: {str(e)}[/red]")
    
    async def test_search(self, query: str = "test"):
        """검색 테스트 - 자동 계정 전환 확인"""
        try:
            console.print(f"[cyan]'{query}' 검색 테스트 중...[/cyan]")
            tweets = []
            async for tweet in self.api.search(query, limit=5):
                tweets.append(tweet)
            
            console.print(f"[green]✅ 검색 성공! {len(tweets)}개 트윗 발견[/green]")
            
            # 계정 사용 통계 다시 확인
            accounts = await self.api.pool.accounts_info()
            used_accounts = [acc for acc in accounts if acc.get('total_req', 0) > 0]
            console.print(f"[cyan]사용된 계정 수: {len(used_accounts)}개[/cyan]")
            
        except Exception as e:
            console.print(f"[red]검색 테스트 실패: {str(e)}[/red]")


async def interactive_menu():
    """대화형 메뉴"""
    manager = TwitterAccountManager()
    
    while True:
        console.print("\n" + "=" * 50)
        console.print("[bold cyan]Twitter/X 계정 관리자[/bold cyan]")
        console.print("=" * 50)
        console.print("1. 계정 상태 보기")
        console.print("2. 쿠키로 계정 추가 (단일)")
        console.print("3. 파일에서 계정 추가 (다중)")
        console.print("4. 실패한 계정 재로그인")
        console.print("5. 계정 삭제")
        console.print("6. 계정 활성/비활성 설정")
        console.print("7. 검색 테스트")
        console.print("8. 예제 파일 생성")
        console.print("0. 종료")
        
        choice = Prompt.ask("선택", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"])
        
        if choice == "0":
            break
        elif choice == "1":
            await manager.show_accounts_status()
        elif choice == "2":
            username = Prompt.ask("Username (@없이)")
            console.print("[yellow]쿠키 획득 방법:[/yellow]")
            console.print("1. Twitter/X 웹사이트 로그인")
            console.print("2. F12 (개발자 도구) → Storage/Application → Cookies")
            console.print("3. ct0와 auth_token 값 복사")
            cookies = Prompt.ask("쿠키 (ct0=xxx;auth_token=yyy 형식)")
            proxy = Prompt.ask("프록시 (선택사항, Enter로 건너뛰기)", default="")
            proxy = proxy if proxy else None
            await manager.add_account_with_cookies(username, cookies, proxy)
        elif choice == "3":
            file_path = Prompt.ask("파일 경로", default="accounts.txt")
            await manager.add_multiple_accounts_from_file(file_path)
        elif choice == "4":
            await manager.relogin_failed_accounts()
        elif choice == "5":
            username = Prompt.ask("삭제할 Username")
            if Confirm.ask(f"정말 @{username} 계정을 삭제하시겠습니까?"):
                await manager.delete_account(username)
        elif choice == "6":
            username = Prompt.ask("Username")
            active = Confirm.ask("활성화하시겠습니까?")
            await manager.set_account_active(username, active)
        elif choice == "7":
            query = Prompt.ask("검색어", default="AI")
            await manager.test_search(query)
        elif choice == "8":
            create_example_file()


def create_example_file():
    """예제 파일 생성"""
    example_content = """# Twitter/X 계정 파일 예제
# 형식: username|cookies|proxy(선택)
# 쿠키는 문자열 또는 JSON 형식 모두 가능

# 예제 1: 문자열 형식 쿠키
user1|ct0=abcd1234567890;auth_token=xyz987654321

# 예제 2: JSON 형식 쿠키
user2|{"ct0": "abcd1234567890", "auth_token": "xyz987654321"}

# 예제 3: 프록시 포함
user3|ct0=abcd1234567890;auth_token=xyz987654321|http://proxy.example.com:8080

# 실제 사용 시:
# 1. Twitter/X 로그인
# 2. F12 → Storage/Application → Cookies → twitter.com
# 3. ct0와 auth_token 값 복사
# 4. 위 형식으로 작성
"""
    
    with open("accounts_example.txt", "w") as f:
        f.write(example_content)
    
    console.print("[green]✅ accounts_example.txt 파일이 생성되었습니다.[/green]")
    console.print("[yellow]이 파일을 참고하여 accounts.txt를 작성하세요.[/yellow]")


async def main():
    """메인 함수"""
    import sys
    
    if len(sys.argv) > 1:
        # 명령줄 인자 처리
        manager = TwitterAccountManager()
        command = sys.argv[1]
        
        if command == "status":
            await manager.show_accounts_status()
        elif command == "add" and len(sys.argv) >= 4:
            username = sys.argv[2]
            cookies = sys.argv[3]
            proxy = sys.argv[4] if len(sys.argv) > 4 else None
            await manager.add_account_with_cookies(username, cookies, proxy)
        elif command == "add-file" and len(sys.argv) >= 3:
            file_path = sys.argv[2]
            await manager.add_multiple_accounts_from_file(file_path)
        elif command == "relogin":
            await manager.relogin_failed_accounts()
        elif command == "test":
            query = sys.argv[2] if len(sys.argv) > 2 else "AI"
            await manager.test_search(query)
        else:
            console.print("[red]사용법:[/red]")
            console.print("  python manage_twitter_accounts.py              # 대화형 메뉴")
            console.print("  python manage_twitter_accounts.py status       # 계정 상태")
            console.print("  python manage_twitter_accounts.py add <username> <cookies> [proxy]")
            console.print("  python manage_twitter_accounts.py add-file <file_path>")
            console.print("  python manage_twitter_accounts.py relogin      # 실패 계정 재로그인")
            console.print("  python manage_twitter_accounts.py test [query] # 검색 테스트")
    else:
        # 대화형 메뉴
        await interactive_menu()


if __name__ == "__main__":
    asyncio.run(main())