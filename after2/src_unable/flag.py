import pandas as pd


def add_columns(before_reconstruction, unable):

    # unable_intu_extu의 hadm_id만 필터링
    before_reconstruction = before_reconstruction[before_reconstruction.hadm_id.isin(unable.hadm_id.unique())].reset_index(drop = True)
    intubation_df = before_reconstruction[['subject_id','hadm_id','stay_id','intubationtime']]
    extubation_df = before_reconstruction[['subject_id','hadm_id','stay_id','extubationtime','extubationcause']]

    # 원본 데이터
    intubation_df['data_type']='real'
    extubation_df['data_type']='real'
    
    # unable 데이터
    unable['data_type']='unable'

    # 필요한 컬럼 추가
    real_intu = intubation_df[['subject_id','hadm_id','stay_id','intubationtime','data_type']]
    real_intu.loc[:,'event_type'] = 'intubation'  # 삽/발관 표시
    real_intu.rename(columns={'intubationtime': 'time'}, inplace=True)

    real_extu = extubation_df[['subject_id','hadm_id','stay_id','extubationtime','data_type','extubationcause']]
    real_extu.loc[:,'event_type'] = 'extubation'
    real_extu.rename(columns={'extubationtime': 'time'}, inplace=True)

    unable_intu = unable[['subject_id','hadm_id','stay_id','intubationtime(un)','data_type']]
    unable_intu.loc[:,'event_type'] = 'intubation'
    unable_intu.rename(columns={'intubationtime(un)': 'time'}, inplace=True)

    unable_extu = unable[['subject_id','hadm_id','stay_id','extubationtime(un)','data_type']]
    unable_extu.loc[:,'event_type'] = 'extubation'
    unable_extu.rename(columns={'extubationtime(un)': 'time'}, inplace=True)

    table = pd.concat([real_intu, real_extu, unable_intu, unable_extu])
    table = table.dropna(subset = ['time'])

    table = table.sort_values(by=['subject_id','hadm_id','stay_id','time']).reset_index(drop = True)

    return table


def duplicates_row_flag(table): 
    '''
    - intubation or extubation이 연달아 나오는 경우
    - 행을 삭제하거나 시간을 새로 추가해야 함
    '''

    table['dup_flag'] = False

    table['next_type'] = table.groupby(['stay_id']).event_type.shift(-1)
    table.loc[table.event_type == table.next_type,'dup_flag'] = True
    table.drop(columns = 'next_type', inplace = True)

    return table


def time_diff(table):
    table['time_diff'] = pd.NaT
    table['time'] = pd.to_datetime(table['time'])
    '''dup_flag가 True인 행과 그 다음 행의 시간 차이를 계산'''
    for idx, row in table[table.dup_flag].iterrows():
        next_idx = idx + 1
        table.loc[idx,'time_diff'] = table.loc[[idx,next_idx]].time.diff().loc[next_idx]

    return table

def alignment_intuextu(table):
    ''' 같은 time일 경우 intubation이 먼저 나오도록 정렬'''
    table['type_order'] = table['event_type'].map({'intubation': 0, 'extubation': 1})
    table.sort_values(by=['subject_id', 'hadm_id', 'stay_id', 'time', 'type_order'], inplace=True)
    table.drop('type_order', axis=1, inplace=True)
    table = table.reset_index(drop = True)
    return table


def drop_duplication(table):

    # 중복 제거
    table.sort_values(by=['subject_id','hadm_id','stay_id','time','data_type'], inplace = True)
    table = table.drop_duplicates(subset=['subject_id', 'hadm_id', 'stay_id', 'time', 'event_type'], keep='first').reset_index(drop=True)

    # 재정렬
    table = alignment_intuextu(table)

    return table





