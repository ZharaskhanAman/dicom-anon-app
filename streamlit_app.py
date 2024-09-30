import streamlit as st
import pydicom
from io import BytesIO
import pandas as pd
import zipfile

def anonymize_dicom(ds):
    tags_to_anonymize = ['PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex',
                         'OtherPatientIDs', 'OtherPatientNames', 'PatientAge',
                         'PatientSize', 'PatientWeight']
    anonymized = False
    for tag in tags_to_anonymize:
        if tag in ds and ds.data_element(tag).value:
            ds.data_element(tag).value = ''
            anonymized = True
    return ds, anonymized

st.title("🕵️‍♀️ Dicom анонимайзер")

uploaded_files = st.file_uploader("Загрузить файлы", type=["dcm"], accept_multiple_files=True)

# Initialize a list to store file data for the dataframe
file_data = {}
expander = st.expander(label="Подробнее", expanded=False)

if uploaded_files:
    for index, uploaded_file in enumerate(uploaded_files):
        bytes_data = uploaded_file.read()

        # Read DICOM file from bytes
        ds = pydicom.dcmread(BytesIO(bytes_data))

        # Anonymize the DICOM data
        ds, anonymized = anonymize_dicom(ds)

        output = BytesIO()
        ds.save_as(output)
        output.seek(0)  # Move the cursor to the beginning of the BytesIO object
        file_data[index] = output



        expander.image(ds.pixel_array, caption=uploaded_file.name, clamp=True, channels="GRAY")
        
        expander.download_button(
            label=f"Скачать анонимизированный { uploaded_file.name}",
                data=file_data[index],
                file_name="anonymized_" + uploaded_file.name,
                mime="application/octet-stream",
                key=index,
        )

    # Create a zip file
    zip_file = BytesIO()
    with zipfile.ZipFile(zip_file, 'w') as zf:
        for index, file in file_data.items():
            # Add each file to the zip
            zf.writestr(f'anonymized_{uploaded_files[index].name}', file.getvalue())

    # Add a download button for the zip file
    st.download_button(
        label='Скачать все анонимизированные файлы',
        data=zip_file.getvalue(),
        file_name=f'anonymized.zip',
        mime='application/zip'
    )

