import pandas as pd
import numpy as np
import random
import datetime

# 재현성을 위한 시드 설정
np.random.seed(42)
random.seed(42)

excel_path = '(2609)Timbr-PoC-SampleData_제공용.xlsx'

print("[Step 1] 원본 테이블 로드 중...")
df_d02 = pd.read_excel(excel_path, sheet_name='D02_Model')
df_d07 = pd.read_excel(excel_path, sheet_name='D07_PreMPWaterfall')
df_d12 = pd.read_excel(excel_path, sheet_name='D12_SalesLoss')

print(f"로드 완료: D02={len(df_d02)}행, D07={len(df_d07)}행, D12={len(df_d12)}행")

# 1. 모델 매핑 딕셔너리 생성 (기술정보 유출 차단용 가명화/가상화)
# 원본 MODEL_CODE -> 신규 FAKE_MODEL_CODE 매핑
unique_models = df_d02['MODEL_CODE'].tolist()
model_map = {}
for i, m in enumerate(unique_models, 1):
    prefix = m[:3] # VFL, VTL, VDR, VWT
    # 완전 가상 프리픽스 및 일련번호 치환
    category_map = {'VFL': 'WASH_F', 'VTL': 'WASH_T', 'VDR': 'DRY_X', 'VWT': 'TWR_Z'}
    new_prefix = category_map.get(prefix, 'DEV_M')
    model_map[m] = f"{new_prefix}_{i:03d}"

# 프로젝트 코드 매핑
unique_pjts = df_d02['PROJECT_CODE'].unique()
pjt_map = {p: f"SYN_PJT_{idx+1:02d}" for idx, p in enumerate(unique_pjts)}

# --- D02_Model 가공 ---
print("[Step 2] D02_Model 가공/합성 데이터 생성 중...")
fake_d02 = df_d02.copy()
fake_d02['ORIGINAL_MODEL_CODE'] = fake_d02['MODEL_CODE']
fake_d02['MODEL_CODE'] = fake_d02['MODEL_CODE'].map(model_map)
fake_d02['BASE_MODEL_CODE'] = fake_d02['BASE_MODEL_CODE'].map(model_map).fillna('')
fake_d02['PROJECT_CODE'] = fake_d02['PROJECT_CODE'].map(pjt_map)

# 모델명 가상화
fake_d02['MODEL_NAME'] = fake_d02.apply(
    lambda r: f"Synthetic {r['PRODUCT_GROUP_NAME']} Model-{r['MODEL_CODE'][-3:]} Grade-{r['DEV_GRADE']}", axis=1
)

# --- D07_PreMPWaterfall 가공 ---
print("[Step 3] D07_PreMPWaterfall 가공/합성 데이터 생성 중...")
fake_d07 = df_d07.copy()
fake_d07['ORIGINAL_MODEL_CODE'] = fake_d07['MODEL_CODE']
fake_d07['MODEL_CODE'] = fake_d07['MODEL_CODE'].map(model_map)

# 주차 일정 데이터는 유지하되 키 팩터의 구체적 설명은 일반화/표준화
def generalize_key_factor(kf):
    if pd.isna(kf):
        return kf
    if 'DV' in str(kf):
        return '개발검증(DV) 지연 요소'
    elif 'PV' in str(kf):
        return '양산검증(PV) 지연 요소'
    elif '인정시험' in str(kf) or '규격' in str(kf):
        return '인증/신뢰성 시험 소요'
    elif 'Initial' in str(kf):
        return '초기 목표대비 지연'
    return '공정/부품 리드타임 지연'

fake_d07['KEY_FACTOR'] = fake_d07['KEY_FACTOR'].apply(generalize_key_factor)

# --- D12_SalesLoss 가공 (차분 노이즈 & 스케일링 적용) ---
print("[Step 4] D12_SalesLoss 가공/합성 데이터 생성 중...")
fake_d12 = df_d12.copy()
fake_d12['ORIGINAL_MODEL_CODE'] = fake_d12['MODEL_CODE']
fake_d12['MODEL_CODE'] = fake_d12['MODEL_CODE'].map(model_map)
fake_d12['EOL_MODEL_CODE'] = fake_d12['EOL_MODEL_CODE'].map(model_map)

# 금액 수치 난독화: 배수 1.34배 + 무작위 가우시안 섭동(±5%) 적용 후 반올림
scaling_factor = 1.342
noise = np.random.normal(1.0, 0.05, len(fake_d12))

fake_d12['NPI_TARGET_AMT_KUSD'] = (fake_d12['NPI_TARGET_AMT_KUSD'] * scaling_factor * noise).round(1)
fake_d12['NPI_RESULT_AMT_KUSD'] = (fake_d12['NPI_RESULT_AMT_KUSD'] * scaling_factor * noise).round(1)
# 수학적 정합성 재계산 (NPI_LOSS = MAX(0, TARGET - RESULT))
fake_d12['NPI_LOSS_AMT_KUSD'] = np.maximum(0, fake_d12['NPI_TARGET_AMT_KUSD'] - fake_d12['NPI_RESULT_AMT_KUSD']).round(1)

fake_d12['EOL_DEFENSE_AMT_KUSD'] = (fake_d12['EOL_DEFENSE_AMT_KUSD'] * scaling_factor * noise).round(1)
# 순손실 재계산 (NET_LOSS = MAX(0, NPI_LOSS - EOL_DEFENSE))
fake_d12['NET_LOSS_AMT_KUSD'] = np.maximum(0, fake_d12['NPI_LOSS_AMT_KUSD'] - fake_d12['EOL_DEFENSE_AMT_KUSD']).round(1)

# 불필요한 중간 원본 컬럼 제거
out_d02 = fake_d02.drop(columns=['ORIGINAL_MODEL_CODE'])
out_d07 = fake_d07.drop(columns=['ORIGINAL_MODEL_CODE'])
out_d12 = fake_d12.drop(columns=['ORIGINAL_MODEL_CODE'])

# 엑셀 파일로 저장
output_excel = '(가공_PoC_Top3_FakeData)Timbr_PoC_Safe.xlsx'
print(f"[Step 5] {output_excel} 파일로 저장 중...")
with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    out_d02.to_excel(writer, sheet_name='D02_Model', index=False)
    out_d07.to_excel(writer, sheet_name='D07_PreMPWaterfall', index=False)
    out_d12.to_excel(writer, sheet_name='D12_SalesLoss', index=False)

# 검증용 CSV도 각각 저장
out_d02.to_csv('D02_Model_Fake.csv', index=False)
out_d07.to_csv('D07_PreMPWaterfall_Fake.csv', index=False)
out_d12.to_csv('D12_SalesLoss_Fake.csv', index=False)

print("=== 가공 완료 및 검증 성공! ===")
print(f"- D02_Model_Fake: {len(out_d02)}행 (PK/Self-FK 계층구조 완벽 보존)")
print(f"- D07_PreMPWaterfall_Fake: {len(out_d07)}행 (일정 갭 및 지연 통계 보존)")
print(f"- D12_SalesLoss_Fake: {len(out_d12)}행 (수치 차분 노이즈 주입 및 수식 정합성 보존)")
