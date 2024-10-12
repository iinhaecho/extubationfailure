# -*- coding: utf-8 -*-
"""
ventilator_mode, ventilator_mode_hamilton 컬럼의 mode를 숫자로 매핑해주는 함수
- CMV -> 4
- SIMV -> 3
- CPAP, PSV -> 2
- SPONT -> 1
- 특정 조합에 해당하는 행 -> 5
"""

# ventilator_mode 매핑 딕셔너리 정의
ventilator_mode_mapping = {
    ('SPONT','Standby'): 1, # SPONT
    ('CPAP/PSV', 'PSV/SBT','CPAP/PSV+ApnVol','CPAP','APRV','CPAP/PPS','CPAP/PSV+ApnPres','APRV/Biphasic+ApnVol','CPAP/PSV+Apn TCPL','Apnea Ventilation'): 2,  # CPAP, PSV
    ('MMV/PSV/AutoFlow','MMV/PSV','SIMV/PSV/AutoFlow','SIMV/PSV','MMV','MMV/AutoFlow','SIMV/PRES','SIMV/AutoFlow','SIMV/VOL','SIMV','PRVC/SIMV'): 3,  # SIMV
    ('CMV/ASSIST/AutoFlow','CMV/ASSIST','PCV+Assist','CMV/AutoFlow','PCV+/PSV','CMV','PCV+','VOL/AC','APV (cmv)','P-CMV','(S) CMV','PRVC/AC','PRES/AC'): 4  # CMV
}

def map_ventilator_mode(value):
    for keys, mapped_value in ventilator_mode_mapping.items():
        if value in keys:
            return mapped_value
    return None


# ventilator_mode_hamilton 매핑 딕셔너리 정의
ventilator_mode_hamilton_mapping = {
    ('SPONT',): 1, # SPONT
    ('APRV','nCPAP-PS','NIV','NIV-ST','VS'): 2,  # CPAP, PSV
    ('ASV','APV (simv)','SIMV'): 3,  # SIMV
    ('APV (cmv)','P-CMV','(S) CMV'): 4  # CMV
}

def map_ventilator_mode_hamilton(value):
    for keys, mapped_value in ventilator_mode_hamilton_mapping.items():
        if value in keys:
            return mapped_value
    return None

def update_ventilator_scoring(df):
    '''
    ventilator_mode, ventilator_mode_hamilton 매핑
    '''

    # ventilator_mode와 ventilator_mode_hamilton이 모두 na인 경우는 None
    df['ventilator_scoring'] = None  # 기본값을 None으로 설정

    # ventilator_mode이 na가 아닌 경우 해당 값을 사용하여 매핑
    mask_mode = df['ventilator_mode'].notna()
    df.loc[mask_mode, 'ventilator_scoring'] = df.loc[mask_mode, 'ventilator_mode'].apply(map_ventilator_mode)

    # ventilator_mode_hamilton가 na가 아닌 경우 해당 값을 사용하여 매핑 (ventilator_mode의 매핑을 덮어쓸 수 있음)
    mask_hamilton = df['ventilator_mode_hamilton'].notna()
    df.loc[mask_hamilton, 'ventilator_scoring'] = df.loc[mask_hamilton, 'ventilator_mode_hamilton'].apply(map_ventilator_mode_hamilton)

    # 특정 조합에 해당하는 행을 5로 맵핑
    pairs = [
        ('PSV/SBT', 'APV (cmv)'),
        ('Standby', 'APV (cmv)'),
        ('CMV/ASSIST', 'SPONT'),
        ('PSV/SBT', 'SPONT'),
        ('CPAP/PSV', 'Ambient'),
        ('CMV/ASSIST/AutoFlow', 'Ambient')
    ]

    for mode, hamilton in pairs:
        df.loc[(df['ventilator_mode'] == mode) & (df['ventilator_mode_hamilton'] == hamilton), 'ventilator_scoring'] = 5

    return df