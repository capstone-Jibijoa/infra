import os
import json
import glob
import re

# --- 1. 경로 설정 ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
INPUT_DIR = os.path.join(
    PROJECT_ROOT,
    'xlsx_to_json_pipeline',
    'qpoll_json_output'
)
INPUT_JSON_FILES = glob.glob(os.path.join(INPUT_DIR, '*.json'))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'sentence_output_by_topic')


# --- 2. 문장 변환 템플릿 정의 ---

# 'list'를 반환하는 헬퍼 함수
def _get_answer_list(surveys, index):
    """
    (헬퍼 함수) surveys 리스트의 'index'에서 [답변 리스트]를 원본 그대로 가져옵니다.
    """
    try:
        # 'survey_answers' 리스트를 반환
        return surveys[index].get('survey_answers', [])
    except IndexError:
        # 인덱스가 없으면 빈 리스트 반환
        return []

# =============== qpoll 파일별로 문장을 반환하는 함수들 ====================

"""여러분은 평소 체력 관리를 위해 어떤 활동을 하고 계신가요? 모두 선택해주세요."""
def format_selectPhysicalActivity_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "체력관리를 위해 하고 있는 활동이 없다" in raw_answer_list:
        return "체력 관리를 위해 하고 있는 활동이 없다"
    
    else:
        EXCLUDE_WORDS = ["기타"]

        # EXCLUDE_WORD에 없는 항목만 필터링
        filtered_list = [
            answer for answer in raw_answer_list
            if answer not in EXCLUDE_WORDS
        ]

        # 필터링된 리스트로 문장 조합
        if not filtered_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(filtered_list)

        return (f"체력 관리를 위해 {answer_str} 활동을 하고 있다.")


"""여러분이 현재 이용 중인 OTT 서비스는 몇 개인가요?"""
def format_countCurrentOttServices_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "이용하지 않는다" in raw_answer_list:
        return "현재 OTT 서비스를 이용하지 않는다."
    
    else:
        if not raw_answer_list:
            # 답변이 없는 경우 
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(raw_answer_list)

        return (f"현재 OTT서비스를 {answer_str}이용 중이다.")

"""여러분은 전통시장을 얼마나 자주 방문하시나요?"""
def format_traditional_market_visit_frequency_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "전혀 방문하지 않음" in raw_answer_list:
        return "전통시장을 전혀 방문하지 않는다."
    
    else:
        if not raw_answer_list:
            # 답변이 없는 경우
            return None
        else:
            answer_str = ", ".join(raw_answer_list)

        return (f"전통시장을 {answer_str}방문한다.")

"""여러분이 가장 선호하는 설 선물 유형은 무엇인가요?"""
def format_preferred_lunar_new_year_gift_type_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "선호하는 선물이 없다" in raw_answer_list:
        return "선호하는 설 선물 유형이 없다"
    
    else:
        EXCLUDE_WORDS = ["기타"]

        # EXCLUDE_WORD에 없는 항목만 필터링
        filtered_list = [
            answer for answer in raw_answer_list
            if answer not in EXCLUDE_WORDS
        ]

        # 필터링된 리스트로 문장 조합
        if not filtered_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            answer_str = ", ".join(filtered_list)

        return (f"가장 선호하는 설 선물 유형은 {answer_str}이다.")

"""초등학생 시절 겨울방학 때 가장 기억에 남는 일은 무엇인가요?"""
def format_elementary_school_winter_break_memory_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)

    EXCLUDE_WORDS = ["기타"]

    # EXCLUDE_WORD에 없는 항목만 필터링
    filtered_list = [
        answer for answer in raw_answer_list
        if answer not in EXCLUDE_WORDS
    ]

    # 필터링된 리스트로 문장 조합
    if not filtered_list:
        # 필터링 후 아무것도 남지 않은 경우
        return None
    else:
        answer_str = ", ".join(filtered_list)

    return (f"초등학생 시절 겨울방학 때 가장 기억에 남는 일은 {answer_str}(이)다.")

"""여러분은 반려동물을 키우는 중이시거나 혹은 키워보신 적이 있으신가요?"""
def format_pet_ownership_experience_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)

    if not raw_answer_list:
        # 아무것도 남지 않은 경우
        return None
    else:
        # "A, B 형식으로 연결"
        answer_str = ", ".join(raw_answer_list)

    return (f"{answer_str}.")

