import os
from dotenv import load_dotenv
from baserowapi import Baserow, Table, Filter
from baserowapi.models.field import Field

# Load environment variables
load_dotenv()

# Read variables from the environment
BASEROW_URL = os.getenv("BASEROW_URL")
BASEROW_TOKEN = os.getenv("BASEROW_TOKEN")

# Check if environment variables are set
if not all([BASEROW_URL, BASEROW_TOKEN]):
    raise EnvironmentError("Both BASEROW_URL and BASEROW_TOKEN must be set in the .env file.")

# import requests

# url = "https://api.baserow.io/api/user-files/upload-file/"
# headers = {
#     "Authorization": "Token TXpzDVBsrZjgMDeOiaDlz0ryiUEnFPmm"
# }

# with open('fixie.jpg', 'rb') as f:
    
#     response = requests.post(url, headers=headers, files={"file": f})

# print(response.text)

# '{"size":1496139,"mime_type":"image/jpeg","is_image":true,"image_width":4758,"image_height":3172,"uploaded_at":"2023-10-05T17:54:43.486367Z","url":"https://baserow-media.ams3.digitaloceanspaces.com/user_files/eqHCVDQ2ZxLxW4quC4U1sgNpsa95Mdlv_f94451b699bb744e2beac065874201fa5201eb75ceb9961d779e72fcbf55f1d7.jpg","thumbnails":{"tiny":{"url":"https://baserow-media.ams3.digitaloceanspaces.com/thumbnails/tiny/eqHCVDQ2ZxLxW4quC4U1sgNpsa95Mdlv_f94451b699bb744e2beac065874201fa5201eb75ceb9961d779e72fcbf55f1d7.jpg","width":null,"height":21},"small":{"url":"https://baserow-media.ams3.digitaloceanspaces.com/thumbnails/small/eqHCVDQ2ZxLxW4quC4U1sgNpsa95Mdlv_f94451b699bb744e2beac065874201fa5201eb75ceb9961d779e72fcbf55f1d7.jpg","width":48,"height":48},"card_cover":{"url":"https://baserow-media.ams3.digitaloceanspaces.com/thumbnails/card_cover/eqHCVDQ2ZxLxW4quC4U1sgNpsa95Mdlv_f94451b699bb744e2beac065874201fa5201eb75ceb9961d779e72fcbf55f1d7.jpg","width":300,"height":160}},"name":"eqHCVDQ2ZxLxW4quC4U1sgNpsa95Mdlv_f94451b699bb744e2beac065874201fa5201eb75ceb9961d779e72fcbf55f1d7.jpg","original_name":"fixie.jpg"}'


# TESTVALUES = {
#     # 'Name': None,
#     # 'Notes': None,
#     # 'Active': False,
#     # 'myNumber': None,
#     # 'myRating': 0,
#     # 'myPhone': None,
#     # 'US Date Time': None,
#     # 'EU Date': '1999-12-30',
#     # 'Last modified': '',
#     # 'Created on': '',
#     # 'myCount': '',
#     # 'MyLookup': '',
#     # 'myURL': None,
#     # 'myEmail': None,
#     'MyFileField': '',
#     # 'mySingleSelect': None,
#     # 'myMultipleSelect': None,
#     # 'MyTableLink': None,
#     # 'myCollaborators': None
# }



# def testField(fieldname=None, fieldvalue=None):
#     # fetch a row, print value, update value, print value again
#     field_object = table.fields[fieldname]
#     print(f"{field_object.field_data}")
#     fetched_row = table.get_rows(
#         include=[fieldname], 
#         return_single=True
#     )
#     print(f"{fetched_row} updating {fieldname}: {fetched_row[fieldname]} -> {fieldvalue}")
#     print(fetched_row.content)
#     if not fetched_row.values[fieldname].is_read_only:
#         print(fetched_row[fieldname])
#         # fetched_row[fieldname] = fieldvalue
#         # fetched_row.update()
#     print('==========')
#     # print(fetched_row.values[fieldname].formatted_date)
#     # fetched_row[fieldname] = fieldvalue
#     # print(fetched_row[fieldname])
#     # fetched_row.update()
#     return fetched_row

