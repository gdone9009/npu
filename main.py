import sys
from npu_engine import calculate_mac, normalize_label, judge_with_epsilon, measure_performance
from data_handler import input_matrix, load_json_data

def run_mode_1():
    """모드 1: 사용자 직접 입력 (3x3)"""
    print("\n" + "="*45)
    print(" [모드 1] 사용자 직접 입력 (3x3)")
    print("="*45)
    
    filter_a = input_matrix("필터 A")
    filter_b = input_matrix("필터 B")
    pattern = input_matrix("패턴")
    
    score_a = calculate_mac(pattern, filter_a)
    score_b = calculate_mac(pattern, filter_b)
    
    avg_time = measure_performance(pattern, filter_a)
    result = judge_with_epsilon(score_a, score_b)
    
    print("\n" + "-"*40)
    print(f"A 점수: {score_a:.4f}")
    print(f"B 점수: {score_b:.4f}")
    print(f"평균 연산 시간(10회): {avg_time:.6f} ms")
    print(f"판정 결과: {result}")
    print("-" * 40)

def run_mode_2():
    """모드 2: data.json 일괄 분석"""
    data = load_json_data('data.json')
    if not data:
        print("❌ data.json 파일을 불러올 수 없습니다.")
        return

    filters = data.get('filters', {})
    patterns = data.get('patterns', {})
    
    results = []
    performance_stats = {}

    print("\n" + "="*50)
    print(" [모드 2] data.json 일괄 분석 및 성능 측정")
    print("="*50)

    for p_key, p_info in patterns.items():
        try:
            # 1. 크기 추출 및 매칭
            size = int(p_key.split('_')[1])
            f_key = f"size_{size}"
            
            target_f = filters.get(f_key)
            if not target_f:
                results.append({"id": p_key, "status": "FAIL", "reason": "필터 없음"})
                continue
                
            # 2. 데이터 정규화 및 로드
            pattern_in = p_info.get('input')
            expected_std = normalize_label(p_info.get('expected'))
            
            # 필터 키 유연성 대응 (+, cross, x, X)
            f_cross = target_f.get('cross') or target_f.get('+')
            f_x = target_f.get('x') or target_f.get('X')
            
            # 3. MAC 연산 및 판정
            sc_cross = calculate_mac(pattern_in, f_cross)
            sc_x = calculate_mac(pattern_in, f_x)
            prediction = judge_with_epsilon(sc_cross, sc_x)
            
            # 4. 결과 비교
            is_pass = (prediction == expected_std)
            status = "PASS" if is_pass else "FAIL"
            results.append({"id": p_key, "status": status, "reason": "판정 불일치" if not is_pass else ""})
            
            # 5. 성능 데이터 수집 (크기별 누적)
            if size not in performance_stats:
                performance_stats[size] = measure_performance(pattern_in, f_cross)
            
            print(f"[{p_key}] Cross:{sc_cross:.2f}, X:{sc_x:.2f} | Result:{prediction} | Exp:{expected_std} | {status}")
            
        except Exception as e:
            print(f"⚠️ {p_key} 처리 중 에러: {e}")
            results.append({"id": p_key, "status": "FAIL", "reason": str(e)})

    # 최종 결과 리포트 출력
    print_report(results, performance_stats)

def print_report(results, stats):
    """성능 분석 표 및 최종 요약 출력"""
    print("\n" + "="*55)
    print(f"{'크기(NxN)':<12} | {'평균 시간(ms)':<15} | {'연산 횟수(N²)'}")
    print("-" * 55)
    for n in sorted(stats.keys()):
        print(f"{f'{n}x{n}':<14} | {stats[n]:<18.6f} | {n*n}")
    
    total = len(results)
    passes = len([r for r in results if r['status'] == "PASS"])
    fails = total - passes
    
    print("\n" + "="*55)
    print(f"✅ 전체 테스트: {total} | 통과: {passes} | 실패: {fails}")
    if fails > 0:
        print("❌ 실패 케이스 목록:")
        for r in results:
            if r['status'] == "FAIL":
                print(f"  - {r['id']}: {r['reason']}")
    print("=" * 55)

def main():
    while True:
        print("\n🧠 === Mini NPU Simulator ===")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        print("q. 종료")
        
        choice = input("\n메뉴를 선택하세요: ").lower().strip()
        
        if choice == '1':
            run_mode_1()
        elif choice == '2':
            run_mode_2()
        elif choice == 'q':
            print("👋 프로그램을 종료합니다.")
            break
        else:
            print("⚠️ 잘못된 입력입니다. 다시 선택해주세요.")

if __name__ == "__main__":
    main()