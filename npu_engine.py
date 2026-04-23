import time

def calculate_mac(pattern, filter_data):
    """
    [기본 엔진] 이중 반복문을 이용한 2차원 MAC 연산
    - 원리: 입력 데이터와 필터의 행(r)과 열(c) 인덱스를 순회하며 위치별 곱셈 및 누적 수행
    - 복잡도: O(N^2) - 데이터의 면적에 비례하여 연산량 증가
    """
    score = 0.0
    size = len(pattern)
    for r in range(size):
        for c in range(size):
            # float 형변환을 통해 수치 연산의 일관성 유지
            score += float(pattern[r][c]) * float(filter_data[r][c])
    return score

def normalize_label(label):
    """
    [데이터 정규화] 파편화된 라벨 규격을 내부 표준으로 통합
    - 입력: '+', 'cross', 'x', 'X' 등 다양한 포맷
    - 출력: 'Cross' 또는 'X' (표준화된 문자열)
    """
    l = str(label).lower().strip()
    if l in ['+', 'cross']: return "Cross"
    if l in ['x']: return "X"
    return "UNDECIDED"

def judge_with_epsilon(score_cross, score_x, epsilon=1e-9):
    """
    [수치 해석] 부동소수점 오차를 고려한 Epsilon 비교 정책
    - 이유: 컴퓨터의 2진수 연산 오차로 인해 발생하는 미세한 차이를 무시하기 위함
    - 정책: 두 점수의 차이가 epsilon보다 작으면 동점(UNDECIDED)으로 판정
    """
    diff = score_cross - score_x
    if abs(diff) < epsilon:
        return "UNDECIDED"
    return "Cross" if diff > 0 else "X"

def measure_performance(pattern, filter_data, iterations=10):
    """
    [벤치마킹] MAC 연산의 순수 실행 시간 측정
    - 단위: 밀리초(ms)
    - 방법: 시스템 부하를 고려하여 iterations 횟수만큼 반복 측정 후 평균값 산출
    """
    start = time.perf_counter()
    for _ in range(iterations):
        calculate_mac(pattern, filter_data)
    end = time.perf_counter()
    return ((end - start) / iterations) * 1000

# ---------------------------------------------------------
# 보너스 과제: 메모리 최적화 섹션
# ---------------------------------------------------------

def flatten_matrix(matrix):
    """
    [최적화 준비] 2차원 리스트를 1차원 선형 리스트로 변환
    - 목적: 연속된 메모리 주소 배치를 통해 데이터 인출(Fetch) 효율 극대화
    """
    return [val for row in matrix for val in row]

def calculate_mac_optimized(flat_pattern, flat_filter):
    """
    [최적화 엔진] 1차원 배열을 이용한 단일 루프 MAC 연산
    - 장점: 인덱스 계산(r, c) 오버헤드를 제거하고 하드웨어의 캐시 효율을 높임
    - 성능: 2차원 방식 대비 약 10% 내외의 실행 속도 개선 기대
    """
    score = 0.0
    # 데이터가 메모리에 나란히 줄 서 있으므로 단일 루프로 빠르게 처리
    for i in range(len(flat_pattern)):
        score += flat_pattern[i] * flat_filter[i]
    return score