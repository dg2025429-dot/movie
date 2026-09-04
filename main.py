import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    # openDt: 여덟 자리 숫자 -> 날짜로 변환
    df["openDt"] = pd.to_datetime(df["openDt"], format="%Y%m%d", errors="coerce")
    # genre: 세로막대(|) 기호로 여러 개 적힌 경우 첫 번째 장르만 사용
    df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()
    return df


df = load_data()

st.caption(
    "1년간 박스오피스 10위권에 든 영화 가운데 해당 기간에 개봉한 216편의 요약 데이터입니다."
)

st.divider()

# ------------------------------------------------------------------
# 그래프 1: 장르별 영화 편수 도넛 그래프
# ------------------------------------------------------------------
st.header("1. 장르별 영화 편수")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig1 = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
    title="장르별 영화 편수",
)
fig1.update_traces(
    hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>"
)
st.plotly_chart(fig1, use_container_width=True)

top_genre = genre_counts.iloc[0]
st.markdown(
    f"**이 그래프로 알 수 있는 것:** 전체 216편 중 '{top_genre['genre']}' 장르가 "
    f"{top_genre['count']}편으로 가장 많아, 특정 장르에 편중된 흥행 구조를 보여줍니다."
)

st.divider()

# ------------------------------------------------------------------
# 그래프 2: 장르 안에 영화가 들어있는 트리맵 (크기 = 총 관객)
# ------------------------------------------------------------------
st.header("2. 장르 · 영화별 총 관객 트리맵")

fig2 = px.treemap(
    df,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화 총 관객 트리맵 (칸 크기 = 총 관객)",
    custom_data=["movieNm", "total_audi"],
)
fig2.update_traces(
    hovertemplate="영화명: %{customdata[0]}<br>총 관객: %{customdata[1]:,}명<extra></extra>"
)
st.plotly_chart(fig2, use_container_width=True)

biggest_movie = df.loc[df["total_audi"].idxmax()]
st.markdown(
    f"**이 그래프로 알 수 있는 것:** 트리맵에서 가장 큰 칸을 차지하는 영화는 "
    f"'{biggest_movie['movieNm']}'({biggest_movie['genre']})로, 총 관객 "
    f"{biggest_movie['total_audi']:,}명을 동원해 해당 장르 흥행을 주도했습니다."
)

st.divider()

# ------------------------------------------------------------------
# 그래프 3: 총 관객 히스토그램
# ------------------------------------------------------------------
st.header("3. 총 관객 분포 히스토그램")

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="영화별 총 관객 분포",
)
fig3.update_layout(xaxis_title="총 관객 수", yaxis_title="영화 편수")
st.plotly_chart(fig3, use_container_width=True)

# 가장 영화가 몰린 구간 계산
cut = pd.cut(df["total_audi"], bins=30)
bin_counts = cut.value_counts().sort_values(ascending=False)
top_bin = bin_counts.index[0]
max_movie = df.loc[df["total_audi"].idxmax()]

st.markdown(
    f"**이 그래프로 알 수 있는 것:** 대부분의 영화는 총 관객 약 "
    f"{int(top_bin.left):,}명 ~ {int(top_bin.right):,}명 구간에 몰려 있으며, "
    f"가장 관객이 많은 영화는 '{max_movie['movieNm']}'"
    f"(총 {max_movie['total_audi']:,}명)입니다."
)

st.divider()

# ------------------------------------------------------------------
# 그래프 4: 개봉일 스크린수 vs 총 관객 산점도 (장르별 색상)
# ------------------------------------------------------------------
st.header("4. 개봉일 스크린수와 총 관객의 관계")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수 vs 총 관객 (장르별 색상)",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객 수"},
)
st.plotly_chart(fig4, use_container_width=True)

corr_4 = df["first_scrn"].corr(df["total_audi"])
st.markdown(
    f"**이 그래프로 알 수 있는 것:** 개봉일 스크린수와 총 관객 사이의 상관계수는 "
    f"약 {corr_4:.2f}로, 스크린을 많이 확보할수록 대체로 총 관객도 늘어나는 경향이 있습니다."
)

st.divider()

# ------------------------------------------------------------------
# 그래프 5: 영화 10편 이상 장르만 골라 총 관객 박스플롯
# ------------------------------------------------------------------
st.header("5. 장르별 총 관객 분포 (박스플롯)")

genre_over_10 = genre_counts[genre_counts["count"] >= 10]["genre"]
df_box = df[df["genre"].isin(genre_over_10)]

fig5 = px.box(
    df_box,
    x="genre",
    y="total_audi",
    points="outliers",
    hover_data=["movieNm"],
    title="영화 10편 이상인 장르의 총 관객 박스플롯",
    labels={"genre": "장르", "total_audi": "총 관객 수"},
)
fig5.update_traces(
    hovertemplate="영화명: %{customdata[0]}<br>총 관객: %{y:,}명<extra></extra>"
)
st.plotly_chart(fig5, use_container_width=True)

median_by_genre = df_box.groupby("genre")["total_audi"].median().sort_values(ascending=False)
st.markdown(
    f"**이 그래프로 알 수 있는 것:** 영화가 10편 이상인 장르 중 '{median_by_genre.index[0]}' 장르가 "
    f"중앙값 기준 총 관객이 가장 높아, 안정적으로 흥행하는 장르임을 알 수 있습니다."
)

st.divider()

# ------------------------------------------------------------------
# 그래프 6: 스크린수-총관객 버블 그래프 (점 크기 = 첫 주 관객)
# ------------------------------------------------------------------
st.header("6. 개봉일 스크린수 · 총 관객 · 첫 주 관객 버블 그래프")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=40,
    title="개봉일 스크린수 vs 총 관객 (점 크기 = 첫 주 관객)",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객 수"},
)
st.plotly_chart(fig6, use_container_width=True)

biggest_bubble = df.loc[df["first_week_audi"].idxmax()]
st.markdown(
    f"**이 그래프로 알 수 있는 것:** 첫 주 관객이 가장 많았던 영화는 "
    f"'{biggest_bubble['movieNm']}'({biggest_bubble['first_week_audi']:,}명)로, "
    f"초반 흥행이 총 관객 규모로 이어지는 흐름을 큰 버블을 통해 확인할 수 있습니다."
)

st.divider()

# ------------------------------------------------------------------
# 그래프 7: 국가 -> 장르 선버스트 (크기 = 영화 편수)
# ------------------------------------------------------------------
st.header("7. 제작 국가별 장르 구성 선버스트")

nation_genre_counts = (
    df.groupby(["nation", "genre"]).size().reset_index(name="count")
)

fig7 = px.sunburst(
    nation_genre_counts,
    path=["nation", "genre"],
    values="count",
    title="제작 국가 → 장르 선버스트 (칸 크기 = 영화 편수)",
)
fig7.update_traces(
    hovertemplate="%{label}<br>편수: %{value}편<extra></extra>"
)
st.plotly_chart(fig7, use_container_width=True)

top_nation = df["nation"].value_counts().index[0]
st.markdown(
    f"**이 그래프로 알 수 있는 것:** '{top_nation}' 제작 영화가 가장 많은 비중을 차지하며, "
    f"국가마다 선호되는 장르 구성이 다르게 나타납니다."
)
