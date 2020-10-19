import imaplib
import mailparser
import xlsxwriter

# login credentials
sender_email = "truongjesse51@gmail.com"
password = "rIbImBLeNu"

# Defining a imaplib var and logining into the email with the credentials
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(sender_email, password)

# Getting all the emails in the Inbox
result, cnt = mail.select('Inbox')

cnt = int(cnt[0])
location = "emails.xlsx"
workbook = xlsxwriter.Workbook(location)
row = 0
col = 0

# Writing first row
sheet1 = workbook._add_sheet('Sheet 1')
sheet1.write(0, 0, 'Subject')
sheet1.write(0, 1, 'Sender')
sheet1.write(0, 2, 'Receiver')
sheet1.write(0, 3, 'Body')
sheet1.write(0, 4, 'Attachment')

# XLS formating
cell_wrap = workbook.add_format()
cell_wrap.set_text_wrap()
cell_wrap.set_align('top')
cell_wrap.set_align('left')
row = row + 1
sheet1.set_column('A:C', 25)
sheet1.set_column('D:E', 50)
sheet1.set_default_row(50)
sheet1.set_row(0, 25)

# Writing all emails in inbox in the email.xls
for i in range(cnt, 0, -1):
    res, msg = mail.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            a = mailparser.parse_from_bytes(response[1])
            sheet1.write(row, 0, a.subject, cell_wrap)
            sheet1.write(row, 1, str(a.from_), cell_wrap)
            sheet1.write(row, 2, str(a.to), cell_wrap)
            sheet1.write(row, 3, str(a.text_plain), cell_wrap)
            sheet1.write(row, 4, str(a.attachments), cell_wrap)
            row = row + 1

workbook.close()
# Note to self, if you get an xlsxwriter.exceptions.FileCreateError: [Errno 13] Permission denied: 'emails.xlsx'
# error, close the excel file
