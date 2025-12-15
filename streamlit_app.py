import time
import streamlit as st

import base64
from pathlib import Path

def img_to_base64(path: str) -> str:
    data = Path(path).read_bytes()
    return base64.b64encode(data).decode("utf-8")

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
      with left:
    # --- 현재 남은 시간 계산 ---
    if st.session_state.running and st.session_state.end_time is not None:
        remaining = int(st.session_state.end_time - time.time())
        if remaining <= 0:
            st.session_state.running = False
            remaining = 0
        ratio = remaining / st.session_state.duration_sec if st.session_state.duration_sec else 0
    else:
        remaining = st.session_state.last_set_minutes * 60
        ratio = 1.0

    # --- 이미지 base64로 HTML에 삽입 (오버레이 하려고) ---
    b64 = img_to_base64("timer.png")

    # --- 오버레이 원(도넛) 설정값: 여기만 튜닝하면 정렬 딱 맞출 수 있음 ---
    IMG_W = 340                 # 화면에서 보일 이미지 가로폭(px)
    SVG_SIZE = 300              # 원 크기(px) - 이미지보다 약간 작게
    TOP_OFFSET = 18             # 원을 위/아래로 이동 (px)
    LEFT_OFFSET = 20            # 원을 좌/우로 이동 (px)
    STROKE = 28                 # 도넛 두께 (두꺼울수록 가운데 구멍 작아짐)
    GREEN = "#1F5E3B"           # 타이머 초록에 가깝게 (원하면 바꿔줘)

    # 원(아크) 계산
    r = (SVG_SIZE - STROKE) / 2
    c = 2 * 3.1415926535 * r
    dash = c * ratio
    gap = c - dash

    html = f"""
    <div style="position:relative; width:{IMG_W}px; margin-top:10px;">
      <img src="data:image/png;base64,{b64}" style="width:{IMG_W}px; display:block;" />

      <!-- 오버레이 SVG: 이미지 위에 겹치기 -->
      <svg width="{SVG_SIZE}" height="{SVG_SIZE}"
           style="position:absolute; top:{TOP_OFFSET}px; left:{LEFT_OFFSET}px; pointer-events:none;">
        <!-- 배경 링(연한 회색) -->
        <circle cx="{SVG_SIZE/2}" cy="{SVG_SIZE/2}" r="{r}"
                fill="none" stroke="rgba(0,0,0,0.08)" stroke-width="{STROKE}"/>
        <!-- 진행 링(초록) -->
        <circle cx="{SVG_SIZE/2}" cy="{SVG_SIZE/2}" r="{r}"
                fill="none" stroke="{GREEN}" stroke-width="{STROKE}"
                stroke-linecap="round"
                stroke-dasharray="{dash} {gap}"
                transform="rotate(-90 {SVG_SIZE/2} {SVG_SIZE/2})"/>
      </svg>
    </div>

    <div style="font-size:52px; font-weight:800; margin-top:14px;">
      {fmt_mmss(remaining)}
      <div style="font-size:14px; font-weight:500; color:#666; margin-top:6px;">
        (분, 초) 남은시간
      </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    if st.session_state.running:
        time.sleep(0.2)
        st.rerun()
