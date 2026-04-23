import sys
import time
from npu_engine import calculate_mac, normalize_label, judge_with_epsilon, measure_performance
from data_handler import get_user_input_matrix, load_json_data, generate_standard_pattern

def safe_exit():
    print("\n" + "!"*40)
    print(" 시스템을 안전하게 종료합니다.")
    print(" 이용해 주셔서 감사합니다, 선생님! 🚀🌕")
    print("!"*40)
    sys.exit(0)

def print_final_report(results, stats):
    print("\n" + "="*55)
    print(f"{'크기(NxN)':<12} | {'평균 시간(ms)':<15} | {'연산 횟수(N²)'}")
    print("-" * 55)
    for n in sorted(stats.keys()):
        print(f"{f'{n}x{n}':<14} | {stats[n]:<18.6f} | {n*n}")

    total = len(results)
    passes = len([r for r in results if r['status'] == "PASS"])
    fails = total - passes
    
    print("\n" + "="*55)
    print(f"✅ 총 테스트: {total} | 통과: {passes} | 실패: {fails}")
    print("=" * 55)

def run_mode_2():
    data = load_json_data('data.json')
    if not data: return

    filters, patterns = data.get('filters', {}), data.get('patterns', {})
    results, performance_stats = [], {}

    print("\n" + "="*50)
    print(" [모드 2] data.json 일괄 분석 시작")
    print("="*50)

    for p_key, p_info in patterns.items():
        try:
            size = int(p_key.split('_')[1])
            f_key = f"size_{size}"
            target_f = filters.get(f_key)
            if not target_f: continue

            p_input = p_info.get('input')
            expected_std = normalize_label(p_info.get('expected'))
            f_cross = target_f.get('cross') or target_f.get('+')
            f_x = target_f.get('x') or target_f.get('X')

            sc_cross = calculate_mac(p_input, f_cross)
            sc_x = calculate_mac(p_input, f_x)
            prediction = judge_with_epsilon(sc_cross, sc_x)

            is_pass = (prediction == expected_std)
            results.append({"id": p_key, "status": "PASS" if is_pass else "FAIL"})

            if size not in performance_stats:
                performance_stats[size] = measure_performance(p_input, f_cross)

            print(f"[{p_key}] Result:{prediction} | Exp:{expected_std} | {'✅' if is_pass else '❌'}")
        except: continue

    print_final_report(results, performance_stats)
    input("\n엔터를 누르면 메뉴로 돌아갑니다...")

def run_mode_1():
    try:
        print("\n" + "-"*40)
        print(" [모드 1] 데이터 준비")
        print(" 1. 표준 패턴 자동 생성 (Cross & X)")
        print(" 2. 직접 데이터 입력 (3x3)")
        print(" 3. 취소")
        print("-" * 40)
        
        choice = input("선택: ").strip()
        if choice == '3': return
        
        if choice == '1':
            f_cross = generate_standard_pattern(3, "Cross")
            f_x = generate_standard_pattern(3, "X")
            print("\n[패턴 생성]")
            print(" 1. 십자가(+)  2. X모양")
            p_choice = input("선택: ").strip()
            pattern = f_cross if p_choice == '1' else f_x
            f_a, f_b = f_cross, f_x
        else:
            f_a = get_user_input_matrix("필터 A")
            f_b = get_user_input_matrix("필터 B")
            pattern = get_user_input_matrix("패턴")

        sc_a, sc_b = calculate_mac(pattern, f_a), calculate_mac(pattern, f_b)
        avg_t = measure_performance(pattern, f_a)
        res = judge_with_epsilon(sc_a, sc_b)

        print("\n" + "*"*40)
        print(f" 판정: {res} | 시간: {avg_t:.6f}ms")
        print(f" 점수: A({sc_a:.1f}) vs B({sc_b:.1f})")
        print("*" * 40)
        input("\n엔터를 누르면 메뉴로 돌아갑니다...")

    except KeyboardInterrupt:
        print("\n⚠️ 중단되었습니다.")

def main():
    while True:
        try:
            print("\n" + "="*30)
            print(" 🧠 Mini NPU Simulator")
            print("="*30)
            print(" 1. 사용자 입력 분석")
            print(" 2. data.json 분석")
            print(" 9. 프로그램 종료")
            print("="*30)
            
            choice = input("\n메뉴 선택: ").strip()
            
            if choice == '1': run_mode_1()
            elif choice == '2': run_mode_2()
            elif choice == '9': safe_exit()
            else: print("⚠️ 1, 2, 9 중 하나를 입력하세요.")
        except (KeyboardInterrupt, EOFError):
            safe_exit()

if __name__ == "__main__":
    main()