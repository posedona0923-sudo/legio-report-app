import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import calendar
from datetime import datetime, date

# 1. 페이지 기본 설정 및 성모님 아이콘(Favicon) 등록
st.set_page_config(
    page_title="레지오 활동 보고",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/4/4e/Miraculous_Medal_Mary.png", # 성모님 메달 이미지
    layout="centered"
)

# 2. 마리안 블루 테마 적용을 위한 커스텀 CSS
st.markdown("""
<style>
    /* 메인 배경 및 텍스트 색상 */
    .stApp {
        background-color: #F8FAFC;
    }
    /* 버튼 스타일 (마리안 블루) */
    div.stButton > button:first-child {
        background-color: #1E40AF;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: all 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #1D4ED8;
        transform: scale(1.02);
    }
    /* 달력 일요일/토요일 색상 설정 */
    .sunday { color: #EF4444; font-weight: bold; }
    .saturday { color: #3B82F6; font-weight: bold; }
    .weekday { color: #1F2937; }
    
    /* 카드 디자인 */
    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets 연결 생성
conn = st.connection("gsheets", type=GSheetsConnection)

# 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "selected_date" not in st.session_state:
    st.session_state.selected_date = None
if "current_year" not in st.session_state:
    st.session_state.current_year = datetime.now().year
if "current_month" not in st.session_state:
    st.session_state.current_month = datetime.now().month

# ----------------- [화면 1: 로그인 화면] -----------------
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #1E40AF;'>💙 레지오 활동 보고</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B;'>성모님의 군대, 단원들의 활동을 기록합니다.</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        presidium = st.text_input("소속 쁘레시디움 (예: 평화의 모후)", key="input_pr")
        name = st.text_input("단원 이름", key="input_name")
        
        if st.button("입장하기"):
            if presidium and name:
                st.session_state.presidium = presidium
                st.session_state.name = name
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.warning("소속 쁘레시디움과 이름을 모두 입력해주세요.")
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- [화면 2: 달력 및 입력/집계 화면] -----------------
else:
    # 상단 단원 정보 바
    st.markdown(f"""
    <div style='background-color: #1E40AF; padding: 15px; border-radius: 8px; color: white; margin-bottom: 20px;'>
        <h4 style='margin:0;'>🇻🇦 {st.session_state.presidium} Pr.</h4>
        <p style='margin:0; font-size: 0.9rem;'>{st.session_state.name} 단원님 환영합니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # 데이터 불러오기
    try:
        df = conn.read()
    except:
        # 구글 시트가 비어있을 경우 예외 처리용 빈 프레임 생성
        df = pd.DataFrame(columns=[
            "날짜", "쁘레시디움", "이름", 
            "묵주기도", "미사영성체", "사제기도", "주모경", "화살기도",
            "교우돌봄", "냉담교우", "입교권면", "연도상가", "본당협조", "본당지시", "기타활동"
        ])

    # ----------------- [달력 영역] -----------------
    if st.session_state.selected_date is None:
        st.markdown("### 📅 활동 날짜 선택")
        
        # 월 이동 컨트롤
        col_prev, col_month, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("◀ 이전 달"):
                if st.session_state.current_month == 1:
                    st.session_state.current_month = 12
                    st.session_state.current_year -= 1
                else:
                    st.session_state.current_month -= 1
                st.rerun()
        with col_month:
            st.markdown(f"<h3 style='text-align: center;'>{st.session_state.current_year}년 {st.session_state.current_month}월</h3>", unsafe_allow_html=True)
        with col_next:
            if st.button("다음 달 ▶"):
                if st.session_state.current_month == 12:
                    st.session_state.current_month = 1
                    st.session_state.current_year += 1
                else:
                    st.session_state.current_month += 1
                st.rerun()

        # 달력 그리드 생성
        cal = calendar.monthcalendar(st.session_state.current_year, st.session_state.current_month)
        days = ["일", "월", "화", "수", "목", "금", "토"]
        
        # 요일 헤더
        cols = st.columns(7)
        for i, day in enumerate(days):
            if i == 0:
                cols[i].markdown(f"<p class='sunday' style='text-align:center;'>{day}</p>", unsafe_allow_html=True)
            elif i == 6:
                cols[i].markdown(f"<p class='saturday' style='text-align:center;'>{day}</p>", unsafe_allow_html=True)
            else:
                cols[i].markdown(f"<p class='weekday' style='text-align:center;'>{day}</p>", unsafe_allow_html=True)

        # 날짜 버튼 배치
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].write("")  # 빈 칸
                else:
                    # 해당 날짜에 기록이 있는지 확인 (파란 점 표시용)
                    target_date_str = f"{st.session_state.current_year}-{st.session_state.current_month:02d}-{day:02d}"
                    has_record = False
                    if not df.empty:
                        has_record = any((df["날짜"] == target_date_str) & (df["이름"] == st.session_state.name))
                    
                    label = f"{day}\n🔵" if has_record else f"{day}"
                    
                    # 일요일은 빨갛게, 토요일은 파랗게 스타일링 적용
                    if cols[i].button(label, key=f"day_{day}"):
                        st.session_state.selected_date = target_date_str
                        st.rerun()

        # ----------------- [기간별 집계 및 카카오톡 생성] -----------------
        st.markdown("---")
        st.markdown("### 📊 기간별 활동 합계")
        
        # 날짜 범위 설정
        col_s, col_e = st.columns(2)
        with col_s:
            start_date = st.date_input("시작일", date(st.session_state.current_year, st.session_state.current_month, 1))
        with col_e:
            end_date = st.date_input("종료일", datetime.today().date())

        if not df.empty:
            # 기간 및 내 기록으로 필터링
            df["날짜_dt"] = pd.to_datetime(df["날짜"]).dt.date
            filtered_df = df[(df["이름"] == st.session_state.name) & (df["날짜_dt"] >= start_date) & (df["날짜_dt"] <= end_date)]
            
            if not filtered_df.empty:
                # 숫자 데이터 합산
                rosary_sum = pd.to_numeric(filtered_df["묵주기도"]).sum()
                mass_sum = pd.to_numeric(filtered_df["미사영성체"]).sum()
                priest_sum = pd.to_numeric(filtered_df["사제기도"]).sum()
                lord_sum = pd.to_numeric(filtered_df["주모경"]).sum()
                arrow_sum = pd.to_numeric(filtered_df["화살기도"]).sum()

                # 화면에 합계 출력
                st.markdown(f"""
                <div class='card'>
                    <h4 style='color: #1E40AF; margin-top:0;'>✨ 집계 결과 ({start_date} ~ {end_date})</h4>
                    <li><b>묵주기도:</b> {int(rosary_sum)}단</li>
                    <li><b>미사영성체:</b> {int(mass_sum)}회</li>
                    <li><b>사제를 위한 기도:</b> {int(priest_sum)}회</li>
                    <li><b>주모경:</b> {int(lord_sum)}회</li>
                    <li><b>화살기도:</b> {int(arrow_sum)}회</li>
                </div>
                """, unsafe_allow_html=True)

                # 활동 텍스트 모으기
                activities = {
                    "교우돌봄": filtered_df["교우돌봄"].dropna().tolist(),
                    "냉담교우": filtered_df["냉담교우"].dropna().tolist(),
                    "입교권면": filtered_df["입교권면"].dropna().tolist(),
                    "연도상가": filtered_df["연도상가"].dropna().tolist(),
                    "본당협조": filtered_df["본당협조"].dropna().tolist(),
                    "본당지시": filtered_df["본당지시"].dropna().tolist(),
                    "기타활동": filtered_df["기타활동"].dropna().tolist(),
                }

                # 카카오톡 보고서 텍스트 빌더
                kakao_report = f"[레지오 단원 활동 보고]\n"
                kakao_report += f"━━━━━━━━━━━━━━━━━━\n"
                kakao_report += f"■ 소속: {st.session_state.presidium} Pr.\n"
                kakao_report += f"■ 단원: {st.session_state.name}\n"
                kakao_report += f"■ 기간: {start_date} ~ {end_date}\n\n"
                kakao_report += f"[1. 기도 및 성사 합계]\n"
                kakao_report += f" - 묵주기도: {int(rosary_sum)}단\n"
                kakao_report += f" - 미사영성체: {int(mass_sum)}회\n"
                kakao_report += f" - 사제를 위한 기도: {int(priest_sum)}회\n"
                kakao_report += f" - 주모경: {int(lord_sum)}회\n"
                kakao_report += f" - 화살기도: {int(arrow_sum)}회\n\n"
                kakao_report += f"[2. 활동 내용 요약]\n"
                
                has_activity_content = False
                for key, items in activities.items():
                    valid_items = [i for i in items if str(i).strip() and str(i).strip() != 'nan']
                    if valid_items:
                        has_activity_content = True
                        kakao_report += f"• {key}:\n"
                        for item in valid_items:
                            kakao_report += f"  - {item}\n"
                
                if not has_activity_content:
                    kakao_report += " - 기간 내 특별한 활동 기록 없음\n"
                kakao_report += f"━━━━━━━━━━━━━━━━━━"

                st.markdown("#### 💬 카카오톡 보고용 텍스트")
                st.text_area("아래 텍스트를 복사해서 카톡방에 올리세요!", value=kakao_report, height=250)
            else:
                st.info("선택한 기간에 등록된 활동 기록이 없습니다.")
        else:
            st.info("아직 등록된 전체 데이터가 없습니다.")

    # ----------------- [화면 3: 활동 입력창 (날짜 클릭 시)] -----------------
    else:
        st.markdown(f"### ✍️ {st.session_state.selected_date} 활동 기록")
        
        # 기존 기록이 있다면 불러와서 채우기
        existing_row = df[(df["날짜"] == st.session_state.selected_date) & (df["이름"] == st.session_state.name)]
        
        # 기본값 세팅
        def get_val(col, default_val=0):
            if not existing_row.empty and col in existing_row.columns:
                val = existing_row.iloc[0][col]
                return int(val) if isinstance(default_val, int) else str(val)
            return default_val

        st.markdown("#### 🛐 기도 · 성사")
        col1, col2 = st.columns(2)
        with col1:
            rosary = st.number_input("1. 묵주기도 (단)", min_value=0, value=get_val("묵주기도"), step=1)
            mass = st.number_input("2. 미사영성체 (회)", min_value=0, value=get_val("미사영성체"), step=1)
            priest = st.number_input("3. 사제를 위한 기도 (회)", min_value=0, value=get_val("사제기도"), step=1)
        with col2:
            lord = st.number_input("4. 주모경 (회)", min_value=0, value=get_val("주모경"), step=1)
            arrow = st.number_input("5. 화살기도 (회)", min_value=0, value=get_val("화살기도"), step=1)

        st.markdown("#### 🤝 활동 내용")
        care_faithful = st.text_input("6. 교우돌봄", value=get_val("교우돌봄", ""))
        care_cold = st.text_input("7. 냉담교우돌봄", value=get_val("냉담교우", ""))
        evangelization = st.text_input("8. 입교권면", value=get_val("입교권면", ""))
        funeral = st.text_input("9. 연도/상가돌봄", value=get_val("연도상가", ""))
        parish_support = st.text_input("10. 본당협조", value=get_val("본당협조", ""))
        parish_command = st.text_input("11. 본당지시", value=get_val("본당지시", ""))
        other_activity = st.text_input("12. 기타 활동", value=get_val("기타활동", ""))

        col_back, col_save = st.columns(2)
        with col_back:
            if st.button("🔙 취소 (달력으로)"):
                st.session_state.selected_date = None
                st.rerun()
        with col_save:
            if st.button("💾 저장하기"):
                # 기존 데이터가 있으면 업데이트, 없으면 행 추가
                new_data = {
                    "날짜": st.session_state.selected_date,
                    "쁘레시디움": st.session_state.presidium,
                    "이름": st.session_state.name,
                    "묵주기도": rosary,
                    "미사영성체": mass,
                    "사제기도": priest,
                    "주모경": lord,
                    "화살기도": arrow,
                    "교우돌봄": care_faithful,
                    "냉담교우": care_cold,
                    "입교권면": evangelization,
                    "연도상가": funeral,
                    "본당협조": parish_support,
                    "본당지시": parish_command,
                    "기타활동": other_activity
                }
                
                # 데이터 프레임 업데이트 로직
                if not df.empty:
                    idx = df[(df["날짜"] == st.session_state.selected_date) & (df["이름"] == st.session_state.name)].index
                    if not idx.empty:
                        for col, val in new_data.items():
                            df.at[idx[0], col] = val
                    else:
                        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                else:
                    df = pd.DataFrame([new_data])
                
                # 구글 시트에 업데이트 반영
                conn.update(data=df)
                st.success("성공적으로 저장되었습니다!")
                st.session_state.selected_date = None
                st.rerun()
