import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# --- 앱 설정 및 디자인 ---
st.set_page_config(page_title="레지오 활동 기록부", page_icon="🙏")

# 성모님 아이콘 및 타이틀
ICON_URL = "https://cdn-icons-png.flaticon.com/512/2850/2850930.png" # 무료 성모님 아이콘
st.image(ICON_URL, width=80)
st.title("레지오 마리에 활동 기록부")

# --- 구글 시트 연결 설정 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 사용자 인증 및 소속 입력 (첫 화면) ---
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'praesidium' not in st.session_state:
    st.session_state.praesidium = ""

# 첫 화면: 쁘레시디움과 이름 입력
if not st.session_state.user_name or not st.session_state.praesidium:
    with st.form("login_form"):
        st.subheader("🍀 단원 로그인")
        praesidium_input = st.text_input("소속 쁘레시디움을 입력하세요 (예: 평화의 모후)")
        name_input = st.text_input("단원 성함을 입력하세요")
        submit_login = st.form_submit_button("입장하기")
        
        if submit_login:
            if praesidium_input and name_input:
                st.session_state.praesidium = praesidium_input
                st.session_state.user_name = name_input
                st.rerun()
            else:
                st.warning("쁘레시디움과 성함을 모두 입력해주세요.")
    st.stop()

# --- 메인 화면 ---
st.sidebar.write(f"⛪ **{st.session_state.praesidium}**")
st.sidebar.write(f"👤 **{st.session_state.user_name}** 단원님")
if st.sidebar.button("로그아웃"):
    del st.session_state.user_name
    del st.session_state.praesidium
    st.rerun()

# 1. 날짜 선택
selected_date = st.date_input("활동 날짜를 선택하세요", date.today())
date_str = selected_date.strftime("%Y-%m-%d")

# 구글 시트에서 데이터 불러오기
try:
    existing_data = conn.read(worksheet="Sheet1")
except Exception:
    existing_data = pd.DataFrame(columns=[
        "날짜", "쁘레시디움", "이름", "묵주기도", "미사", "주교기도", "사제기도", "주모경", "화살기도", 
        "활동7", "활동8", "활동9", "활동10"
    ])

# 해당 날짜/쁘레시디움/이름에 맞는 기존 기록 찾기
current_row = existing_data[
    (existing_data["날짜"] == date_str) & 
    (existing_data["쁘레시디움"] == st.session_state.praesidium) & 
    (existing_data["이름"] == st.session_state.user_name)
]

# 기존 입력값이 있으면 가져오고, 없으면 기본값 설정
def get_val(col, default=0):
    if not current_row.empty and col in current_row.columns:
        val = current_row[col].values[0]
        return val if pd.notna(val) else default
    return default

# --- 활동 기록 입력 UI ---
st.subheader(f"📅 {date_str} 활동 기록")

col1, col2 = st.columns(2)

with col1:
    st.write("**[수치 입력 (기도 및 성사)]**")
    r_val = st.number_input("1. 묵주기도 (단)", value=int(get_val("묵주기도")), step=5)
    m_val = st.number_input("2. 미사영성체 (회)", value=int(get_val("미사")), step=1)
    b_val = st.number_input("3. 주교를 위한 기도 (회)", value=int(get_val("주교기도")), step=1)
    p_val = st.number_input("4. 사제를 위한 기도 (회)", value=int(get_val("사제기도")), step=1)
    j_val = st.number_input("5. 주모경 (회)", value=int(get_val("주모경")), step=1)
    a_val = st.number_input("6. 화살기도 (회)", value=int(get_val("화살기도")), step=1)

with col2:
    st.write("**[텍스트 입력 (활동 내용)]**")
    t7 = st.text_input("7. 입교권면/예신돌봄/교우돌봄", value=str(get_val("활동7", "")))
    t8 = st.text_input("8. 레지오확장/소공동체활동/본당협조", value=str(get_val("활동8", "")))
    t9 = st.text_input("9. 가정성화/개인성화", value=str(get_val("활동9", "")))
    t10 = st.text_input("10. 본당지시/냉담교우돌봄/기타", value=str(get_val("활동10", "")))

