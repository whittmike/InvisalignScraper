# ---------------------------------------- [ LIBRARY IMPORT ] -----
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
import os
import pandas as pd
import time as tm
import re

# ---------------------------------------- [ DEFINE PRIMARY VARS ] -----
# --- set working directory
# --- os.chdir('c:/Users/mwhittlesey/Desktop/SELENIUM_PY')

# --- read csv
zip_lst = [98901, 55555, 90201, 99732, 83686, 83646]

# --- configure options for chrome driver
options = Options()
options.headless = False

# --- declare lst to append to in function
provider_lst = []

# ---------------------------------------- [ FUNCTIONS ] -----
# -- --- ---- function opens web page ---- --- --
def open_page(zip_code):
            
    # -- find primary webpage
    driver.get(f"""https://www.invisalign.com/get-started/find-a-doctor?zip={zip_code}""")
    
    # -- define check to continue
    check_path = []
    obj_alert_message = ''
    continue_loop = 1
    try_i = 1
    
    # -- --- initial check to see if alert or valid 
    while continue_loop == 1:
        # -- make sure there are no alerts
        try:        
            obj_alert_message = driver.switch_to.alert.text
            if obj_alert_message:
                driver.switch_to.alert.accept()
                driver.close()
                continue_loop = 0
                print(f"""{obj_alert_message} for zip code {zip_code}""")
                break
        except:
            # - check to see if any results
            try:
                check_path = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "search-result-desc", " " ))]')
                if check_path:
                    continue_loop = 0
                    try:
                        driver.find_elements_by_xpath('//*[(@id = "epdsubmit")]')[0].click()
                        break
                    except:
                        break
            except:
                 print(f"""try {try_i} for zip {zip_code}""")
                 try_i += 1
                 tm.sleep(.5)
                 # if loop has gone on too long
                 if(try_i > 10):
                     continue_loop = 0
                     break
            # - final except
            print(f"""try {try_i} for zip {zip_code}""")
            try_i += 1
            tm.sleep(.5)
            # - if loop has gone on too long
            if(try_i > 10):
                continue_loop = 0
                driver.close()
                break
            
    # -- proceed through return scenarios
    if check_path:
        lst_out = [zip_code, check_path[0].text, 1]
    elif obj_alert_message:
        lst_out = [zip_code, obj_alert_message, 0]
    else:
        lst_out = [zip_code, 'time out', 0]
    
    # -- return required output
    return(lst_out)

# -- --- ---- function to get info from indidivual providers ---- --- --
def get_provider_info(x_str, open_res_lst):
    
    # -- establish patterns and constants
    pattern_type = re.compile("(general dentist|orthodontist)")
    pattern_tel = re.compile("^.*(?<=tel: )(.*)$")
    
    # -- dictionary to append to
    tmp_dict = {'search_zip':open_res_lst[0],'search_message':open_res_lst[1]}
    provider_key = '-' + str(open_res_lst[0]) + '-'
    
    # -- gather name
    for i in range(len(x_str)):
        if(pattern_type.match(x_str[i].strip())):
            try:
                tmp_dict['provider_name'] = ' '.join(x_str[0:i]).strip()
                provider_key = provider_key + ' '.join(x_str[0:i]).strip() + '-'
            except:
                tmp_dict['provider_name'] = None
                provider_key = provider_key + ' ' + '-'
    # -- gather type
    for i in range(len(x_str)):
        if(pattern_type.match(x_str[i].strip())):
            try:
                tmp_dict['provider_type'] = x_str[i]
                provider_key = provider_key + x_str[i] + '-'
            except:
                tmp_dict['provider_type'] = None
                provider_key = provider_key + ' ' + '-'
    
    # -- gather telephone
    for i in range(len(x_str)):
        if(pattern_tel.match(x_str[i].strip())):
            try:
                tmp_dict['provider_tel'] = re.sub(r'[^0-9]', '',x_str[i])
                provider_key = provider_key + re.sub(r'[^0-9]', '',x_str[i]) + '-'
            except:
                tmp_dict['provider_tel'] = None
                provider_key = provider_key + ' ' + '-'
             
    # -- gather address
    for i in range(len(x_str)):
        if(pattern_type.match(x_str[i].strip())):
           try: 
               tmp_dict['provider_street'] = x_str[i+1].strip()
               provider_key = provider_key + x_str[i+1].strip() + '-'
           except:
               tmp_dict['provider_street'] = None
               provider_key = provider_key + ' ' + '-'
    
    # -- gather state_zip
    for i in range(len(x_str)):
        if(pattern_tel.match(x_str[i].strip())):
            try:
                tmp_dict['provider_state_zip'] = x_str[i-1].strip()
                provider_key = provider_key + x_str[i-1].strip() + '-'
            except:
                tmp_dict['provider_state_zip'] = None
                provider_key = provider_key + ' ' + '-'
    
    # -- establish provider key
    tmp_dict['provider_key'] = provider_key
    
    # -- return final output
    return(tmp_dict)

