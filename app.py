import os

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="K-Beauty Insight Lab V2",
    page_icon="🧴",
    layout="wide",
)


DATA_PATHS = [
    "data_726.xlsx",
    r"C:\Users\why\Desktop\kbeauty-dashboard-v2\data_726.xlsx",
]

LANGUAGE_LABELS = {
    "ko": "한국어",
    "zh": "중국어",
}

SENTIMENT_MAP = {
    "positive": "긍정",
    "neutral": "중립",
    "negative": "부정",
    "긍정": "긍정",
    "중립": "중립",
    "부정": "부정",
}

SENTIMENT_ORDER = ["긍정", "중립", "부정"]


def classify_product(product):
    text = str(product).lower()

    if "toner" in text or "爽肤水" in text:
        return "토너"
    elif "serum" in text or "essence" in text or "精华" in text:
        return "세럼"
    elif "cream" in text or "面霜" in text:
        return "크림"
    elif "cushion" in text or "气垫" in text:
        return "쿠션"
    elif "foundation" in text or "粉底" in text:
        return "파운데이션"
    else:
        return "기타"


def calculate_satisfaction(data):
    total_count = len(data)

    if total_count == 0:
        return 0

    positive_count = (data["sentiment"] == "긍정").sum()
    neutral_count = (data["sentiment"] == "중립").sum()

    satisfaction = (
        (positive_count + neutral_count * 0.5)
        / total_count
        * 100
    )

    return round(satisfaction, 2)


@st.cache_data
def load_data():
    data_path = None

    for path in DATA_PATHS:
        if os.path.exists(path):
            data_path = path
            break

    if data_path is None:
        st.error("data_726.xlsx 파일을 찾을 수 없습니다.")
        st.stop()

    df = pd.read_excel(data_path)
    df.columns = df.columns.str.strip()

    df["language"] = df["language"].astype(str).str.strip()
    df["platform"] = df["platform"].astype(str).str.strip()
    df["product"] = df["product"].fillna("미상").astype(str).str.strip()
    df["review"] = df["review"].fillna("").astype(str)
    df["issue_type"] = df["issue_type"].fillna("미상").astype(str).str.strip()

    original_sentiment = df["sentiment"].astype(str).str.strip()
    df["sentiment"] = (
        original_sentiment
        .str.lower()
        .map(SENTIMENT_MAP)
        .fillna(original_sentiment)
    )

    df["language_label"] = df["language"].map(LANGUAGE_LABELS).fillna(df["language"])
    df["product_category"] = df["product"].apply(classify_product)

    return df


def calculate_product_satisfaction(data):
    result = (
        data.groupby("product")
        .apply(
            lambda x: pd.Series(
                {
                    "리뷰 수": len(x),
                    "긍정": (x["sentiment"] == "긍정").sum(),
                    "중립": (x["sentiment"] == "중립").sum(),
                    "부정": (x["sentiment"] == "부정").sum(),
                    "만족도": calculate_satisfaction(x),
                }
            )
        )
        .reset_index()
    )

    result = result.sort_values(
        by=["만족도", "리뷰 수"],
        ascending=[False, False],
    )

    return result


df = load_data()

st.title("K-Beauty Insight Lab V2")

total_reviews = len(df)
ko_reviews = (df["language"] == "ko").sum()
zh_reviews = (df["language"] == "zh").sum()
product_count = df["product"].nunique()

col1, col2, col3, col4 = st.columns(4)

col1.metric("총 리뷰 수", f"{total_reviews:,}")
col2.metric("한국어 리뷰 수", f"{ko_reviews:,}")
col3.metric("중국어 리뷰 수", f"{zh_reviews:,}")
col4.metric("제품 수", f"{product_count:,}")

st.divider()

st.subheader("한·중 리뷰 수 비교")

language_counts = (
    df["language_label"]
    .value_counts()
    .reindex(["한국어", "중국어"])
    .fillna(0)
    .reset_index()
)

language_counts.columns = ["언어", "리뷰 수"]

fig_language = px.bar(
    language_counts,
    x="언어",
    y="리뷰 수",
    color="언어",
    text="리뷰 수",
    color_discrete_map={
        "한국어": "#2F80ED",
        "중국어": "#EB5757",
    },
)

fig_language.update_layout(showlegend=False)
fig_language.update_traces(textposition="outside")

st.plotly_chart(fig_language, use_container_width=True)

st.subheader("한·중 감성 비교")

language_sentiment = pd.crosstab(
    df["language_label"],
    df["sentiment"],
)

language_sentiment = language_sentiment.reindex(
    index=["한국어", "중국어"],
    fill_value=0,
)

language_sentiment = language_sentiment.reindex(
    columns=SENTIMENT_ORDER,
    fill_value=0,
)

language_sentiment_chart = language_sentiment.reset_index().melt(
    id_vars="language_label",
    var_name="감성",
    value_name="리뷰 수",
)

fig_language_sentiment = px.bar(
    language_sentiment_chart,
    x="language_label",
    y="리뷰 수",
    color="감성",
    barmode="group",
    text="리뷰 수",
    category_orders={
        "language_label": ["한국어", "중국어"],
        "감성": SENTIMENT_ORDER,
    },
    color_discrete_map={
        "긍정": "#27AE60",
        "중립": "#F2C94C",
        "부정": "#EB5757",
    },
    labels={
        "language_label": "언어",
    },
)

fig_language_sentiment.update_traces(textposition="outside")

