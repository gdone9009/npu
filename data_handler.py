import json
import os

def get_user_input_matrix(name, size=3):
    """최소한의 타이핑으로 행렬을 입력받습니다."""
    print(f"\n[{name}] {size}x{size} 데이터를 입력하세요.")
    print(f"(예: 1 0 1 0 1 0 1 0 1 처럼 9개를 한꺼번에 써도 됩니다)")
    
    all_numbers = []
    while len(all_numbers) < size * size:
        try:
            line = input(f"> ").strip()
            if not line: continue
            
            # 숫자만 추출하여 리스트에 추가
            numbers = [float(x) for x in line.split()]
            all_numbers.extend(numbers)
            
            if len(all_numbers) < size * size:
                print(f"현재 {len(all_numbers)}개 입력됨... {size*size - len(all_numbers)}개 더 필요합니다.")
        except ValueError:
            print("⚠️ 숫자만 입력 가능합니다.")
    
    # 1차원 리스트를 2차원 행렬로 변환
    return [all_numbers[i:i+size] for i in range(0, size*size, size)]

def load_json_data(file_path='data.json'):
    """data.json 안전 로드"""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None
    
def generate_standard_pattern(size, pattern_type):
    """
    N x N 크기의 표준 십자가(Cross) 또는 X 패턴을 생성합니다.
    """
    # 0.0으로 채워진 빈 행렬 생성
    matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    mid = size // 2

    if pattern_type == "Cross":
        for i in range(size):
            matrix[mid][i] = 1.0  # 가로줄 (ㅡ)
            matrix[i][mid] = 1.0  # 세로줄 (ㅣ)
            
    elif pattern_type == "X":
        for i in range(size):
            matrix[i][i] = 1.0                # 주 대각선 (\)
            matrix[i][size - 1 - i] = 1.0     # 부 대각선 (/)
            
    return matrix


import json
import os

def create_default_json(file_path):
    """과제 요구사항에 맞는 표준 data.json 파일을 생성합니다."""
    
    # 1. 필터 생성 (5x5, 13x13, 25x25)
    # generate_standard_pattern 함수를 활용합니다.
    filters = {
        "size_5": {
            "cross": generate_standard_pattern(5, "Cross"),
            "x": generate_standard_pattern(5, "X")
        },
        "size_13": {
            "cross": generate_standard_pattern(13, "Cross"),
            "x": generate_standard_pattern(13, "X")
        },
        "size_25": {
            "cross": generate_standard_pattern(25, "Cross"),
            "x": generate_standard_pattern(25, "X")
        }
    }

    # 2. 테스트용 패턴 생성 (일부 의도적 동점 케이스 포함)
    patterns = {
        "size_5_1": {
            "input": generate_standard_pattern(5, "X"),
            "expected": "x"
        },
        "size_5_2": {
            "input": generate_standard_pattern(5, "Cross"),
            "expected": "+"
        },
        "size_13_1": {
            "input": generate_standard_pattern(13, "X"),
            "expected": "x"
        },
        "size_25_1": {
            "input": generate_standard_pattern(25, "Cross"),
            "expected": "cross"
        }
    }

    default_data = {
        "filters": filters,
        "patterns": patterns
    }

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(default_data, f, indent=4)
    print(f"✅ {file_path} 파일이 존재하지 않아 기본 샘플을 생성했습니다.")

def load_json_data(file_path='data.json'):
    """파일 로드 시 없으면 자동 생성 후 로드"""
    if not os.path.exists(file_path):
        create_default_json(file_path)
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ JSON 로드 에러: {e}")
        return None