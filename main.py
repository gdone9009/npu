import time
import os
import sys
# 엔진 및 데이터 핸들러에서 필요한 함수들을 로드합니다.
from npu_engine import (
    calculate_mac, calculate_mac_optimized, flatten_matrix,
    normalize_label, judge_with_epsilon, measure_performance
)
from data_handler import (
    get_user_input_matrix, load_json_data, generate_standard_pattern
)

def print_header(title):
    """콘솔 화면에 강조된 헤더를 출력하여 가시성을 높입니다."""
    print("\n" + "="*50)
    print(f" {title:^48}")
    print("="*50)

def run_optimization_test(size=25):
    """
    [보너스 과제] 메모리 접근 최적화 성능 비교
    2차원 리스트 구조와 1차원 선형 구조의 연산 속도 차이를 데이터로 증명합니다.
    """
    print_header(f"🚀 {size}x{size} NPU 최적화 벤치마킹")
    
    # 1. 테스트 데이터 생성 및 전처리
    p_2d = generate_standard_pattern(size, "Cross")
    f_2d = generate_standard_pattern(size, "Cross")
    
    # 2차원 데이터를 1차원으로 펼침 (Memory Flattening)
    p_1d = flatten_matrix(p_2d)
    f_1d = flatten_matrix(f_2d)

    print(f" 연산 횟수: {size*size}회 x 1000번 반복 측정 시작...")

    # 2. 기존 방식 (2차원 리스트 순회) 성능 측정
    start_2d = time.perf_counter()
    for _ in range(1000):
        calculate_mac(p_2d, f_2d)
    time_2d = time.perf_counter() - start_2d

    # 3. 최적화 방식 (1차원 선형 순회) 성능 측정
    start_1d = time.perf_counter()
    for _ in range(1000):
        calculate_mac_optimized(p_1d, f_1d)
    time_1d = time.perf_counter() - start_1d

    # 4. 결과 분석 리포트 출력
    improvement = ((time_2d - time_1d) / time_2d) * 100
    print("\n" + "-"*40)
    print(f" • 기존 방식(2D) 소요 시간 : {time_2d:.4f}s")
    print(f" • 최적화 방식(1D) 소요 시간 : {time_1d:.4f}s")
    print(f" • 하드웨어 효율 향상률    : {improvement:.1f}% 개선")
    print("-" * 40)
    print(" 💡 분석: 연속된 메모리 주소 접근(Spatial Locality)으로 연산 오버헤드가 감소했습니다.")
    input("\n 엔터를 누르면 메뉴로 돌아갑니다...")

def run_mode_1():
    """모드 1: 3x3 개별 패턴에 대한 실시간 MAC 연산 시뮬레이션"""
    print_header("모드 1: 실시간 패턴 분석")
    print(" 1. 표준 샘플 사용 (3x3 Cross/X 자동 생성)")
    print(" 2. 수동 데이터 입력 (3x3 직접 타이핑)")
    print(" 0. 뒤로 가기")
    
    choice = input("\n 선택 > ").strip()
    if choice == '0': return

    if choice == '1':
        f_cross = generate_standard_pattern(3, "Cross")
        f_x = generate_standard_pattern(3, "X")
        
        print("\n [생성된 필터 모양 가시화]")
        print("  <Cross 필터>")
        for r in f_cross: print("  " + " ".join(["■" if v else "□" for v in r]))
        
        p_choice = input("\n 테스트할 패턴 선택 (1:Cross, 2:X) > ")
        pattern = f_cross if p_choice == '1' else f_x
        f_a, f_b = f_cross, f_x
    else:
        # 수동 입력 시 data_handler의 예외 처리 로직이 작동합니다.
        f_a = get_user_input_matrix("필터 A")
        f_b = get_user_input_matrix("필터 B")
        pattern = get_user_input_matrix("테스트 패턴")

    # 가상 NPU 연산 시각화 효과
    print("\n 🔍 NPU 가속기 가동 중...", end="", flush=True)
    for _ in range(3): time.sleep(0.2); print(".", end="", flush=True)
    
    # 코어 엔진 호출 (MAC 연산)
    sc_a = calculate_mac(pattern, f_a)
    sc_b = calculate_mac(pattern, f_b)
    # Epsilon 정책 기반 최종 판정
    res = judge_with_epsilon(sc_a, sc_b)
    
    print("\n\n" + " ✨ 분석 결과 " + "-"*35)
    print(f"  • 필터 A 유사도 점수 : {sc_a:>6.2f}")
    print(f"  • 필터 B 유사도 점수 : {sc_b:>6.2f}")
    print(f"  • 최종 알고리즘 판정 : 【 {res} 】")
    print("-" * 50)
    input("\n 엔터를 누르면 메뉴로 돌아갑니다...")

