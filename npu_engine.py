import time

def calculate_mac(pattern, filter_data):
    """이중 반복문을 이용한 MAC(Multiply-Accumulate) 연산"""
    score = 0.0
    size = len(pattern)
    for r in range(size):
        for c in range(size):
            # 외부 라이브러리 없이 직접 구현
            score += float(pattern[r][c]) * float(filter_data[r][c])
    return score

def normalize_label(label):
    """입력 라벨 표준화 (정규화)"""
    l = str(label).lower().strip()
    if l in ['+', 'cross']: return "Cross"
    if l in ['x']: return "X"
    return "UNDECIDED"

def judge_with_epsilon(score_cross, score_x, epsilon=1e-9):
    """허용오차(epsilon) 기반 비교 정책"""
    diff = score_cross - score_x
    if abs(diff) < epsilon:
        return "UNDECIDED"
    return "Cross" if diff > 0 else "X"

def measure_performance(pattern, filter_data, iterations=10):
    """MAC 연산 순수 실행 시간 측정 (ms)"""
    start = time.perf_counter()
    for _ in range(iterations):
        calculate_mac(pattern, filter_data)
    end = time.perf_counter()
    # 10회 평균 측정 및 ms 단위 변환
    return ((end - start) / iterations) * 1000