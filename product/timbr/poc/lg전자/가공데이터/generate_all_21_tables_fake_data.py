import pandas as pd
import numpy as np
import random
import openpyxl
import os

# 재현성을 위한 시드 설정
np.random.seed(42)
random.seed(42)

excel_path = '(2609)Timbr-PoC-SampleData_제공용.xlsx'
wb_in = pd.ExcelFile(excel_path)

print("[Step 1] 기본 메타데이터 및 전체 테이블 로드 시작...")

# 1. 원본 메타데이터 시트 읽기
meta_sheet_names = ['00_가이드', '01_명세서-시트', '02_명세서-컬럼', '03_명세서-관계', '04_명세서-코드값', '05_용어집', '06_업무로직', '07_테스트항목']
meta_dfs = {s: pd.read_excel(excel_path, sheet_name=s) for s in meta_sheet_names if s in wb_in.sheet_names}

# 2. 21개 데이터 시트 읽기
data_sheet_names = [s for s in wb_in.sheet_names if s.startswith('D')]
data_dfs = {s: pd.read_excel(excel_path, sheet_name=s) for s in data_sheet_names}

print(f"메타 시트 {len(meta_dfs)}개, 데이터 시트 {len(data_dfs)}개 로드 완료.")

# --- 매핑 사전 구축 ---
# 1) 모델 코드 매핑 (D02_Model 기준)
df_d02 = data_dfs['D02_Model']
unique_models = df_d02['MODEL_CODE'].tolist()
category_map = {'VFL': 'WASH_F', 'VTL': 'WASH_T', 'VDR': 'DRY_X', 'VWT': 'TWR_Z'}

model_map = {}
for i, m in enumerate(unique_models, 1):
    prefix = m[:3]
    new_prefix = category_map.get(prefix, 'DEV_M')
    model_map[m] = f"{new_prefix}_{i:03d}"

# 2) 프로젝트 코드 매핑 (D03_Project 기준)
df_d03 = data_dfs['D03_Project']
unique_pjts = df_d03['PROJECT_CODE'].tolist()
pjt_map = {p: f"SYN_PJT_{i+1:02d}" for i, p in enumerate(unique_pjts)}
pjt_name_map = {p: f"Project-Neo{chr(65+i%26)}" for i, p in enumerate(unique_pjts)}

# 3) 인력 ID 매핑 (D04_Person 기준)
df_d04 = data_dfs['D04_Person']
unique_persons = df_d04['PERSON_ID'].tolist()
person_map = {p: f"SYN_EMP_{i+1:03d}" for i, p in enumerate(unique_persons)}
person_name_map = {p: f"가상엔지니어{i+1:02d}" for i, p in enumerate(unique_persons)}

print(f"매핑 구축 완료: 모델={len(model_map)}개, 프로젝트={len(pjt_map)}개, 인력={len(person_map)}개")

def safe_map_model(series):
    return series.map(lambda x: model_map.get(x, x) if pd.notna(x) else x)

def safe_map_pjt(series):
    return series.map(lambda x: pjt_map.get(x, x) if pd.notna(x) else x)

def safe_map_person(series):
    return series.map(lambda x: person_map.get(x, x) if pd.notna(x) else x)

# 전역 스케일링 계수 및 노이즈 주입 함수
GLOBAL_SCALE = 1.342

def apply_scale_noise(series, scale=GLOBAL_SCALE, noise_std=0.03, decimals=1):
    if len(series) == 0:
        return series
    noise = np.random.normal(1.0, noise_std, len(series))
    return (series * scale * noise).round(decimals)

# 텍스트 일반화 함수
def generalize_text(text):
    if pd.isna(text):
        return text
    text_str = str(text)
    if 'DV' in text_str:
        return '개발설계(DV) 일정 지연 검증'
    elif 'PV' in text_str:
        return '양산검증(PV) 공정 점검 소요'
    elif '인정' in text_str or '규격' in text_str:
        return '신뢰성/인증 시험 리드타임'
    elif 'Initial' in text_str:
        return '초기 목표일정 대비 편차'
    elif 'Capa' in text_str or '투입' in text_str:
        return '개발 Capa 투입율 조정'
    return text_str