"""여러분은 이사할 때 가장 스트레스 받는 부분은 어떤걸까요?"""
def format_moving_stress_factors_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "스트레스 받지 않는다" in raw_answer_list:
        return "이사할 때 스트레스를 받지 않는다."
    
    else:
        EXCLUDE_WORDS = ["기타"]

        # EXCLUDE_WORD에 없는 항목만 필터링
        filtered_list = [
            answer for answer in raw_answer_list
            if answer not in EXCLUDE_WORDS
        ]

        # 필터링된 리스트로 문장 조합
        if not filtered_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(filtered_list)

        return (f"이사할 때 {answer_str}(으)로 가장 스트레스 받는다.")

"""여러분은 본인을 위해 소비하는 것 중 가장 기분 좋아지는 소비는 무엇인가요?"""
def format_most_satisfying_self_care_spending_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)

    EXCLUDE_WORDS = ["기타"]

    # EXCLUDE_WORD에 없는 항목만 필터링
    filtered_list = [
        answer for answer in raw_answer_list
        if answer not in EXCLUDE_WORDS
    ]

    # 필터링된 리스트로 문장 조합
    if not filtered_list:
        # 필터링 후 아무것도 남지 않은 경우
        return None
    else:
        # "A, B 형식으로 연결"
        answer_str = ", ".join(filtered_list)

    return (f"본인을 위해 소비하는 것 중 가장 기분 좋아지는 소비는 {answer_str}이 다.")

"""여러분은 요즘 가장 많이 사용하는 앱은 무엇인가요?"""
def format_most_frequently_used_app_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)

    EXCLUDE_WORDS = ["기타"]

    # EXCLUDE_WORD에 없는 항목만 필터링
    filtered_list = [
        answer for answer in raw_answer_list
        if answer not in EXCLUDE_WORDS
    ]

    # 필터링된 리스트로 문장 조합
    if not filtered_list:
        # 필터링 후 아무것도 남지 않은 경우
        return None
    else:
        # "A, B 형식으로 연결"
        answer_str = ", ".join(filtered_list)

    return (f"요즘 가장 많이 사용하는 앱은 {answer_str}이다.")

"""
다음 중 가장 스트레스를 많이 느끼는 상황은 무엇인가요? 
스트레스를 해소하는 방법으로 주로 사용하는 것은 무엇인가요?
"""
def format_stressful_situation_and_coping_methods_file(panel_id, answers, question):
    # question 텍스트에 따라 다음 문장을 반환한다.
    answer_str = ", ".join(answers) if answers else None

    if "다음 중 가장 스트레스를 많이 느끼는 상황은 무엇인가요?" in question:
        filtered_list = [
            ans for ans in answers 
            if ans not in ["기타"]
        ]
        if not filtered_list: 
            return None
        
        answer_str = "와(과) ".join(filtered_list) if filtered_list else None
        return (f"{answer_str}에서 스트레스를 가장 많이 느낀다.")
    
    elif "스트레스를 해소하는 방법으로 주로 사용하는 것은 무엇인가요?" in question:
        filtered_list = [
            ans for ans in answers 
            if ans not in ["기타"]
        ]
        if not filtered_list: 
            return None
        
        answer_str = "와(과) ".join(filtered_list) if filtered_list else None
        return (f"스트레스를 해소하는데 주로 사용하는 방법은 {answer_str}이다.")

"""
현재 본인의 피부 상태에 얼마나 만족하시나요?
한 달 기준으로 스킨케어 제품에 평균적으로 얼마나 소비하시나요?
스킨케어 제품을 구매할 때 가장 중요하게 고려하는 요소는 무엇인가요?
"""
def format_skincare_satisfaction_spending_and_priority_file(panel_id, answers, question):
    # question 텍스트에 따라 다음 문장을 반환한다.
    answer_str = ", ".join(answers) if answers else None

    if "현재 본인의 피부 상태에 얼마나 만족하시나요?" in question:
        filtered_list = [
            ans for ans in answers 
            if ans not in ["기타"]
        ]
        if not filtered_list: 
            return None
        
        answer_str = "와(과) ".join(filtered_list) if filtered_list else None
        if answer_str == "보통이다":
            return (f"현재 본인의 피부 상테에 보통 만큼 만족한다.")
        else:
            return (f"현재 본인의 피부 상태에 {answer_str}.")
    
    elif "한 달 기준으로 스킨케어 제품에 평균적으로 얼마나 소비하시나요?" in question:
        filtered_list = [
            ans for ans in answers 
            if ans not in ["기타"]
        ]
        if not filtered_list: 
            return None
        
        answer_str = "와(과) ".join(filtered_list) if filtered_list else None
        return (f"한 달 기준으로 스킨케어 제품에 평균 {answer_str}만큼 소비한다.")
    
    elif "스킨케어 제품을 구매할 때 가장 중요하게 고려하는 요소는 무엇인가요?" in question:
        filtered_list = [
            ans for ans in answers 
            if ans not in ["기타"]
        ]
        if not filtered_list: 
            return None
        
        answer_str = "와(과) ".join(filtered_list) if filtered_list else None
        return (f"스킨케어 제품을 구매할 떄 가장 중요하게 생각하는 요소는 {answer_str}이다.")

