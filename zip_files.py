import zipfile, os

FOLDER_TO_ZIP = 'app_code/lambda_functions/'
files_to_zip = os.listdir(FOLDER_TO_ZIP)
os.chdir(FOLDER_TO_ZIP)
for file in files_to_zip:
    if file.endswith('.py'):
        with zipfile.ZipFile(file.split('.')[0]+".zip",'w') as zip_file:
            zip_file.write(file)

