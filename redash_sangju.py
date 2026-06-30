import streamlit as st
import pandas as pd
import plotly.express as px
import json
import requests
from pathlib import Path
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium

# ==========================================
# 담당자 매핑 (Redash RegionManager CTE 대체)
# key: 시도+시군구 (공백 제거), value: (바로고, 모아라인, 딜버)
# ==========================================
REGION_MANAGER = {
    '강원강릉시':('정규호','평정현','정규호'),'강원고성군':('정규호','평정현','정규호'),
    '강원동해시':('정규호','평정현','정규호'),'강원삼척시':('정규호','평정현','정규호'),
    '강원속초시':('정규호','평정현','정규호'),'강원양구군':('정규호','평정현','정규호'),
    '강원양양군':('정규호','평정현','정규호'),'강원영월군':('정규호','평정현','정규호'),
    '강원원주시':('정규호','평정현','정규호'),'강원인제군':('정규호','평정현','정규호'),
    '강원정선군':('정규호','평정현','정규호'),'강원철원군':('정규호','평정현','정규호'),
    '강원춘천시':('정규호','평정현','정규호'),'강원태백시':('정규호','평정현','정규호'),
    '강원평창군':('정규호','평정현','정규호'),'강원홍천군':('정규호','평정현','정규호'),
    '강원화천군':('정규호','평정현','정규호'),'강원횡성군':('정규호','평정현','정규호'),
    '경기가평군':('손정','평정현','손정'),'경기고양시':('박상무','평정현','손정'),
    '경기고양시덕양구':('박상무','평정현','박상무'),'경기고양시일산동구':('손정','평정현','손정'),
    '경기고양시일산서구':('손정','평정현','손정'),'경기과천시':('유승우','평정현','유승우'),
    '경기광명시':('정승기','평정현','정승기'),'경기광주시':('정승기','평정현','정승기'),
    '경기구리시':('손정','평정현','손정'),'경기군포시':('유승우','평정현','유승우'),
    '경기김포시':('유승우','평정현','유승우'),'경기남양주시':('손정','평정현','손정'),
    '경기동두천시':('손정','평정현','손정'),'경기부천시':('유승우','평정현','유승우'),
    '경기부천시소사구':('유승우','평정현','유승우'),'경기부천시오정구':('유승우','평정현','유승우'),
    '경기부천시원미구':('유승우','평정현','유승우'),'경기성남시':('정승기','평정현','정승기'),
    '경기성남시분당구':('정승기','평정현','정승기'),'경기성남시수정구':('정승기','평정현','정승기'),
    '경기성남시중원구':('정승기','평정현','정승기'),'경기수원시':('권혁희','평정현','권혁희'),
    '경기수원시권선구':('권혁희','평정현','권혁희'),'경기수원시영통구':('권혁희','평정현','권혁희'),
    '경기수원시장안구':('권혁희','평정현','권혁희'),'경기수원시팔달구':('권혁희','평정현','권혁희'),
    '경기시흥시':('유승우','평정현','유승우'),'경기안산시':('유승우','평정현','유승우'),
    '경기안산시단원구':('유승우','평정현','유승우'),'경기안산시상록구':('유승우','평정현','유승우'),
    '경기안성시':('정승기','평정현','정승기'),'경기안양시':('유승우','평정현','유승우'),
    '경기안양시동안구':('유승우','평정현','유승우'),'경기안양시만안구':('유승우','평정현','유승우'),
    '경기양주시':('손정','평정현','손정'),'경기양평군':('손정','평정현','손정'),
    '경기여주시':('정승기','평정현','정승기'),'경기연천군':('손정','평정현','손정'),
    '경기오산시':('권혁희','평정현','권혁희'),'경기용인시':('정승기','평정현','정승기'),
    '경기용인시기흥구':('권혁희','평정현','권혁희'),'경기용인시수지구':('권혁희','평정현','권혁희'),
    '경기용인시처인구':('정승기','평정현','정승기'),'경기의왕시':('유승우','평정현','유승우'),
    '경기의정부시':('손정','평정현','손정'),'경기이천시':('정승기','평정현','정승기'),
    '경기일산동구':('손정','평정현','손정'),'경기일산서구':('손정','평정현','손정'),
    '경기파주시':('손정','평정현','손정'),'경기평택시':('정승기','평정현','정승기'),
    '경기포천시':('손정','평정현','손정'),'경기하남시':('정승기','평정현','정승기'),
    '경기화성시':('권혁희','평정현','권혁희'),'경기화성시동탄구':('권혁희','평정현','권혁희'),
    '경기화성시병점구':('권혁희','평정현','권혁희'),'경기화성시효행구':('권혁희','평정현','권혁희'),
    '경기화성시만세구':('권혁희','평정현','권혁희'),
    '경남거제시':('왕지현','왕지현','왕지현'),'경남거창군':('왕지현','왕지현','왕지현'),
    '경남고성군':('왕지현','왕지현','왕지현'),'경남김해시':('김영철','김영철','김영철'),
    '경남남해군':('왕지현','왕지현','왕지현'),'경남밀양시':('왕지현','왕지현','왕지현'),
    '경남사천시':('왕지현','왕지현','왕지현'),'경남산청군':('왕지현','왕지현','왕지현'),
    '경남양산시':('정승기','정승기','정승기'),'경남의령군':('왕지현','왕지현','왕지현'),
    '경남진주시':('김영철','김영철','김영철'),'경남창녕군':('왕지현','왕지현','왕지현'),
    '경남창원시':('김영철','김영철','김영철'),'경남창원시마산합포구':('김영철','김영철','김영철'),
    '경남창원시마산회원구':('김영철','김영철','김영철'),'경남창원시성산구':('김영철','김영철','김영철'),
    '경남창원시의창구':('김영철','김영철','김영철'),'경남창원시진해구':('김영철','김영철','김영철'),
    '경남통영시':('왕지현','왕지현','왕지현'),'경남하동군':('왕지현','왕지현','왕지현'),
    '경남함안군':('왕지현','왕지현','왕지현'),'경남함양군':('왕지현','왕지현','왕지현'),
    '경남합천군':('왕지현','왕지현','왕지현'),
    '경북경산시':('왕지현','왕지현','왕지현'),'경북경주시':('정승기','정승기','정승기'),
    '경북고령군':('왕지현','왕지현','왕지현'),'경북구미시':('권혁희','권혁희','권혁희'),
    '경북김천시':('권혁희','권혁희','권혁희'),'경북문경시':('정규호','정규호','정규호'),
    '경북봉화군':('권혁희','권혁희','권혁희'),'경북상주시':('정규호','정규호','정규호'),
    '경북성주군':('왕지현','왕지현','왕지현'),'경북안동시':('심항보','심항보','심항보'),
    '경북영덕군':('왕지현','왕지현','왕지현'),'경북영양군':('왕지현','왕지현','왕지현'),
    '경북영주시':('왕지현','왕지현','왕지현'),'경북영천시':('권혁희','권혁희','권혁희'),
    '경북예천군':('권혁희','권혁희','권혁희'),'경북울진군':('왕지현','왕지현','왕지현'),
    '경북의성군':('왕지현','왕지현','왕지현'),'경북청도군':('왕지현','왕지현','왕지현'),
    '경북청송군':('왕지현','왕지현','왕지현'),'경북칠곡군':('왕지현','왕지현','왕지현'),
    '경북포항시':('정승기','정승기','정승기'),'경북포항시남구':('정승기','정승기','정승기'),
    '경북포항시북구':('정승기','정승기','정승기'),
    '광주광산구':('이윤상','이윤상','이윤상'),'광주남구':('이윤상','이윤상','이윤상'),
    '광주동구':('이윤상','이윤상','이윤상'),'광주북구':('이윤상','이윤상','이윤상'),
    '광주서구':('이윤상','이윤상','이윤상'),
    '대구군위군':('김완욱','김다한','김다한'),'대구남구':('정규호','정규호','정규호'),
    '대구달서구':('정규호','정규호','정규호'),'대구달성군':('정규호','정규호','정규호'),
    '대구동구':('정규호','정규호','정규호'),'대구북구':('정규호','정규호','정규호'),
    '대구서구':('정규호','정규호','정규호'),'대구수성구':('정규호','정규호','정규호'),
    '대구중구':('정규호','정규호','정규호'),
    '대전대덕구':('심항보','심항보','심항보'),'대전동구':('심항보','심항보','심항보'),
    '대전서구':('심항보','심항보','심항보'),'대전유성구':('심항보','심항보','심항보'),
    '대전중구':('심항보','심항보','심항보'),
    '부산강서구':('김영철','김영철','김영철'),'부산금정구':('김영철','김영철','김영철'),
    '부산기장군':('김영철','김영철','김영철'),'부산남구':('김영철','김영철','김영철'),
    '부산동구':('김영철','김영철','김영철'),'부산동래구':('김영철','김영철','김영철'),
    '부산부산진구':('김영철','김영철','김영철'),'부산북구':('김영철','김영철','김영철'),
    '부산사상구':('김영철','김영철','김영철'),'부산사하구':('김영철','김영철','김영철'),
    '부산서구':('김영철','김영철','김영철'),'부산수영구':('김영철','김영철','김영철'),
    '부산연제구':('김영철','김영철','김영철'),'부산영도구':('김영철','김영철','김영철'),
    '부산중구':('김영철','김영철','김영철'),'부산해운대구':('김영철','김영철','김영철'),
    '서울강남구':('박상무','평정현','박상무'),'서울강동구':('박상무','평정현','박상무'),
    '서울강북구':('박상무','평정현','박상무'),'서울강서구':('박상무','평정현','박상무'),
    '서울관악구':('박상무','평정현','박상무'),'서울광진구':('박상무','평정현','박상무'),
    '서울구로구':('박상무','평정현','박상무'),'서울금천구':('박상무','평정현','박상무'),
    '서울노원구':('박상무','평정현','박상무'),'서울도봉구':('박상무','평정현','박상무'),
    '서울동대문구':('박상무','평정현','박상무'),'서울동작구':('박상무','평정현','박상무'),
    '서울마포구':('박상무','평정현','박상무'),'서울서대문구':('박상무','평정현','박상무'),
    '서울서초구':('박상무','평정현','박상무'),'서울성동구':('박상무','평정현','박상무'),
    '서울성북구':('박상무','평정현','박상무'),'서울송파구':('박상무','평정현','박상무'),
    '서울양천구':('박상무','평정현','박상무'),'서울영등포구':('박상무','평정현','박상무'),
    '서울용산구':('박상무','평정현','박상무'),'서울은평구':('박상무','평정현','박상무'),
    '서울종로구':('박상무','평정현','박상무'),'서울중구':('박상무','평정현','박상무'),
    '서울중랑구':('박상무','평정현','박상무'),
    '세종세종시':('심항보','심항보','심항보'),'세종조치원읍':('심항보','심항보','심항보'),
    '울산남구':('왕지현','왕지현','왕지현'),'울산동구':('왕지현','왕지현','왕지현'),
    '울산북구':('왕지현','왕지현','왕지현'),'울산울주군':('왕지현','왕지현','왕지현'),
    '울산중구':('왕지현','왕지현','왕지현'),
    '인천강화군':('손정','평정현','손정'),'인천계양구':('유승우','평정현','유승우'),
    '인천남동구':('손정','평정현','손정'),'인천남동구구월동':('손정','평정현','손정'),
    '인천동구':('손정','평정현','손정'),'인천미추홀구':('손정','평정현','손정'),
    '인천부평구':('유승우','평정현','유승우'),'인천서구':('손정','평정현','손정'),
    '인천연수구':('손정','평정현','손정'),'인천옹진군':('손정','평정현','손정'),
    '인천중구':('손정','평정현','손정'),
    '전남강진군':('이윤상','이윤상','이윤상'),'전남고흥군':('이윤상','이윤상','이윤상'),
    '전남곡성군':('이윤상','이윤상','이윤상'),'전남광양시':('이윤상','이윤상','이윤상'),
    '전남구례군':('이윤상','이윤상','이윤상'),'전남나주시':('이윤상','이윤상','이윤상'),
    '전남담양군':('이윤상','이윤상','이윤상'),'전남목포시':('이윤상','이윤상','이윤상'),
    '전남무안군':('이윤상','이윤상','이윤상'),'전남보성군':('이윤상','이윤상','이윤상'),
    '전남순천시':('이윤상','이윤상','이윤상'),'전남신안군':('이윤상','이윤상','이윤상'),
    '전남여수시':('이윤상','이윤상','이윤상'),'전남영광군':('이윤상','이윤상','이윤상'),
    '전남영암군':('이윤상','이윤상','이윤상'),'전남완도군':('이윤상','이윤상','이윤상'),
    '전남장성군':('이윤상','이윤상','이윤상'),'전남장흥군':('이윤상','이윤상','이윤상'),
    '전남진도군':('이윤상','이윤상','이윤상'),'전남함평군':('이윤상','이윤상','이윤상'),
    '전남해남군':('이윤상','이윤상','이윤상'),'전남화순군':('이윤상','이윤상','이윤상'),
    '전북고창군':('이윤상','이윤상','이윤상'),'전북군산시':('심항보','심항보','심항보'),
    '전북김제시':('심항보','심항보','심항보'),'전북남원시':('이윤상','이윤상','이윤상'),
    '전북무주군':('심항보','심항보','심항보'),'전북부안군':('김정교','김정교','김정교'),
    '전북순창군':('전정재','김정교','김정교'),'전북완주군':('심항보','심항보','심항보'),
    '전북익산시':('심항보','심항보','심항보'),'전북임실군':('이윤상','이윤상','이윤상'),
    '전북장수군':('이윤상','이윤상','이윤상'),'전북전주시':('심항보','심항보','심항보'),
    '전북전주시덕진구':('심항보','심항보','심항보'),'전북전주시완산구':('심항보','심항보','심항보'),
    '전북정읍시':('이윤상','이윤상','이윤상'),'전북진안군':('심항보','심항보','심항보'),
    '제주서귀포시':('정승기','정승기','정승기'),'제주제주시':('정승기','정승기','정승기'),
    '충남계룡시':('강인선','강인선','강인선'),'충남공주시':('강인선','강인선','강인선'),
    '충남금산군':('강인선','강인선','강인선'),'충남논산시':('강인선','강인선','강인선'),
    '충남당진시':('강인선','강인선','강인선'),'충남보령시':('강인선','강인선','강인선'),
    '충남부여군':('강인선','강인선','강인선'),'충남서산시':('강인선','강인선','강인선'),
    '충남서천군':('강인선','강인선','강인선'),'충남아산시':('강인선','강인선','강인선'),
    '충남예산군':('강인선','강인선','강인선'),'충남천안시':('강인선','강인선','강인선'),
    '충남천안시동남구':('강인선','강인선','강인선'),'충남천안시서북구':('강인선','강인선','강인선'),
    '충남청양군':('강인선','강인선','강인선'),'충남태안군':('강인선','강인선','강인선'),
    '충남홍성군':('강인선','강인선','강인선'),
    '충북괴산군':('심항보','심항보','심항보'),'충북단양군':('심항보','심항보','심항보'),
    '충북보은군':('심항보','심항보','심항보'),'충북영동군':('심항보','심항보','심항보'),
    '충북옥천군':('심항보','심항보','심항보'),'충북음성군':('심항보','심항보','심항보'),
    '충북제천시':('심항보','심항보','심항보'),'충북증평군':('심항보','심항보','심항보'),
    '충북진천군':('심항보','심항보','심항보'),'충북청주시':('심항보','심항보','심항보'),
    '충북청주시상당구':('심항보','심항보','심항보'),'충북청주시서원구':('심항보','심항보','심항보'),
    '충북청주시청원구':('심항보','심항보','심항보'),'충북청주시흥덕구':('심항보','심항보','심항보'),
    '충북충주시':('심항보','심항보','심항보'),
}

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(page_title="B2B 요금제 전략 대시보드", layout="wide")
st.title("🗺️ 전국 B2B 상점/주소기반 현황")

