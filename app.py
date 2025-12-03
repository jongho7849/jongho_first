import streamlit as st

# ==============================
#  기본 추천 로직 함수들
# ==============================

def detect_cluster(middle_school: str) -> str:
    """중학교 이름을 기반으로 권역 클러스터 분류"""
    if not middle_school:
        return ""

    ms = middle_school.strip()

    # 북측권: 창북중 / 북면 / 동읍 / 감계
    north_keywords = ["창북중", "창북", "북면", "동읍", "감계", "감계중"]
    if any(k in ms for k in north_keywords):
        return "north"

    # 마산 핵심권
    masan_keywords = ["양덕", "석전", "합성", "회원", "내서", "월영", "자산", "오동"]
    if any(k in ms for k in masan_keywords):
        return "masan_core"

    # 의창 핵심권
    uichang_keywords = ["용지", "팔용", "명서", "창원중"]
    if any(k in ms for k in uichang_keywords):
        return "uichang_core"

    # 성산 핵심권
    seongsan_keywords = ["상남", "사파", "반송", "성주", "용호"]
    if any(k in ms for k in seongsan_keywords):
        return "seongsan_core"

    # 진해
    jinhae_keywords = ["풍호", "여좌", "병암", "진해"]
    if any(k in ms for k in jinhae_keywords):
        return "jinhae_core"

    return ""


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
            elif zone == "진해":
                return "진해고"
        elif score >= 85:
            if zone == "의창":
                return "창원중앙고"
            elif zone == "성산":
                return "창원남고"
            elif zone == "마산":
                return "마산고"
            elif zone == "진해":
                return "진해고"
        if zone in ["의창", "성산"]:
            return "사파고"
        elif zone == "마산":
            return "마산고"
        elif zone == "진해":
            return "진해고"

    elif s_type == "안정형":
        if zone in ["의창", "성산"]:
            return "사파고"
        elif zone == "마산":
            return "문성고"
        elif zone == "진해":
            return "진해고"

    elif s_type == "도전형":
        if zone == "의창":
            return "창원중앙고"
        elif zone == "성산":
            return "창원남고"
        elif zone == "마산":
            return "마산고"
        elif zone == "진해":
            return "진해고"

    return ""


def base_second_choice(s_type: str, score: float, zone: str) -> str:
    """2지망 기본 로직"""
    if s_type == "탐구형":
        if zone == "의창":
            return "창원남고"
        elif zone == "성산":
            return "창원중앙고"
        elif zone == "마산":
            return "창원중앙고"
        elif zone == "진해":
            return "진해여고"

    elif s_type == "안정형":
        if zone in ["의창", "성산"]:
            return "문성고"
        elif zone == "마산":
            return "사파고"
        elif zone == "진해":
            return "진해여고"

    elif s_type == "도전형":
        if zone == "의창":
            return "창원남고"
        elif zone == "성산":
            return "창원중앙고"
        elif zone == "마산":
            return "창원중앙고"
        elif zone == "진해":
            return "진해여고"

    return ""


def adjust_for_gender(rec_list, gender: str):
    """성별에 따른 남녀 전용학교 필터링"""
    if gender == "무관":
        return rec_list[:5]

    boys_only = ["창원남고", "마산고", "진해고", "창원중앙고"]
    girls_only = ["명지여고", "창원여고", "마산여고", "진해여고"]

    if gender == "남":
        filtered = [r for r in rec_list if r not in girls_only]
    elif gender == "여":
        filtered = [r for r in rec_list if r not in boys_only]
    else:
        filtered = rec_list

    if not filtered:
        filtered = rec_list

    return filtered[:5]


# ------------------------------
#  학교별 상세 특징
# ------------------------------

SCHOOL_PROFILES = {
    "창원중앙고": [
        "의창구 상위권 남자 일반고입니다.",
        "내신 경쟁이 다소 치열한 편입니다.",
        "팔용·용지권에서 선호도가 높습니다."
    ],
    "창원남고": [
        "성산구 대표 남자 일반고입니다.",
        "상남·사파권 학생의 진학 비율이 높습니다."
    ],
    "마산고": [
        "마산권 상위 남자 일반고입니다.",
        "양덕·회원·내서권 학생 비율이 높습니다."
    ],
    "명지여고": [
        "성산·의창권 상위 여고입니다.",
        "내신·비교과 균형이 잘 잡혀 있습니다."
    ],
    "창원여고": [
        "창원 전역에서 지원하는 여고입니다.",
        "중상위권 여학생에게 안정적입니다."
    ],
    "마산여고": [
        "마산 대표 여고입니다.",
        "마산권 조합에서 자주 선택됩니다."
    ],
    "진해고": [
        "진해 대표 남자 일반고입니다.",
        "통학이 용이해 지역 선호도가 높습니다."
    ],
    "진해여고": [
        "진해권 대표 여고입니다.",
        "내신 관리가 비교적 안정적입니다."
    ],
    "사파고": [
        "의창·성산 경계에 위치한 공학 일반고입니다.",
        "중상위권 학생에게 안정적인 선택입니다."
    ],
    "문성고": [
        "마산·의창 학생 모두 선택 가능한 공학 일반고입니다.",
        "내신 부담이 상대적으로 낮은 편입니다."
    ],
    "신월고": [
        "안정적인 학교생활을 원하는 학생에게 적합한 일반고입니다.",
        "중위권 학생의 안정 지망입니다."
    ],
    "북면고": [
        "북면·동읍·감계 학생에게 통학 접근성이 가장 좋습니다.",
        "북측권 학생의 대표 지망입니다."
    ],
}


