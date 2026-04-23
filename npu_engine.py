import time

def calculate_mac(pattern, filter_data):
    """
    이중 for문을 이용한 MAC(Multiply-Accumulate) 연산
    """
    score = 0.0
    size = len(pattern)
    
    for r in range(size):
        for c in range(size):
            score += float(pattern[r][c]) * float(filter_data[r][c])
            
    return score

def normalize_label(label):
    """
    다양한 입력 라벨을 표준 라벨(Cross, X)로 정규화
    """
    label = str(label).lower().strip()
    if label in ['+', 'cross']:
        return "Cross"
    if label in ['x']:
        return "X"
    return "UNDECIDED"

def judge_with_epsilon(score_cross, score_x, epsilon=1e-9):
    """
    부동소수점 오차를 고려한 판정 로직
    """
    diff = score_cross - score_x
    
    if abs(diff) < epsilon:
        return "UNDECIDED"
    
    return "Cross" if diff > 0 else "X"

def judge_pattern(score_a, score_b, epsilon=1e-9):
    """
    두 필터의 점수를 비교하여 판정 결과를 반환합니다.
    """
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    
    return "Cross" if score_a > score_b else "X"

def measure_performance(pattern, filter_data, iterations=10):
    """
    MAC 연산을 반복 수행하여 평균 실행 시간(ms)을 측정
    """
    start_time = time.perf_counter()
    
    for _ in range(iterations):
        calculate_mac(pattern, filter_data)
        
    end_time = time.perf_counter()
    
    # 초 단위 차이를 밀리초(ms)로 변환 후 평균 계산
    avg_time_ms = ((end_time - start_time) / iterations) * 1000
    return avg_time_ms