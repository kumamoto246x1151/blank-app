import streamlit as st
import pandas as pd
import datetime
import os

# ページ設定
st.set_page_config(page_title="健康管理トラッカー", layout="wide")

# データ保存用のファイル名
DATA_FILE = "health_data.csv"

# データの読み込み関数
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # ファイルがない場合は空のDataFrameを作成
        return pd.DataFrame(columns=["日付", "運動時間(分)", "睡眠時間(時間)", "気分", "メモ"])

# データの保存関数
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# メイン処理
def main():
    st.title("🏃‍♂️ シンプル健康管理アプリ")
    
    # データのロード
    df = load_data()

    # --- サイドバー：データ入力 ---
    with st.sidebar:
        st.header("📝 今日の記録")
        
        input_date = st.date_input("日付", datetime.date.today())
        input_exercise = st.number_input("運動時間 (分)", min_value=0, max_value=300, step=10, value=30)
        input_sleep = st.number_input("睡眠時間 (時間)", min_value=0.0, max_value=24.0, step=0.5, value=7.0)
        input_mood = st.selectbox("今日の気分", ["😊 最高", "🙂 普通", "😫 疲れた"])
        input_memo = st.text_area("ひとことメモ", height=100)

        if st.button("記録を追加する"):
            # 新しいデータ行を作成
            new_data = pd.DataFrame({
                "日付": [input_date],
                "運動時間(分)": [input_exercise],
                "睡眠時間(時間)": [input_sleep],
                "気分": [input_mood],
                "メモ": [input_memo]
            })
            
            # 既存データと結合（日付を文字列に変換して重複排除などの処理を入れても良いが今回は単純追加）
            df = pd.concat([df, new_data], ignore_index=True)
            
            # 日付でソート
            df["日付"] = pd.to_datetime(df["日付"])
            df = df.sort_values("日付")
            
            save_data(df)
            st.success("記録しました！")

    # --- メインエリア：可視化 ---
    
    # データが存在する場合のみ表示
    if not df.empty:
        # 日付型への変換（念のため）
        df["日付"] = pd.to_datetime(df["日付"]).dt.date

        # 重要指標（KPI）の表示
        st.subheader("📊 直近のサマリー")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_sleep = df["睡眠時間(時間)"].mean()
            st.metric("平均睡眠時間", f"{avg_sleep:.1f} 時間")
        
        with col2:
            total_exercise = df["運動時間(分)"].sum()
            st.metric("累計運動時間", f"{total_exercise} 分")
        
        with col3:
            # 最新の気分を表示
            latest_mood = df.iloc[-1]["気分"]
            st.metric("最新の気分", latest_mood)

        st.divider()

        # グラフエリア
        st.subheader("📈 推移グラフ")
        
        tab1, tab2 = st.tabs(["睡眠時間の推移", "運動時間の推移"])
        
        with tab1:
            # 日付をインデックスにするとチャートが見やすい
            chart_data = df.set_index("日付")
            st.line_chart(chart_data["睡眠時間(時間)"])
            
        with tab2:
            st.bar_chart(chart_data["運動時間(分)"])

        st.divider()

        # データ一覧
        with st.expander("詳細データを見る"):
            st.dataframe(df, use_container_width=True)
            
            # CSVダウンロードボタン
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="CSVデータをダウンロード",
                data=csv,
                file_name='health_data.csv',
                mime='text/csv',
            )
    else:
        st.info("サイドバーから今日のデータを入力してください👈")

if __name__ == "__main__":
    main()
