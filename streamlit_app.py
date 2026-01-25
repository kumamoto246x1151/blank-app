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
        # 日付カラムをdatetime型として読み込む
        df = pd.read_csv(DATA_FILE)
        return df
    else:
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
            # 新しいデータ行
            new_data = pd.DataFrame({
                "日付": [input_date],
                "運動時間(分)": [input_exercise],
                "睡眠時間(時間)": [input_sleep],
                "気分": [input_mood],
                "メモ": [input_memo]
            })
            
            # 日付を統一して扱うために一旦datetime型に変換
            new_data["日付"] = pd.to_datetime(new_data["日付"]).dt.date
            if not df.empty:
                df["日付"] = pd.to_datetime(df["日付"]).dt.date

            # 既存データと結合
            df = pd.concat([df, new_data], ignore_index=True)
            
            # 同じ日のデータが既にある場合は、古い方を消して新しい方を残す（上書き保存のような挙動）
            df = df.drop_duplicates(subset=["日付"], keep='last')
            
            # 日付でソート
            df = df.sort_values("日付")
            
            save_data(df)
            st.success("記録しました！")
            st.rerun() # 画面を更新

    # --- メインエリア：可視化 ---
    if not df.empty:
        # データ処理用に日付型を確実に変換
        df["日付"] = pd.to_datetime(df["日付"]).dt.date

        # 重要指標（KPI）
        st.subheader("📊 直近のサマリー")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_sleep = df["睡眠時間(時間)"].mean()
            st.metric("平均睡眠時間", f"{avg_sleep:.1f} 時間")
        
        with col2:
            total_exercise = df["運動時間(分)"].sum()
            st.metric("累計運動時間", f"{total_exercise} 分")
        
        with col3:
            latest_mood = df.iloc[-1]["気分"]
            st.metric("最新の気分", latest_mood)

        st.divider()

        # グラフエリア
        st.subheader("📈 推移グラフ")
        tab1, tab2 = st.tabs(["睡眠時間の推移", "運動時間の推移"])
        
        chart_data = df.set_index("日付")
        
        with tab1:
            st.line_chart(chart_data["睡眠時間(時間)"])
        with tab2:
            st.bar_chart(chart_data["運動時間(分)"])

        st.divider()

        # --- データ管理エリア（削除機能付き） ---
        st.subheader("🛠 データ管理")
        
        with st.expander("データの確認・削除はこちら"):
            st.dataframe(df, use_container_width=True)
            
            st.write("---")
            st.write("🗑 **データの削除**")
            
            # 削除対象の日付を選択するセレクトボックス
            # 日付リストを作成（新しい順）
            date_options = df["日付"].sort_values(ascending=False).astype(str).unique()
            delete_target = st.selectbox("削除したい日付を選択してください", options=date_options)
            
            if st.button("選択した日のデータを削除"):
                # 文字列比較で削除対象を特定
                df = df[df["日付"].astype(str) != delete_target]
                save_data(df)
                st.warning(f"{delete_target} のデータを削除しました。")
                st.rerun() # 画面をリロードして反映

            st.write("---")
            # CSVダウンロード
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
