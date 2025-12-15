import time
import streamlit as st

st.set_page_config(page_title="Pomodoro Timer", page_icon="⏳", layout="centered")

st.title("⏳ 온라인 뽀모도로 타이머")

# --- 상태 저장(새로고침해도 값 유지) ---
if "running" not in st.session_state:
    st.session_state.running = False
if "duration_sec" not in st.session_state:
    st.session_state.duration_sec = 25 * 60
if "end_time" not in st.session_state:
    st.session_state.end_time = None

# --- 설정 UI ---
col1, col2 = st.columns([2, 1])

with col1:
    minutes = st.slider("타이머 설정 (분)", min_value=1, max_value=60, value=25)
with col2:
    st.write("")
    st.write("")
    start_clicked = st.button("▶ 시작", use_container_width=True)

stop_clicked = st.button("■ 중지/리셋", use_container_width=True)

# --- 버튼 동작 ---
if start_clicked and not st.session_state.running:
    st.session_state.duration_sec = minutes * 60
    st.session_state.end_time = time.time() + st.session_state.duration_sec
    st.session_state.running = True

if stop_clicked:
    st.session_state.running = False
    st.session_state.end_time = None

# --- 표시 영역 ---
progress_placeholder = st.empty()
text_placeholder = st.empty()

def fmt_mmss(sec: int) -> str:
    m = sec // 60
    s = sec % 60
    return f"{m:02d}:{s:02d}"

# --- 실행 루프 (짧은 주기로 화면 갱신) ---
if st.session_state.running and st.session_state.end_time is not None:
    remaining = int(st.session_state.end_time - time.time())
    if remaining <= 0:
        st.session_state.running = False
        remaining = 0

    # 진행률(0~1). 시간이 줄수록 원이 줄어들게 = 남은 비율 사용
    remaining_ratio = remaining / st.session_state.duration_sec if st.session_state.duration_sec else 0

    # Streamlit 기본 progress bar는 막대지만,
    # "원형처럼" 보이게 간단한 SVG를 만들어서 보여줌 (이미지처럼 줄어드는 원)
    size = 220
    stroke = 16
    r = (size - stroke) / 2
    c = 2 * 3.1415926535 * r
    dash = c * remaining_ratio
    gap = c - dash

    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{size/2}" cy="{size/2}" r="{r}"
              fill="none" stroke="#e6e6e6" stroke-width="{stroke}"/>
      <circle cx="{size/2}" cy="{size/2}" r="{r}"
              fill="none" stroke="#4C78A8" stroke-width="{stroke}"
              stroke-linecap="round"
              stroke-dasharray="{dash} {gap}"
              transform="rotate(-90 {size/2} {size/2})"/>
    </svg>
    """

    progress_placeholder.markdown(svg, unsafe_allow_html=True)
    text_placeholder.markdown(
        f"<h2 style='text-align:center; margin-top:-10px;'>남은 시간: {fmt_mmss(remaining)}</h2>",
        unsafe_allow_html=True,
    )

    # 0.2초마다 갱신 (너무 빠르면 서버 부담)
    time.sleep(0.2)
    st.rerun()

else:
    # 대기 상태(시작 전)
    progress_placeholder.markdown(
        "<div style='text-align:center; color: #888;'>설정 후 시작을 눌러주세요.</div>",
        unsafe_allow_html=True,
    )
    text_placeholder.markdown(
        f"<h2 style='text-align:center;'>설정 시간: {minutes:02d}:00</h2>",
        unsafe_allow_html=True,
    )
