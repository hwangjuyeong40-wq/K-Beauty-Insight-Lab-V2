import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------

# 페이지 설정

# ----------------------------------

st.set_page_config(
page_title="K-Beauty Insight Lab V2",
page_icon="🧴",
layout="wide"
)

# ----------------------------------

# 데이터 불러오기

# ----------------------------------

@st.cache_data
def load_data():

```
df = pd.read_excel("data_726.xlsx")

df.columns = [str(col).strip() for col in df.columns]

sentiment_map = {
    "positive": "긍정",
    "neutral": "중립",
    "negative": "부정",
    "긍정": "긍정",
    "중립": "중립",
    "부정": "부정"
}

df["sentiment"] = (
    df["sentiment"]
    .astype(str)
    .str.strip()
    .map(sentiment_map)
    .fillna("중립")
)

df["product"] = (
    df["product"]
    .fillna("제품명 없음")
    .astype(str)
)

df["review"] = (
    df["review"]
    .fillna("")
    .astype(str)
)

def classify_product(product):

    product = str(product).lower()

    if "toner" in product or "爽肤水" in product:
        return "토너"

    elif (
        "serum" in product
        or "essence" in product
        or "精华" in product
    ):
        return "세럼"

    elif (
        "cream" in product
        or "面霜" in product
    ):
        return "크림"

    elif (
        "cushion" in product
        or "气垫" in product
    ):
        return "쿠션"

    elif (
        "foundation" in product
        or "粉底" in product
    ):
        return "파운데이션"

    return "기타"

df["category"] = df["product"].apply(classify_product)

return df
```

df = load_data()

# ----------------------------------

# 제목

# ----------------------------------

st.title(
"🧴 K-Beauty Insight Lab V2"
)

st.caption(
"한·중 소비자 리뷰 기반 K-뷰티 만족도 분석 및 추천 플랫폼"
)

st.divider()

# ----------------------------------

# 프로젝트 개요

# ----------------------------------

st.subheader("📊 프로젝트 개요")

c1, c2, c3, c4 = st.columns(4)

with c1:
st.metric("총 리뷰 수", len(df))

with c2:
st.metric(
"한국어 리뷰",
len(df[df["language"] == "ko"])
)

with c3:
st.metric(
"중국어 리뷰",
len(df[df["language"] == "zh"])
)

with c4:
st.metric(
"제품 수",
df["product"].nunique()
)

st.divider()

# ----------------------------------

# 언어별 리뷰 수

# ----------------------------------

st.subheader("🌏 한·중 리뷰 수 비교")

lang_df = (
df["language"]
.replace({
"ko": "한국어",
"zh": "중국어"
})
.value_counts()
.reset_index()
)

lang_df.columns = ["language", "count"]

fig_lang = px.bar(
lang_df,
x="language",
y="count"
)

st.plotly_chart(
fig_lang,
use_container_width=True
)

# ----------------------------------

# 감성 비교

# ----------------------------------

st.subheader("😊 한·중 소비자 감성 비교")

compare_df = pd.crosstab(
df["language"],
df["sentiment"]
)

for col in ["긍정", "중립", "부정"]:
if col not in compare_df.columns:
compare_df[col] = 0

compare_df = compare_df.reset_index()

compare_df["language"] = (
compare_df["language"]
.replace({
"ko": "한국어",
"zh": "중국어"
})
)

fig_compare = px.bar(
compare_df,
x="language",
y=["긍정", "중립", "부정"],
barmode="group"
)

st.plotly_chart(
fig_compare,
use_container_width=True
)

# ----------------------------------

# 제품군 분포

# ----------------------------------

st.subheader("🧴 제품군 분포")

category_df = (
df["category"]
.value_counts()
.reset_index()
)

category_df.columns = [
"category",
"count"
]

fig_category = px.bar(
category_df,
x="category",
y="count"
)

st.plotly_chart(
fig_category,
use_container_width=True
)

# ----------------------------------

# 리뷰 검색

# ----------------------------------

st.subheader("🔍 리뷰 검색")

keyword = st.text_input(
"검색어 입력"
)

if keyword:

```
result = df[
    df["review"]
    .str.contains(
        keyword,
        case=False,
        na=False
    )
]

st.write(
    f"검색 결과 : {len(result)}건"
)

st.dataframe(
    result[
        [
            "product",
            "sentiment",
            "review"
        ]
    ].head(30)
)
```

# ----------------------------------

# 원본 데이터

# ----------------------------------

st.subheader("📂 원본 데이터")

st.dataframe(
df.head(100),
use_container_width=True
)

st.success(
"🚀 K-Beauty Insight Lab V2 실행 중"
)
