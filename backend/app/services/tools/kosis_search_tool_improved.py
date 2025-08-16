"""KOSIS Search Tool - 개선된 버전 (오류 수정 및 더 많은 데이터 수집)"""

from typing import Type, Optional, Dict, List, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import os
import PublicDataReader as pdr
import pandas as pd
from datetime import datetime, timedelta


class KOSISSearchInput(BaseModel):
    query: str = Field(..., description="검색어 (예: GDP, 인구, 실업률)")
    limit: int = Field(5, description="검색 결과 개수 (최대 20)")
    fetch_data: bool = Field(True, description="통계 데이터도 함께 가져올지 여부")
    years: int = Field(10, description="최근 몇 년 데이터를 가져올지")


class KOSISSearchTool(BaseTool):
    """KOSIS 통합검색을 통한 자연어 통계 검색 (개선된 버전)"""

    name: str = "KOSIS_Natural_Search_Improved"
    description: str = (
        "KOSIS 통계를 자연어로 검색하고 데이터를 가져옵니다. "
        "예: 'GDP', '인구', '실업률', '소비자물가지수' 등"
    )
    args_schema: Type[BaseModel] = KOSISSearchInput

    def _run(
        self,
        query: str,
        limit: int = 5,
        fetch_data: bool = True,
        years: int = 10
    ) -> str:
        """KOSIS 자연어 검색 실행 (개선된 버전)"""
        
        # API 키 확인 (따옴표 제거)
        api_key = os.getenv("KOSIS_API_KEY", "").strip('"')
        if not api_key:
            return "❌ KOSIS API 키가 설정되지 않았습니다. 환경변수 KOSIS_API_KEY를 설정하세요."

        collected_data = []  # 수집된 모든 데이터 저장
        
        try:
            # PublicDataReader API 인스턴스 생성
            api = pdr.Kosis(api_key)
            
            # 1단계: 통합검색 (오류 발생 전 부분)
            try:
                # 통합검색 API 호출 - PublicDataReader 문서 기반
                search_results = api.get_data(
                    "KOSIS통합검색",
                    searchNm=query
                    # sort, startCount, resultCount는 선택사항
                )
            except Exception as search_error:
                # 통합검색 실패 시 직접 알려진 테이블 검색
                print(f"통합검색 API 오류: {search_error}")
                search_results = self._fallback_search(api, query, limit)
            
            if not isinstance(search_results, pd.DataFrame) or search_results.empty:
                return f"❌ '{query}'에 대한 통계표를 찾을 수 없습니다."
            
            # 결과 포맷팅
            result = f"🔍 KOSIS 검색: '{query}'\n"
            result += f"📊 {len(search_results)}개 통계표 발견\n\n"
            
            # 검색 결과 표시 및 데이터 수집
            data_fetched_count = 0
            max_data_fetch = min(3, len(search_results))  # 최대 3개 테이블에서 데이터 가져오기
            
            for idx in range(min(len(search_results), limit)):
                row = search_results.iloc[idx]
                
                # 컬럼명 확인 (한글/영문)
                org_id = row.get('기관ID', row.get('ORG_ID', ''))
                tbl_id = row.get('통계표ID', row.get('TBL_ID', ''))
                tbl_nm = row.get('통계표명', row.get('TBL_NM', ''))
                org_nm = row.get('기관명', row.get('ORG_NM', ''))
                contents = row.get('통계표주요내용', row.get('CONTENTS', ''))
                
                result += f"[{idx + 1}] {tbl_nm}\n"
                result += f"    기관: {org_nm} ({org_id})\n"
                result += f"    테이블ID: {tbl_id}\n"
                
                if contents:
                    content_preview = contents[:100] + "..." if len(contents) > 100 else contents
                    result += f"    설명: {content_preview}\n"
                
                # 상위 3개 테이블의 데이터 가져오기
                if fetch_data and data_fetched_count < max_data_fetch:
                    result += f"\n    📈 데이터 ({years}년간):\n"
                    table_data = self._fetch_table_data_improved(
                        api, org_id, tbl_id, tbl_nm, years
                    )
                    
                    if table_data["success"]:
                        result += table_data["formatted"]
                        collected_data.append({
                            "table_name": tbl_nm,
                            "table_id": tbl_id,
                            "data": table_data["raw_data"]
                        })
                        data_fetched_count += 1
                    else:
                        result += f"    {table_data['error']}\n"
                
                result += "\n"
            
            # 수집된 데이터 요약
            if collected_data:
                result += "\n📊 데이터 수집 요약:\n"
                for data_item in collected_data:
                    result += f"  - {data_item['table_name']}: {len(data_item['data'])}개 데이터포인트\n"
            
            # 데이터를 파일로 저장 (선택적)
            if collected_data and fetch_data:
                self._save_collected_data(query, collected_data)
                result += f"\n💾 상세 데이터가 저장되었습니다."
            
            return result
            
        except Exception as e:
            return f"❌ KOSIS API 오류: {str(e)}"
    
    def _fallback_search(self, api, query: str, limit: int) -> pd.DataFrame:
        """통합검색 실패 시 알려진 테이블 직접 검색"""
        # GDP 관련 알려진 테이블
        known_tables = {
            "GDP": [
                {"기관ID": "301", "통계표ID": "DT_200Y001", "통계표명": "국내총생산(명목, 원화표시)", "기관명": "한국은행"},
                {"기관ID": "301", "통계표ID": "DT_200Y002", "통계표명": "경제활동별 GDP", "기관명": "한국은행"},
                {"기관ID": "301", "통계표ID": "DT_200Y003", "통계표명": "지출항목별 GDP", "기관명": "한국은행"}
            ],
            "실업률": [
                {"기관ID": "101", "통계표ID": "DT_1DA7002S", "통계표명": "실업률", "기관명": "통계청"},
                {"기관ID": "101", "통계표ID": "DT_1DA7004S", "통계표명": "고용률", "기관명": "통계청"}
            ],
            "인구": [
                {"기관ID": "101", "통계표ID": "DT_1B040A3", "통계표명": "주민등록인구", "기관명": "통계청"},
                {"기관ID": "101", "통계표ID": "DT_1B040M5", "통계표명": "시도별 인구", "기관명": "통계청"}
            ]
        }
        
        # 쿼리와 매칭되는 테이블 찾기
        matched_tables = []
        query_lower = query.lower()
        
        for key, tables in known_tables.items():
            if key.lower() in query_lower or query_lower in key.lower():
                matched_tables.extend(tables[:limit])
        
        if matched_tables:
            return pd.DataFrame(matched_tables)
        else:
            return pd.DataFrame()
    
    def _fetch_table_data_improved(
        self, api, org_id: str, tbl_id: str, tbl_nm: str, years: int
    ) -> Dict[str, Any]:
        """개선된 데이터 가져오기 - 더 많은 시도와 대체 방법"""
        
        current_year = datetime.now().year
        start_year = current_year - years
        
        # 여러 방법으로 데이터 가져오기 시도
        attempts = [
            # 시도 1: 연간 데이터 (전체 기간)
            {
                "params": {
                    "orgId": str(org_id),
                    "tblId": str(tbl_id),
                    "itmId": "ALL",
                    "objL1": "ALL",
                    "objL2": "ALL",
                    "objL3": "ALL",
                    "objL4": "ALL",
                    "objL5": "ALL",
                    "objL6": "ALL",
                    "objL7": "ALL",
                    "objL8": "ALL",
                    "prdSe": "Y",
                    "startPrdDe": str(start_year),
                    "endPrdDe": str(current_year),
                    "apiKey": api.api_key  # apiKey 명시적 추가
                },
                "description": "연간 전체 기간"
            },
            # 시도 2: 최근 N개 연간 데이터
            {
                "params": {
                    "orgId": str(org_id),
                    "tblId": str(tbl_id),
                    "itmId": "ALL",
                    "objL1": "ALL",
                    "objL2": "ALL",
                    "prdSe": "Y",
                    "newEstPrdCnt": str(years),
                    "apiKey": api.api_key  # apiKey 명시적 추가
                },
                "description": f"최근 {years}년"
            },
            # 시도 3: 분기 데이터
            {
                "params": {
                    "orgId": str(org_id),
                    "tblId": str(tbl_id),
                    "itmId": "ALL",
                    "objL1": "ALL",
                    "objL2": "ALL",
                    "prdSe": "Q",
                    "newEstPrdCnt": "20",
                    "apiKey": api.api_key  # apiKey 명시적 추가
                },
                "description": "최근 20분기"
            },
            # 시도 4: 월간 데이터
            {
                "params": {
                    "orgId": str(org_id),
                    "tblId": str(tbl_id),
                    "itmId": "ALL",
                    "objL1": "ALL",
                    "objL2": "ALL",
                    "prdSe": "M",
                    "newEstPrdCnt": "60",
                    "apiKey": api.api_key  # apiKey 명시적 추가
                },
                "description": "최근 60개월"
            }
        ]
        
        for attempt in attempts:
            try:
                data = api.get_data("통계자료", **attempt["params"])
                
                if isinstance(data, pd.DataFrame) and not data.empty:
                    # 데이터 포맷팅
                    formatted_data, raw_data = self._format_data_improved(data, tbl_nm)
                    
                    if formatted_data:
                        return {
                            "success": True,
                            "formatted": formatted_data,
                            "raw_data": raw_data,
                            "method": attempt["description"]
                        }
            except Exception as e:
                continue
        
        return {
            "success": False,
            "error": "(데이터 조회 실패 - 모든 방법 시도함)",
            "raw_data": []
        }
    
    def _format_data_improved(self, data: pd.DataFrame, tbl_nm: str) -> tuple:
        """개선된 데이터 포맷팅 - 더 많은 데이터 표시"""
        
        # 주요 컬럼 찾기
        period_cols = ['PRD_DE', 'PRD_YM', '수록시점', 'PERIOD', 'TIME']
        value_cols = ['DT', '수치값', 'DATA_VALUE', 'VAL', 'VALUE']
        unit_cols = ['UNIT_NM', '단위명', 'UNIT', '단위']
        item_cols = ['ITM_NM', '항목명', 'ITEM', '항목']
        c1_cols = ['C1_NM', '분류1명', 'CLASS1', 'C1', '분류1']
        c2_cols = ['C2_NM', '분류2명', 'CLASS2', 'C2', '분류2']
        
        # 실제 컬럼 찾기
        period_col = next((col for col in period_cols if col in data.columns), None)
        value_col = next((col for col in value_cols if col in data.columns), None)
        unit_col = next((col for col in unit_cols if col in data.columns), None)
        item_col = next((col for col in item_cols if col in data.columns), None)
        c1_col = next((col for col in c1_cols if col in data.columns), None)
        c2_col = next((col for col in c2_cols if col in data.columns), None)
        
        if not period_col or not value_col:
            return "", []
        
        # 데이터 정렬 및 필터링
        data_sorted = data.sort_values(by=period_col, ascending=False)
        
        # NULL이 아닌 값만 필터링
        data_valid = data_sorted[data_sorted[value_col].notna()]
        
        if data_valid.empty:
            return "", []
        
        # 최대 20개 데이터 포인트 표시
        display_limit = min(20, len(data_valid))
        formatted_lines = []
        raw_data = []
        
        # 항목별로 그룹화 (있는 경우)
        if item_col and item_col in data_valid.columns:
            items = data_valid[item_col].unique()[:3]  # 최대 3개 항목
            
            for item in items:
                item_data = data_valid[data_valid[item_col] == item].head(5)
                if not item_data.empty:
                    formatted_lines.append(f"    [{item}]")
                    
                    for _, row in item_data.iterrows():
                        period = row[period_col]
                        value = row[value_col]
                        
                        # 값 포맷팅
                        try:
                            val = float(value)
                            if "율" in tbl_nm or "%" in str(row.get(unit_col, "")):
                                formatted_value = f"{val:.2f}%"
                            elif val > 1e12:
                                formatted_value = f"{val/1e12:.2f}조"
                            elif val > 1e8:
                                formatted_value = f"{val/1e8:.2f}억"
                            elif val > 1e4:
                                formatted_value = f"{val/1e4:.1f}만"
                            else:
                                formatted_value = f"{val:,.2f}"
                        except:
                            formatted_value = str(value)
                        
                        line = f"      {period}: {formatted_value}"
                        
                        if unit_col and pd.notna(row.get(unit_col)):
                            unit = row[unit_col]
                            if unit and unit not in formatted_value:
                                line += f" {unit}"
                        
                        formatted_lines.append(line)
                        
                        # Raw data 저장
                        raw_data.append({
                            "period": str(period),
                            "value": value,
                            "item": item,
                            "unit": row.get(unit_col, "")
                        })
        else:
            # 항목 구분 없이 표시
            for idx, row in data_valid.head(display_limit).iterrows():
                period = row[period_col]
                value = row[value_col]
                
                # 값 포맷팅
                try:
                    val = float(value)
                    if "율" in tbl_nm or "%" in str(row.get(unit_col, "")):
                        formatted_value = f"{val:.2f}%"
                    elif val > 1e12:
                        formatted_value = f"{val/1e12:.2f}조"
                    elif val > 1e8:
                        formatted_value = f"{val/1e8:.2f}억"
                    elif val > 1e4:
                        formatted_value = f"{val/1e4:.1f}만"
                    else:
                        formatted_value = f"{val:,.2f}"
                except:
                    formatted_value = str(value)
                
                line = f"    {period}: {formatted_value}"
                
                if unit_col and pd.notna(row.get(unit_col)):
                    unit = row[unit_col]
                    if unit and unit not in formatted_value:
                        line += f" {unit}"
                
                if c1_col and pd.notna(row.get(c1_col)):
                    line += f" [{row[c1_col]}]"
                
                formatted_lines.append(line)
                
                # Raw data 저장
                raw_data.append({
                    "period": str(period),
                    "value": value,
                    "unit": row.get(unit_col, ""),
                    "class1": row.get(c1_col, "")
                })
        
        # 데이터가 더 있으면 표시
        if len(data_valid) > display_limit:
            formatted_lines.append(f"    ... 외 {len(data_valid) - display_limit}개 데이터")
        
        return "\n".join(formatted_lines), raw_data
    
    def _save_collected_data(self, query: str, collected_data: List[Dict]):
        """수집된 데이터를 파일로 저장"""
        import json
        from pathlib import Path
        
        # 저장 디렉토리 생성
        save_dir = Path("kosis_data")
        save_dir.mkdir(exist_ok=True)
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = save_dir / f"kosis_{query}_{timestamp}.json"
        
        # 데이터 저장
        save_data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "tables": collected_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 데이터 저장: {filename}")