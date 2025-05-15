import gspread
from oauth2client.service_account import ServiceAccountCredentials

def save_to_gsheet(df, sheet_name="ShopeeAutoSourcing"):
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name).sheet1
    sheet.clear()
    sheet.insert_row(df.columns.tolist(), 1)
    for i, row in df.iterrows():
        sheet.insert_row(row.tolist(), i + 2)