"""
여러분이 사용해 본 AI 챗봇 서비스는 무엇인가요? 모두 선택해주세요.
사용해 본 AI 챗봇 서비스 중 주로 사용하는 것은 무엇인가요?
AI 챗봇 서비스를 주로 어떤 용도로 활용하셨거나, 앞으로 활용하고 싶으신가요?
다음 두 서비스 중, 어느 서비스에 더 호감이 가나요? 현재 사용 여부는 고려하지 않고 응답해 주세요.
"""
def format_ai_chatbot_usage_and_preference_file(panel_id, answers, question):
    # question 텍스트에 따라 다음 문장을 반환한다.
    answer_str = ", ".join(answers) if answers else None

    if "여러분이 사용해 본 AI 챗봇 서비스는 무엇인가요? 모두 선택해주세요." in question:
        filtered_list = [
            ans for ans in answers 
            if ans not in ["기타"]
        ]
        if not filtered_list: 
            return None
        
        answer_str = ", ".join(filtered_list) if filtered_list else None
        return (f"사용해 본 AI 챗봇 서비스는 {answer_str}이다.")
    
    elif "사용해 본 AI 챗봇 서비스 중 주로 사용하는 것은 무엇인가요?" in question:
        filtered_list = [
            ans for ans in answers 
            if ans not in ["기타"]
        ]
        if not filtered_list: 
            return None
        
        answer_str = ", ".join(filtered_list) if filtered_list else None
        return (f"사용해 본 AI 챗봇 서비스 중 주로 사용하는 것은 {answer_str}이다.")
    
    elif "AI 챗봇 서비스를 주로 어떤 용도로 활용하셨거나, 앞으로 활용하고 싶으신가요?" in question:
        filtered_list = [
            ans for ans in answers 
            if ans not in ["기타"]
        ]
        if not filtered_list: 
            return None
        
        answer_str = ", ".join(filtered_list) if filtered_list else None
        return (f"AI 챗봇 서비스를 주로 {answer_str} 용도로 활용하였거나, 앞으로 활용하고 싶다.")
    
    elif "다음 두 서비스 중, 어느 서비스에 더 호감이 가나요? 현재 사용 여부는 고려하지 않고 응답해 주세요." in question:
        filtered_list = [
            ans for ans in answers 
            if ans not in ["기타"]
        ]
        if not filtered_list: 
            return None
        
        answer_str = ", ".join(filtered_list) if filtered_list else None
        return (f"ChatGPT와 딥시크 중 {answer_str}에 더 호감이 간다.")

"""여러분은 올해 해외여행을 간다면 어디로 가고 싶나요? 모두 선택해주세요"""
def format_preferred_overseas_travel_destination_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "해외여행을 가고싶지 않다" in raw_answer_list:
        return "올해 해외여행을 가고 싶지 않다."
    
    else:
        EXCLUDE_WORDS = ["기타"]

        # EXCLUDE_WORD에 없는 항목만 필터링
        filtered_list = [
            answer for answer in raw_answer_list
            if answer not in EXCLUDE_WORDS
        ]

        # 필터링된 리스트로 문장 조합
        if not filtered_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(filtered_list)

        return (f"올해 해외여행을 {answer_str}(으)로 가고 싶다.")

"""빠른 배송(당일·새벽·직진 배송) 서비스를 주로 어떤 제품을 구매할 때 이용하시나요?"""
def format_fast_delivery_product_type_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "빠른 배송 서비스를 이용해 본 적 없다" in raw_answer_list:
        return "빠른 배송 서비스를 이용해 본 적 없다."
    
    else:
        EXCLUDE_WORDS = ["기타"]

        # EXCLUDE_WORD에 없는 항목만 필터링
        filtered_list = [
            answer for answer in raw_answer_list
            if answer not in EXCLUDE_WORDS
        ]

        # 필터링된 리스트로 문장 조합
        if not filtered_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(filtered_list)

        return (f"빠른 배송(당일·새벽·직진 배송) 서비스를 주로 {answer_str}을 구매할 때 이용한다.")