if st.button("💾 활동 기록 저장하기", use_container_width=True):
    # 새 데이터 행 생성
    new_data = pd.DataFrame([{
        "날짜": date_str, 
        "쁘레시디움": st.session_state.praesidium, 
        "이름": st.session_state.user_name,
        "묵주기도": r_val, "미사": m_val, "주교기도": b_val, "사제기도": p_val, "주모경": j_val, "화살기도": a_val,
        "활동7": t7.strip(), "활동8": t8.strip(), "활동9": t9.strip(), "활동10": t10.strip()
    }])
    
    # 중복 제거 후 병합 (동일 날짜, 동일인 기록 덮어쓰기)
    filtered_existing = existing_data[
        ~((existing_data["날짜"] == date_str) & 
          (existing_data["쁘레시디움"] == st.session_state.praesidium) & 
          (existing_data["이름"] == st.session_state.user_name))
    ]
    updated_df = pd.concat([filtered_existing, new_data], ignore_index=True)
    
    conn.update(worksheet="Sheet1", data=updated_df)
    st.success("성공적으로 저장되었습니다!")

st.divider()

# --- 통계 및 카톡 보고 기능 ---
st.subheader("📊 기간별 활동 합계 및 카톡 보고")
s_date = st.date_input("시작 날짜", date.today().replace(day=1))
e_date = st.date_input("종료 날짜", date.today())

# 텍스트 활동 내역 병합용 함수
def aggregate_text_activity(df, col_name):
    # 빈 값(NaN, 공백) 제외하고 유효한 글자만 리스트로 추출
    valid_entries = df[col_name].dropna().astype(str).str.strip()
    valid_entries = valid_entries[valid_entries != ""]
    
    count = len(valid_entries)
    if count > 0:
        details = ", ".join(valid_entries)
        return f"{count}회 ({details})"
    return "0회"

if st.button("보고서 생성 및 카톡 텍스트 만들기"):
    # 현재 로그인한 단원의 해당 기간 데이터 필터링
    report_df = existing_data[
        (existing_data["쁘레시디움"] == st.session_state.praesidium) &
        (existing_data["이름"] == st.session_state.user_name) & 
        (existing_data["날짜"].between(s_date.strftime("%Y-%m-%d"), e_date.strftime("%Y-%m-%d")))
    ]
    
    if not report_df.empty:
        # 수치 항목 합계 구하기
        sum_r = int(report_df["묵주기도"].fillna(0).astype(int).sum())
        sum_m = int(report_df["미사"].fillna(0).astype(int).sum())
        sum_b = int(report_df["주교기도"].fillna(0).astype(int).sum())
        sum_p = int(report_df["사제기도"].fillna(0).astype(int).sum())
        sum_j = int(report_df["주모경"].fillna(0).astype(int).sum())
        sum_a = int(report_df["화살기도"].fillna(0).astype(int).sum())
        
        # 텍스트 항목 스마트 합산
        agg_7 = aggregate_text_activity(report_df, "활동7")
        agg_8 = aggregate_text_activity(report_df, "활동8")
        agg_9 = aggregate_text_activity(report_df, "활동9")
        agg_10 = aggregate_text_activity(report_df, "활동10")
        
        # 화면에 요약 표 보여주기
        st.write(f"**[{s_date} ~ {e_date}] 합산 결과**")
        st.table(pd.DataFrame({
            "활동 구분": ["묵주기도(단)", "미사영성체(회)", "주교기도(회)", "사제기도(회)", "주모경(회)", "화살기도(회)"],
            "총 합계": [sum_r, sum_m, sum_b, sum_p, sum_j, sum_a]
        }))
        
        # 카톡 전송용 텍스트 포맷 (날짜별 나열 없이 깔끔하게 합산된 것만 표시)
        report_text = (
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🙏 [{st.session_state.praesidium}] 활동 보고\n"
            f"👤 단원명: {st.session_state.user_name}\n"
            f"📅 기간: {s_date} ~ {e_date}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"1. 묵주기도: {sum_r}단\n"
            f"2. 미사영성체: {sum_m}회\n"
            f"3. 주교를 위한 기도: {sum_b}회\n"
            f"4. 사제를 위한 기도: {sum_p}회\n"
            f"5. 주모경: {sum_j}회\n"
            f"6. 화살기도: {sum_a}회\n"
            f"7. 입교/예신/교우돌봄: {agg_7}\n"
            f"8. 레지오확장/소공동체/본당협조: {agg_8}\n"
            f"9. 가정성화/개인성화: {agg_9}\n"
            f"10. 본당지시/냉담교우돌봄/기타: {agg_10}\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )
        
        st.text_area("📋 아래 텍스트를 복사해서 카톡에 붙여넣으세요!", value=report_text, height=320)
    else:
        st.warning("선택하신 기간에는 저장된 활동 기록이 없습니다. 날짜를 확인해 주세요!")