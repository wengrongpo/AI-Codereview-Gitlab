import datetime
import streamlit as st
import pandas as pd

from biz.service.review_service import ReviewService


# 获取数据函数
def get_data_by_date(authors=None, updated_at_gte=None, updated_at_lte=None):
    df = ReviewService().get_mr_review_logs(authors=authors, updated_at_gte=updated_at_gte,
                                            updated_at_lte=updated_at_lte)

    if df.empty:
        return pd.DataFrame(columns=["project_name", "author", "source_branch", "target_branch",
                                     "updated_at", "commit_messages", "score", "url"])

    if "updated_at" in df.columns:
        df["updated_at"] = df["updated_at"].apply(
            lambda ts: datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(ts, (int, float)) else ts
        )

    if "url" in df.columns:
        df["url"] = df["url"].apply(lambda x: f"[查看]({x})" if pd.notna(x) else "")

    return df[
        ["project_name", "author", "source_branch", "target_branch", "updated_at", "commit_messages", "score", "url"]]


# Streamlit 配置
st.set_page_config(layout="wide")
st.markdown("### 审查日志")

current_date = datetime.date.today()
start_date_default = current_date - datetime.timedelta(days=7)

col1, col2, col3 = st.columns(3)
with col1:
    startdate = st.date_input("开始日期", start_date_default)

with col2:
    enddate = st.date_input("结束日期", current_date)

start_datetime = datetime.datetime.combine(startdate, datetime.time.min)
end_datetime = datetime.datetime.combine(enddate, datetime.time.max)

# 先获取数据
data = get_data_by_date(updated_at_gte=int(start_datetime.timestamp()), updated_at_lte=int(end_datetime.timestamp()))
df = pd.DataFrame(data)

# 动态获取 `authors` 选项
unique_authors = sorted(df["author"].dropna().unique().tolist()) if not df.empty else []

with col3:
    authors = st.multiselect("用户名", unique_authors, default=[])

# 重新获取数据（带 `authors` 过滤）
data = get_data_by_date(authors=authors, updated_at_gte=int(start_datetime.timestamp()),
                        updated_at_lte=int(end_datetime.timestamp()))
df = pd.DataFrame(data)


def highlight_score(val):
    """根据分数高低设置单元格背景颜色"""
    if val >= 85:
        color = "green"
    elif 70 <= val < 85:
        color = "orange"
    else:
        color = "red"
    return f"background-color: {color}; color: white; text-align: center;"


df = df.style.map(highlight_score, subset=["score"])

# 定义每一列的最小宽度
column_widths = {
    1: 30,  # A列
    2: 120,  # B列
    3: 100,  # C列
    4: 120,  # D列
    5: 120,  # E列
    6: 80,  # F列
    8: 50,  # H列
    9: 50  # I列
}
# 生成 CSS 代码
css = "<style>table { width: 100%; }"
for col, width in column_widths.items():
    css += f"th:nth-child({col}), td:nth-child({col}) {{ min-width: {width}px; }}\n"
css += "</style>"
# 应用 CSS
st.markdown(css, unsafe_allow_html=True)

st.table(df)