st.plotly_chart(fig_language_sentiment, use_container_width=True)

st.subheader("플랫폼별 감성 비교")

platform_sentiment = pd.crosstab(
    df["platform"],
    df["sentiment"],
)

platform_sentiment = platform_sentiment.reindex(
    columns=SENTIMENT_ORDER,
    fill_value=0,
)

platform_sentiment_chart = platform_sentiment.reset_index().melt(
    id_vars="platform",
    var_name="감성",
    value_name="리뷰 수",
)

fig_platform_sentiment = px.bar(
    platform_sentiment_chart,
    x="platform",
    y="리뷰 수",
    color="감성",
    barmode="group",
    text="리뷰 수",
    category_orders={
        "감성": SENTIMENT_ORDER,
    },
    color_discrete_map={
        "긍정": "#27AE60",
        "중립": "#F2C94C",
        "부정": "#EB5757",
    },
    labels={
        "platform": "플랫폼",
    },
)

fig_platform_sentiment.update_traces(textposition="outside")

st.plotly_chart(fig_platform_sentiment, use_container_width=True)

st.subheader("제품군 분류")

category_counts = df["product_category"].value_counts().reset_index()
category_counts.columns = ["제품군", "리뷰 수"]

fig_category = px.bar(
    category_counts,
    x="제품군",
    y="리뷰 수",
    color="제품군",
    text="리뷰 수",
)

fig_category.update_layout(showlegend=False)
fig_category.update_traces(textposition="outside")

st.plotly_chart(fig_category, use_container_width=True)

st.divider()

st.subheader("감성 기반 만족도 계산")

overall_satisfaction = calculate_satisfaction(df)

st.metric("전체 만족도", f"{overall_satisfaction:.2f}%")

st.info(
    "만족도는 긍정 리뷰를 1점, 중립 리뷰를 0.5점, 부정 리뷰를 0점으로 환산하여 계산한 감성 기반 지표입니다.\n\n"
    "계산식: (긍정 리뷰 수 + 중립 리뷰 수 × 0.5) ÷ 전체 리뷰 수 × 100\n\n"
    "네이버 쇼핑 데이터에는 별점 정보가 포함되어 있지 않아,\n"
    "본 대시보드에서는 감성분석 결과를 기반으로 만족도를 계산했습니다."
)

st.subheader("제품 만족도 TOP10")

product_satisfaction = calculate_product_satisfaction(df)
top10_products = product_satisfaction.head(10)

st.dataframe(
    top10_products,
    use_container_width=True,
    hide_index=True,
)

fig_top10 = px.bar(
    top10_products.sort_values("만족도"),
    x="만족도",
    y="product",
    orientation="h",
    color="만족도",
    text="만족도",
    color_continuous_scale="Tealgrn",
    labels={
        "product": "제품",
        "만족도": "만족도(%)",
    },
)

fig_top10.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
)

fig_top10.update_layout(coloraxis_showscale=False)

st.plotly_chart(fig_top10, use_container_width=True)

st.subheader("이슈 유형 기반 추천")

issue_options = sorted(df["issue_type"].dropna().unique().tolist())

selected_issue = st.selectbox(
    "issue_type 선택",
    issue_options,
)

issue_df = df[df["issue_type"] == selected_issue]
issue_recommendations = calculate_product_satisfaction(issue_df).head(5)

st.dataframe(
    issue_recommendations,
    use_container_width=True,
    hide_index=True,
)

if not issue_recommendations.empty:
    fig_issue = px.bar(
        issue_recommendations.sort_values("만족도"),
        x="만족도",
        y="product",
        orientation="h",
        color="만족도",
        text="만족도",
        color_continuous_scale="Mint",
        labels={
            "product": "추천 제품",
            "만족도": "만족도(%)",
        },
    )

    fig_issue.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
    )

    fig_issue.update_layout(coloraxis_showscale=False)

    st.plotly_chart(fig_issue, use_container_width=True)
else:
    st.warning("선택한 이슈 유형에 해당하는 추천 제품이 없습니다.")

st.divider()

st.subheader("리뷰 검색")

search_col1, search_col2 = st.columns([1, 3])

with search_col1:
    selected_language = st.selectbox(
        "언어 선택",
        ["전체", "한국어", "중국어"],
    )

with search_col2:
    keyword = st.text_input(
        "키워드 입력",
        placeholder="검색할 리뷰 키워드를 입력하세요",
    )

filtered_df = df.copy()

if selected_language == "한국어":
    filtered_df = filtered_df[filtered_df["language"] == "ko"]
elif selected_language == "중국어":
    filtered_df = filtered_df[filtered_df["language"] == "zh"]

if keyword.strip():
    filtered_df = filtered_df[
        filtered_df["review"].str.contains(
            keyword.strip(),
            case=False,
            na=False,
        )
    ]

st.dataframe(
    filtered_df[
        [
            "id",
            "platform",
            "language_label",
            "product",
            "review",
            "sentiment",
            "rating",
            "issue_type",
            "product_category",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.subheader("원본 데이터 조회")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

st.subheader("V3 로드맵")

roadmap_col1, roadmap_col2, roadmap_col3, roadmap_col4 = st.columns(4)

roadmap_col1.success("피부 고민 자동 분류")
roadmap_col2.success("AI 기반 제품 추천")
roadmap_col3.success("리뷰 자동 요약")
roadmap_col4.success("피부 타입 기반 추천")