print("[Step 2] 21개 테이블 가공 및 합성 변환 적용 중...")

out_dfs = {}

# D01_Subsidiary
d01 = data_dfs['D01_Subsidiary'].copy()
out_dfs['D01_Subsidiary'] = d01

# D02_Model
d02 = data_dfs['D02_Model'].copy()
d02['MODEL_CODE'] = safe_map_model(d02['MODEL_CODE'])
d02['BASE_MODEL_CODE'] = safe_map_model(d02['BASE_MODEL_CODE'])
d02['PROJECT_CODE'] = safe_map_pjt(d02['PROJECT_CODE'])
d02['MODEL_NAME'] = d02.apply(lambda r: f"Synthetic {r['PRODUCT_GROUP_NAME']} Model-{r['MODEL_CODE'][-3:]} Grade-{r['DEV_GRADE']}", axis=1)
out_dfs['D02_Model'] = d02

# D03_Project
d03 = data_dfs['D03_Project'].copy()
d03['PROJECT_CODE'] = safe_map_pjt(d03['PROJECT_CODE'])
d03['PROJECT_NAME'] = d03['PROJECT_CODE'].map(lambda x: f"Project-Neo{x[-2:]}")
d03['PROJECT_TEAM'] = d03['PROJECT_TEAM'].map(lambda x: f"가상개발TF_{x[:3]}" if pd.notna(x) else x)
d03['DEV_LEADER_ID'] = safe_map_person(d03['DEV_LEADER_ID'])
out_dfs['D03_Project'] = d03

# D04_Person
d04 = data_dfs['D04_Person'].copy()
d04['PERSON_ID'] = safe_map_person(d04['PERSON_ID'])
d04['PERSON_NAME'] = d04['PERSON_ID'].map(lambda x: f"가상연구원_{x[-3:]}")
out_dfs['D04_Person'] = d04

# D05_Calendar (일자/주차 체계 유지)
out_dfs['D05_Calendar'] = data_dfs['D05_Calendar'].copy()

# D06_DevEvent
d06 = data_dfs['D06_DevEvent'].copy()
d06['MODEL_CODE'] = safe_map_model(d06['MODEL_CODE'])
d06['EVENT_DESC'] = d06['EVENT_DESC'].apply(generalize_text)
out_dfs['D06_DevEvent'] = d06

# D07_PreMPWaterfall
d07 = data_dfs['D07_PreMPWaterfall'].copy()
d07['MODEL_CODE'] = safe_map_model(d07['MODEL_CODE'])
d07['KEY_FACTOR'] = d07['KEY_FACTOR'].apply(generalize_text)
out_dfs['D07_PreMPWaterfall'] = d07

# D08_PlanWaterfall (대용량 팩트)
d08 = data_dfs['D08_PlanWaterfall'].copy()
d08['MODEL_CODE'] = safe_map_model(d08['MODEL_CODE'])
d08['PLAN_QTY'] = (d08['PLAN_QTY'] * np.random.normal(1.0, 0.05, len(d08))).round(0).astype(int)
d08['UNIT_PRICE_USD'] = (d08['UNIT_PRICE_USD'] * GLOBAL_SCALE * np.random.normal(1.0, 0.02, len(d08))).round(1)
d08['PLAN_AMT_USD'] = (d08['PLAN_QTY'] * d08['UNIT_PRICE_USD']).round(0).astype(int)
out_dfs['D08_PlanWaterfall'] = d08

# D09_ShipmentResult
d09 = data_dfs['D09_ShipmentResult'].copy()
d09['MODEL_CODE'] = safe_map_model(d09['MODEL_CODE'])
d09['RESULT_QTY'] = (d09['RESULT_QTY'] * np.random.normal(1.0, 0.05, len(d09))).round(0).astype(int)
d09['UNIT_PRICE_USD'] = (d09['UNIT_PRICE_USD'] * GLOBAL_SCALE * np.random.normal(1.0, 0.02, len(d09))).round(1)
d09['RESULT_AMT_USD'] = (d09['RESULT_QTY'] * d09['UNIT_PRICE_USD']).round(0).astype(int)
out_dfs['D09_ShipmentResult'] = d09