"""여러분은 다가오는 여름철 가장 걱정되는 점이 무엇인가요?"""
def format_biggest_concern_for_upcoming_summer_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "특별히 걱정되는 것이 없다" in raw_answer_list:
        return "다가오는 여름철 특별히 걱정되는 것이 없다."
    
    else:
        # 필터링된 리스트로 문장 조합
        if not raw_answer_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(raw_answer_list)

        return (f"다가오는 여름철 {answer_str}이(가) 가장 걱정된다.")

"""여러분은 버리기 아까운 물건이 있을 때, 주로 어떻게 하시나요?"""
def format_disposal_method_for_valued_items_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "바로 버린다" in raw_answer_list:
        return "버리기 아까운 물건이 있을 때, 주로 바로 버린다"
    
    else:
        if not raw_answer_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(raw_answer_list)

        return (f"버리기 아까운 물건이 있을 때, 주로 {answer_str}한다.")

"""여러분은 아침에 기상하기 위해 어떤 방식으로 알람을 설정해두시나요?"""
def format_morning_wake_up_alarm_method_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)

    if "한 개만 설정해놓고 바로 일어난다" in raw_answer_list:
        return (f"아침에 기상하기 위해 알람을 한 개만 설정해놓고 바로 일어난다")

    # 필터링된 리스트로 문장 조합
    if not raw_answer_list:
        # 필터링 후 아무것도 남지 않은 경우
        return None
    else:
        # "A, B 형식으로 연결"
        answer_str = ", ".join(raw_answer_list)

    return (f"아침에 기상하기 위해 {answer_str}.")

"""여러분은 외부 식당에서 혼자 식사하는 빈도는 어느 정도인가요?"""
def format_solo_dining_frequency_outside_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "거의 하지 않거나 한 번도 해본 적 없다" in raw_answer_list:
        return "외부 식당에서 식사를 거의 하지 않거나 한 번도 해본 적 없다"
    
    else:
        # 필터링된 리스트로 문장 조합
        if not raw_answer_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(raw_answer_list)

        return (f"외부 식당에서 식사를 {answer_str} 한다.")

"""여러분이 가장 중요하다고 생각하는 행복한 노년의 조건은 무엇인가요?"""
def format_key_condition_for_happy_old_age_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)

    if not raw_answer_list:
        # 아무것도 남지 않은 경우
        return None
    else:
        # "A, B 형식으로 연결"
        answer_str = ", ".join(raw_answer_list)

    return (f"가장 중요한 행복한 노년의 조건은 {answer_str}이다.")

"""여름철 땀 때문에 겪는 불편함은 어떤 것이 있는지 모두 선택해주세요."""
def format_summer_sweating_discomforts_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)

    if "특별히 불편한 점이 없다" in raw_answer_list:
        return "여름철 땀 때문에 특별히 불편한 점이 없다"
    else:
        ANSWER_MAP = {
            "옷이 젖거나 얼룩지는 것이 신경쓰인다": "옷이 젖거나 얼룩지는 것이 신경쓰이",
            "땀 냄새가 걱정된다": "땀 냄새가 걱정되",
            "메이크업이 무너진다": "메이크업이 무너지",
            "머리나 두피가 금방 기름진다": "머리나 두피가 금방 기름지",
            "피부 트러블이 생긴다": "피부 트러블이 생기",
            "다른 사람의 땀 냄새가 불쾌하다": "다른 사람의 땀 냄새개 불쾌하"
        }
        
        processed_list = []
        for answer in raw_answer_list:
            processed_list.append(ANSWER_MAP.get(answer, answer))

        # 필터링된 리스트로 문장 조합
        if not processed_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A고, B 형식으로 연결"
            answer_str = "고, ".join(processed_list)

        return (f"여름철 땀 때문에 {answer_str}는 불편함이 있다.")

"""여러분이 지금까지 해본 다이어트 중 가장 효과 있었던 방법은 무엇인가요?"""
def format_most_effective_diet_method_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "없다" in raw_answer_list:
        return "지금까지 다이어트를 해본적이 없다."
    
    else:
        EXCLUDE_WORDS = ["기타"]

        # EXCLUDE_WORD에 없는 항목만 필터링
        filtered_list = [
            answer for answer in raw_answer_list
            if answer not in EXCLUDE_WORDS
        ]

        # 필터링된 리스트로 문장 조합
        if not filtered_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(filtered_list)

        return (f"지금까지 해본 다이어트 중 {answer_str}가 가장 효과 있었다.")

