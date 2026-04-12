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
exclude_list = ["버거킹(우딜)", "해피크루","오투플러스"]
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
only_active = st.sidebar.checkbox("최근 한 달 주문 발생 상점 보기", value=False)

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
st.markdown("### 📊 현재 상점/주소기반 전환 현황")

if not filtered_df.empty:
    # 핵심 지표 계산
    total_count = len(filtered_df)
    address_fee_count = len(filtered_df[filtered_df['매입타입'] == '고릴라지역요금제(주소)'])
    store_fee_count = total_count - address_fee_count
    address_rate = (address_fee_count / total_count * 100) if total_count > 0 else 0

    # KPI 카드 4개를 위쪽에 한 줄로 나란히 배치!
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("총 조회 상점 수", f"{total_count:,}개")
    with c2:
        st.metric("주소기반 전환률", f"{address_rate:.1f}%")
    with c3:
        st.metric("주소기반(완료)", f"{address_fee_count:,}개", delta_color="normal")
    with c4:
        st.metric("상점기반(타겟)", f"{store_fee_count:,}개", delta="미전환", delta_color="inverse")
    
    st.markdown("<br>", unsafe_allow_html=True) # 살짝 여백 주기
    
# 2. 획기적인 가로형 막대그래프 (가독성 & 영업 타겟팅 끝판왕!)
    st.markdown("<br>", unsafe_allow_html=True) # 살짝 여백 주기
    
    # 데이터 가공: 브랜드별로 '상점요금제(빨간색)'가 몇 개인지 세서 정렬 기준으로 삼기!
    insight_df = filtered_df.groupby(['상점관리주체(브랜드)', '매입타입']).size().reset_index(name='상점수')
    
    # 빨간색(타겟) 개수 구하기
    target_count = insight_df[insight_df['매입타입'] == '배달대행사요금제(상점)'].rename(columns={'상점수': '타겟수'})
    insight_df = pd.merge(insight_df, target_count[['상점관리주체(브랜드)', '타겟수']], on='상점관리주체(브랜드)', how='left').fillna(0)

    # 타겟수(빨간색)가 많은 순서대로 정렬! 
    # (Plotly 가로형 그래프는 밑에서부터 위로 그려지므로 오름차순(True)으로 해야 제일 큰 게 맨 위에 옴!)
    insight_df = insight_df.sort_values(by=['타겟수', '상점수'], ascending=[True, True])

    # 획기적인 변화: x축 y축 뒤집기 (orientation='h')
    fig_bar = px.bar(
        insight_df, 
        y='상점관리주체(브랜드)',  # Y축에 브랜드명 눕혀서 배치 (글씨 절대 안 짤림!)
        x='상점수',              # X축에 개수
        color='매입타입', 
        orientation='h',        # ⭐️ 가로형 그래프로 변신하는 핵심 마법!
        title="🎯 요금제 미전환 타겟 현황 (위에서부터 영업하세요!)",
        color_discrete_map={"고릴라지역요금제(주소)": "#2ecc71", "배달대행사요금제(상점)": "#e74c3c"},
        text_auto=True
    )
    
    # ⭐️ 잼민이의 디테일: 검색된 브랜드 개수에 따라 그래프 세로 길이를 자동으로 늘려줌!
    brand_count = len(insight_df['상점관리주체(브랜드)'].unique())
    fig_bar.update_layout(
        height=max(400, brand_count * 30), # 브랜드 하나당 30픽셀씩 넉넉하게 공간 확보
        yaxis_title=None,
        xaxis_title="상점 수",
        showlegend=True
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 6. 📍 상세 지도 (색상: 요금제 종류 구분)
# ==========================================
st.markdown("---")
st.subheader(f"📍 지도 기준 상점/주소기반 현황 확인")

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
    
    st.info("💡 초록색 점은 주소기반 요금제 적용 완료, 빨간색 점은 상점기반 요금제 사용 중인 곳입니다.")
else:
    st.warning("조건에 맞는 상점이 없습니다. 필터를 조절해 보세요!")

# ==========================================
# 6-5. 🏢 지역별 브랜드 요금제 전환 뷰어 (브랜드 단위 O, 상점 단위 X)
# ==========================================
st.markdown("---")
st.subheader("🏢 선택 지역 내 '브랜드별' 요금제 전환 뷰어")
st.markdown("왼쪽 필터에서 선택한 지역(시도/시군구) 안에서 **각 브랜드가 주소요금제로 얼마나 전환되었는지** 한눈에 파악합니다.")

# area_df는 위에서 지역 필터만 적용해서 만들어둔 데이터프레임!
area_df = df[df['시도'].isin(selected_sido) & df['sigungu'].isin(selected_sigungu)]

if not area_df.empty:
    # 1. 브랜드별, 매입타입별로 개수 세기 (상점 단위 -> 브랜드 단위로 압축!)
    brand_summary = area_df.groupby(['상점관리주체(브랜드)', '매입타입']).size().unstack(fill_value=0).reset_index()
    
    # 만약 데이터에 특정 요금제가 아예 없으면 에러 안 나게 0으로 채워주기
    if '고릴라지역요금제(주소)' not in brand_summary.columns:
        brand_summary['고릴라지역요금제(주소)'] = 0
    if '배달대행사요금제(상점)' not in brand_summary.columns:
        brand_summary['배달대행사요금제(상점)'] = 0
        
    # 2. 총 상점 수랑 '주소요금제 전환율(%)' 계산하기
    brand_summary['총 상점 수'] = brand_summary['고릴라지역요금제(주소)'] + brand_summary['배달대행사요금제(상점)']
    # 상점이 0개인 곳은 0%, 아니면 비율 계산
    brand_summary['주소요금제 전환율(%)'] = brand_summary.apply(
        lambda row: (row['고릴라지역요금제(주소)'] / row['총 상점 수'] * 100) if row['총 상점 수'] > 0 else 0, 
        axis=1
    )
    
    # 3. 뷰어 정렬: 총 상점 수가 많으면서, 전환율이 낮은(영업이 시급한) 순서대로 정렬!
    brand_summary = brand_summary.sort_values(by=['총 상점 수', '주소요금제 전환율(%)'], ascending=[False, True])
    
    # 4. 스트림릿 마법! 엑셀 표 안에 '프로그레스 바' 예쁘게 그리기
    st.dataframe(
        brand_summary,
        column_config={
            "상점관리주체(브랜드)": st.column_config.TextColumn("🏢 브랜드명"),
            "총 상점 수": st.column_config.NumberColumn("총 상점 수", format="%d 개"),
            "고릴라지역요금제(주소)": st.column_config.NumberColumn("✅ 주소기반(완료)"),
            "배달대행사요금제(상점)": st.column_config.NumberColumn("🚨 상점기반(타겟)"),
            "주소요금제 전환율(%)": st.column_config.ProgressColumn(
                "📈 주소요금제 전환율",
                help="100%에 가까울수록 주소기반 전환이 완료된 브랜드입니다.",
                format="%.1f %%",
                min_value=0,
                max_value=100,
            ),
        },
        hide_index=True, # 쓸데없는 숫자 인덱스 숨기기
        use_container_width=True # 화면 넓이에 꽉 차게!
    )
else:
    st.info("선택한 지역에 상점 데이터가 없습니다.")

# ==========================================
# 6-6. ✅ 주소요금제 전환 완료 리스트 (영업 레퍼런스용 - 상세 표)
# ==========================================
st.markdown("---")
st.subheader("✅ 주소기반 전환 완료 리스트")
st.markdown("해당 지역에서 이미 주소요금제를 사용 중인 **'전환 완료 브랜드'** 목록입니다.")

# 1. 주소요금제(고릴라지역요금제)를 쓰는 데이터만 쏙 뽑아내기! (.copy()를 써서 안전하게 복사)
completed_df = filtered_df[filtered_df['매입타입'] == '고릴라지역요금제(주소)'].copy()

if not completed_df.empty:
    # 2. 혹시 모를 에러를 방지하기 위해 주문 건수를 확실한 '숫자'로 바꿔주기
    completed_df['최근 한 달 주문 건수'] = pd.to_numeric(completed_df['최근 한 달 주문 건수'], errors='coerce').fillna(0)

    # 3. 지역(시도, 시군구)과 브랜드별로 묶어서 상점수와 총 주문수 계산하기! (판다스 마법 🧙‍♂️)
    success_summary = completed_df.groupby(['시도', 'sigungu', '상점관리주체(브랜드)']).agg(
        상점수=('고릴라 상점명', 'count'),       # 상점 이름 개수 세기
        총주문수=('최근 한 달 주문 건수', 'sum')  # 주문 건수 전부 다 더하기
    ).reset_index()

    # 4. '시도'와 '시군구' 합쳐서 네가 원했던 '시도시군구' 컬럼 만들기
    success_summary['시도시군구'] = success_summary['시도'] + " " + success_summary['sigungu']

    # 5. 화면에 보여줄 4개 열만 쏙 골라내고 순서 맞추기
    display_df = success_summary[['시도시군구', '상점관리주체(브랜드)', '상점수', '총주문수']]
    
    # 6. 정렬: 주문수가 많은 곳(액티브한 곳)부터 먼저 보이게 내림차순 정렬!
    display_df = display_df.sort_values(by=['총주문수', '상점수'], ascending=[False, False])

    # 7. 스트림릿 표로 예쁘게 출력하기 (숫자 포맷팅까지 완벽하게!)
    st.dataframe(
        display_df,
        column_config={
            "시도시군구": st.column_config.TextColumn("📍 지역 (시도+시군구)"),
            "상점관리주체(브랜드)": st.column_config.TextColumn("🏢 브랜드명"),
            "상점수": st.column_config.NumberColumn("✅ 설정된 상점 수", format="%d 개"),
            "총주문수": st.column_config.NumberColumn("📦 최근 1개월 총 주문수", format="%d 건")
        },
        hide_index=True,
        use_container_width=True,
        height=400 # 스크롤바 예쁘게 생기도록 높이 고정
    )
else:
    st.info("현재 선택된 필터 내에는 주소요금제로 전환된 상점이 없습니다. 😭")

# ==========================================
# 7. 데이터 리스트 다운로드
# ==========================================
with st.expander("📄 상세 데이터 리스트 보기"):
    st.dataframe(filtered_df, use_container_width=True)