# D10_ModelMapping
d10 = data_dfs['D10_ModelMapping'].copy()
d10['NPI_MODEL_CODE'] = safe_map_model(d10['NPI_MODEL_CODE'])
d10['EOL_MODEL_CODE'] = safe_map_model(d10['EOL_MODEL_CODE'])
out_dfs['D10_ModelMapping'] = d10

# D11_Inventory
d11 = data_dfs['D11_Inventory'].copy()
d11['MODEL_CODE'] = safe_map_model(d11['MODEL_CODE'])
d11['ONHAND_QTY'] = (d11['ONHAND_QTY'] * np.random.normal(1.0, 0.05, len(d11))).round(0).astype(int)
d11['ONHAND_AMT_USD'] = (d11['ONHAND_AMT_USD'] * GLOBAL_SCALE * np.random.normal(1.0, 0.03, len(d11))).round(0).astype(int)
d11['INTRANSIT_QTY'] = (d11['INTRANSIT_QTY'] * np.random.normal(1.0, 0.05, len(d11))).round(0).astype(int)
d11['LT_INV_QTY'] = (d11['LT_INV_QTY'] * np.random.normal(1.0, 0.05, len(d11))).round(0).astype(int)
d11['LT_INV_AMT_USD'] = (d11['LT_INV_AMT_USD'] * GLOBAL_SCALE * np.random.normal(1.0, 0.03, len(d11))).round(0).astype(int)
d11['LT_INV_RATIO'] = np.where(d11['ONHAND_QTY'] > 0, (d11['LT_INV_QTY'] / d11['ONHAND_QTY'] * 100).round(1), 0.0)
out_dfs['D11_Inventory'] = d11

# D12_SalesLoss
d12 = data_dfs['D12_SalesLoss'].copy()
d12['MODEL_CODE'] = safe_map_model(d12['MODEL_CODE'])
d12['EOL_MODEL_CODE'] = safe_map_model(d12['EOL_MODEL_CODE'])
noise_12 = np.random.normal(1.0, 0.05, len(d12))
d12['NPI_TARGET_AMT_KUSD'] = (d12['NPI_TARGET_AMT_KUSD'] * GLOBAL_SCALE * noise_12).round(1)
d12['NPI_RESULT_AMT_KUSD'] = (d12['NPI_RESULT_AMT_KUSD'] * GLOBAL_SCALE * noise_12).round(1)
d12['NPI_LOSS_AMT_KUSD'] = np.maximum(0, d12['NPI_TARGET_AMT_KUSD'] - d12['NPI_RESULT_AMT_KUSD']).round(1)
d12['EOL_DEFENSE_AMT_KUSD'] = (d12['EOL_DEFENSE_AMT_KUSD'] * GLOBAL_SCALE * noise_12).round(1)
d12['NET_LOSS_AMT_KUSD'] = np.maximum(0, d12['NPI_LOSS_AMT_KUSD'] - d12['EOL_DEFENSE_AMT_KUSD']).round(1)
out_dfs['D12_SalesLoss'] = d12

# D13_PDR
d13 = data_dfs['D13_PDR'].copy()
d13['MODEL_CODE'] = safe_map_model(d13['MODEL_CODE'])
d13['SALES_TARGET_QTY'] = (d13['SALES_TARGET_QTY'] * np.random.normal(1.0, 0.05, len(d13))).round(0).astype(int)
d13['SALES_TARGET_AMT_KUSD'] = (d13['SALES_TARGET_AMT_KUSD'] * GLOBAL_SCALE * np.random.normal(1.0, 0.03, len(d13))).round(1)
out_dfs['D13_PDR'] = d13

# D14_CapaStandard
out_dfs['D14_CapaStandard'] = data_dfs['D14_CapaStandard'].copy()

# D15_DevCapa
d15 = data_dfs['D15_DevCapa'].copy()
d15['PROJECT_CODE'] = safe_map_pjt(d15['PROJECT_CODE'])
d15['REQUIRED_CAPA'] = (d15['REQUIRED_CAPA'] * np.random.normal(1.0, 0.02, len(d15))).round(1)
d15['AVAILABLE_CAPA'] = (d15['AVAILABLE_CAPA'] * np.random.normal(1.0, 0.02, len(d15))).round(1)
d15['DEV_INPUT_RATE_PCT'] = np.where(d15['REQUIRED_CAPA'] > 0, (d15['AVAILABLE_CAPA'] / d15['REQUIRED_CAPA'] * 100).round(1), 0.0)
out_dfs['D15_DevCapa'] = d15

