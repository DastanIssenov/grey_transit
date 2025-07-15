import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile

USER_CREDENTIALS = {
    "ktzh": "ktzhpass"
}

def login():
    st.title("🔒 Login Required")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if USER_CREDENTIALS.get(username) == password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Grey Transit')
    output.seek(0)
    return output

def read_single_csv_from_zip(uploaded_file):
    with zipfile.ZipFile(uploaded_file) as z:
        # Get list of files that are not hidden/macOS junk
        valid_files = [f for f in z.namelist() if f.endswith('.csv') and '__MACOSX' not in f and not f.startswith('.')]
        if len(valid_files) != 1:
            raise ValueError(f"Expected 1 CSV file, found {len(valid_files)}: {valid_files}")
        return pd.read_csv(z.open(valid_files[0]))

st.set_page_config(page_title="Grey Transit Matcher", layout="wide")
st.title("🚂 Grey Transit Data Processor")

st.subheader("1. Upload 3 Import and 3 Export `.csv.zip` Files")

# Upload zipped import files
im_10 = st.file_uploader("Upload Import File Q1 (.csv.zip)", type="zip", key="im10")
im_11 = st.file_uploader("Upload Import File Q2 (.csv.zip)", type="zip", key="im11")
im_12 = st.file_uploader("Upload Import File Q3 (.csv.zip)", type="zip", key="im12")

# Upload zipped export files
ex_10 = st.file_uploader("Upload Export File Q1 (.csv.zip)", type="zip", key="ex10")
ex_11 = st.file_uploader("Upload Export File Q2 (.csv.zip)", type="zip", key="ex11")
ex_12 = st.file_uploader("Upload Export File Q3 (.csv.zip)", type="zip", key="ex12")

# Proceed if all files are uploaded
if all([im_10, im_11, im_12, ex_10, ex_11, ex_12]):

    # Read zipped CSVs
    im_10_df = read_single_csv_from_zip(im_10)
    im_11_df = read_single_csv_from_zip(im_11)
    im_12_df = read_single_csv_from_zip(im_12)
    ex_10_df = read_single_csv_from_zip(ex_10)
    ex_11_df = read_single_csv_from_zip(ex_11)
    ex_12_df = read_single_csv_from_zip(ex_12)

    # Intersection and concat for export
    common_columns_ex = ex_10_df.columns.intersection(ex_11_df.columns).intersection(ex_12_df.columns)
    export_all = pd.concat([ex_10_df[common_columns_ex], ex_11_df[common_columns_ex], ex_12_df[common_columns_ex]], ignore_index=True)

    # Intersection and concat for import
    common_columns_im = im_10_df.columns.intersection(im_11_df.columns).intersection(im_12_df.columns)
    import_all = pd.concat([im_10_df[common_columns_im], im_11_df[common_columns_im], im_12_df[common_columns_im]], ignore_index=True)

    # --- Continue previous transformation ---
    


    common_columns_ex = ex_10_df.columns.intersection(ex_11_df.columns).intersection(ex_12_df.columns)
    export_all = pd.concat([ex_10_df[common_columns_ex], ex_11_df[common_columns_ex], ex_12_df[common_columns_ex]], ignore_index=True)


    common_columns_im = im_10_df.columns.intersection(im_11_df.columns).intersection(im_12_df.columns)
    import_all = pd.concat([im_10_df[common_columns_im], im_11_df[common_columns_im], im_12_df[common_columns_im]], ignore_index=True)

    import_all = import_all[import_all['Наименование ГП'].notna()]
    export_all = export_all[export_all['Наименование ГП'].notna()]
    import_all["Наименование ГП"] = import_all["Наименование ГП"].apply(lambda x: x.replace('ТОВАРИЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "QAZEXPOCENTRE - PIPE"', 'ТОО "QAZEXPOCENTRE - PIPE"'))
    export_all["Наименование ГП"] = export_all["Наименование ГП"].apply(lambda x: x.replace('ТОВАРИЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "QAZEXPOCENTRE - PIPE"', 'ТОО "QAZEXPOCENTRE - PIPE"'))



    import_df = import_all.copy()
    export_df = export_all.copy()


    import_df.rename(columns={"Вес на вагон (кг)": "Вес на вагон (кг)_x",
                                "Код груза": "Код груза_x",
                                "Номер вагона\\конт": "Номер вагона_x",
                                "Наименование станции назнаения": "Наименование станции назначения"}, inplace=True)

    export_df.rename(columns={"Вес на вагон (кг)": "Вес на вагон (кг)_y",
                                "Код груза": "Код груза_y",
                                "Номер вагона\\конт": "Номер вагона_y"}, inplace = True)


    import_df = import_df[['Документ', 'Наименование ГО', 'Наименование ГП', 'Наименование страны отправления',
                            "Наименование станции отправления", "Станция отправления", "Наименование страны назначения",
                            "Наименование станции назначения", 'Станция назначения', "Номер вагона_x",
                            'Общий вес по документу (кг)', 'Вес на вагон (кг)_x', 'Код груза_x', 'Наименование груза',
                            'Код грузополучателя', 'Дата прибытия', 'Взыскано по прибытию (последние 2 знака тиыны)']]

    export_df = export_df[['Документ', "Наименование ГО", "Наименование ГП", 'Наименование страны отправления',
                            "Наименование станции отправления", "Станция отправления", "Наименование страны назначения",
                            "Наименование станции назначения", 'Станция назначения', "Номер вагона_y",
                            'Общий вес по документу (кг)', 'Вес на вагон (кг)_y', 'Код груза_y', 'Наименование груза',
                            'Код грузоотправителя', 'Дата отправления',
                            'Взыскано при отправления  (последние 2 знака тиыны)']]



    import_df['Дата прибытия'] = pd.to_datetime(import_df['Дата прибытия'], dayfirst=True, errors='coerce')
    export_df['Дата отправления'] = pd.to_datetime(export_df['Дата отправления'], dayfirst=True, errors='coerce')

    merged = pd.merge(
        import_df,
        export_df,
        left_on=['Номер вагона_x', 'Наименование ГП', 'Станция назначения', "Вес на вагон (кг)_x"],
        right_on=['Номер вагона_y', 'Наименование ГО', 'Станция отправления', "Вес на вагон (кг)_y"],
        how='inner'
    )

    merged = merged[merged['Наименование страны отправления_x'] != merged['Наименование страны назначения_y']]
    merged = merged[merged['Дата прибытия'] <= merged['Дата отправления']]
    merged = merged[merged["Вес на вагон (кг)_x"] != 0]

    grey_transit = merged.copy()

    st.success(f"✅ Successfully matched {len(grey_transit)} rows.")

    st.subheader("2. Preview of Merged Grey Transit Data")
    st.dataframe(grey_transit, use_container_width=True)

    st.subheader("3. Download Result")
    
    excel_file = convert_df_to_excel(grey_transit)
    st.download_button(
        label="📥 Download Grey Transit Excel",
        data=excel_file,
        file_name="grey_transit_quarter_2024_Q4.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # except Exception as e:
    #     st.error(f"⚠️ Error while processing files: {e}")
else:
    st.info("👆 Please upload all 6 files to continue.")
