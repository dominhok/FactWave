"""KOSIS Search Tool - PublicDataReader 기반 자연어 검색"""

from typing import Type, Optional, Dict, List, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import os
import PublicDataReader as pdr
import pandas as pd


class KOSISSearchInput(BaseModel):
    query: str = Field(..., description="검색어 (예: GDP, 인구, 실업률)")
    limit: int = Field(5, description="검색 결과 개수 (최대 20)")
    fetch_data: bool = Field(True, description="통계 데이터도 함께 가져올지 여부")


class KOSISSearchTool(BaseTool):
    """KOSIS 통합검색을 통한 자연어 통계 검색 (PublicDataReader 사용)"""

    name: str = "KOSIS_Natural_Search"
    description: str = (
        "KOSIS 통계를 자연어로 검색하고 데이터를 가져옵니다. "
        "예: 'GDP', '인구', '실업률', '소비자물가지수' 등"
    )
    args_schema: Type[BaseModel] = KOSISSearchInput

    def _run(
        self,
        query: str,
        limit: int = 5,
        fetch_data: bool = True
    ) -> str:
        """KOSIS 자연어 검색 실행 - LLM 친화적 구조화 출력"""
        
        # API 키 확인 (따옴표 제거)
        api_key = os.getenv("KOSIS_API_KEY", "").strip('"')
        if not api_key:
            return "❌ KOSIS API 키가 설정되지 않았습니다. 환경변수 KOSIS_API_KEY를 설정하세요."

        try:
            # PublicDataReader API 인스턴스 생성
            api = pdr.Kosis(api_key)
            
            # 1단계: 통합검색
            search_results = api.get_data(
                "KOSIS통합검색",
                searchNm=query
                # sort, startCount, resultCount는 선택사항
            )
            
            if not isinstance(search_results, pd.DataFrame) or search_results.empty:
                return f"❌ '{query}'에 대한 통계표를 찾을 수 없습니다."
            
            # LLM 친화적 구조화 출력 생성
            return self._format_structured_output(query, search_results, api, limit, fetch_data)
            
        except Exception as e:
            return f"❌ KOSIS API 오류: {str(e)}"
    
    def _format_structured_output(self, query: str, search_results: pd.DataFrame, api, limit: int, fetch_data: bool) -> str:
        """구조화된 LLM 친화적 출력 형식으로 변환"""
        
        if not isinstance(search_results, pd.DataFrame) or search_results.empty:
            return f"❌ '{query}'에 대한 통계표를 찾을 수 없습니다."
        
        # 출력 시작
        result = []
        result.append(f"📊 KOSIS 통계 검색 결과: '{query}'")
        result.append("━" * 60)
        result.append(f"📌 출처: 통계청 국가통계포털(KOSIS)")
        result.append(f"📊 발견된 통계표: {len(search_results)}개\n")
        
        # 각 통계표별 구조화된 정보 표시
        for idx in range(min(len(search_results), limit)):
            row = search_results.iloc[idx]
            
            # 메타데이터 추출
            metadata = self._extract_table_metadata(row)
            
            # 구조화된 테이블 정보
            result.append(f"📈 [{idx + 1}] {metadata['table_name']}")
            result.append("─" * 40)
            result.append(f"🏛️  제공기관: {metadata['organization']}")
            result.append(f"📋  테이블ID: {metadata['table_id']}")
            
            if metadata['description']:
                result.append(f"📝  설명: {metadata['description']}")
            
            # 실제 데이터 가져오기
            if fetch_data:
                data_summary = self._fetch_and_format_data(
                    api, metadata['org_id'], metadata['table_id'], metadata['table_name']
                )
                result.append("")
                result.append("📊 실제 통계 데이터:")
                result.append(data_summary)
            
            result.append("")  # 구분선
        
        return "\n".join(result)
    
    def _extract_table_metadata(self, row: pd.Series) -> Dict[str, str]:
        """통계표 메타데이터 추출"""
        
        # 기관명 매핑
        org_id = str(row.get('기관ID', row.get('ORG_ID', '')))
        org_map = {'101': '통계청', '301': '한국은행', '136': '고용노동부'}
        org_name = org_map.get(org_id, f"기관ID {org_id}")
        
        return {
            'org_id': org_id,
            'organization': org_name,
            'table_id': str(row.get('통계표ID', row.get('TBL_ID', ''))),
            'table_name': str(row.get('통계표명', row.get('TBL_NM', ''))),
            'description': str(row.get('통계표주요내용', row.get('CONTENTS', '')))[:150] + "..." if len(str(row.get('통계표주요내용', row.get('CONTENTS', '')))) > 150 else str(row.get('통계표주요내용', row.get('CONTENTS', '')))
        }
    
    def _fetch_and_format_data(self, api, org_id: str, tbl_id: str, table_name: str) -> str:
        """데이터를 가져와서 LLM 친화적 형식으로 포맷팅"""
        
        try:
            # 기본 파라미터로 데이터 조회
            data = api.get_data(
                "통계자료",
                orgId=str(org_id),
                tblId=str(tbl_id),
                objL1="ALL",
                itmId="ALL",
                prdSe="Y",  # 연간
                newEstPrdCnt="5"  # 최근 5개년
            )
            
            if isinstance(data, pd.DataFrame) and not data.empty:
                return self._format_data_for_llm(data, table_name)
            else:
                return "  ⚠️ 데이터를 불러올 수 없습니다."
                
        except Exception as e:
            return f"  ⚠️ 데이터 조회 실패: {str(e)[:50]}..."
    
    def _format_data_for_llm(self, data: pd.DataFrame, table_name: str) -> str:
        """데이터와 모든 메타데이터를 있는 그대로 전달"""
        
        if data.empty:
            return "  ⚠️ 데이터가 없습니다."
        
        # 첫 번째 행의 모든 메타데이터 표시
        first_row = data.iloc[0]
        result = []
        result.append("  📁 데이터 메타데이터:")
        
        # 모든 컬럼을 있는 그대로 표시
        for col_name, col_value in first_row.items():
            if pd.notna(col_value) and str(col_value).strip():
                result.append(f"    • {col_name}: {col_value}")
        
        result.append("")
        result.append(f"  📈 샘플 데이터 (10개 행):")
        
        # 최대 10개 행의 모든 데이터 표시
        sample_data = data.head(10)
        for idx, row in sample_data.iterrows():
            result.append(f"    [{idx+1}]")
            for col_name, col_value in row.items():
                if pd.notna(col_value) and str(col_value).strip():
                    result.append(f"      {col_name}: {col_value}")
            result.append("")
        
        if len(data) > 10:
            result.append(f"  … 외 {len(data)-10}개 행 더 있음")
        
        return "\n".join(result)
    
    
