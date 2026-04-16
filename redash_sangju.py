import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(page_title="B2B 요금제 전략 대시보드", layout="wide")
st.title("🗺️ 전국 B2B 상점/주소기반 현황")

# ==========================================
# 2. 데이터 로드 (실시간 구글 시트)
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStjwgRnDKfM7PwYLh_aJ3cPPbk49ipGAvIVU0C9wUwJ6Rn-ZoY_UMsN-pNDJuR0Qq7jkFX6rA-Cfq0/pub?output=csv"

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df = df.rename(columns={'위도(Latitude)': 'lon', '경도(Longitude)': 'lat'})
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    df = df.dropna(subset=['lat', 'lon'])
    return df

df = load_data()

# ==========================================
# 3. 사이드바 - 스마트 필터 설정
# ==========================================
st.sidebar.header("🔍 상세 필터")

all_brands = sorted(df['상점관리주체(브랜드)'].dropna().unique().tolist())
exclude_list = ["버거킹(우딜)", "해피크루","오투플러스"]
default_brands = [b for b in all_brands if b not in exclude_list]
selected_brands = st.sidebar.multiselect("브랜드 선택", all_brands, default=default_brands)

fee_types = sorted(df['매입타입'].dropna().unique().tolist())
selected_fees = st.sidebar.multiselect("요금제 종류", fee_types, default=fee_types)

sido_list = sorted(df['시도'].dropna().unique().tolist())
selected_sido = st.sidebar.multiselect("시도 선택", sido_list, default=sido_list)

sido_filtered_df = df[df['시도'].isin(selected_sido)]
sigungu_list = sorted(sido_filtered_df['sigungu'].dropna().unique().tolist())
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
    df['sigungu'].isin(selected_sigungu)
].copy()

# 주문 건수 숫자 변환 및 결측치 처리
filtered_df['최근 한 달 주문 건수'] = pd.to_numeric(filtered_df['최근 한 달 주문 건수'], errors='coerce').fillna(0)

if only_active:
    filtered_df = filtered_df[filtered_df['최근 한 달 주문 건수'] >= 1]

# ==========================================
# [순서 1] 💡 요금제 현황 요약 (KPI)
# ==========================================
st.markdown("### 📊 현재 상점/주소기반 전환 현황")

if not filtered_df.empty:
    total_count = len(filtered_df)
    address_fee_count = len(filtered_df[filtered_df['매입타입'] == '고릴라지역요금제(주소)'])
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

area_df = filtered_df.copy() # 이미 지역 필터가 적용된 filtered_df 사용

if not area_df.empty:
    brand_summary = area_df.groupby(['상점관리주체(브랜드)', '매입타입']).size().unstack(fill_value=0).reset_index()
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
st.subheader(f"📍 지도 기준 상점/주소기반 현황 확인")

if not filtered_df.empty:
    fig_map = px.scatter_mapbox(
        filtered_df, lat="lat", lon="lon",
        color="매입타입", 
        color_discrete_map={"고릴라지역요금제(주소)": "#2ecc71", "배달대행사요금제(상점)": "#e74c3c"},
        hover_name="상점관리주체(브랜드)",
        hover_data={"시도": True, "sigungu": True, "상점관리주체(브랜드)": False, "고릴라 상점명": True, "lat": False, "lon": False, "매입타입": False},
        zoom=6, height=700
    )
    fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0}, clickmode='event+select', dragmode='pan')
    st.plotly_chart(fig_map, use_container_width=True, config={'scrollZoom': True})
    st.info("💡 초록색 점은 주소기반 적용 완료, 빨간색 점은 상점기반 사용 중인 곳입니다.")

# ==========================================
# [순서 4] ✅ 요금제 현황 리스트 (시도 단위) - 획기적 통합!
# ==========================================
st.markdown("---")
st.subheader("✅ 요금제 현황 리스트 (시도 단위)")
st.info("👆 행을 클릭하면 아래에 상세 상점 리스트가 나타납니다.")

