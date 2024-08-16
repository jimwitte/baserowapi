# Baserow Test Table Schema

This README file describes the schema of the test tables used for functional testing of the Baserow API. Each column corresponds to a specific field type available in Baserow. The environment variable for the table ID is `BASEROW_TABLE_ID`.

## All Fields Testing Table

### Columns

#### Basic Information
- **id**: Integer - Unique identifier for each row.
- **Name**: Text - A text field for the name.
- **Notes**: Long Text - A long text field for additional notes.
- **Active**: Boolean - A boolean field indicating active status.

#### Numeric and Rating Fields
- **Number**: Number - A numeric field.
- **Rating**: Rating - A rating field with integer values.

#### Date and Time Fields
- **US Date Time**: Date/Time - Date and time field in US format.
- **Last modified**: Date/Time - The last modified date and time.
- **Created on**: Date/Time - The creation date and time.
- **EU Date**: Date/Time - Date and time field in EU format.

#### URL and Email Fields
- **URL**: URL - A URL field.
- **Email**: Email - An email field.

#### File Fields
- **FileField**: File - A field for file attachments.

#### Select Fields
- **SingleSelect**: Single Select - A single select field with predefined options.
- **MultipleSelect**: Multiple Select - A multiple select field with predefined options.

#### Phone and Formula Fields
- **Phone**: Phone Number - A phone number field.
- **Formula**: Formula - A formula field that computes its value.

#### Link and Count Fields
- **TableLink**: Link - A field that links to rows in another table.
- **myCount**: Count - A read-only field that returns the number of relations in a linked table.

#### Lookup and Collaborator Fields
- **Lookup**: Lookup - A field connected to a link to table field, returning an array of values and row ids from the chosen lookup field in the linked table.
- **Collaborators**: Multiple Collaborators - A list of Baserow collaborators.

#### Other Fields
- **Last name**: Text - A text field for the last name.
- **UUID**: UUID - A read-only field that generates a UUID.
- **Autonumber**: Autonumber - A read-only field with an auto-incrementing integer value.
- **Password**: Password - A password field. When read, it provides "true" or "null" depending on if the field has been set. When written, it sets the password to the provided value. Setting the field value to None will "unset" the password.

## Table Link Field Testing Table

### Columns

#### Basic Information
- **Name**: Text - A text field for the name.
- **Notes**: Long Text - A long text field for additional notes.
- **Active**: Boolean - A boolean field indicating active status.

#### Link Field
- **All Fields Testing Table**: Link - A field that links to rows in the "All Fields Testing Table".

## Environment Variables

- **BASEROW_URL**: The URL of the Baserow instance.
- **BASEROW_TOKEN**: The API token for authentication.
- **BASEROW_TABLE_ID**: The ID of the test table.

Ensure that the .env file contains the correct values for these environment variables.