def run_mode_2():
    """모드 2: data.json 파일 기반 일괄 배치 분석 및 성능 지표 산출"""
    data = load_json_data()
    if not data: return

    patterns = data.get('patterns', {})
    filters = data.get('filters', {})
    results, stats = [], {}

    print_header("모드 2: data.json 배치(Batch) 분석")
    total_count = len(patterns)
    print(f" 📂 총 {total_count}개의 패턴을 로드했습니다. 순차 분석을 시작합니다.\n")

    for i, (p_key, p_info) in enumerate(patterns.items(), 1):
        # 1. 키에서 데이터 크기(N) 추출
        try:
            size = int(p_key.split('_')[1])
            target_f = filters.get(f"size_{size}")
        except:
            continue # 스키마 오류 시 건너뜀
        
        # 2. 실시간 진행률(Progress) 표시
        print(f" [{i}/{total_count}] 연산 중: {p_key:<15}", end="\r")
        
        # 3. MAC 연산 및 라벨 정규화 비교
        sc_c = calculate_mac(p_info['input'], target_f.get('cross') or target_f.get('+'))
        sc_x = calculate_mac(p_info['input'], target_f.get('x') or target_f.get('X'))
        
        pred = judge_with_epsilon(sc_c, sc_x)
        expected = normalize_label(p_info['expected'])
        is_pass = (pred == expected)
        
        # 4. 결과 아카이빙
        results.append({"id": p_key, "status": "PASS" if is_pass else "FAIL", "pred": pred, "exp": expected})
        
        # 5. 성능 지표 측정 (크기별 1회 수행)
        if size not in stats:
            stats[size] = measure_performance(p_info['input'], target_f.get('cross') or target_f.get('+'))
        time.sleep(0.05) # 시각적 피드백을 위한 미세 지연

    print("\n\n ✅ 전수 분석 완료!")
    
    # 배치 분석 최종 요약 리포트
    pass_count = len([r for r in results if r['status'] == "PASS"])
    print(f"\n 📊 테스트 통계: {pass_count}/{total_count} 통과 (성공률 {(pass_count/total_count)*100:.1f}%)")
    
    if total_count > pass_count:
        print("\n ❌ 실패 케이스 분석 (수치 오차 및 라벨 불일치):")
        for r in results:
            if r['status'] == "FAIL":
                print(f"   - {r['id']}: 판정({r['pred']}) != 기대({r['exp']})")

    # O(N^2) 시간 복잡도 증명 표
    print("\n" + "-"*60)
    print(f" {'패턴 크기':<12} | {'평균 연산 시간(ms)':<18} | {'MAC 연산 횟수'}")
    print("-" * 60)
    for s in sorted(stats.keys()):
        # 숫자-문자 결합 에러 방지를 위해 str() 형변환 적용
        size_label = f"{s}x{s}"
        print(f"  {size_label:<11} | {stats[s]:<20.6f} | {s*s:>10}회")
    print("-" * 60)
    
    input("\n 엔터를 누르면 메뉴로 돌아갑니다...")

def main():
    """메인 컨트롤 루프: 시스템 진입점"""
    while True:
        # 터미널 화면 정리를 통해 쾌적한 UX 제공
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + " " * 12 + "🚀 Mini NPU Simulator v1.5")
        print("="*55)
        print("  1. [개별 분석] 3x3 사용자 패턴 시뮬레이션")
        print("  2. [배치 분석] data.json 일괄 분석 및 성능 리포트")
        print("  3. [보너스] 1차원 배열 메모리 최적화 성능 벤치마크")
        print("  9. [시스템 종료] 프로그램 안전 마감")
        print("="*55)
        
        choice = input("\n 메뉴를 선택해 주세요 > ").strip()
        
        try:
            if choice == '1': run_mode_1()
            elif choice == '2': run_mode_2()
            elif choice == '3': run_optimization_test(25)
            elif choice == '9': 
                print("\n 시스템을 종료합니다. 프로젝트 완수를 축하드립니다! 👋"); break
            else:
                print("\n ⚠️ 알림: 올바른 메뉴 번호를 입력해 주세요."); time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n ⚠️ 사용자에 의해 강제 중단되었습니다. 메뉴로 돌아갑니다."); time.sleep(1)
        except Exception as e:
            print(f"\n ❌ 예기치 못한 시스템 오류 발생: {e}"); input("\n 엔터를 눌러 복구...")

if __name__ == "__main__":
    main()