if not filtered_df.empty:
    # 잼민이의 마법: 한 번에 두 요금제 집계하기
    sido_summary = filtered_df.groupby(['시도', '상점관리주체(브랜드)']).apply(lambda x: pd.Series({
        '상점수(상점기반)': (x['매입타입'] == '배달대행사요금제(상점)').sum(),
        '최근 1개월 총 주문수(상점기반)': x[x['매입타입'] == '배달대행사요금제(상점)']['최근 한 달 주문 건수'].sum(),
        '상점수(주소기반)': (x['매입타입'] == '고릴라지역요금제(주소)').sum(),
        '최근 1개월 총 주문수(주소기반)': x[x['매입타입'] == '고릴라지역요금제(주소)']['최근 한 달 주문 건수'].sum(),
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
        detail_df = filtered_df[(filtered_df['시도'] == clicked_sido) & (filtered_df['상점관리주체(브랜드)'] == clicked_brand)]
        st.success(f"🔎 **[{clicked_sido}] {clicked_brand}** 상세 리스트")
        st.dataframe(detail_df[['sigungu', '고릴라 상점명', '매입타입', '최근 한 달 주문 건수']], hide_index=True, use_container_width=True)

# ==========================================
# [순서 5] ✅ 요금제 현황 리스트 (시군구 단위) - 획기적 통합!
# ==========================================
st.markdown("---")
st.subheader("✅ 요금제 현황 리스트 (시군구 단위)")
st.info("👆 행을 클릭하면 아래에 상세 상점 리스트가 나타납니다.")

if not filtered_df.empty:
    sigungu_summary = filtered_df.groupby(['시도', 'sigungu', '상점관리주체(브랜드)']).apply(lambda x: pd.Series({
        '상점수(상점기반)': (x['매입타입'] == '배달대행사요금제(상점)').sum(),
        '최근 1개월 총 주문수(상점기반)': x[x['매입타입'] == '배달대행사요금제(상점)']['최근 한 달 주문 건수'].sum(),
        '상점수(주소기반)': (x['매입타입'] == '고릴라지역요금제(주소)').sum(),
        '최근 1개월 총 주문수(주소기반)': x[x['매입타입'] == '고릴라지역요금제(주소)']['최근 한 달 주문 건수'].sum(),
    })).reset_index()
    
    sigungu_summary['시도시군구'] = sigungu_summary['시도'] + " " + sigungu_summary['sigungu']
    display_sigungu = sigungu_summary.sort_values(by=['최근 1개월 총 주문수(상점기반)', '상점수(상점기반)'], ascending=[False, False])

    sigungu_event = st.dataframe(
        display_sigungu,
        column_config={
            "시도": None, "sigungu": None,
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
        c_sigungu = display_sigungu.iloc[idx]['sigungu']
        c_brand = display_sigungu.iloc[idx]['상점관리주체(브랜드)']
        detail_df = filtered_df[(filtered_df['시도'] == c_sido) & (filtered_df['sigungu'] == c_sigungu) & (filtered_df['상점관리주체(브랜드)'] == c_brand)]
        st.success(f"🔎 **[{c_sido} {c_sigungu}] {c_brand}** 상세 리스트")
        st.dataframe(detail_df[['고릴라 상점명', '매입타입', '최근 한 달 주문 건수']], hide_index=True, use_container_width=True)

# ==========================================
# [순서 6] 🎯 브랜드별 요금제 전환 전체 현황 (가로형 차트)
# ==========================================
st.markdown("---")
st.subheader("🎯 브랜드별 요금제 전환 전체 현황 (가로형 차트)")

if not filtered_df.empty:
    insight_df = filtered_df.groupby(['상점관리주체(브랜드)', '매입타입']).size().reset_index(name='상점수')
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
    st.dataframe(filtered_df, use_container_width=True)
