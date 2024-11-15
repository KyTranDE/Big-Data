import pandas as pd
import os 

def load_data(path_data):
    """
    Tải dữ liệu email từ URL và trả về DataFrame chứa dữ liệu email.
    
    Returns:
        DataFrame chúa dữ liệu email.
        
    """
    df = pd.read_csv(path_data)
    processed_indices_path = '/opt/airflow/dags/Utils/data/processed_indices.csv'
    
    if os.path.exists(processed_indices_path):
        processed_indices = pd.read_csv(processed_indices_path)['index'].tolist()
    else:
        processed_indices = []

    unprocessed_df = df.loc[~df.index.isin(processed_indices)]
    sample_df = unprocessed_df.sample(200)
    processed_indices.extend(sample_df.index.tolist())
    
    return sample_df, processed_indices

def save_processed_indices(processed_indices):
    """
    Lưu các chỉ số đã xử lý vào file CSV.
    
    Args:
        processed_indices (list): Danh sách các chỉ số đã xử lý.
        
    """
    processed_indices_path = '/opt/airflow/dags/Utils/data/processed_indices.csv'
    pd.DataFrame({'index': processed_indices}).to_csv(processed_indices_path, index=False)