"""여러분은 야식을 먹을 때 보통 어떤 방법으로 드시나요?"""
def format_usual_late_night_snack_method_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "야식을 거의 먹지 않는다" in raw_answer_list:
        return "야식을 거의 먹지 않는다."
    
    else:
        # 필터링된 리스트로 문장 조합
        if not raw_answer_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(raw_answer_list)

        return (f"야식을 먹을 때 보통 {answer_str}.")

"""여러분의 여름철 최애 간식은 무엇인가요?"""
def format_favorite_summer_snack_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "없다" in raw_answer_list:
        return "여름철 최애 간식은 없다"
    
    else:
        EXCLUDE_WORDS = ["기타"]

        # EXCLUDE_WORD에 없는 항목만 필터링
        filtered_list = [
            answer for answer in raw_answer_list
            if answer not in EXCLUDE_WORDS
        ]

        # 필터링된 리스트로 문장 조합
        if not filtered_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(filtered_list)

        return (f"여름철 최애 간식은 {answer_str}이다.")

"""여러분은 최근 가장 지출을 많이 한 곳은 어디입니까?"""
def format_area_of_highest_recent_spending_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)

    EXCLUDE_WORDS = ["기타"]

    # EXCLUDE_WORD에 없는 항목만 필터링
    filtered_list = [
        answer for answer in raw_answer_list
        if answer not in EXCLUDE_WORDS
    ]

    # 필터링된 리스트로 문장 조합
    if not filtered_list:
        # 필터링 후 아무것도 남지 않은 경우
        return None
    else:
        # "A, B 형식으로 연결"
        answer_str = ", ".join(filtered_list)

    return (f"최근 가장 지출을 많이 한 곳은 {answer_str}이다.")

"""여러분은 요즘 어떤 분야에서 AI 서비스를 활용하고 계신가요?"""
def format_current_ai_service_utilization_field_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "AI 서베스를 사용해본 적 없다" in raw_answer_list:
        return "AI 서비스를 사용해본 적 없다."
    
    else:
        EXCLUDE_WORDS = ["기타"]

        # EXCLUDE_WORD에 없는 항목만 필터링
        filtered_list = [
            answer for answer in raw_answer_list
            if answer not in EXCLUDE_WORDS
        ]

        # 필터링된 리스트로 문장 조합
        if not filtered_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(filtered_list)

        return (f"요즘 {answer_str} 분야에서 AI 서비스를 활용하고 있다.")

"""여러분은 본인을 미니멀리스트와 맥시멀리스트 중 어디에 더 가깝다고 생각하시나요?"""
def format_minimalist_vs_maximalist_tendency_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if not raw_answer_list:
        # 아무것도 남지 않은 경우
        return None
    else:
        # "A, B 형식으로 연결"
        answer_str = ", ".join(raw_answer_list)

    return (f"나는 {answer_str}에 더 가깝다.")

"""어려분은 여행갈 때 어떤 스타일에 더 가까우신가요?"""
def format_preferred_travel_style_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "잘 모르겠다" in raw_answer_list:
        return "여행갈 때 어떤 스타일인지 잘 모르겠다."
    
    # 문장 조합
    if not raw_answer_list:
        # 아무것도 남지 않은 경우
        return None
    else:
        answer_str = ", ".join(raw_answer_list)

    return (f"여행갈 때 {answer_str} 스타일에 더 가깝다.")

"""평소 일회용 비닐봉투 사용을 줄이기 위해 어떤 노력을 하고 계신가요?"""
def format_effort_to_reduce_plastic_bag_use_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "따로 노력하고 있지 않다" in raw_answer_list:
        return "평소 일회용 비닐봉투 사용을 줄이기 위해 따로 노력하고 있지 않다."
    
    else:
        # 필터링된 리스트로 문장 조합
        if not raw_answer_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(raw_answer_list)

        return (f"평소 일회용 비닐봉투 사용을 줄이기 위해 {answer_str}.")

"""여러분은 할인, 캐시백, 멤버십 등 포인트 적립 혜택을 얼마나 신경 쓰시나요?"""
def format_interest_in_point_and_discount_benefits_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "전혀 관심 없다" in raw_answer_list:
        return "할인, 캐시백, 멤버십 등 포인트 적립 혜택에 전혀 관심 없다."
    
    else:
        # 필터링된 리스트로 문장 조합
        if not raw_answer_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(raw_answer_list)

        return (f"할인, 캐시백, 멤버십 등 포인트 적립 혜택을 {answer_str}.")