# ==========================================
# 2. 데이터 로드 (Google Sheets CSV)
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1G51UtaMeDoPEyo6gJQHZMUoxqjcYLVA70C4axZjOj84/export?format=csv&gid=0"

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(SHEET_URL)

    # 메모리 절약: 집계/표시에 필요한 컬럼만 유지
    # 메인수행허브·공유수행허브는 허브명 수십 개가 들어간 긴 문자열 → 제외
    keep_cols = [
        '상점관리주체(브랜드)', '고릴라상점코드', '최신타임라인날짜', '상점명', '상태',
        '배송사', '시도', '시군구', '읍면동', '매입타입',
        '매입대행료(기본)', '총판선차감', '허브선차감',
        '최근한달주문건수', '위도(Latitude)', '경도(Longitude)'
    ]
    df = df[[c for c in keep_cols if c in df.columns]]

    df = df.rename(columns={'위도(Latitude)': 'lon', '경도(Longitude)': 'lat'})
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    # dropna는 지도 섹션에서만 적용 — 여기서 날리면 좌표 없는 상점이 집계에서 사라짐

    # 담당자 계산: 시도+시군구 → REGION_MANAGER 딕셔너리 조회
    region_key = (df['시도'].fillna('') + df['시군구'].fillna('')).str.replace(' ', '', regex=False)
    barogo_map  = {k: v[0] for k, v in REGION_MANAGER.items()}
    moa_map     = {k: v[1] for k, v in REGION_MANAGER.items()}
    dealver_map = {k: v[2] for k, v in REGION_MANAGER.items()}

    df['담당자'] = None
    mask_br = df['배송사'] == '바로고'
    mask_mo = df['배송사'] == '모아라인'
    mask_dv = df['배송사'] == '딜버'
    df.loc[mask_br, '담당자'] = region_key[mask_br].map(barogo_map)
    df.loc[mask_mo, '담당자'] = region_key[mask_mo].map(moa_map)
    df.loc[mask_dv, '담당자'] = region_key[mask_dv].map(dealver_map)

    return df

