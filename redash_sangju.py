import streamlit as st
import pandas as pd
import plotly.express as px

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
    df = df.rename(columns={'위도(Latitude)': 'lon', '경도(Longitude)': 'lat'})
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    df = df.dropna(subset=['lat', 'lon'])

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
    df['시군구'].isin(selected_sigungu)
].copy()

# 주문 건수 숫자 변환 및 결측치 처리
filtered_df['최근한달주문건수'] = pd.to_numeric(filtered_df['최근한달주문건수'], errors='coerce').fillna(0)

if only_active:
    filtered_df = filtered_df[filtered_df['최근한달주문건수'] >= 1]

# 상점 단위 집계 df (배대사 중복 제거 — 시도/시군구/차트 섹션 공용)
_sk_global = '고릴라상점코드' if '고릴라상점코드' in filtered_df.columns else '상점명'
_gcols = [c for c in ['상점관리주체(브랜드)', '시도', '시군구', '읍면동', _sk_global] if c in filtered_df.columns]
store_agg_df = (
    filtered_df.dropna(subset=[_sk_global])
    .groupby(_gcols)
    .agg(
        매입타입=('매입타입', lambda x: '고릴라지역요금제(주소)' if (x == '고릴라지역요금제(주소)').all() else '배달대행사요금제(상점)'),
        최근한달주문건수=('최근한달주문건수', 'sum')
    )
    .reset_index()
)

# ==========================================
# [순서 1] 💡 요금제 현황 요약 (KPI)
# ==========================================
st.markdown("### 📊 현재 상점/주소기반 전환 현황")

if not filtered_df.empty:
    _sk = '고릴라상점코드' if '고릴라상점코드' in filtered_df.columns else '상점명'
    _kpi_base = filtered_df.dropna(subset=[_sk])
    # 상점 단위 매입타입 판별: 모든 배대사가 주소기반이어야 완료
    _store_type = (
        _kpi_base.groupby(_sk)['매입타입']
        .apply(lambda x: '고릴라지역요금제(주소)' if (x == '고릴라지역요금제(주소)').all() else '배달대행사요금제(상점)')
    )
    total_count = len(_store_type)
    address_fee_count = int((_store_type == '고릴라지역요금제(주소)').sum())
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

area_df = filtered_df.copy()

if not area_df.empty:
    _sk2 = '고릴라상점코드' if '고릴라상점코드' in area_df.columns else '상점명'
    # 브랜드+상점코드 단위로 매입타입 판별 후 집계
    _store_brand = (
        area_df.dropna(subset=[_sk2])
        .groupby(['상점관리주체(브랜드)', _sk2])['매입타입']
        .apply(lambda x: '고릴라지역요금제(주소)' if (x == '고릴라지역요금제(주소)').all() else '배달대행사요금제(상점)')
        .reset_index(name='매입타입')
    )
    brand_summary = _store_brand.groupby(['상점관리주체(브랜드)', '매입타입']).size().unstack(fill_value=0).reset_index()
    if '고릴라지역요금제(주소)' not in brand_summary.columns: brand_summary['고릴라지역요금제(주소)'] = 0
    if '배달대행사요금제(상점)' not in brand_summary.columns: brand_summary['배달대행사요금제(상점)'] = 0

    brand_summary['총 상점 수'] = brand_summary['고릴라지역요금제(주소)'] + brand_summary['배달대행사요금제(상점)']
    brand_summary['주소요금제 전환율(%)'] = brand_summary.apply(
        lambda row: (row['고릴라지역요금제(주소)'] / row['총 상점 수'] * 100) if row['총 상점 수'] > 0 else 0, axis=1
    )
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
# [순서 3] 📍 상세 지도
# ==========================================
st.markdown("---")
st.subheader("📍 지도 기준 상점/주소기반 현황 확인")

if not filtered_df.empty:
    fig_map = px.scatter_mapbox(
        filtered_df, lat="lat", lon="lon",
        color="매입타입",
        color_discrete_map={"고릴라지역요금제(주소)": "#2ecc71", "배달대행사요금제(상점)": "#e74c3c"},
        hover_name="상점관리주체(브랜드)",
        hover_data={"시도": True, "시군구": True, "상점관리주체(브랜드)": False, "상점명": True, "lat": False, "lon": False, "매입타입": False},
        zoom=6, height=700
    )
    fig_map.update_layout(mapbox_style="carto-positron", margin={"r": 0, "t": 0, "l": 0, "b": 0}, clickmode='event+select', dragmode='pan')
    st.plotly_chart(fig_map, use_container_width=True, config={'scrollZoom': True})
    st.info("💡 초록색 점은 주소기반 적용 완료, 빨간색 점은 상점기반 사용 중인 곳입니다.")

# ==========================================
# [순서 4] ✅ 요금제 현황 리스트 (시도 단위)
# ==========================================
st.markdown("---")
st.subheader("✅ 요금제 현황 리스트 (시도 단위)")
st.info("👆 행을 클릭하면 아래에 상세 상점 리스트가 나타납니다.")

if not filtered_df.empty:
    sido_summary = store_agg_df.groupby(['시도', '상점관리주체(브랜드)']).apply(lambda x: pd.Series({
        '상점수(상점기반)': (x['매입타입'] == '배달대행사요금제(상점)').sum(),
        '최근 1개월 총 주문수(상점기반)': x[x['매입타입'] == '배달대행사요금제(상점)']['최근한달주문건수'].sum(),
        '상점수(주소기반)': (x['매입타입'] == '고릴라지역요금제(주소)').sum(),
        '최근 1개월 총 주문수(주소기반)': x[x['매입타입'] == '고릴라지역요금제(주소)']['최근한달주문건수'].sum(),
    })).reset_index()

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

if not filtered_df.empty:
    sigungu_summary = store_agg_df.groupby(['시도', '시군구', '상점관리주체(브랜드)']).apply(lambda x: pd.Series({
        '상점수(상점기반)': (x['매입타입'] == '배달대행사요금제(상점)').sum(),
        '최근 1개월 총 주문수(상점기반)': x[x['매입타입'] == '배달대행사요금제(상점)']['최근한달주문건수'].sum(),
        '상점수(주소기반)': (x['매입타입'] == '고릴라지역요금제(주소)').sum(),
        '최근 1개월 총 주문수(주소기반)': x[x['매입타입'] == '고릴라지역요금제(주소)']['최근한달주문건수'].sum(),
    })).reset_index()

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
    insight_df = store_agg_df.groupby(['상점관리주체(브랜드)', '매입타입']).size().reset_index(name='상점수')
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