"""여러분은 초콜릿을 주로 언제 드시나요?"""
def format_usual_chocolate_consumption_time_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "거의 먹지 않는다" in raw_answer_list:
        return "초콜릿을 거의 먹지 않는다."
    
    else:
        EXCLUDE_WORDS = ["기타"]

        # EXCLUDE_WORD에 없는 항목만 필터링
        filtered_list = [
            answer for answer in raw_answer_list
            if answer not in EXCLUDE_WORDS
        ]

        # 필터링된 리스트로 문장 조합
        if not filtered_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(filtered_list)

        return (f"초콜릿을 주로 {answer_str} 먹는다.")

"""여러분은 평소 개인정보보호를 위해 어떤 습관이 있으신가요?"""
def format_personal_information_protection_habits_file(panel): 
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    EXCLUDE_WORDS = ["기타"]

    # EXCLUDE_WORD에 없는 항목만 필터링
    filtered_list = [
        answer for answer in raw_answer_list
        if answer not in EXCLUDE_WORDS
    ]

    # 필터링된 리스트로 문장 조합
    if not filtered_list:
        # 필터링 후 아무것도 남지 않은 경우
        return None
    else:
        # "A, B 형식으로 연결"
        answer_str = ", ".join(filtered_list)

    return (f"평소 개인정보보호를 위해 {answer_str}.")

"""여러분이 절대 포기할 수 없는 여름 패션 필수템은 무엇인가요?"""
def format_must_have_summer_fashion_item_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)

    EXCLUDE_WORDS = ["기타"]

    # EXCLUDE_WORD에 없는 항목만 필터링
    filtered_list = [
        answer for answer in raw_answer_list
        if answer not in EXCLUDE_WORDS
    ]

    # 필터링된 리스트로 문장 조합
    if not filtered_list:
        # 필터링 후 아무것도 남지 않은 경우
        return None
    else:
        # "A, B 형식으로 연결"
        answer_str = ", ".join(filtered_list)

    return (f"절대 포기할 수 없는 여름 패션 필수탬은 {answer_str} 이다.")

"""갑작스런 비로 우산이 없을 때 여러분은 어떻게 하시나요?"""
def format_action_when_caught_in_rain_without_umbrella_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)

    if not raw_answer_list:
        # 아무것도 남지 않은 경우
        return None
    else:
        # "A, B 형식으로 연결"
        answer_str = ", ".join(raw_answer_list)

    return (f"갑작스런 비로 우산이 없을 때 {answer_str}.")

"""여러분의 휴대폰 갤러리에 가장 많이 저장되어져 있는 사진은 무엇인가요?"""
def format_most_stored_photo_type_in_gallery_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    EXCLUDE_WORDS = ["기타"]

    # EXCLUDE_WORD에 없는 항목만 필터링
    filtered_list = [
        answer for answer in raw_answer_list
        if answer not in EXCLUDE_WORDS
    ]

    # 필터링된 리스트로 문장 조합
    if not filtered_list:
        # 필터링 후 아무것도 남지 않은 경우
        return None
    else:
        # "A, B 형식으로 연결"
        answer_str = ", ".join(filtered_list)

    return (f"휴대폰 갤러리에 가장 많이 저장되어져 있는 사진은 {answer_str}이다.")

"""여러분이 여름철 물놀이 장소로 가장 선호하는 곳은 어디입니까?"""
def format_preferred_summer_water_play_spot_file(panel):
    surveys = panel.get('surveys', [])
    # 질문의 원본 답변 [리스트]를 가져온다.
    raw_answer_list = _get_answer_list(surveys, 0)
    
    if "물놀이를 좋아하지 않는다" in raw_answer_list:
        return "물놀이를 좋아하지 않는다."
    
    else:
        EXCLUDE_WORDS = ["기타"]

        # EXCLUDE_WORD에 없는 항목만 필터링
        filtered_list = [
            answer for answer in raw_answer_list
            if answer not in EXCLUDE_WORDS
        ]

        # 필터링된 리스트로 문장 조합
        if not filtered_list:
            # 필터링 후 아무것도 남지 않은 경우
            return None
        else:
            # "A, B 형식으로 연결"
            answer_str = ", ".join(filtered_list)

        return (f"여름철 물놀이 장소로 가장 선호하는 곳은 {answer_str}이다.")