# # baserow client
db = Baserow(url='https://api.baserow.io',token='TXpzDVBsrZjgMDeOiaDlz0ryiUEnFPmm', logging_level='DEBUG')
print(db)


# # get table
table_id = 198958
table = db.get_table(table_id)


# # working with TextField
# print(table.fields['Name'].name) 
# print(table.fields['Name'].type)
# print(table.fields['Name'].text_default)
# print(table.fields['Name'].field_data)

# # working with filefield
single_row = table.get_rows(include=['myFileField','Name'], return_single=True, filters=[Filter('Name','Ema')])
print(single_row.content)
print(table.fields['myFileField'].field_data)
download_result = single_row.values['myFileField'].download_files('/tmp')
print(download_result)
# single_row.values['myFileField'].upload_file_to_server('fixie.jpg')
# single_row.values['myFileField'].upload_file_to_server(url='https://www.jimwitte.net/bison.jpg', file_path='fixie.jpg')
# print(single_row['myFileField'])
# single_row.update()

# single_row.values['myFileField']

# print(single_row.values['MyFileField'].value)
# single_row['MyFileField'] = [{'url': 'https://baserow-media.ams3.digitaloceanspaces.com/user_files/xC64AcZManNeeBfKRaD4n3rCTggFQ4yY_3162f80e9db2a1c7229ce55d6dbc8c4496936f66c7df5136d24e8f9973cf64bc.txt', 'thumbnails': None, 'visible_name': 'test2.txt', 'name': 'xC64AcZManNeeBfKRaD4n3rCTggFQ4yY_3162f80e9db2a1c7229ce55d6dbc8c4496936f66c7df5136d24e8f9973cf64bc.txt', 'size': 26, 'mime_type': 'text/plain', 'is_image': False, 'image_width': None, 'image_height': None, 'uploaded_at': '2023-09-22T19:49:03.634193+00:00'}]
# single_row.values['MyFileField'].upload_file('/home/jwitte/CodeProjects/baserow/fixie.jpg')
# single_row['MyFileField'] = [{'url': 'https://baserow-media.ams3.digitaloceanspaces.com/user_files/xC64AcZManNeeBfKRaD4n3rCTggFQ4yY_3162f80e9db2a1c7229ce55d6dbc8c4496936f66c7df5136d24e8f9973cf64bc.txt', 'thumbnails': None, 'visible_name': 'test2.txt', 'name': 'xC64AcZManNeeBfKRaD4n3rCTggFQ4yY_3162f80e9db2a1c7229ce55d6dbc8c4496936f66c7df5136d24e8f9973cf64bc.txt', 'size': 26, 'mime_type': 'text/plain', 'is_image': False, 'image_width': None, 'image_height': None, 'uploaded_at': '2023-09-22T19:49:03.634193+00:00'}, {'size': 1496139, 'mime_type': 'image/jpeg', 'is_image': True, 'image_width': 4758, 'image_height': 3172, 'uploaded_at': '2023-10-05T17:54:43.486367Z', 'url': 'https://baserow-media.ams3.digitaloceanspaces.com/user_files/eqHCVDQ2ZxLxW4quC4U1sgNpsa95Mdlv_f94451b699bb744e2beac065874201fa5201eb75ceb9961d779e72fcbf55f1d7.jpg', 'thumbnails': {'tiny': {'url': 'https://baserow-media.ams3.digitaloceanspaces.com/thumbnails/tiny/eqHCVDQ2ZxLxW4quC4U1sgNpsa95Mdlv_f94451b699bb744e2beac065874201fa5201eb75ceb9961d779e72fcbf55f1d7.jpg', 'width': None, 'height': 21}, 'small': {'url': 'https://baserow-media.ams3.digitaloceanspaces.com/thumbnails/small/eqHCVDQ2ZxLxW4quC4U1sgNpsa95Mdlv_f94451b699bb744e2beac065874201fa5201eb75ceb9961d779e72fcbf55f1d7.jpg', 'width': 48, 'height': 48}, 'card_cover': {'url': 'https://baserow-media.ams3.digitaloceanspaces.com/thumbnails/card_cover/eqHCVDQ2ZxLxW4quC4U1sgNpsa95Mdlv_f94451b699bb744e2beac065874201fa5201eb75ceb9961d779e72fcbf55f1d7.jpg', 'width': 300, 'height': 160}}, 'name': 'eqHCVDQ2ZxLxW4quC4U1sgNpsa95Mdlv_f94451b699bb744e2beac065874201fa5201eb75ceb9961d779e72fcbf55f1d7.jpg', 'original_name': 'fixie.jpg'}]
# single_row.values['MyFileField'].upload_file_via_url(url='https://www.jimwitte.net/bison.jpg')
# single_row.update()
# single_row.values['MyFileField'].upload_file('/home/jwitte/Downloads/baserow_files')
# print(single_row['MyFileField'])
# single_row.update()

