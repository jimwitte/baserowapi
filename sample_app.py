import os
from dotenv import load_dotenv
from baserowapi import Baserow, Table, Filter

# Load environment variables
load_dotenv()

# Read variables from the environment
BASEROW_URL = os.getenv("BASEROW_URL")
BASEROW_TOKEN = os.getenv("BASEROW_TOKEN")

# Check if environment variables are set
if not all([BASEROW_URL, BASEROW_TOKEN]):
    raise EnvironmentError("Both BASEROW_URL and BASEROW_TOKEN must be set in the .env file.")

def main():


    db1 = Baserow(url='https://api.baserow.io',token='TXpzDVBsrZjgMDeOiaDlz0ryiUEnFPmm')
    db1_table = db1.get_table(198958)
    # print(db1_table)
    # print(db1_table.fields)
    # print(db1_table.fields['Name'])
    # name_field = db1_table.fields['Name']
    # name_field_type = name_field.type
    # print(f"Name field type: {name_field_type}")

    # for field in db1_table.fields:
    #     print(field.attributes)

    print(db1_table.fields['Multiple select']['select_options'])
    all_select_options = db1_table.get_field("Multiple select").attributes.get("select_options", None)
    option1 = all_select_options[0].get('id')
    print(option1)

    spot_row = db1_table.get_rows(return_single=True, include=['Name','Multiple select'])
    spot_row.fields['Name'] = "Spot"
    # spot_row.fields['Multiple select'] = [option1]
    print(spot_row.fields)
    spot_row.update()
    

    exit(0)

    print("\n=== Get Table ===")
    db = Baserow(url='https://api.baserow.io',token='TXpzDVBsrZjgMDeOiaDlz0ryiUEnFPmm', log_file='test.log', logging_level='DEBUG')
    print(db)

    class_table_test = Table('123', db)

    table_id = 195388
    table = db.get_table(table_id)
    print(table)
    print(table.fields)
    print(table.primary_field)

    print("\n=== Get Row ===")
    my_row = table.get_row(1)
    print(my_row)
    print(my_row.fields)

    print("\n=== All Rows ===")
    all_my_rows = table.get_rows()
    for row in all_my_rows:
        print(row)

    print("\n=== Filter object implied equal ===")
    name_equal_grace = Filter("Name", "Grace")
    print(name_equal_grace.query_string)

    print("\n=== Filter object contains_not ===")
    name_contains_not_A = Filter("Name", "A", 'contains_not')
    print(name_contains_not_A.query_string)

    print("\n=== Get Rows with filter ===")
    rows_with_name_grace = table.get_rows(filters=[name_equal_grace])
    for row in rows_with_name_grace:
        print(row.fields)

    print("\n=== contains_not Filter ===")
    rows_without_A = table.get_rows(filters=[name_contains_not_A])
    for row in rows_without_A:
        print(row.fields)

    # print("\n=== lower_than filter with text field ===")
    # try:
    #     rows_bad_filter_for_text_field = table.get_rows(filters=[Filter("Name", 1, "lower_than")])
    #     for row in rows_bad_filter_for_text_field:
    #         print(row.fields)
    # except ValueError as e:
    #     print(f"bad filter/field type combo: {e}")

    print("\n=== Filter on field with space in field name ===")
    rows_with_last_name_hopper = table.get_rows(filters=[Filter("Last name","Hopper")])
    for row in rows_with_last_name_hopper:
        print(row.fields)

    print("\n=== Multiple Filters Same Field ===")
    rows_with_name_ada_or_grace = table.get_rows(filters=[Filter("Name", "Ada"), Filter("Name", "Grace")], filter_type='OR')
    for row in rows_with_name_ada_or_grace:
        print(row.fields)

    print("\n=== Multiple Filters Different Fields, OR ===")
    rows_with_name_ada_or_last_name_pascal = table.get_rows(filters=[Filter("Name","Ada"), Filter("Last name", "Pascal")], filter_type='OR')
    for row in rows_with_name_ada_or_last_name_pascal:
        print(row.fields)

    print("\n=== Get Rows ordered by field ascending ===")
    rows_name_ascending = table.get_rows(order_by=["Name"])
    for row in rows_name_ascending:
        print(row.fields)

    print("\n=== Get Rows ordered by field descending ===")
    rows = table.get_rows(order_by=["-Name"])
    for row in rows:
        print(row.fields)

    print("\n=== Get Rows ordered by multiple fields ===")
    rows = table.get_rows(order_by=["Name", "-Last name"])
    for row in rows:
        print(row.fields)

    print("\n=== Search rows for test ===")
    rows_with_test = table.get_rows(search="test")
    for row in rows_with_test:
        print(row.fields)

    print("\n=== Add New Row ===")
    new_row_data = {
        'Name': 'Blaiser',
        'Last name': 'Pascal again',
        'Notes': 'testing',
        'Active': True
    }
    added_row = table.add_row(new_row_data)
    print(added_row)

    print("\n=== Delete added row ===")
    status_code = added_row.delete()
    print(status_code)

    add_multiple_row_data = [
        {
            'Name': 'Nick',
            'Last name': 'Saban',
            'Notes': 'Head coach of Alabama Crimson Tide',
            'Active': True
        },
        {
            'Name': 'Dabo',
            'Last name': 'Swinney',
            'Notes': 'Head coach of Clemson Tigers',
            'Active': True
        },
        {
            'Name': 'Urban',
            'Last name': 'Meyer',
            'Notes': 'Former head coach of Ohio State Buckeyes',
            'Active': False
        }
    ]

    print("\n=== Add Multiple rows ===")
    added_rows = table.add_row(add_multiple_row_data)
    for row in added_rows:
        print(row)
    
    print("\n=== Delete Multiple rows ===")
    status_code = table.delete_rows(added_rows)
    print(status_code)

    print("\n=== Update Multiple rows via dictionary ===")
    update_rows_data = [
        {"id": 1, "Notes": "dict update test"},
        {"id": 2, "Notes": "dict update test"},
        {"id": 3, "Notes": "dict update test"}
    ]
    updated_rows = table.update_rows(update_rows_data)
    for row in updated_rows:
        print(row)

    print("\n=== Update Multiple rows via updated Row objects ===")
    my_rows = list(table.get_rows(filters={"Notes": "dict update test"}))
    for row in my_rows:
        print(row)
    for row in my_rows:
        row.update_fields({'Notes': 'Row object update test'})
    updated_rows = table.update_rows(my_rows)
    for row in updated_rows:
        print(row)

    print("\n=== Get single row from filter, no match ===")
    single_row = table.get_rows(filters={"Notes": "asdfjkl;"}, return_single=True)
    if single_row:
        print(single_row)
    else:
        print("No row found with matching criteria.")

    print("\n=== Get single row from filter, with match ===")
    single_row = table.get_rows(filters={"Notes": "Row object update test"}, return_single=True)
    print(single_row)

    print("\n=== Update single row from filter using row.update function ===")
    update_data = {'Notes': "The updated note from row.update"}
    single_row = single_row.update(update_data)
    print(single_row.fields)

    print("\n=== Get and Set row data dict style ===")
    single_row = table.get_rows(filters={"Notes": "Row object update test"}, single=True)
    print(single_row['Name'])
    single_row['Name'] = 'Fred'
    print(single_row.fields)

if __name__ == "__main__":
    main()
