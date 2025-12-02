import streamlit as st

# -------------------
# 추천 로직 함수들
# -------------------

def detect_cluster(middle_school: str) -> str:
    """중학교 이름을 기반으로 권역 클러스터 분류"""
    if not middle_school:
        return ""

    ms = middle_school.strip()

    # 북면/동읍권 -> 문성고 중심
    north_keywords = ["북면", "동읍"]
    if any(k in ms for k in north_keywords):
        return "north"

    # 마산 핵심권 -> 마산고/마산여고
    masan_keywords = ["양덕", "석전", "합성", "회원", "내서", "월영", "자산", "오동"]
    if any(k in ms for k in masan_keywords):
        return "masan_core"

    # 의창 핵심권 -> 중앙/사파
    uichang_keywords = ["용지", "팔용", "명서", "창원중"]
    if any(k in ms for k in uichang_keywords):
        return "uichang_core"

    # 성산 핵심권 -> 남고/명지여
    seongsan_keywords = ["상남", "사파", "반송", "성주", "용호"]
    if any(k in ms for k in seongsan_keywords):
        return "seongsan_core"

    return ""  # 특별 클러스터 없음


def base_first_choice(s_type: str, score: float, zone: str) -> str:
    """중학교 클러스터가 없을 때 사용하는 1지망 기본 로직"""
    if s_type == "탐구형":
        if score >= 90:
            if zone == "의창":
                return "창원중앙고"
            elif zone == "성산":
                return "창원남고"
            elif zone == "마산":
                return "마산고"
        elif score >= 85:
            if zone == "의창":
                return "창원중앙고"
            elif zone == "성산":
                return "창원남고"
            elif zone == "마산":
                return "마산고"
        # 85 미만
        if zone in ["의창", "성산"]:
            return "사파고"
        elif zone == "마산":
            return "마산고"

    elif s_type == "안정형":
        if zone in ["의창", "성산"]:
            return "사파고"
        elif zone == "마산":
            return "문성고"

    elif s_type == "도전형":
        if zone == "의창":
            return "창원중앙고"
        elif zone == "성산":
            return "창원남고"
        elif zone == "마산":
            return "마산고"

    return ""


def base_second_choice(s_type: str, score: float, zone: str) -> str:
    """중학교 클러스터가 없을 때 사용하는 2지망 기본 로직"""
    if s_type == "탐구형":
        if zone == "의창":
            return "창원남고"
        elif zone == "성산":
            return "창원중앙고"
        elif zone == "마산":
            return "창원중앙고"

    elif s_type == "안정형":
        if zone in ["의창", "성산"]:
            return "문성고"
        elif zone == "마산":
            return "사파고"

    elif s_type == "도전형":
        if zone == "의창":
            return "창원남고"
        elif zone == "성산":
            return "창원중앙고"
        elif zone == "마산":
            return "창원중앙고"

    return ""


def recommend_schools(name: str,
                      middle_school: str,
                      s_type: str,
                      score: float,
                      zone: str,
                      pref1: str = "",
                      pref2: str = ""):
    """
    지망 1~5 추천
    - name: 학생이름 (출력용)
    - middle_school: 중학교명
    - s_type: 성향 (탐구형/안정형/도전형)
    - score: 내신 평균
    - zone: 통학구역 (의창/성산/마산)
    - pref1, pref2: 선호학교 (로직에는 아직 직접 반영 X, 메모용)
    """

    cluster = detect_cluster(middle_school)
    rec1 = ""
    rec2 = ""
    rec3 = ""
    rec4 = ""
    rec5 = ""

    # 1지망: 중학교 클러스터 우선 + 기본로직 보완
    if cluster == "north":
        rec1 = "문성고"
    elif cluster == "masan_core":
        rec1 = "마산고"
    elif cluster == "uichang_core":
        rec1 = "창원중앙고"
    elif cluster == "seongsan_core":
        rec1 = "창원남고"
    else:
        rec1 = base_first_choice(s_type, score, zone)

    # 2지망: 클러스터별 2순위 + 기본로직
    if cluster == "north":
        rec2 = "창원중앙고"
    elif cluster == "masan_core":
        rec2 = "마산여고"
    elif cluster == "uichang_core":
        rec2 = "사파고"
    elif cluster == "seongsan_core":
        rec2 = "명지여고"
    else:
        rec2 = base_second_choice(s_type, score, zone)

    # 3,4,5지망: 통학구역 기반 안정 조합
    if zone in ["의창", "성산"]:
        rec3 = "사파고"
        rec4 = "문성고"
        rec5 = "신월고"
    elif zone == "마산":
        rec3 = "문성고"
        rec4 = "사파고"
        rec5 = "마산여고"

    # 중복 제거 간단 처리 (필요시 더 정교하게 가능)
    rec_list = []
    for r in [rec1, rec2, rec3, rec4, rec5]:
        if r and r not in rec_list:
            rec_list.append(r)

    # 5개 미만이면 신월고/문성고 등으로 채워도 되지만, 여기서는 있는 만큼만 반환
    return rec_list[:5]


# -------------------
# Streamlit UI
# -------------------

def main():
    st.set_page_config(page_title="창원 고입 지망 추천기", layout="centered")
    st.title("창원 고입 지망 자동 추천기 (학원용)")
    st.write("중학교, 성향, 내신, 통학구역을 입력하면 지망 1~5를 자동으로 추천합니다.")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("학생 이름", value="예시학생A")
        middle_school = st.text_input("중학교 이름", value="용지중")
        s_type = st.selectbox("성향 선택", ["탐구형", "안정형", "도전형"])
    with col2:
        score = st.number_input("내신 평균 점수 (예: 87)", min_value=0.0, max_value=100.0, value=93.0, step=0.5)
        zone = st.selectbox("통학구역", ["의창", "성산", "마산"])
        pref1 = st.text_input("선호학교1 (선택)", value="")
        pref2 = st.text_input("선호학교2 (선택)", value="")

    if st.button("지망 추천 보기"):
        recs = recommend_schools(name, middle_school, s_type, score, zone, pref1, pref2)

        if not recs:
            st.warning("조건에 맞는 추천 조합이 없습니다. 입력값을 다시 확인해 주세요.")
        else:
            st.subheader(f"📝 {name} 학생 추천 지망 결과")
            for i, school in enumerate(recs, start=1):
                st.write(f"**{i}지망:** {school}")

            st.markdown("---")
            st.caption("※ 실제 배정은 교육청 배정 기준 및 해당 연도 통계에 따라 달라질 수 있습니다.")


if __name__ == "__main__":
    main()
