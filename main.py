# ============================================================
#  기온과 전력, 그리고 열섬현상 — 서울·양평 기온 + 전국 전력수요
#  (데이터: 기상청 시간별 기온 + 전력거래소 시간별 전국 전력수요)
# ============================================================
import streamlit as st
import pandas as pd

# ---------- 1단계. 데이터 불러오기 (한글 파일이라 encoding 지정!) ----------
seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
yang = pd.read_csv("양평_기온.csv", encoding="cp949")
power = pd.read_csv("전력수요.csv", encoding="cp949")

# ---------- 2단계. 데이터 정리하기 ----------
for df in (seoul, yang):
    df.columns = ["지점", "지점명", "일시", "기온"]
    df["일시"] = pd.to_datetime(df["일시"])
power.columns = ["일시", "전력수요"]
power["일시"] = pd.to_datetime(power["일시"])

# 서울 기온과 전국 전력을 같은 시각끼리 합치기
data = pd.merge(seoul[["일시", "기온"]], power[["일시", "전력수요"]], on="일시")
data["월"] = data["일시"].dt.month
data["시각"] = data["일시"].dt.hour

# ---------- 3단계. 화면 만들기 ----------
st.title("🌡️⚡ 기온과 전력, 그리고 열섬현상")
st.write("도시가 더워지면 우리는 무엇을 할까? 기온과 전력 사용량의 관계에서 **열섬현상의 되먹임**을 찾아보자.")

st.sidebar.header("🔍 살펴볼 달 고르기")
months = sorted(data["월"].unique())
sel = st.sidebar.multiselect("월 (여러 개 선택 가능)", months, default=months)
view = data[data["월"].isin(sel)] if sel else data

# 핵심 숫자
c1, c2, c3 = st.columns(3)
c1.metric("평균 기온", f"{view['기온'].mean():.1f} °C")
c2.metric("평균 전력수요", f"{view['전력수요'].mean():,.0f} MWh")
c3.metric("기온-전력 상관", f"{view['기온'].corr(view['전력수요']):.2f}")

# ---------- 4단계. 그래프 ① 기온 vs 전력 산점도 (핵심!) ----------
st.subheader("① 기온이 오르면 전력 사용도 늘어날까? (산점도)")
st.scatter_chart(view, x="기온", y="전력수요")
st.caption("점 하나가 한 시간. 가로=기온, 세로=전력수요. 어떤 모양이 보이나요? (힌트: 알파벳 U 또는 나이키 로고)")

# ---------- 5단계. 그래프 ② 기온 구간별 평균 전력 ----------
st.subheader("② 기온 구간별 평균 전력수요")
view = view.copy()
view["기온구간"] = (view["기온"] // 5 * 5).astype(int)
st.bar_chart(view.groupby("기온구간")["전력수요"].mean())
st.caption("가장 쾌적한 기온에서 전력이 가장 적고, 덥거나 추우면 늘어난다 — 냉방과 난방 때문!")

# ---------- 6단계. 그래프 ③ 시각별 평균 전력수요 ----------
st.subheader("③ 하루 중 전력을 언제 가장 많이 쓸까? (시각별)")
st.line_chart(view.groupby("시각")["전력수요"].mean())
st.caption("낮에 높고 밤에 낮아진다. 그런데 도시의 열섬은 '밤'에 심하다는 것을 기억하자.")

# ---------- 마무리 질문 ----------
st.divider()
st.info("💬 **생각해 보기** — 도시는 밤에 잘 식지 않아 더 덥습니다(열섬현상). "
        "더우면 사람들은 냉방을 켜고, 냉방기(실외기)는 다시 열을 내뿜습니다. "
        "기온과 전력 그래프를 근거로, 이 '더위 → 냉방 → 더 더위'의 고리를 설명해 봅시다.")