# D16_QualityTest
d16 = data_dfs['D16_QualityTest'].copy()
d16['MODEL_CODE'] = safe_map_model(d16['MODEL_CODE'])
out_dfs['D16_QualityTest'] = d16

# D17_CertLeadtime
out_dfs['D17_CertLeadtime'] = data_dfs['D17_CertLeadtime'].copy()

# D18_AnomalyRule
d18 = data_dfs['D18_AnomalyRule'].copy()
d18['DEFINITION'] = d18['DEFINITION'].apply(generalize_text)
out_dfs['D18_AnomalyRule'] = d18

# D19_AnomalyResult
d19 = data_dfs['D19_AnomalyResult'].copy()
d19['MODEL_CODE'] = safe_map_model(d19['MODEL_CODE'])
d19['EXPECTED_LOSS_KUSD'] = (d19['EXPECTED_LOSS_KUSD'] * GLOBAL_SCALE * np.random.normal(1.0, 0.04, len(d19))).round(1)
d19['KEY_FACTOR'] = d19['KEY_FACTOR'].apply(generalize_text)
out_dfs['D19_AnomalyResult'] = d19

# D20_ActionRule
d20 = data_dfs['D20_ActionRule'].copy()
d20['ACTION_DESC'] = d20['ACTION_DESC'].apply(generalize_text)
out_dfs['D20_ActionRule'] = d20

# D21_ModelSubsidiary
d21 = data_dfs['D21_ModelSubsidiary'].copy()
d21['MODEL_CODE'] = safe_map_model(d21['MODEL_CODE'])
d21['EOL_MODEL_CODE'] = safe_map_model(d21['EOL_MODEL_CODE'])
out_dfs['D21_ModelSubsidiary'] = d21

print("21개 전체 테이블 가공 완료! 파일 저장 시작...")

# [Step 3] 통합 엑셀 저장
output_excel = '(2609)Timbr-PoC-SampleData_전체21개_가공완료.xlsx'
print(f"통합 엑셀 생성 중: {output_excel}")

with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    # 1) 메타데이터 시트 저장
    for s_name, m_df in meta_dfs.items():
        m_df.to_excel(writer, sheet_name=s_name, index=False)
    # 2) 21개 가공 데이터 시트 저장
    for s_name, d_df in out_dfs.items():
        d_df.to_excel(writer, sheet_name=s_name, index=False)

print(f"통합 엑셀 저장 완료! 총 시트 수: {len(meta_dfs) + len(out_dfs)}개")

# [Step 4] 개별 CSV 파일 덤프 (csv_dump 디렉토리)
csv_dir = 'csv_tables'
os.makedirs(csv_dir, exist_ok=True)
for s_name, d_df in out_dfs.items():
    csv_file = os.path.join(csv_dir, f"{s_name}.csv")
    d_df.to_csv(csv_file, index=False)
print(f"21개 개별 CSV 저장 완료: {csv_dir}/ 하위 21개 파일")

# [Step 5] 데이터 무결성 검증
print("\n=== 무결성 검증 (Data Integrity Check) ===")
d02_models = set(out_dfs['D02_Model']['MODEL_CODE'])

for s_name in ['D06_DevEvent', 'D07_PreMPWaterfall', 'D08_PlanWaterfall', 'D09_ShipmentResult', 'D10_ModelMapping', 'D11_Inventory', 'D12_SalesLoss', 'D13_PDR', 'D16_QualityTest', 'D19_AnomalyResult', 'D21_ModelSubsidiary']:
    col = 'NPI_MODEL_CODE' if s_name == 'D10_ModelMapping' else 'MODEL_CODE'
    fk_models = set(out_dfs[s_name][col].dropna())
    is_valid = fk_models.issubset(d02_models)
    print(f"FK 검증 [{s_name}.{col} -> D02_Model]: {'✅ 정상' if is_valid else '❌ 오류'}")

print("=== 21개 전체 가공 완료 ===")
