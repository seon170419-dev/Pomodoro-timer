import time
import streamlit as st

st.set_page_config(page_title="Pomodoro Timer", page_icon="⏳", layout="wide")

# ----------------------
# 상태 저장
# ----------------------
if "running" not in st.session_state:
    st.session_state.running = False
if "duration_sec" not in st.session_state:
    st.session_state.duration_sec = 25 * 60
if "end_time" not in st.session_state:
    st.session_state.end_time = None
if "last_set_minutes" not in st.session_state:
    st.session_state.last_set_minutes = 25

def fmt_mmss(sec: int) -> str:
    m = sec // 60
    s = sec % 60
    return f"{m:02d}:{s:02d}"

# ----------------------
# 상단 타이틀
# ----------------------
st.markdown("# ⏳ Online Pomodore Timer")

# ----------------------
# 2열 레이아웃 (왼쪽=이미지/남은시간, 오른쪽=설정/버튼)
# ----------------------
left, right = st.columns([1.2, 1])

# ===== 오른쪽: 설정/버튼 =====
with right:
    st.subheader("설정")

    minutes = st.slider(
        "타이머 설정 (분)",
        min_value=1, max_value=60,
        value=st.session_state.last_set_minutes,
        disabled=st.session_state.running,  # 실행 중엔 설정 잠금(원하면 이 줄 삭제 가능)
    )

    colA, colB = st.columns(2)
    with colA:
        start_clicked = st.button("▶ 시작", use_container_width=True, disabled=st.session_state.running)
    with colB:
        stop_clicked = st.button("■ 중지/리셋", use_container_width=True)

    # 버튼 동작
    if start_clicked:
        st.session_state.last_set_minutes = minutes
        st.session_state.duration_sec = minutes * 60
        st.session_state.end_time = time.time() + st.session_state.duration_sec
        st.session_state.running = True

    if stop_clicked:
        st.session_state.running = False
        st.session_state.end_time = None

    st.markdown("---")
    if st.session_state.running and st.session_state.end_time:
        remaining = max(0, int(st.session_state.end_time - time.time()))
        st.write("상태: ⏱ 진행 중")
        st.write(f"설정시간: **{st.session_state.duration_sec//60:02d}:00**")
        st.write(f"남은시간: **{fmt_mmss(remaining)}**")
    else:
        st.write("상태: ⏸ 대기")
        st.write(f"설정시간: **{minutes:02d}:00**")
        st.caption("설정 후 시작을 눌러주세요.")

# ===== 왼쪽: 이미지 + 남은시간(크게) =====
with left:
    # (1) 이미지 표시: 레포에 업로드한 timer.png를 불러옴
    #     파일명이 다르면 여기만 바꿔줘.
    try:
        st.image("낼나 타이머 이미지.png", use_container_width=True)
    except Exception:
        st.info("왼쪽에 보여줄 이미지 파일을 레포에 `낼나 타이머 이미지.png`로 업로드해 주세요.")

    # (2) 남은 시간/원형 진행 표시
    progress_placeholder = st.empty()
    text_placeholder = st.empty()

    if st.session_state.running and st.session_state.end_time is not None:
        remaining = int(st.session_state.end_time - time.time())
        if remaining <= 0:
            st.session_state.running = False
            remaining = 0

        remaining_ratio = remaining / st.session_state.duration_sec if st.session_state.duration_sec else 0

        # 원형이 줄어드는 SVG
        size = 220
        stroke = 16
        r = (size - stroke) / 2
        c = 2 * 3.1415926535 * r
        dash = c * remaining_ratio
        gap = c - dash

        svg = f"""
        <div style="display:flex; justify-content:flex-start; gap:24px; align-items:center; margin-top:8px;">
          <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
            <circle cx="{size/2}" cy="{size/2}" r="{r}"
                    fill="none" stroke="#e6e6e6" stroke-width="{stroke}"/>
            <circle cx="{size/2}" cy="{size/2}" r="{r}"
                    fill="none" stroke="#4C78A8" stroke-width="{stroke}"
                    stroke-linecap="round"
                    stroke-dasharray="{dash} {gap}"
                    transform="rotate(-90 {size/2} {size/2})"/>
          </svg>
          <div style="font-size:44px; font-weight:800;">
            {fmt_mmss(remaining)}
            <div style="font-size:14px; font-weight:500; color:#666; margin-top:6px;">
              (분, 초) 남은시간
            </div>
          </div>
        </div>
        """
        progress_placeholder.markdown(svg, unsafe_allow_html=True)
        text_placeholder.empty()

        time.sleep(0.2)
        st.rerun()
    else:
        # 대기 상태 표시
        progress_placeholder.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:16px; margin-top:10px;">
              <div style="font-size:44px; font-weight:800;">{st.session_state.last_set_minutes:02d}:00</div>
              <div style="color:#666;">설정 후 시작을 눌러주세요.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        text_placeholder.empty()