def school_profile(school: str):
    if school in SCHOOL_PROFILES:
        return SCHOOL_PROFILES[school]
    return ["학교 특징 정보가 준비되어 있습니다."]


def school_reason_brief(school: str) -> str:
    top_schools = [
        "창원중앙고", "창원남고", "마산고",
        "명지여고", "창원여고", "마산여고",
        "진해고", "진해여고"
    ]
    balance_schools = ["사파고", "문성고", "북면고"]
    safe_schools = ["신월고"]

    if school in top_schools:
        return "상위권 도전 지망입니다."
    if school in balance_schools:
        return "성적과 통학을 균형 있게 고려한 안정 지망입니다."
    if school in safe_schools:
        return "안정적인 내신 관리가 가능한 안전 지망입니다."
    return "해당 권역에서 적합한 일반고입니다."


def recommend_schools(name, middle_school, s_type, score, zone, gender):

    cluster = detect_cluster(middle_school)

    # 1지망
    if cluster == "north":
        rec1 = "북면고"
    elif cluster == "masan_core":
        rec1 = "마산고"
    elif cluster == "uichang_core":
        rec1 = "창원중앙고"
    elif cluster == "seongsan_core":
        rec1 = "창원남고"
    elif cluster == "jinhae_core":
        rec1 = "진해고"
    else:
        rec1 = base_first_choice(s_type, score, zone)

    # 2지망
    if cluster == "north":
        rec2 = "문성고"
    elif cluster == "masan_core":
        rec2 = "마산여고"
    elif cluster == "uichang_core":
        rec2 = "사파고"
    elif cluster == "seongsan_core":
        rec2 = "명지여고"
    elif cluster == "jinhae_core":
        rec2 = "진해여고"
    else:
        rec2 = base_second_choice(s_type, score, zone)

    # 3~5지망
    if zone in ["의창", "성산"]:
        rec3 = "사파고"
        rec4 = "문성고"
        rec5 = "신월고"
    elif zone == "마산":
        rec3 = "문성고"
        rec4 = "사파고"
        rec5 = "마산여고"
    elif zone == "진해":
        rec3 = "진해고"
        rec4 = "진해여고"
        rec5 = "진해고"

    # 북측권일 경우: 대산고 없이 단순 조합
    if cluster == "north":
        rec3 = "사파고"
        rec4 = "문성고"
        rec5 = "신월고"

    # 중복 제거
    rec_list = []
    for r in [rec1, rec2, rec3, rec4, rec5]:
        if r not in rec_list:
            rec_list.append(r)

    # 성별 필터 적용
    rec_list = adjust_for_gender(rec_list, gender)

    # 설명 생성
    brief = [school_reason_brief(x) for x in rec_list]
    profs = [school_profile(x) for x in rec_list]

    cluster_map = {
        "north": "북면·동읍·감계·창북중 등 북측권",
        "masan_core": "마산 핵심권",
        "uichang_core": "의창 핵심권",
        "seongsan_core": "성산 핵심권",
        "jinhae_core": "진해권",
        "": "일반권"
    }

    summary = (
        f"- 중학교: **{middle_school}** (권역: {cluster_map[cluster]})\n"
        f"- 통학구역: **{zone}** / 성향: **{s_type}** / 내신: **{score}점**\n"
        + ("- 성별 필터 적용됨\n" if gender != "무관" else "")
        + "- 지망 조합은 실제 진학 패턴과 통학 조건을 기준으로 구성했습니다."
    )

    return rec_list, brief, profs, summary


# ==============================
#  Streamlit UI
# ==============================

def main():
    st.set_page_config(page_title="창원 고입 지망 자동 추천기", layout="centered")
    st.title("창원 고입 지망 자동 추천기")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("학생 이름", value="예시학생A")
        middle_school = st.text_input("중학교 이름", value="창북중")
        s_type = st.selectbox("성향", ["탐구형", "안정형", "도전형"])
        gender_sel = st.selectbox("성별", ["선택 안 함", "남", "여"])
    with col2:
        score = st.number_input("내신 평균", min_value=0.0, max_value=100.0, value=90.0)
        zone = st.selectbox("통학구역", ["의창", "성산", "마산", "진해"])

    gender = "무관" if gender_sel == "선택 안 함" else gender_sel

    if st.button("지망 추천 보기"):
        recs, briefs, profiles, summary = recommend_schools(
            name, middle_school, s_type, score, zone, gender
        )

        st.subheader("추천 결과")
        for i, (school, b, prof) in enumerate(zip(recs, briefs, profiles), start=1):
            st.markdown(f"### {i}지망: **{school}**")
            st.caption(b)
            for line in prof:
                st.markdown(f"- {line}")
            st.markdown("---")

        st.markdown("#### 기준 요약")
        st.markdown(summary)


if __name__ == "__main__":
    main()
