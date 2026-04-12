import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(page_title="B2B 요금제 전략 대시보드", layout="wide")
st.title("🗺️ 전국 B2B 상점 요금제 현황 & 영업 인사이트")

# ==========================================
# 2. 데이터 로드 (실시간 구글 시트)
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStjwgRnDKfM7PwYLh_aJ3cPPbk49ipGAvIVU0C9wUwJ6Rn-ZoY_UMsN-pNDJuR0Qq7jkFX6rA-Cfq0/pub?output=csv"

@st.cache_data(ttl=3600) # 하루 한 번 업데이트
def load_data():
    df = pd.read_csv(SHEET_URL)
    # 위도/경도 데이터 반대로 들어오는 것 수정 (lon/lat 스왑)
    df = df.rename(columns={'위도(Latitude)': 'lon', '경도(Longitude)': 'lat'})
    # 문자를 숫자로 강제 변환
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    # 좌표 비어있는 데이터 빼기
    df = df.dropna(subset=['lat', 'lon'])
    return df

df = load_data()

# ==========================================
# 3. 사이드바 - 스마트 필터 설정
# ==========================================
st.sidebar.header("🔍 상세 필터")

# 1) 브랜드 선택 (버거킹(우딜), 해피크루 제외하고 전체 선택)
all_brands = sorted(df['상점관리주체(브랜드)'].dropna().unique().tolist())
exclude_list = ["버거킹(우딜)", "해피크루"]
default_brands = [b for b in all_brands if b not in exclude_list]
selected_brands = st.sidebar.multiselect("브랜드 선택", all_brands, default=default_brands)

# 2) 요금제 종류 (주소, 상점 둘 다 기본 선택)
fee_types = sorted(df['매입타입'].dropna().unique().tolist())
selected_fees = st.sidebar.multiselect("요금제 종류", fee_types, default=fee_types)

# 3) 시도/시군구 (전체 선택)
sido_list = sorted(df['시도'].dropna().unique().tolist())
selected_sido = st.sidebar.multiselect("시도 선택", sido_list, default=sido_list)

sido_filtered_df = df[df['시도'].isin(selected_sido)]
sigungu_list = sorted(sido_filtered_df['sigungu'].dropna().unique().tolist())
selected_sigungu = st.sidebar.multiselect("시군구 선택", sigungu_list, default=sigungu_list)

# 🚨 4) 주문 활성 상점 필터 (영업 타겟 발굴용!)
st.sidebar.markdown("---")
st.sidebar.subheader("📈 상점 활동성 필터")
only_active = st.sidebar.checkbox("최근 한 달 주문 1건 이상인 상점만 보기", value=False)

# ==========================================
# 4. 데이터 필터링 적용
# ==========================================
filtered_df = df[
    df['상점관리주체(브랜드)'].isin(selected_brands) & 
    df['매입타입'].isin(selected_fees) & 
    df['시도'].isin(selected_sido) & 
    df['sigungu'].isin(selected_sigungu)
]

# 체크박스 켜져있으면 주문 건수 1 이상인 것만 추가 필터링
if only_active:
    filtered_df = filtered_df[filtered_df['최근 한 달 주문 건수'] >= 1]

# ==========================================
# 5. 💡 한눈에 빡!! 요금제 현황 요약 (인사이트 영역)
# ==========================================
st.markdown("### 📊 현재 지역/브랜드 요금제 보급 현황")

if not filtered_df.empty:
    # 핵심 지표 계산
    total_count = len(filtered_df)
    address_fee_count = len(filtered_df[filtered_df['매입타입'] == '고릴라지역요금제(주소)'])
    store_fee_count = total_count - address_fee_count
    address_rate = (address_fee_count / total_count * 100) if total_count > 0 else 0

    # KPI 카드 4개를 위쪽에 한 줄로 나란히 배치!
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("총 검색 상점 수", f"{total_count:,}개")
    with c2:
        st.metric("주소요금제 보급률", f"{address_rate:.1f}%")
    with c3:
        st.metric("주소요금제(완료)", f"{address_fee_count:,}개", delta_color="normal")
    with c4:
        st.metric("상점요금제(타겟)", f"{store_fee_count:,}개", delta="-미전환", delta_color="inverse")
    
    st.markdown("<br>", unsafe_allow_html=True) # 살짝 여백 주기
    
    # 막대그래프 (브랜드 이름 45도 기울이기 적용)
    insight_df = filtered_df.groupby(['상점관리주체(브랜드)', '매입타입']).size().reset_index(name='상점수')
    fig_bar = px.bar(insight_df, x='상점관리주체(브랜드)', y='상점수', color='매입타입', 
                     title="🏢 브랜드별 요금제 혼용 현황 (미전환 타겟 확인)",
                     color_discrete_map={"고릴라지역요금제(주소)": "#2ecc71", "배달대행사요금제(상점)": "#e74c3c"},
                     text_auto=True)
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 6. 📍 상세 지도 (색상: 요금제 종류 구분)
# ==========================================
st.markdown("---")
st.subheader(f"📍 상세 위치 확인 (색상: 요금제 구분 / 휠로 줌 가능)")

if not filtered_df.empty:
    fig_map = px.scatter_mapbox(
        filtered_df,
        lat="lat", lon="lon",
        color="매입타입", # 요금제로 색상 구분
        color_discrete_map={
            "고릴라지역요금제(주소)": "#2ecc71", # 초록색 (전환완료)
            "배달대행사요금제(상점)": "#e74c3c"  # 빨간색 (영업타겟)
        },
        hover_name="상점관리주체(브랜드)", # 상단 제목
        hover_data={
            "시도": True,
            "sigungu": True,
            "상점관리주체(브랜드)": False, # 제목과 겹치므로 숨김
            "고릴라 상점명": True,
            "lat": False, "lon": False, "매입타입": False # 불필요 정보 숨김
        },
        zoom=6, height=700
    )
    
    # 에러 나던 토큰 지우고 깔끔하게 휠 줌 세팅!
    fig_map.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":0,"l":0,"b":0},
        clickmode='event+select',
        dragmode='pan'
    )
    
    st.plotly_chart(fig_map, use_container_width=True, config={'scrollZoom': True})
    
    st.info("💡 팁: 초록색 점은 주소기반 요금제 적용 완료, 빨간색 점은 상점기반 요금제 사용 중인 곳입니다.")
else:
    st.warning("조건에 맞는 상점이 없습니다. 필터를 조절해 보세요!")

# ==========================================
# 7. 데이터 리스트 다운로드
# ==========================================
with st.expander("📄 상세 데이터 리스트 보기"):
    st.dataframe(filtered_df, use_container_width=True)
