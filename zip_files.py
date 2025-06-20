import zipfile, os

FOLDER_TO_ZIP = 'app_code/lambda_functions/'

for file in os.listdir(FOLDER_TO_ZIP):
    print(file)
    if file.endswith('.py'):
        with zipfile.ZipFile(FOLDER_TO_ZIP +'/'+file.split('.')[0]+".zip",'w') as zip_file:
            zip_file.write(FOLDER_TO_ZIP + file)

