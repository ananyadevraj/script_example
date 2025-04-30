
#%% package imports 

import pandas as pd
import pickle
import os
import numpy as np
from enum import Enum 
import streamlit as st

#%%

class InputIds(Enum):
    '''
    Uses enum to assign the Excel sheets uploaded into the Streamlit app to IDs containing info about the sheet.
    Specific IDs removed for privacy purposes.
	'''

# mapping ids to display names 
needed_sheets_dict = {
    # repeating this to map all Excel IDs to display names 
    InputIds.example: "example",
    
}

#bucket definitions dictionary - removed for privacy purposes, repeated this to map all Excel sheets to 
#program names 

bucket_definitions = {
    "bucket": InputIds.example
}


#%%
#extracted the necessary ID columns from the sheet 
id_cols = ["list_of_id_colums"]

def run_from_script(file_name_mapper: pd.DataFrame):
    def get_df_from_id(id):
        file = file_name_mapper.at[id.value, "file"]
        return pd.read_excel(file)
    
    #create dict to store program dataframes 
    program_dataframes = {}
    
    uploaded_ids = file_name_mapper.index.tolist()
    
    for id_enum in InputIds:
        if id_enum.value in file_name_mapper.index:
            try: 
                df = get_df_from_id(id_enum)
                program_name = needed_sheets_dict[id_enum]
                df.name = program_name 
                program_dataframes[program_name] = df 
                st.success(f"Successfully loaded: {program_name}")
            except Exception as e: 
                st.error(f"Error reading file for {needed_sheets_dict[id_enum]}: {e}")
    if not program_dataframes:
        st.warning("No files were successfully loaded. Please upload at least one valid Excel file.")
        return pd.DataFrame(), {}

    #extracting id columns
    id_col_dataframes = get_id_cols(program_dataframes, id_cols)
    
    #apply one-hot encoding for programs 
    one_hot_dataframes = one_hot(id_col_dataframes)
    
    #create bucket dataframes 
    bucket_dataframes = create_bucket_dataframes(one_hot_dataframes, bucket_definitions)
    
    #make master list 
    
    master_list, combined_dfs = concat_master(bucket_dataframes, id_cols)
    
    if not master_list.empty:
        #reorder columns 
        master_list = reorder(master_list)
        
        #handle duplicates 
        master_list = handle_duplicates(master_list)
        
        #dual enrollment 
        master_list = mark_dually_enrolled(master_list)
        
        #return processed data 
    
    return master_list, bucket_dataframes 

#%% Extracting ID columns 
def get_id_cols(program_dataframes, id_cols):
    """ extract id columns from each program dataframe """
    
    id_col_dataframes = {}
    for program_name, dataframe in program_dataframes.items():
        id_col_dataframes[program_name] = dataframe[id_cols]
        id_col_dataframes[program_name].name = program_name
    return id_col_dataframes


#%% one-hot encoding  for programs 

def one_hot(id_col_dataframes):
    """ create one-hot encoding for program enrollment """
    program_names = list(id_col_dataframes.keys())
    
    for program_name, dataframe in id_col_dataframes.items():
        for name in program_names: 
            if dataframe.name == name: 
                dataframe[f"is_{name}"]= 1
            else: 
                dataframe[f"is_{name}"] = 0
    return id_col_dataframes

#%% creating the bucket dataframes 

def create_bucket_dataframes(one_hot_dataframes, bucket_definitions):
    """
    creates dataframe for each bucket by combining program dataframes 

    """
    bucket_dataframes = {}
    
    program_to_bucket = {}
    
    #reverse mapping from program names to bucket names
    for bucket_name, program_ids in bucket_definitions.items():
        for program_id in program_ids: 
            program_name = needed_sheets_dict[program_id]
            program_to_bucket[program_name] = bucket_name
    #initializing bucket dataframes
    
    for bucket_name in bucket_definitions.keys():
        bucket_dataframes[bucket_name] = []
    
    #assigning programs to buckets 
    for program_name, dataframe in one_hot_dataframes.items():
        bucket_name = program_to_bucket.get(program_name)
        if bucket_name:
            if bucket_name not in bucket_dataframes:
                bucket_dataframes[bucket_name] = []
            bucket_dataframes[bucket_name].append(dataframe)

    #concat programs within each bucket 
    final_bucket_dataframes = {}

    for bucket_name, dfs in list(bucket_dataframes.items()):
        if dfs: 
            bucket_df = pd.concat(dfs, ignore_index = True)
            bucket_df[f"is_bucket_{bucket_name}"] = 1 
            final_bucket_dataframes[bucket_name] = bucket_df

    return final_bucket_dataframes
            

#%% CONCAT BUCKETS TO MASTER