# [A] 패널당 1개 문장으로 만들 파일 목록 (단일 질문 파일용)
TOPIC_FORMATTERS_BY_PANEL = {
    "qpoll_join_250106": format_selectPhysicalActivity_file,
    "qpoll_join_250107": format_countCurrentOttServices_file,
    "qpoll_join_250116": format_traditional_market_visit_frequency_file,
    "qpoll_join_250123": format_preferred_lunar_new_year_gift_type_file,
    "qpoll_join_250204": format_elementary_school_winter_break_memory_file,
    "qpoll_join_250206": format_pet_ownership_experience_file,
    "qpoll_join_250221": format_moving_stress_factors_file,
    "qpoll_join_250224": format_most_satisfying_self_care_spending_file,
    "qpoll_join_250226": format_most_frequently_used_app_file,
    "qpoll_join_250326": format_preferred_overseas_travel_destination_file,
    "qpoll_join_250328": format_fast_delivery_product_type_file,
    "qpoll_join_250604": format_biggest_concern_for_upcoming_summer_file,
    "qpoll_join_250605": format_disposal_method_for_valued_items_file,
    "qpoll_join_250610": format_morning_wake_up_alarm_method_file,
    "qpoll_join_250611": format_solo_dining_frequency_outside_file,
    "qpoll_join_250616": format_key_condition_for_happy_old_age_file,
    "qpoll_join_250617": format_summer_sweating_discomforts_file,
    "qpoll_join_250619": format_most_effective_diet_method_file,
    "qpoll_join_250620": format_usual_late_night_snack_method_file,
    "qpoll_join_250623": format_favorite_summer_snack_file,
    "qpoll_join_250624": format_area_of_highest_recent_spending_file,
    "qpoll_join_250626": format_current_ai_service_utilization_field_file,
    "qpoll_join_250627": format_minimalist_vs_maximalist_tendency_file,
    "qpoll_join_250702": format_preferred_travel_style_file,
    "qpoll_join_250703": format_effort_to_reduce_plastic_bag_use_file,
    "qpoll_join_250704": format_interest_in_point_and_discount_benefits_file,
    "qpoll_join_250707": format_usual_chocolate_consumption_time_file,
    "qpoll_join_250709": format_personal_information_protection_habits_file,
    "qpoll_join_250710": format_must_have_summer_fashion_item_file,
    "qpoll_join_250714": format_action_when_caught_in_rain_without_umbrella_file,
    "qpoll_join_250716": format_most_stored_photo_type_in_gallery_file,
    "qpoll_join_250723": format_preferred_summer_water_play_spot_file
}

# [B] 답변당 1개 객체로 만들 파일(다중 질문 파일용 )
TOPIC_FORMATTERS_BY_SURVEY = {
    "qpoll_join_250304": format_stressful_situation_and_coping_methods_file,
    "qpoll_join_250310": format_skincare_satisfaction_spending_and_priority_file,
    "qpoll_join_250317": format_ai_chatbot_usage_and_preference_file,
}

# --- 3. 헬퍼 함수 ---

def load_data(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"    - JSON 로드 오류: {e}")
        return None

def clean_filename(text):
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    return text.strip()[:50]

