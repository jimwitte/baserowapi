import os
from dotenv import load_dotenv
from baserowapi import Baserow, Filter

# Load environment variables
load_dotenv()

# Read variables from the environment
BASEROW_URL = os.getenv("BASEROW_URL")
BASEROW_TOKEN = os.getenv("BASEROW_TOKEN")

# Check if environment variables are set
if not all([BASEROW_URL, BASEROW_TOKEN]):
    raise EnvironmentError("Both BASEROW_URL and BASEROW_TOKEN must be set in the .env file.")

def main():

    
    # baserow client
    db = Baserow(url='https://api.baserow.io',token='TXpzDVBsrZjgMDeOiaDlz0ryiUEnFPmm', logging_level='DEBUG')
    print(db)

   
    # get table
    table_id = 198958
    table = db.get_table(table_id)
    print(table)
    print(table.id)
    print(table.primary_field)
    print(table.fields)
    print(table.fields['Name']) 
    print(table.fields['Name'].order)
    print(table.fields['Name'].field_data)
    print(table.field_names)


    # get row
    my_row = table.get_row(1)
    print(my_row)
    print(my_row.table_id)
    print(my_row.values)
    print(my_row.content)
    print(my_row['Name'])

    # get all rows as iterator object
    all_my_rows = table.get_rows()
    for row in all_my_rows:
        print(row)

    # filter object implied equal
    name_equal_grace = Filter("Name", "Grace")
    print(name_equal_grace.query_string)

    # contains_not filter
    name_contains_not_A = Filter("Name", "A", 'contains_not')
    print(name_contains_not_A.query_string)

    # get rows with equal filter
    rows_with_name_grace = table.get_rows(filters=[name_equal_grace])
    for row in rows_with_name_grace:
        print(row.content)

    # get rows with contains_not filter
    rows_without_A = table.get_rows(filters=[name_contains_not_A])
    for row in rows_without_A:
        print(row.content)

    # get rows with equal filter, space in field name
    rows_with_last_name_hopper = table.get_rows(filters=[Filter("Last name","Hopper")])
    for row in rows_with_last_name_hopper:
        print(row.content)

    # get rows with multiple filters on same field, OR
    rows_with_name_ada_or_grace = table.get_rows(filters=[Filter("Name", "Ada"), Filter("Name", "Grace")], filter_type='OR')
    for row in rows_with_name_ada_or_grace:
        print(row.content)

    # get rows with multiple filters on different fields, OR
    rows_with_name_ada_or_last_name_pascal = table.get_rows(filters=[Filter("Name","Ada"), Filter("Last name", "Pascal")], filter_type='OR')
    for row in rows_with_name_ada_or_last_name_pascal:
        print(row.content)

    # get rows sorted ascending by field
    rows_name_ascending = table.get_rows(order_by=["Name"])
    for row in rows_name_ascending:
        print(row.content)

    # get rows sorted descending by field
    rows = table.get_rows(order_by=["-Name"])
    for row in rows:
        print(row.content)

    # get rews sorted by multiple fields
    rows = table.get_rows(order_by=["Name", "-Last name"])
    for row in rows:
        print(row.content)

    # get rows with search
    rows_with_test = table.get_rows(search="test")
    for row in rows_with_test:
        print(row.content)

    # get rows from view
    rows_from_view = table.get_rows(view_id=329207)
    for row in rows_from_view:
        print(row.content)

    # get rows with include
    rows_with_include = table.get_rows(include=['Name','Last name', 'Notes', 'Active'])
    for row in rows_with_include:
        print(row.content)
    
    # get rows with exclude
    rows_with_exclude = table.get_rows(exclude=['Notes','Active'])
    for row in rows_with_exclude:
        print(row.content)

    # add new row from dict
    new_row_data = {
        'Name': 'Ringo',
        'Last name': 'Staar',
        'Notes': 'drums',
        'Active': True
    }
    added_row = table.add_row(new_row_data)
    print(added_row.content)

    # delete row
    deleted_status = added_row.delete()
    print(deleted_status)

    # add multiple rows from list of dicts
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

    added_rows = table.add_row(add_multiple_row_data)
    for row in added_rows:
        print(row.content)
    
    # delete multiple rows
    deleted_status = table.delete_rows(added_rows)
    print(deleted_status)

    # delete multiple rows using list of ids
    re_added_rows = table.add_row(add_multiple_row_data)
    rows_to_delete = []
    for row in re_added_rows:
        rows_to_delete.append(row.id)
    delete_status = table.delete_rows(rows_to_delete)

    # update rows from dict
    update_rows_data = [
        {"id": 3, "Notes": "dict update test"},
        {"id": 4, "Notes": "dict update test"},
        {"id": 5, "Notes": "dict update test"}
    ]
    updated_rows = table.update_rows(update_rows_data)
    for row in updated_rows:
        print(row.content)

    # update rows from Row objects
    my_rows = list(table.get_rows(filters=[Filter("Notes", "dict update test")]))
    for row in my_rows:
        row.update(values={'Notes': 'Row object update test'}, memory_only=True)
        print(row.content)
    updated_rows = table.update_rows(my_rows)
    for row in updated_rows:
        print(row.content)

    # return single row with empty filtered rows
    single_row = table.get_rows(filters=[Filter("Notes", "asdfjkl;")], return_single=True)
    if single_row:
        print(single_row.content)
    else:
        print("No row found with matching criteria.")

    # return single row 
    single_row = table.get_rows(return_single=True)
    print(single_row.content)

    # set value for in-memory Row object
    single_row['Notes'] = "Changed note in memory"
    print(single_row['Notes'])

    # update Row with current row values
    updated_row = single_row.update()
    print(updated_row.content)

    # update Row with dictionary
    updated_row = single_row.update({'Notes': 'Updated row via dictionary'})


if __name__ == "__main__":
    main()
