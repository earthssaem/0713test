# ============================================================
#  서울 vs 양평 기온 비교 웹앱 — 열섬현상을 찾아라!
#  (2차시 시연용 · 데이터: 기상청 시간별 기온, 2026.6.1 ~ 7.11)
# ============================================================
import streamlit as st
import pandas as pd

# ---------- 1단계. 데이터 불러오기 ----------
# 기상청 CSV는 한글 인코딩(cp949)이라서 encoding을 꼭 지정해야 합니다!
seoul = pd.read_csv("서울_기온.csv", encoding="utf-8")
yang = pd.read_csv("양평_기온.csv", encoding="utf-8")

# ---------- 2단계. 데이터 정리하기 ----------
# 열 이름을 다루기 쉽게 바꾸고, '일시'를 날짜/시간 형식으로 변환
for df in (seoul, yang):
    df.columns = ["지점", "지점명", "일시", "기온"]
    df["일시"] = pd.to_datetime(df["일시"])

# 두 지역을 하나의 표로 합치기 (같은 시각끼리 나란히)
data = pd.merge(
    seoul[["일시", "기온"]], yang[["일시", "기온"]],
    on="일시", suffixes=("_서울", "_양평"),
).rename(columns={"기온_서울": "서울", "기온_양평": "양평"})
data["기온차"] = data["서울"] - data["양평"]   # 서울 - 양평
data["시각"] = data["일시"].dt.hour
data["날짜"] = data["일시"].dt.date

# ---------- 3단계. 화면 만들기 ----------
st.title("🌡️ 서울 vs 양평 기온 비교")
st.write("같은 시각, 두 지역의 기온은 얼마나 다를까? 그래프에서 **열섬현상**의 증거를 찾아보자.")

# 사이드바: 기간 선택
st.sidebar.header("🔍 보고 싶은 기간")
start = st.sidebar.date_input("시작일", data["날짜"].min(),
                              min_value=data["날짜"].min(), max_value=data["날짜"].max())
end = st.sidebar.date_input("종료일", data["날짜"].max(),
                            min_value=data["날짜"].min(), max_value=data["날짜"].max())
selected = data[(data["날짜"] >= start) & (data["날짜"] <= end)]

# 핵심 숫자 3개
c1, c2, c3 = st.columns(3)
c1.metric("서울 평균기온", f"{selected['서울'].mean():.1f} °C")
c2.metric("양평 평균기온", f"{selected['양평'].mean():.1f} °C")
c3.metric("평균 기온차 (서울-양평)", f"{selected['기온차'].mean():+.2f} °C")

# ---------- 4단계. 그래프 ① 시간에 따른 기온 변화 ----------
st.subheader("① 시간에 따른 기온 변화")
st.line_chart(selected.set_index("일시")[["서울", "양평"]])
st.caption("두 선이 벌어지는 곳은 언제일까? 확대해서(기간을 줄여서) 살펴보자.")

# ---------- 5단계. 그래프 ② 하루 동안의 평균 기온 (핵심!) ----------
st.subheader("② 시각별 평균 기온 — 하루의 리듬")
hourly = selected.groupby("시각")[["서울", "양평"]].mean()
st.line_chart(hourly)
st.caption("0~23시 각 시각의 평균. 낮과 밤 중 언제 두 지역의 차이가 클까?")

# ---------- 6단계. 그래프 ③ 시각별 기온차 = 열섬의 지문 ----------
st.subheader("③ 시각별 기온차 (서울 − 양평)")
st.bar_chart(selected.groupby("시각")["기온차"].mean())
st.caption("막대가 높은 시간대 = 서울이 양평보다 더운 시간대. 이 모양이 왜 나올까?")

# ---------- 7단계. 열대야 비교 ----------
st.subheader("④ 열대야 일수 (밤 최저기온 25°C 이상)")
daily_min = selected.groupby("날짜")[["서울", "양평"]].min()  # 날짜별 최저기온
c4, c5 = st.columns(2)
c4.metric("서울 열대야", f"{(daily_min['서울'] >= 25).sum()} 일")
c5.metric("양평 열대야", f"{(daily_min['양평'] >= 25).sum()} 일")

# ---------- 마무리 질문 ----------
st.divider()
st.info("💬 **생각해 보기** — 그래프 ③에서 기온차가 가장 큰 시간대는 언제인가? "
        "왜 도시는 그 시간에 시골보다 더 더울까? (힌트: 아스팔트와 콘크리트는 낮 동안 무엇을 저장할까?)")
