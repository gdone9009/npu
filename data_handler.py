def input_matrix(name, size=3):
    """
    사용자로부터 n x n 행렬을 안전하게 입력받습니다.
    """
    print(f"\n{name} ({size}줄 입력, 공백 구분):")
    matrix = []
    
    while len(matrix) < size:
        try:
            line = input(f"{len(matrix) + 1}행: ").strip()
            if not line:
                print("⚠️ 데이터를 입력해주세요.")
                continue
                
            # 공백으로 나누고 숫자로 변환
            row = [float(x) for x in line.split()]
            
            # 열 개수 검증
            if len(row) != size:
                print(f"⚠️ 에러: {size}개의 숫자를 공백으로 구분해 입력하세요. (현재 {len(row)}개)")
                continue
                
            matrix.append(row)
            
        except ValueError:
            print("⚠️ 에러: 숫자만 입력 가능합니다. 다시 입력해주세요.")
            
    return matrix

def load_json_data(file_path):
    """
    data.json 파일을 로드하고 기본적인 구조를 반환합니다.
    """
    import json
    import os
    
    if not os.path.exists(file_path):
        print(f"❌ 에러: {file_path} 파일을 찾을 수 없습니다.")
        return None
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ JSON 로드 중 에러 발생: {e}")
        return None