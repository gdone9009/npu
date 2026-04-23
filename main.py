import time
import os
from npu_engine import calculate_mac, normalize_label, judge_with_epsilon, measure_performance
from data_handler import get_user_input_matrix, load_json_data, generate_standard_pattern

def print_header(title):
    print("\n" + "="*50)
    print(f" {title:^48}")
    print("="*50)

def run_optimization_test(size=25):
    """보너스 과제: 최적화 전/후 성능 비교 측정"""
    print(f"\n🚀 {size}x{size} 크기 최적화 성능 테스트 중...")
    
    # 데이터 준비
    p_2d = generate_standard_pattern(size, "Cross")
    f_2d = generate_standard_pattern(size, "Cross")
    
    p_1d = flatten_matrix(p_2d)
    f_1d = flatten_matrix(f_2d)

    # 1. 최적화 전 (2차원) 측정
    start = time.perf_counter()
    for _ in range(1000): # 차이를 확인하기 위해 반복 횟수 증가
        calculate_mac(p_2d, f_2d)
    time_2d = (time.perf_counter() - start)

    # 2. 최적화 후 (1차원) 측정
    start = time.perf_counter()
    for _ in range(1000):
        calculate_mac_optimized(p_1d, f_1d)
    time_1d = (time.perf_counter() - start)

    improvement = ((time_2d - time_1d) / time_2d) * 100
    print(f"  • 최적화 전(2D): {time_2d:.4f}s")
    print(f"  • 최적화 후(1D): {time_1d:.4f}s")
    print(f"  • 성능 향상률  : {improvement:.1f}% 개선")

def run_mode_1():
    print_header("모드 1: 실시간 패턴 분석")
    print(" 1. 표준 샘플 사용 (3x3 Cross/X)")
    print(" 2. 수동 데이터 입력")
    print(" 0. 뒤로 가기")
    
    choice = input("\n 선택 > ").strip()
    if choice == '0': return

    if choice == '1':
        f_cross = generate_standard_pattern(3, "Cross")
        f_x = generate_standard_pattern(3, "X")
        print("\n [생성된 필터 모양]")
        print("  <Cross 필터>")
        for r in f_cross: print("  " + " ".join(["■" if v else "□" for v in r]))
        
        p_choice = input("\n 테스트할 패턴 선택 (1:Cross, 2:X) > ")
        pattern = f_cross if p_choice == '1' else f_x
        f_a, f_b = f_cross, f_x
    else:
        f_a = get_user_input_matrix("필터 A")
        f_b = get_user_input_matrix("필터 B")
        pattern = get_user_input_matrix("테스트 패턴")

    # 연산 애니메이션 효과 (사용자 친화적 연출)
    print("\n 🔍 NPU 가속기 가동 중...", end="", flush=True)
    for _ in range(3): time.sleep(0.2); print(".", end="", flush=True)
    
    sc_a = calculate_mac(pattern, f_a)
    sc_b = calculate_mac(pattern, f_b)
    res = judge_with_epsilon(sc_a, sc_b)
    
    print("\n\n" + " ✨ 분석 결과 " + "-"*35)
    print(f"  • 필터 A 점수 : {sc_a:>6.2f}")
    print(f"  • 필터 B 점수 : {sc_b:>6.2f}")
    print(f"  • 최종 판정   : 【 {res} 】")
    print("-" * 50)
    input("\n 엔터를 누르면 메뉴로 돌아갑니다...")

def run_mode_2():
    data = load_json_data()
    if not data: return

    patterns = data.get('patterns', {})
    filters = data.get('filters', {})
    results, stats = [], {}

    print_header("모드 2: data.json 일괄 분석")
    total_count = len(patterns)
    print(f" 📂 총 {total_count}개의 패턴을 발견했습니다. 분석을 시작합니다.\n")

    for i, (p_key, p_info) in enumerate(patterns.items(), 1):
        size = int(p_key.split('_')[1])
        target_f = filters.get(f"size_{size}")
        
        # 진행률 표시
        print(f" [{i}/{total_count}] 분석 중: {p_key:<15}", end="\r")
        
        sc_c = calculate_mac(p_info['input'], target_f.get('cross') or target_f.get('+'))
        sc_x = calculate_mac(p_info['input'], target_f.get('x') or target_f.get('X'))
        
        pred = judge_with_epsilon(sc_c, sc_x)
        expected = normalize_label(p_info['expected'])
        is_pass = (pred == expected)
        
        results.append({"id": p_key, "status": "PASS" if is_pass else "FAIL", "pred": pred, "exp": expected})
        if size not in stats:
            stats[size] = measure_performance(p_info['input'], target_f.get('cross') or target_f.get('+'))
        time.sleep(0.05) # 시각적 효과를 위한 미세 지연

    print("\n\n ✅ 분석 완료!")
    
    # 결과 요약 출력
    pass_count = len([r for r in results if r['status'] == "PASS"])
    print(f"\n 📊 통계: {pass_count}/{total_count} 통과 (성공률 {(pass_count/total_count)*100:.1f}%)")
    
    if total_count > pass_count:
        print("\n ❌ 실패 케이스 리포트:")
        for r in results:
            if r['status'] == "FAIL":
                print(f"   - {r['id']}: 판정({r['pred']}) != 기대({r['exp']})")

    # 성능 표 출력
    print("\n" + "-"*50)
    print(f" {'크기':<10} | {'평균 시간(ms)':<15} | {'연산 횟수'}")
    print("-" * 50)
    for s in sorted(stats.keys()):
        print(f"  {str(s)+'x'+str(s):<9} | {stats[s]:<14.6f} | {s*s:>8}회")
    print("-" * 50)
    
    input("\n 엔터를 누르면 메뉴로 돌아갑니다...")

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear') # 화면 깔끔하게 정리
        print("\n" + " " * 12 + "🚀 Mini NPU Simulator v1.2")
        print("="*50)
        print("  1. [개별 분석] 3x3 사용자 패턴 테스트")
        print("  2. [일괄 분석] data.json 라이브러리 검증")
        print("  9. [시스템 종료] 프로그램 마감")
        print("="*50)
        
        choice = input("\n 메뉴 선택 > ").strip()
        if choice == '1': run_mode_1()
        elif choice == '2': run_mode_2()
        elif choice == '9': 
            print("\n 시스템을 종료합니다. 안녕히 가세요! 👋"); break
        else:
            print("\n ⚠️ 알림: 1, 2, 9번 중에서 선택해주세요."); time.sleep(1)

if __name__ == "__main__":
    main()

