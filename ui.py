import datetime

import streamlit as st
import pandas as pd

from biz.service.review_service import ReviewService


# 获取数据函数
def get_data_by_date(authors=None, updated_at_gte=None, updated_at_lte=None):
    df = ReviewService().get_mr_review_logs(authors=authors, updated_at_gte=updated_at_gte, updated_at_lte=updated_at_lte)

    if "updated_at" in df.columns:
        df["updated_at"] = df["updated_at"].apply(
            lambda ts: datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(ts, (int, float)) else ts
        )

    if "url" in df.columns:
        df["url"] = df["url"].apply(lambda x: f"[查看]({x})" if pd.notna(x) else "")
    return df[
        ["project_name", "author", "source_branch", "target_branch", "updated_at", "commit_messages", "score", "url"]]


st.set_page_config(layout="wide")
current_date = datetime.date.today()
start_date_default = current_date - datetime.timedelta(days=7)

col1, col2, col3 = st.columns(3)
with col1:
    startdate = st.date_input("开始日期", start_date_default)

with col2:
    enddate = st.date_input("结束日期", current_date)

start_datetime = datetime.datetime.combine(startdate, datetime.time.min)
end_datetime = datetime.datetime.combine(enddate, datetime.time.max)

with col3:
    authors = st.multiselect("用户名", ["sunminghui", "raopinbin", "lisi"], [], )

data = get_data_by_date(authors=authors, updated_at_gte=int(start_datetime.timestamp()),
                        updated_at_lte=int(end_datetime.timestamp()))
df = pd.DataFrame(data)
# st.dataframe(df,use_container_width=True)
# 使用 st.markdown + st.table 让 URL 可点击
st.markdown("### 审查日志")
st.table(df)
