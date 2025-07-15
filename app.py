import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Grey Transit Matcher", layout="wide")
st.title("🚂 Grey Transit Data Processor")

st.subheader("1. Upload 3 Import Files and 3 Export Files")

# Upload import files
im_10 = st.file_uploader("Upload Import File Q1", type="csv", key="im10")
im_11 = st.file_uploader("Upload Import File Q2", type="csv", key="im11")
im_12 = st.file_uploader("Upload Import File Q3", type="csv", key="im12")

# Upload export files
ex_10 = st.file_uploader("Upload Export File Q1", type="csv", key="ex10")
ex_11 = st.file_uploader("Upload Export File Q2", type="csv", key="ex11")
ex_12 = st.file_uploader("Upload Export File Q3", type="csv", key="ex12")

# Proceed if all files are uploaded
if all([im_10, im_11, im_12, ex_10, ex_11, ex_12]):
    # try:
    # Read all files
    im_10_df = pd.read_csv(im_10)
    im_11_df = pd.read_csv(im_11)
    im_12_df = pd.read_csv(im_12)
    ex_10_df = pd.read_csv(ex_10)
    ex_11_df = pd.read_csv(ex_11)
    ex_12_df = pd.read_csv(ex_12)

    # Intersection and concat for export
    common_columns_ex = ex_10_df.columns.intersection(ex_11_df.columns).intersection(ex_12_df.columns)
    export_all = pd.concat([ex_10_df[common_columns_ex], ex_11_df[common_columns_ex], ex_12_df[common_columns_ex]], ignore_index=True)

    # Intersection and concat for import
    common_columns_im = im_10_df.columns.intersection(im_11_df.columns).intersection(im_12_df.columns)
    import_all = pd.concat([im_10_df[common_columns_im], im_11_df[common_columns_im], im_12_df[common_columns_im]], ignore_index=True)

    # --- Continue previous transformation ---
    ex_12_df.rename(columns={'Станция назначения.1': 'Станция отправления',
                         'Наименование станции назначения.1':'Наименование станции отправления'}, inplace=True)

    ex_11_df.rename(columns = {"Наименование станции назнаения": "Наименование станции назначения"}, inplace=True)


    common_columns_ex = ex_10_df.columns.intersection(ex_11_df.columns).intersection(ex_12_df.columns)
    export_all = pd.concat([ex_10_df[common_columns_ex], ex_11_df[common_columns_ex], ex_12_df[common_columns_ex]], ignore_index=True)


    common_columns_im = im_10_df.columns.intersection(im_11_df.columns).intersection(im_12_df.columns)
    import_all = pd.concat([im_10_df[common_columns_im], im_11_df[common_columns_im], im_12_df[common_columns_im]], ignore_index=True)
    import_all = import_all[import_all['Наименование ГП'].notna()]
    import_all["Наименование ГП"] = import_all["Наименование ГП"].apply(lambda x: x.replace('ТОВАРИЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "QAZEXPOCENTRE - PIPE"', 'ТОО "QAZEXPOCENTRE - PIPE"'))



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

    print((export_df[['Номер вагона_y', 'Наименование ГО', 'Станция отправления', "Вес на вагон (кг)_y"]]).shape, (import_df[['Номер вагона_x', 'Наименование ГП', 'Станция назначения', "Вес на вагон (кг)_x"]]).shape)

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
    def convert_df(df):
        output = BytesIO()
        df.to_csv(output, index=False)
        return output.getvalue()

    csv = convert_df(grey_transit)
    st.download_button(
        label="📥 Download Grey Transit CSV",
        data=csv,
        file_name="grey_transit_quarter_2024_Q4.csv",
        mime="text/csv",
    )

    # except Exception as e:
    #     st.error(f"⚠️ Error while processing files: {e}")
else:
    st.info("👆 Please upload all 6 files to continue.")
