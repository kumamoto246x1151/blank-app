import streamlit as st
import pandas as pd
import datetime
from supabase import create_client

# -----------------------------
# Supabase 接続設定
# -----------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_ANON_KEY"]
supabase = create_client(url, key)

# -----------------------------
# ページ設定
# -----------------------------
st.set_page_config(page_title="健康管理トラッカー", layout="wide")

# -----------------------------
# データ読み込み（Supabase）
# -----------------------------
def load_data():
    res = supabase.table("health_data").select("*").order("date").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df
    else:
        return pd.DataFrame(columns=["date", "exercise", "sleep", "mood", "memo"])

# -----------------------------
# メイン処理
# -----------------------------
def main():
    st.title("🏃‍♂️ シンプル健康管理アプリ")

    df = load_data()

    # =============================
    # サイドバー：入力
    # =============================
    with st.sidebar:
        st.header("📝 今日の記録")

        input_date = st.date_input("日付", datetime.date.today())
        input_exercise = st.number_input(
            "運動時間 (分)", min_value=0, max_value=300, step=10, value=30
        )
        input_sleep = st.number_input(
            "睡眠時間 (時間)", min_value=0.0, max_value=24.0, step=0.5, value=7.0
        )
        input_mood = st.selectbox("今日の気分", ["😊 最高", "🙂 普通", "😫 疲れた"])
        input_memo = st.text_area("ひとことメモ", height=100)

        if st.button("記録を追加する"):
            supabase.table("health_data").upsert({
                "date": input_date,
                "exercise": input_exercise,
                "sleep": input_sleep,
                "mood": input_mood,
                "memo": input_memo
            }).execute()

            st.success("記録しました！")
            st.rerun()

    # =============================
    # メイン表示
    # =============================
    if not df.empty:
        # 表示用に列名を日本語に変換
        df_disp = df.rename(columns={
            "date": "日付",
            "exercise": "運動時間(分)",
            "sleep": "睡眠時間(時間)",
            "mood": "気分",
            "memo": "メモ"
        })

        # KPI
        st.subheader("📊 直近のサマリー")
        col1, col2, col3 = st.columns(3)

        with col1:
            avg_sleep = df_disp["睡眠時間(時間)"].mean()
            st.metric("平均睡眠時間", f"{avg_sleep:.1f} 時間")

        with col2:
            total_exercise = df_disp["運動時間(分)"].sum()
            st.metric("累計運動時間", f"{total_exercise} 分")

        with col3:
            latest_mood = df_disp.iloc[-1]["気分"]
            st.metric("最新の気分", latest_mood)

        st.divider()

        # グラフ
        st.subheader("📈 推移グラフ")
        tab1, tab2 = st.tabs(["睡眠時間の推移", "運動時間の推移"])

        chart_data = df_disp.set_index("日付")

        with tab1:
            st.line_chart(chart_data["睡眠時間(時間)"])

        with tab2:
            st.bar_chart(chart_data["運動時間(分)"])

        st.divider()

        # =============================
        # データ管理（削除）
        # =============================
        st.subheader("🛠 データ管理")

        with st.expander("データの確認・削除はこちら"):
            st.dataframe(df_disp, use_container_width=True)

            st.write("---")
            st.write("🗑 **データの削除**")

            date_options = (
                df_disp["日付"]
                .sort_values(ascending=False)
                .astype(str)
                .unique()
            )

            delete_target = st.selectbox(
                "削除したい日付を選択してください",
                options=date_options
            )

            if st.button("選択した日のデータを削除"):
                supabase.table("health_data").delete().eq(
                    "date", delete_target
                ).execute()

                st.warning(f"{delete_target} のデータを削除しました。")
                st.rerun()

            st.write("---")

            # CSV ダウンロード
            csv = df_disp.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="CSVデータをダウンロード",
                data=csv,
                file_name="health_data.csv",
                mime="text/csv",
            )

    else:
        st.info("サイドバーから今日のデータを入力してください👈")

# -----------------------------
# 実行
# -----------------------------
if __name__ == "__main__":
    main()