# --- 4. 메인 실행 로직 ---

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not INPUT_JSON_FILES:
        print(f"오류: '{INPUT_DIR}' 폴더에서 qpoll JSON 파일을 찾을 수 없습니다.")
        return

    print(f"총 {len(INPUT_JSON_FILES)}개의 개별 JSON 파일을 변환합니다...")
    
    file_count = 0
    
    for i, file_path in enumerate(INPUT_JSON_FILES):
        
        # 파일 이름
        base_name = os.path.basename(file_path)
        topic_file_id, _ = os.path.splitext(base_name)
        
        print(f"\n({i+1}/{len(INPUT_JSON_FILES)}) 처리 중: {base_name}")

        panel_data = load_data(file_path)
        if not isinstance(panel_data, list):
            print(f"  > 오류: '{base_name}' 파일 데이터 형식이 잘못되었습니다. 건너뜁니다.")
            continue
            
        generated_data = [] # 이 파일의 최종 결과물 리스트
        
        # 파일 ID가 어느 맵에 있는지 확인하여 처리 방식을 분기
        
        if topic_file_id in TOPIC_FORMATTERS_BY_PANEL:
            # --- 처리 방식 A: 패널당 1개 문장 (단일 질문 파일용) ---
            formatter = TOPIC_FORMATTERS_BY_PANEL[topic_file_id]
            print(f"  > (방식 A: 패널 단위) '{formatter.__name__}' 함수 적용")

            for panel in panel_data:
                if not isinstance(panel, dict): continue
                
                sentence = formatter(panel) # 포맷터가 'panel' 객체를 통째로 받음
                
                generated_data.append({
                    "panel_id": panel.get('panel_id', 'UNKNOWN_ID'),
                    "sentence_for_embedding": sentence
                })

        elif topic_file_id in TOPIC_FORMATTERS_BY_SURVEY:
            # --- 처리 방식 B: 답변당 1개 객체 (질문별로 파일 분리) ---
            formatter = TOPIC_FORMATTERS_BY_SURVEY[topic_file_id]
            print(f"  > (방식 B: 답변 단위) '{formatter.__name__}' 함수 적용")
            
            # 1. 데이터를 질문별로 임시 저장할 딕셔너리
            data_by_question = {}

            for panel in panel_data:
                if not isinstance(panel, dict): continue
                
                panel_id = panel.get('panel_id', 'UNKNOWN_ID')
                
                for survey in panel.get('surveys', []):
                    if not isinstance(survey, dict): continue
                    
                    # 키 이름을 'survey_question'으로 변경
                    question = survey.get('survey_question', 'N/A')
                    if question == 'N/A': continue # 질문 없는 데이터 건너뛰기

                    answers = survey.get('survey_answers', [])
                    
                    # 2. 데이터를 질문 텍스트를 Key로 하여 재그룹화
                    if question not in data_by_question:
                        data_by_question[question] = []
                    
                    # (panel_id, answers) 튜플을 임시 저장
                    data_by_question[question].append((panel_id, answers))

            # 3. 재그룹화된 딕셔너리를 순회하며 '질문별'로 파일 생성
            print(f"  > {len(data_by_question)}개의 하위 질문을 발견. 개별 파일로 분리합니다.")
            
            sub_question_index = 0
            for question, responses in data_by_question.items():
                sub_question_index += 1
                generated_data_for_this_question = []
                
                # 4. 이 질문에 해당하는 모든 응답(responses)을 순회
                for panel_id, answers in responses:
                    # 5. 포맷터가 (panel_id, answers, question)을 받아 문장 생성
                    sentence = formatter(panel_id, answers, question)
                    
                    generated_data_for_this_question.append({
                        "panel_id": panel_id,
                        "original_question": question,
                        "sentence_for_embedding": sentence
                    })

                # 6. 이 '질문'에 대한 최종 출력 객체 생성
                output_data = {
                    "topic_file_id": topic_file_id, # 원본 파일 (예: qpoll_ai_chatbots)
                    "topic_question": question,   # 이 파일의 특정 질문
                    "generated_data": generated_data_for_this_question
                }

                # 7. 파일명 생성 (예: 03_1_AI 챗봇 서비스는.json)
                safe_question_name = clean_filename(question)
                # (입력파일 순번)_(하위질문 순번)_(질문명).json
                filename = f"{i+1:02d}_{sub_question_index}_{safe_question_name}.json"
                output_path = os.path.join(OUTPUT_DIR, filename)
                
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(output_data, f, ensure_ascii=False, indent=4)
                    file_count += 1 # 👈 파일 생성마다 카운트 증가
                except Exception as e:
                    print(f"  > 파일 저장 오류 ({filename}): {e}")
        else:
            # --- 처리 방식 C: 매핑되지 않은 파일 처리 ---
            print(f"  > [경고] 이 파일은 'TOPIC_FORMATTERS_BY_PANEL' 또는 'TOPIC_FORMATTERS_BY_SURVEY' 맵에 등록되지 않았습니다.")
            print(f"  > 파일을 건너뜁니다. (파일 ID: {topic_file_id})")
            continue # 👈 다음 파일로 넘어감

        # --- 이하 파일 저장 로직 동일 ---
        output_data = {
            "topic_file_id": topic_file_id,
            "generated_data": generated_data
        }

        safe_name = clean_filename(topic_file_id)
        filename = f"{i+1:02d}_{safe_name}.json"
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=4)
            file_count += 1
        except Exception as e:
            print(f"  > 파일 저장 오류 ({filename}): {e}")

    print(f"\n--- 작업 완료 ---")
    print(f"총 {file_count}개의 주제 파일을 '{OUTPUT_DIR}' 폴더에 저장했습니다.")

if __name__ == '__main__':
    main()