df = load_data()

# ==========================================
# 행정경계 GeoJSON 로드 함수
# ==========================================
@st.cache_data(ttl=86400)
def load_sigungu_geojson():
    try:
        with open("assets/sigungu.geojson", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

@st.cache_data
def load_beopjeongdong():
    path = Path(__file__).parent / "assets" / "beopjeongdong.geojson"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

@st.cache_data(ttl=86400)
def load_hangjeongdong():
    url = (
        "https://raw.githubusercontent.com/vuski/admdongkor"
        "/master/ver20260401/HangJeongDong_ver20260401.geojson"
    )
    try:
        return requests.get(url, timeout=90).json()
    except Exception:
        return None

SIDO_NAME_MAP = {
    '서울': '서울특별시', '부산': '부산광역시', '대구': '대구광역시',
    '인천': '인천광역시', '광주': '광주광역시', '대전': '대전광역시',
    '울산': '울산광역시', '세종': '세종특별자치시', '경기': '경기도',
    '강원': '강원특별자치도', '충북': '충청북도', '충남': '충청남도',
    '전북': '전북특별자치도', '전남': '전라남도', '경북': '경상북도',
    '경남': '경상남도', '제주': '제주특별자치도',
}

# ==========================================
# 3. 사이드바 - 스마트 필터 설정
# ==========================================
st.sidebar.header("🔍 상세 필터")

all_brands = sorted(df['상점관리주체(브랜드)'].dropna().unique().tolist())
exclude_list = ["버거킹(우딜)", "해피크루", "오투플러스"]
default_brands = [b for b in all_brands if b not in exclude_list]
selected_brands = st.sidebar.multiselect("브랜드 선택", all_brands, default=default_brands)

fee_types = sorted(df['매입타입'].dropna().unique().tolist())
selected_fees = st.sidebar.multiselect("요금제 종류", fee_types, default=fee_types)

sido_list = sorted(df['시도'].dropna().unique().tolist())
selected_sido = st.sidebar.multiselect("시도 선택", sido_list, default=sido_list)

sido_filtered_df = df[df['시도'].isin(selected_sido)]
sigungu_list = sorted(sido_filtered_df['시군구'].dropna().unique().tolist())
selected_sigungu = st.sidebar.multiselect("시군구 선택", sigungu_list, default=sigungu_list)

sigungu_filtered_df = sido_filtered_df[sido_filtered_df['시군구'].isin(selected_sigungu)]
eupmyeondong_list = sorted(sigungu_filtered_df['읍면동'].dropna().unique().tolist())

# 시군구 선택이 바뀌면 읍면동 위젯 초기화 (이전 선택값 유지 버그 방지)
_sig_key = tuple(sorted(selected_sigungu))
if st.session_state.get("_prev_sigungu") != _sig_key:
    st.session_state["_prev_sigungu"] = _sig_key
    st.session_state.pop("emd_filter", None)

selected_eupmyeondong = st.sidebar.multiselect("읍면동 선택", eupmyeondong_list, default=eupmyeondong_list, key="emd_filter")

st.sidebar.markdown("---")
st.sidebar.subheader("📈 상점 활동성 필터")
only_active = st.sidebar.checkbox("최근 한 달 주문 발생 상점 보기", value=False)

# ==========================================
# 4. 데이터 필터링 적용
# ==========================================
filtered_df = df[
    df['상점관리주체(브랜드)'].isin(selected_brands) &
    df['매입타입'].isin(selected_fees) &
    df['시도'].isin(selected_sido) &
    df['시군구'].isin(selected_sigungu) &
    df['읍면동'].isin(selected_eupmyeondong)
].copy()

# 주문 건수 숫자 변환 및 결측치 처리
filtered_df['최근한달주문건수'] = pd.to_numeric(filtered_df['최근한달주문건수'], errors='coerce').fillna(0)

if only_active:
    filtered_df = filtered_df[filtered_df['최근한달주문건수'] >= 1]

# 상점 단위 집계 df — 고릴라상점코드 기준 중복 제거, 이후 전 섹션 공용
_sk_global = '고릴라상점코드' if '고릴라상점코드' in filtered_df.columns else '상점명'
_gcols = [c for c in ['상점관리주체(브랜드)', '시도', '시군구', _sk_global] if c in filtered_df.columns]
store_agg_df = (
    filtered_df
    .groupby(_gcols, observed=True)
    .agg(
        매입타입=('매입타입', lambda x: '고릴라지역요금제(주소)' if (x == '고릴라지역요금제(주소)').all() else '배달대행사요금제(상점)'),
        최근한달주문건수=('최근한달주문건수', 'sum')
    )
    .reset_index()
)
# 벡터화 집계용 헬퍼 컬럼 (apply 대체)
store_agg_df['_is_addr']  = (store_agg_df['매입타입'] == '고릴라지역요금제(주소)').astype(int)
store_agg_df['_is_store'] = 1 - store_agg_df['_is_addr']
store_agg_df['_ord_addr'] = store_agg_df['최근한달주문건수'] * store_agg_df['_is_addr']
store_agg_df['_ord_store'] = store_agg_df['최근한달주문건수'] * store_agg_df['_is_store']

# ==========================================
# [순서 1] 💡 요금제 현황 요약 (KPI)
# ==========================================
st.markdown("### 📊 현재 상점/주소기반 전환 현황")

if not store_agg_df.empty:
    total_count = len(store_agg_df)
    address_fee_count = int(store_agg_df['_is_addr'].sum())
    store_fee_count = total_count - address_fee_count
    address_rate = (address_fee_count / total_count * 100) if total_count > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("총 조회 상점 수", f"{total_count:,}개")
    with c2: st.metric("주소기반 전환률", f"{address_rate:.1f}%")
    with c3: st.metric("주소기반(완료)", f"{address_fee_count:,}개", delta_color="normal")
    with c4: st.metric("상점기반(타겟)", f"{store_fee_count:,}개", delta="미전환", delta_color="inverse")
else:
    st.warning("조건에 맞는 상점이 없습니다.")

# ==========================================
# [순서 2] 🏢 지역별 브랜드 요금제 전환 뷰어
# ==========================================
st.markdown("---")
st.subheader("🏢 선택 지역 내 '브랜드별' 요금제 전환 뷰어")

if not store_agg_df.empty:
    brand_summary = (
        store_agg_df.groupby('상점관리주체(브랜드)', observed=True)
        .agg(주소기반=('_is_addr', 'sum'), 상점기반=('_is_store', 'sum'))
        .reset_index()
        .rename(columns={'주소기반': '고릴라지역요금제(주소)', '상점기반': '배달대행사요금제(상점)'})
    )
    brand_summary['총 상점 수'] = brand_summary['고릴라지역요금제(주소)'] + brand_summary['배달대행사요금제(상점)']
    brand_summary['주소요금제 전환율(%)'] = (brand_summary['고릴라지역요금제(주소)'] / brand_summary['총 상점 수'] * 100).fillna(0)
    brand_summary = brand_summary.sort_values(by=['총 상점 수', '주소요금제 전환율(%)'], ascending=[False, True])

    st.dataframe(
        brand_summary,
        column_config={
            "상점관리주체(브랜드)": st.column_config.TextColumn("🏢 브랜드명"),
            "총 상점 수": st.column_config.NumberColumn("총 상점 수", format="%d 개"),
            "고릴라지역요금제(주소)": st.column_config.NumberColumn("✅ 주소기반(완료)"),
            "배달대행사요금제(상점)": st.column_config.NumberColumn("🚨 상점기반(타겟)"),
            "주소요금제 전환율(%)": st.column_config.ProgressColumn(
                "📈 주소요금제 전환율", help="100%에 가까울수록 완료된 브랜드", format="%.1f %%", min_value=0, max_value=100
            ),
        },
        hide_index=True, use_container_width=True
    )

# ==========================================
# [순서 3] 📍 상세 지도 (Folium — 폴리곤 선택 + 경계 오버레이)
# ==========================================
st.markdown("---")
st.subheader("📍 지도 기준 상점/주소기반 현황 확인")

with st.expander("💡 사용법 안내 (클릭하여 펼치기)", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
**📍 마커 색상**
| 색상 | 의미 |
|---|---|
| 🟢 초록 점 | 주소기반 상점 (전환 완료) |
| 🔴 빨간 점 | 상점기반 상점 (전환 필요) |

**🗺️ 경계 레이어 ON/OFF 방법**

👈 **왼쪽 사이드바 하단** "🗺️ 지도 경계 레이어" 섹션에서 체크박스로 조작

| 체크박스 | 선 색상 | 설명 |
|---|---|---|
| 시군구 경계 | 회색 굵은 선 | 시·군·구 단위 경계 |
| 법정동 경계 | 파란 얇은 선 | 법정 행정구역 단위 |
| 행정동 경계 | 주황 얇은 선 | 실제 행정 운영 단위 |

> ⚠️ 경계 레이어는 **필터링된 지역이 좁을수록** 빠르게 표시됩니다.
""")
    with col2:
        st.markdown("""
**✏️ 지도 좌측 도구 모음**
| 아이콘 | 기능 |
|---|---|
| ⬡ (오각형) | 자유 다각형으로 영역 그리기 |
| ■ (사각형) | 사각형으로 영역 그리기 |
| ✏️ (연필) | 그린 도형 꼭짓점 수정 |
| 🗑️ (휴지통) | 그린 도형 전체 삭제 |

**🖱️ 영역 선택 방법**
1. ⬡ 또는 ■ 아이콘 클릭
2. 지도에서 원하는 영역을 그리고 마무리
3. 지도 아래에 해당 영역 내 상점 목록 자동 표시
4. 🗑️ 버튼으로 선택 해제
""")

st.sidebar.markdown("---")
st.sidebar.subheader("🗺️ 지도 경계 레이어")
show_sigungu_layer  = st.sidebar.checkbox("시군구 경계", value=False)
show_beopjeong_layer = st.sidebar.checkbox("법정동 경계", value=False)
show_hangjeong      = st.sidebar.checkbox("행정동 경계 (첫 로드 느릴 수 있음)", value=False)

if not filtered_df.empty:
    map_df = filtered_df.dropna(subset=['lat', 'lon'])

    # 지도 중심·줌 계산
    if not map_df.empty:
        center_lat = map_df['lat'].mean()
        center_lon = map_df['lon'].mean()
        n_sigungu = len(selected_sigungu)
        n_sido    = len(selected_sido)
        zoom = 13 if n_sigungu == 1 else (11 if n_sigungu <= 3 else (9 if n_sido == 1 else 7))
    else:
        center_lat, center_lon, zoom = 36.5, 127.5, 7

    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="CartoDB positron")

    from folium.plugins import FastMarkerCluster

    # --- 경계 레이어: 체크박스 ON일 때만 지도에 추가 (미체크 시 데이터 전송 없음) ---
    if show_sigungu_layer:
        sigungu_gj = load_sigungu_geojson()
        if sigungu_gj:
            folium.GeoJson(
                sigungu_gj, name="시군구 경계",
                style_function=lambda f: {"color": "#888", "weight": 1.5, "fillOpacity": 0, "opacity": 0.5},
                tooltip=folium.GeoJsonTooltip(fields=["SIG_KOR_NM"], aliases=["시군구"])
            ).add_to(m)

    if show_beopjeong_layer:
        beopjeong_gj = load_beopjeongdong()
        if beopjeong_gj:
            # 시군구 코드(앞 5자리) → 시군구명 매핑
            sig_gj_for_lookup = load_sigungu_geojson()
            sig_lookup = {}
            if sig_gj_for_lookup:
                sig_lookup = {
                    str(f["properties"].get("SIG_CD", "")): f["properties"].get("SIG_KOR_NM", "")
                    for f in sig_gj_for_lookup["features"]
                    if f["properties"].get("SIG_CD") and f["properties"].get("SIG_KOR_NM")
                }

            # 캐시 객체 직접 변경 금지 → 새 dict 생성으로 enrichment + filtering 한 번에
            sigungu_set = set(selected_sigungu)
            filtered_features = []
            for f in beopjeong_gj["features"]:
                code = str(f["properties"].get("EMD_CD", ""))
                sig_nm = sig_lookup.get(code[:5], "")
                if not sigungu_set or sig_nm in sigungu_set:
                    new_props = dict(f["properties"])
                    new_props["sigungu_nm"] = sig_nm
                    filtered_features.append({
                        "type": "Feature",
                        "properties": new_props,
                        "geometry": f["geometry"]
                    })

            if filtered_features:
                filtered_bj = {"type": "FeatureCollection", "features": filtered_features}
                folium.GeoJson(
                    filtered_bj, name="법정동 경계",
                    style_function=lambda f: {"color": "#3a86ff", "weight": 0.8, "fillOpacity": 0.02},
                    tooltip=folium.GeoJsonTooltip(
                        fields=["sigungu_nm", "EMD_NM"],
                        aliases=["시군구", "법정동명"]
                    )
                ).add_to(m)

                # 법정동명 중심점 레이블
                from shapely.geometry import shape as shp_shape
                label_fg = folium.FeatureGroup(name="법정동명 레이블", show=True)
                for f in filtered_features:
                    try:
                        centroid = shp_shape(f["geometry"]).centroid
                        nm = f["properties"].get("EMD_NM", "")
                        folium.Marker(
                            [centroid.y, centroid.x],
                            icon=folium.DivIcon(
                                html=f'<div style="font-size:9px;color:#1a5fb4;font-weight:600;white-space:nowrap;text-shadow:0 0 3px #fff,0 0 3px #fff">{sig_nm} {nm}</div>',
                                icon_size=(120, 16),
                                icon_anchor=(60, 8)
                            )
                        ).add_to(label_fg)
                    except Exception:
                        pass
                label_fg.add_to(m)

    if show_hangjeong:
        hangjeong_gj = load_hangjeongdong()
        if hangjeong_gj:
            sido_full = {SIDO_NAME_MAP.get(s, s) for s in selected_sido}
            sigungu_set = set(selected_sigungu)
            filtered_hj = {
                "type": "FeatureCollection",
                "features": [
                    f for f in hangjeong_gj["features"]
                    if f["properties"].get("sidonm") in sido_full
                    and f["properties"].get("sggnm") in sigungu_set
                ]
            }
            if filtered_hj["features"]:
                folium.GeoJson(
                    filtered_hj, name="행정동 경계",
                    style_function=lambda f: {"color": "#fb8500", "weight": 0.8, "fillOpacity": 0.02},
                    tooltip=folium.GeoJsonTooltip(
                        fields=["sggnm", "adm_nm"],
                        aliases=["시군구", "행정동명"]
                    )
                ).add_to(m)

    # --- 상점 마커: FastMarkerCluster (JS 콜백 방식, 개별 Python 객체 생성 없음) ---
    # 상점 수 경고
    n_markers = len(map_df)
    if n_markers > 3000:
        st.warning(f"⚠️ 현재 {n_markers:,}개 상점이 표시됩니다. 사이드바에서 시도·시군구를 좁히면 속도가 빨라집니다.")

    addr_df  = map_df[map_df["매입타입"] == "고릴라지역요금제(주소)"]
    store_df = map_df[map_df["매입타입"] != "고릴라지역요금제(주소)"]

    addr_data  = addr_df[["lat", "lon"]].values.tolist()
    store_data = store_df[["lat", "lon"]].values.tolist()

    GREEN_CB = """
    function(row) {
        return L.circleMarker(new L.LatLng(row[0], row[1]),
            {radius:5, color:'#2ecc71', fillColor:'#2ecc71', fillOpacity:0.85, weight:1.5});
    }"""
    RED_CB = """
    function(row) {
        return L.circleMarker(new L.LatLng(row[0], row[1]),
            {radius:5, color:'#e74c3c', fillColor:'#e74c3c', fillOpacity:0.85, weight:1.5});
    }"""

    _cluster_opts = {
        "showCoverageOnHover": False,
        "polygonOptions": {"weight": 0, "opacity": 0, "fillOpacity": 0}
    }
    if addr_data:
        FastMarkerCluster(addr_data, callback=GREEN_CB, name="✅ 주소기반 상점", options=_cluster_opts).add_to(m)
    if store_data:
        FastMarkerCluster(store_data, callback=RED_CB, name="🚨 상점기반 상점", options=_cluster_opts).add_to(m)

    # --- Draw 컨트롤 (좌하단 배치 — 줌/지도 이동 클릭과 겹치지 않도록) ---
    Draw(
        position="bottomleft",
        export=False,
        draw_options={
            "polyline": False, "circlemarker": False, "marker": False,
            "circle": False, "rectangle": True, "polygon": True
        },
        edit_options={"edit": True, "remove": True}
    ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    # 그린 도형 초기화 버튼 (map_key 변경 → 지도 컴포넌트 완전 재마운트)
    if "map_reset_key" not in st.session_state:
        st.session_state.map_reset_key = 0
    if st.button("🗑️ 그린 영역 초기화"):
        st.session_state.map_reset_key += 1

    map_output = st_folium(
        m, use_container_width=True, height=700,
        returned_objects=["last_active_drawing"],
        key=f"folium_map_{st.session_state.map_reset_key}"
    )
    st.info("💡 초록: 주소기반 완료 / 빨강: 상점기반(전환 필요) | 우측 ▭/⬡ 도구로 영역 그리기 → 해당 상점 목록 표시\n경계선은 사이드바 체크박스에서 켜세요")

    # --- 폴리곤 선택 결과 ---
    drawn = (map_output or {}).get("last_active_drawing")
    if drawn and drawn.get("geometry"):
        from shapely.geometry import shape, Point
        try:
            poly = shape(drawn["geometry"])
            mask = map_df.apply(lambda r: poly.contains(Point(r["lon"], r["lat"])), axis=1)
            selected_in_poly = map_df[mask]
            st.success(f"🎯 선택 영역 내 상점 **{len(selected_in_poly)}개** (사이드바 필터 적용됨)")
            if not selected_in_poly.empty:
                poly_cols = [c for c in [
                    '상점관리주체(브랜드)', '상점명', '시도', '시군구', '읍면동',
                    '매입타입', '배송사', '담당자', '최근한달주문건수'
                ] if c in selected_in_poly.columns]
                st.dataframe(
                    selected_in_poly[poly_cols],
                    column_config={
                        "상점관리주체(브랜드)": st.column_config.TextColumn("브랜드"),
                        "상점명": st.column_config.TextColumn("상점명"),
                        "시도": st.column_config.TextColumn("시도"),
                        "시군구": st.column_config.TextColumn("시군구"),
                        "읍면동": st.column_config.TextColumn("읍면동"),
                        "매입타입": st.column_config.TextColumn("매입타입"),
                        "배송사": st.column_config.TextColumn("배송사"),
                        "담당자": st.column_config.TextColumn("담당자"),
                        "최근한달주문건수": st.column_config.NumberColumn("최근1달 주문수", format="%d 건"),
                    },
                    hide_index=True, use_container_width=True
                )
        except Exception as e:
            st.warning(f"영역 선택 처리 오류: {e}")
    else:
        st.caption("🗺️ 지도 우측 툴바의 ▭(사각형) 또는 ⬡(폴리곤) 버튼으로 영역을 그리면 해당 구역 상점 목록이 표시됩니다.")

else:
    st.warning("조건에 맞는 상점이 없습니다.")

# ==========================================
# [순서 4] ✅ 요금제 현황 리스트 (시도 단위)
# ==========================================
st.markdown("---")
st.subheader("✅ 요금제 현황 리스트 (시도 단위)")
st.info("👆 행을 클릭하면 아래에 상세 상점 리스트가 나타납니다.")

if not store_agg_df.empty:
    sido_summary = (
        store_agg_df.groupby(['시도', '상점관리주체(브랜드)'], observed=True)
        .agg(상점수_store=('_is_store','sum'), 주문수_store=('_ord_store','sum'),
             상점수_addr=('_is_addr','sum'),  주문수_addr=('_ord_addr','sum'))
        .reset_index()
        .rename(columns={'상점수_store':'상점수(상점기반)','주문수_store':'최근 1개월 총 주문수(상점기반)',
                         '상점수_addr':'상점수(주소기반)','주문수_addr':'최근 1개월 총 주문수(주소기반)'})
    )

    display_sido = sido_summary.sort_values(by=['최근 1개월 총 주문수(상점기반)', '상점수(상점기반)'], ascending=[False, False])

    sido_event = st.dataframe(
        display_sido,
        column_config={
            "시도": st.column_config.TextColumn("📍 지역(시도)"),
            "상점관리주체(브랜드)": st.column_config.TextColumn("브랜드명"),
            "상점수(상점기반)": st.column_config.NumberColumn("상점수(상점기반)", format="%d 개"),
            "최근 1개월 총 주문수(상점기반)": st.column_config.NumberColumn("최근 1개월 총 주문수(상점기반)", format="%d 건"),
            "상점수(주소기반)": st.column_config.NumberColumn("상점수(주소기반)", format="%d 개"),
            "최근 1개월 총 주문수(주소기반)": st.column_config.NumberColumn("최근 1개월 총 주문수(주소기반)", format="%d 건"),
        },
        hide_index=True, use_container_width=True, height=300,
        on_select="rerun", selection_mode="single-row"
    )

    if len(sido_event.selection.rows) > 0:
        idx = sido_event.selection.rows[0]
        clicked_sido = display_sido.iloc[idx]['시도']
        clicked_brand = display_sido.iloc[idx]['상점관리주체(브랜드)']
        detail_df = filtered_df[
            (filtered_df['시도'] == clicked_sido) &
            (filtered_df['상점관리주체(브랜드)'] == clicked_brand)
        ]
        st.success(f"🔎 **[{clicked_sido}] {clicked_brand}** 상세 리스트")
        sido_detail_cols = [c for c in ['시군구', '읍면동', '상점명', '상태', '배송사', '매입타입', '매입대행료(기본)', '담당자', '최근한달주문건수'] if c in detail_df.columns]
        st.dataframe(
            detail_df[sido_detail_cols],
            column_config={
                "시군구": st.column_config.TextColumn("시군구"),
                "읍면동": st.column_config.TextColumn("읍면동"),
                "상점명": st.column_config.TextColumn("상점명"),
                "상태": st.column_config.TextColumn("상태"),
                "배송사": st.column_config.TextColumn("배송사"),
                "매입타입": st.column_config.TextColumn("매입타입"),
                "매입대행료(기본)": st.column_config.NumberColumn("매입대행료(기본)"),
                "담당자": st.column_config.TextColumn("담당자"),
                "최근한달주문건수": st.column_config.NumberColumn("최근한달주문건수", format="%d 건"),
            },
            hide_index=True, use_container_width=True
        )

# ==========================================
# [순서 5] ✅ 요금제 현황 리스트 (시군구 단위)
# ==========================================
st.markdown("---")
st.subheader("✅ 요금제 현황 리스트 (시군구 단위)")
st.info("👆 행을 클릭하면 아래에 상세 상점 리스트가 나타납니다.")

if not store_agg_df.empty:
    sigungu_summary = (
        store_agg_df.groupby(['시도', '시군구', '상점관리주체(브랜드)'], observed=True)
        .agg(상점수_store=('_is_store','sum'), 주문수_store=('_ord_store','sum'),
             상점수_addr=('_is_addr','sum'),  주문수_addr=('_ord_addr','sum'))
        .reset_index()
        .rename(columns={'상점수_store':'상점수(상점기반)','주문수_store':'최근 1개월 총 주문수(상점기반)',
                         '상점수_addr':'상점수(주소기반)','주문수_addr':'최근 1개월 총 주문수(주소기반)'})
    )

    sigungu_summary['시도시군구'] = sigungu_summary['시도'] + " " + sigungu_summary['시군구']
    display_sigungu = sigungu_summary.sort_values(by=['최근 1개월 총 주문수(상점기반)', '상점수(상점기반)'], ascending=[False, False])

    sigungu_event = st.dataframe(
        display_sigungu,
        column_config={
            "시도": None, "시군구": None,
            "시도시군구": st.column_config.TextColumn("📍 지역(시도+시군구)"),
            "상점관리주체(브랜드)": st.column_config.TextColumn("브랜드명"),
            "상점수(상점기반)": st.column_config.NumberColumn("상점수(상점기반)", format="%d 개"),
            "최근 1개월 총 주문수(상점기반)": st.column_config.NumberColumn("최근 1개월 총 주문수(상점기반)", format="%d 건"),
            "상점수(주소기반)": st.column_config.NumberColumn("상점수(주소기반)", format="%d 개"),
            "최근 1개월 총 주문수(주소기반)": st.column_config.NumberColumn("최근 1개월 총 주문수(주소기반)", format="%d 건"),
        },
        hide_index=True, use_container_width=True, height=400,
        on_select="rerun", selection_mode="single-row"
    )

    if len(sigungu_event.selection.rows) > 0:
        idx = sigungu_event.selection.rows[0]
        c_sido = display_sigungu.iloc[idx]['시도']
        c_sigungu = display_sigungu.iloc[idx]['시군구']
        c_brand = display_sigungu.iloc[idx]['상점관리주체(브랜드)']
        detail_df = filtered_df[
            (filtered_df['시도'] == c_sido) &
            (filtered_df['시군구'] == c_sigungu) &
            (filtered_df['상점관리주체(브랜드)'] == c_brand)
        ]
        st.success(f"🔎 **[{c_sido} {c_sigungu}] {c_brand}** 상세 리스트")
        sigungu_detail_cols = [c for c in ['읍면동', '상점명', '상태', '배송사', '매입타입', '매입대행료(기본)', '담당자', '최근한달주문건수'] if c in detail_df.columns]
        st.dataframe(
            detail_df[sigungu_detail_cols],
            column_config={
                "읍면동": st.column_config.TextColumn("읍면동"),
                "상점명": st.column_config.TextColumn("상점명"),
                "상태": st.column_config.TextColumn("상태"),
                "배송사": st.column_config.TextColumn("배송사"),
                "매입타입": st.column_config.TextColumn("매입타입"),
                "매입대행료(기본)": st.column_config.NumberColumn("매입대행료(기본)"),
                "담당자": st.column_config.TextColumn("담당자"),
                "최근한달주문건수": st.column_config.NumberColumn("최근한달주문건수", format="%d 건"),
            },
            hide_index=True, use_container_width=True
        )

# ==========================================
# [순서 6] 🎯 브랜드별 요금제 전환 전체 현황 (가로형 차트)
# ==========================================
st.markdown("---")
st.subheader("🎯 브랜드별 요금제 전환 전체 현황 (가로형 차트)")

if not filtered_df.empty:
    insight_df = store_agg_df.groupby(['상점관리주체(브랜드)', '매입타입'], observed=True).size().reset_index(name='상점수')
    target_count = insight_df[insight_df['매입타입'] == '배달대행사요금제(상점)'].rename(columns={'상점수': '타겟수'})
    insight_df = pd.merge(insight_df, target_count[['상점관리주체(브랜드)', '타겟수']], on='상점관리주체(브랜드)', how='left').fillna(0)
    insight_df = insight_df.sort_values(by=['타겟수', '상점수'], ascending=[True, True])

    fig_bar = px.bar(
        insight_df, y='상점관리주체(브랜드)', x='상점수', color='매입타입', orientation='h',
        title="🎯 브랜드별 전환 현황",
        color_discrete_map={"고릴라지역요금제(주소)": "#2ecc71", "배달대행사요금제(상점)": "#e74c3c"}, text_auto=True
    )
    brand_count = len(insight_df['상점관리주체(브랜드)'].unique())
    fig_bar.update_layout(height=max(400, brand_count * 30), yaxis_title=None, xaxis_title="상점 수", showlegend=True)
    st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# [순서 7] 📄 상세 데이터 리스트
# ==========================================
with st.expander("📄 상세 데이터 리스트 보기"):
    display_cols = [
        '상점관리주체(브랜드)', '고릴라상점코드', '최신타임라인날짜', '상점명', '상태',
        '배송사', '시도', '시군구', '읍면동', '매입타입',
        '메인수행허브', '공유수행허브', '수행허브사용상태',
        '매입대행료(기본)', '총판선차감', '허브선차감',
        '담당자', '최근한달주문건수'
    ]
    available_cols = [c for c in display_cols if c in filtered_df.columns]
    st.dataframe(
        filtered_df[available_cols],
        column_config={
            "상점관리주체(브랜드)": st.column_config.TextColumn("🏢 브랜드"),
            "고릴라상점코드": st.column_config.TextColumn("고릴라상점코드"),
            "최신타임라인날짜": st.column_config.TextColumn("최신타임라인날짜"),
            "상점명": st.column_config.TextColumn("상점명"),
            "상태": st.column_config.TextColumn("상태"),
            "배송사": st.column_config.TextColumn("배송사"),
            "시도": st.column_config.TextColumn("시도"),
            "시군구": st.column_config.TextColumn("시군구"),
            "읍면동": st.column_config.TextColumn("읍면동"),
            "매입타입": st.column_config.TextColumn("매입타입"),
            "메인수행허브": st.column_config.TextColumn("메인수행허브"),
            "공유수행허브": st.column_config.TextColumn("공유수행허브"),
            "수행허브사용상태": st.column_config.TextColumn("수행허브사용상태"),
            "매입대행료(기본)": st.column_config.NumberColumn("매입대행료(기본)"),
            "총판선차감": st.column_config.NumberColumn("총판선차감"),
            "허브선차감": st.column_config.NumberColumn("허브선차감"),
            "담당자": st.column_config.TextColumn("담당자"),
            "최근한달주문건수": st.column_config.NumberColumn("최근한달주문건수", format="%d 건"),
        },
        hide_index=True, use_container_width=True
    )
