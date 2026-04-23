import json
import os

def get_user_input_matrix(name, size=3):
    """
    사용자로부터 최적화된 방식으로 행렬 데이터를 입력받습니다.
    한 줄에 하나씩 입력하거나, 모든 데이터를 한꺼번에 복사해서 붙여넣어도 인식합니다.
    """
    print(f"\n[{name}] {size}x{size} 데이터를 입력하세요.")
    print(f"(가이드: 숫자를 공백으로 구분하여 총 {size*size}개를 입력하세요)")
    
    all_numbers = []
    while len(all_numbers) < size * size:
        try:
            line = input(f"> ").strip()
            if not line: continue
            
            # 숫자만 추출하여 리스트에 추가
            numbers = [float(x) for x in line.split()]
            all_numbers.extend(numbers)
            
            if len(all_numbers) < size * size:
                print(f" 현재 {len(all_numbers)}개 입력됨... {size*size - len(all_numbers)}개 더 필요합니다.")
        except ValueError:
            print(" ⚠️ 알림: 유효한 숫자만 입력 가능합니다.")
    
    # 1차원 리스트를 사용자가 보기 편한 2차원 행렬로 변환하여 반환
    return [all_numbers[i:i+size] for i in range(0, size*size, size)]

def generate_standard_pattern(size, pattern_type):
    """
    N x N 크기에 맞는 표준 십자가(Cross) 또는 X 패턴을 자동 생성합니다.
    이 함수는 모드 1의 자동 생성 및 data.json 초기 생성 시 호출됩니다.
    """
    matrix = [[0.0] * size for _ in range(size)]
    mid = size // 2

    if pattern_type == "Cross":
        for i in range(size):
            matrix[mid][i] = 1.0  # 가로축 채우기
            matrix[i][mid] = 1.0  # 세로축 채우기
    elif pattern_type == "X":
        for i in range(size):
            matrix[i][i] = 1.0                # 주 대각선 (\)
            matrix[i][size - 1 - i] = 1.0     # 부 대각선 (/)
            
    return matrix

def create_default_json(file_path):
    """
    과제 요구사항에 명시된 5x5, 13x13, 25x25 필터와 패턴을 포함한 
    기본 data.json 파일을 생성합니다.
    """
    # 표준 크기별 필터 세트 구성
    filters = {
        f"size_{n}": {
            "cross": generate_standard_pattern(n, "Cross"),
            "x": generate_standard_pattern(n, "X")
        } for n in [5, 13, 25]
    }

    # 검증용 테스트 패턴 세트 구성
    patterns = {
        "size_5_1": {"input": generate_standard_pattern(5, "X"), "expected": "x"},
        "size_5_2": {"input": generate_standard_pattern(5, "Cross"), "expected": "+"},
        "size_13_1": {"input": generate_standard_pattern(13, "X"), "expected": "x"},
        "size_25_1": {"input": generate_standard_pattern(25, "Cross"), "expected": "cross"}
    }

    default_data = {"filters": filters, "patterns": patterns}

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=4)
        print(f" ✅ 알림: {file_path}가 없어 표준 규격으로 자동 생성했습니다.")
    except Exception as e:
        print(f" ❌ 파일 생성 실패: {e}")

def load_json_data(file_path='data.json'):
    """
    JSON 데이터를 로드합니다. 파일이 없을 경우 기본값으로 자동 생성 후 로드합니다.
    """
    if not os.path.exists(file_path):
        create_default_json(file_path)
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f" ❌ JSON 로드 에러: {e}")
        return None