def concat_master(bucket_dataframes, id_cols):
    """concat all bucket dataframes into a master list"""
    combined_dfs= []
    
    for bucket_name, dataframe in bucket_dataframes.items():
        combined_dfs.append(dataframe)
    if combined_dfs:
        master_list = pd.concat(combined_dfs, ignore_index = True)
    else: 
        master_list = pd.DataFrame(columns = id_cols)

    return master_list, combined_dfs

#%% REORDERING COLUMNS 
    
def reorder(master_list):
    
    #all columns 
    
    all_columns= master_list.columns
    
    program_indicators = [col for col in all_columns if col.startswith('is_') and not col.startswith('is_bucket_')]
    bucket_indicators = [col for col in all_columns if col.startswith('is_bucket_')]
    
    # reordering
    
    final_column_order = id_cols + sorted(program_indicators) + sorted(bucket_indicators)

    # reordering, fill na with 0
    master_list = master_list[final_column_order].fillna(0)     
    
    return master_list


#%% check duplicates 

def merge_rows(group):
    """merge duplicate rows according to specified rules:
        ids get matched 
        if there is a row where one id is missing but clients have the same name and birthday
        then merge them and update the id with the non-null value
        """
    merged_row = {}
    
    # indicator columns 
    program_indicators = [col for col in group.columns if col.startswith('is_') and not col.startswith('is_bucket_')]
    bucket_indicators = [col for col in group.columns if col.startswith('is_bucket_')]
    
    for column in group.columns:
        if column in program_indicators + bucket_indicators:
            # prioritize 1 over 0 for program
            merged_row[column] = group[column].max()
        elif column in ["id_columns_1_to_4"]:
            # take the non zero value for 
            non_null_values = group[column][group[column] != 0]
            merged_row[column] = non_null_values.iloc[0] if not non_null_values.empty else 0
        else:
            # take non-null values 
            non_null_values = group[column].dropna()
            merged_row[column] = non_null_values.iloc[0] if not non_null_values.empty else None
    
    return pd.Series(merged_row)
#%% 

def handle_duplicates(master_list):
    """duplicate rows"""
    
    # converting name to lowercase
    if 'Name' in master_list.columns:
        master_list["Name"] = master_list["Name"].str.lower()
    
    # id duplicates
    id_duplicates = []
    if 'ID' in master_list.columns:
        # non-zero  ids
        valid_id = master_list[master_list["ID"] != 0]
        if not valid_id.empty:
            id_groups = valid_id.groupby("ID")
            
            for id, group in id_groups:
                if len(group) > 1:
                    id_duplicates.append(merge_rows(group))
                    # remove duplicates to add back later 
                    master_list = master_list[~master_list["ID"].isin([id])]
    
    # name/dob duplicates
    name_dob_duplicates = []
    if 'Name' in master_list.columns and 'DoB' in master_list.columns:
        # convert dob to string
        master_list['DoB_str'] = master_list['DoB'].astype(str)
        
        # group by name and dob 
        name_dob_groups = master_list.groupby(["Name", "DoB_str"])
        
        for (name, dob_str), group in name_dob_groups:
            if len(group) > 1:
                # check if there is missing and non-missing ids
                has_missing_id = (group['ID'] == 0).any() if 'ID' in group.columns else False
                has_valid_id = (group['ID'] != 0).any() if 'ID' in group.columns else False
                
                if has_missing_id and has_valid_id:
                    group = group.drop(columns=['DoB_str'])
                    name_dob_duplicates.append(merge_rows(group))
                    
                    # remove duplicates to add back later
                    indices_to_remove = group.index
                    master_list = master_list.drop(indices_to_remove)
        
        # remove temporary dob column 
        master_list = master_list.drop(columns=['DoB_str'])
    
    # Aadd back merged rows 
    all_duplicates = id_duplicates + name_dob_duplicates
    if all_duplicates:
        master_list = pd.concat([master_list, pd.DataFrame(all_duplicates)], ignore_index=True)
    
    return master_list

#%% 
#dual enrollment 

def mark_dually_enrolled(master_list):
    """find clients enrolled in multiple buckets"""
    # get indicators
    bucket_indicators = [col for col in master_list.columns if col.startswith('is_bucket_')]
    
    # add dual enrollment 
    if bucket_indicators:
        master_list["DuallyEnrolled"] = (master_list[bucket_indicators].sum(axis=1) > 1).astype(int)
    
    return master_list
#%% EXPORTING TO EXCEL 

def export_multiple_dfs_to_excel(master_list, bucket_dataframes, filename='master_list.xlsx'):
    """
    export all dataframes to an excel file 
   
    """
    #add master list to bucket dataframes 
    export_dataframes = bucket_dataframes.copy()
    export_dataframes["master_list"] = master_list
 
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # write each DataFrame to a different sheet
        for sheet_name, dataframe in export_dataframes.items():
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
            
    st.success(f"DataFrames successfully exported to {filename}")
    return filename 