# -- --- ---- function cycles through valid page ---- --- --
def cycle_page():
    
    # -- wait for repeat
    tm.sleep(.5)
    dent_lst = []
    # -- commence
    try:
        dent_lst = driver.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "name-details", " " ))]')
        # - if list is gathered
        if dent_lst:
            # go through dent_lst and append
            for i in range(len(dent_lst)):
                try:
                    # declare tmp lst to append
                    tmp_dict = get_provider_info(dent_lst[i].text.lower().split('\n'), open_res_lst)
                    # make sure provider key is not present
                    if(tmp_dict['provider_key'] not in [i['provider_key'] for i in provider_lst]):
                        provider_lst.append(tmp_dict)
                except:
                    print('bad list')
            # purge dent list
            dent_lst = []
            # try to go to next page
            try: 
                next_button = driver.find_elements_by_link_text('Next')[1]
                if next_button:
                    next_button.click()
                    cycle_page()
            except:
                if [i.text for i in driver.find_elements_by_xpath('//*[(@id = "dlResultsHeaderLabel")]') if i.text.lower() == '1 page']:
                    return(False)
                elif driver.find_elements_by_link_text('First'):
                    return(False)
                else:
                    cycle_page()
    except:
        return(False)

# ---------------------------------------- [ LOOP THROUGH ZIP CODES ] -----
for i in range(len(zip_lst)):
    
    # --- declare zip code
    zip_code = zip_lst[i]
        
    # -- open driver
    driver = webdriver.Chrome('C:/drivers/chromedriver.exe', options=options)
    
    # --- test web page
    open_res_lst = open_page(zip_code)
    # provider_count = int(re.search('showing (\d+)', open_res_lst[1], re.IGNORECASE).group(1))
    
    # --- check if browser is still open
    try:
        driver.title
        driver_open = True
    except WebDriverException:
        driver_open = False
    
    # --- quick rest
    tm.sleep(.5)
    
    # --- check if driver is open
    if driver_open:
        try:
            cycle_page()
            print(f'good cycle {zip_code}')
            driver.close()
        except:
            print(f'bad cycle {zip_code}')
            driver.close()
    else:
        print(f'bad cycle {zip_code}')

# ---------------------------------------- [ EXPORT ] -----
# --- export function
def df_dict_xl(df_dict, xl_file_name, col_buff = 2):
    
    # --- function returns length of columns to set length to
    def get_col_len(dfx):
        # define list to append to
        col_len_lst = []
        # declare list of column names
        col_lst = [col for col in dfx.columns]
        # obtain max char count for each column
        for i in range(len(col_lst)):
            col_len_lst.append(max(list(dfx[col_lst[i]].astype(str).str.len()) + [len(col_lst[i]) * 1.25]))
        # return col length list
        return(col_len_lst)
    
    # --- define excel writer
    writer = pd.ExcelWriter(xl_file_name, engine='xlsxwriter')
    
    # --- itterate to find list of sheet names and data found in dictionary
    sheet_name_lst = [key for key in df_dict]
    df_lst = [df_dict.get(i) for i in sheet_name_lst]
    
    # --- loop through list of sheet names to get custom col width
    for i in range(len(sheet_name_lst)):
        # save data to work sheet
        df_lst[i].to_excel(writer, sheet_name = sheet_name_lst[i], index = False)
        # define sheet to modify column lengths
        worksheet = writer.sheets[sheet_name_lst[i]]
        # define col lengths for each col in data frame
        df_col_len = get_col_len(df_lst[i])
        # loop through columns and modify column length
        for i in range(len(df_col_len)):
            worksheet.set_column(i, i, (df_col_len[i] + col_buff))

    # --- save workbook
    writer.save()

# --- export data in usable format
df_dict = {'PROVIDER_LIST': pd.DataFrame(provider_lst)}
df_dict_xl(df_dict, 'c:/Users/mwhittlesey/Desktop/provider_lst.xlsx', 0)