# single_row.move_row()

# single_row.move_row(before_id=4)
# exit(0)

# fieldname = 'US Date Time'
# # fieldname = "EU Date"

# single_row = table.get_rows(include=[fieldname], return_single=True)
# print(table.fields[fieldname].field_data)
# print(single_row.values[fieldname].value)
# print(single_row.values[fieldname]._raw_value)
# print(single_row.values[fieldname].formatted_date)
# print(single_row.values[fieldname].as_datetime())

# field_date = single_row.values[fieldname].as_datetime()
# # Add one day
# new_date = field_date + timedelta(days=1)
# # Print the new date
# print(new_date)

# # update with datetime object
# single_row[fieldname] = new_date
# single_row.update()

# single_row = table.get_rows(include=[fieldname], return_single=True)
# print(single_row[fieldname])

# # update with row value
# date_value = single_row[fieldname]
# single_row[fieldname] = date_value
# single_row.update()


# access associated field properties
# commonly used field properties and methods should be included in rowValue
# print(single_row.values['Name'].field.order)

# test getting and setting values
# for field, value in TESTVALUES.items():
#     single_row = testField(field,value)

# # working with TextRowValue
# single_row = table.get_rows(
#     include=['Name'], 
#     return_single=True
# )

# print(single_row.values)
# print(single_row['Name'])



# # update TextRowValue with a multiline value
# # api seems to transform newline into a space
# single_row['Name'] = """
# Spot
# Spotness
# """

# updated_row = single_row.update()
# print(updated_row.content)

# # working with LongTextField
# single_row = table.get_rows(
#         include=['Notes'], 
#         return_single=True
#     )

# single_row['Notes'] = """
# Spotty dog.
# Her Spotness
# Spotticus
# """
# updated_row = single_row.update()

# # working with UrlField
# single_row = table.get_rows(
#     include=['myURL'], 
#     return_single=True
# )
# print(single_row['myURL'])
# single_row['myURL'] = 'http://www.example.com/search?q=hello%20world'
# updated_row = single_row.update()

# # working with email field
# value_name = 'myEmail'
# single_row = table.get_rows(
#     include=[value_name], 
#     return_single=True
# )
# print(single_row[value_name])
# single_row[value_name] = 'spot@thunderingbison.com'
# updated_row = single_row.update()

# # working with phone number
# value_name = 'myPhone'
# single_row = table.get_rows(
#     include=[value_name], 
#     return_single=True
# )
# print(single_row[value_name])
# single_row[value_name] = '217-867-5309'
# updated_row = single_row.update()

# # working with boolean
# value_name = 'Active'
# single_row = table.get_rows(
#     include=[value_name], 
#     return_single=True
# )
# print(single_row[value_name])
# single_row[value_name] = True
# updated_row = single_row.update()

# # working with Number
# value_name = 'myNumber'
# single_row = table.get_rows(
#     include=[value_name], 
#     return_single=True
# )
# print(single_row[value_name])
# single_row[value_name] = 99.99
# updated_row = single_row.update()

# # working with rating
# value_name = 'myRating'
# single_row = table.get_rows(
#     include=[value_name], 
#     return_single=True
# )
# print(single_row[value_name])
# print(single_row.content)
# single_row[value_name] = 0
# updated_row = single_row.update()
