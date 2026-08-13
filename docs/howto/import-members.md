# Importing Members

Bitcaster allows you to add multiple members at once by importing them from a comma-separated values (CSV) file. This is useful for populating the system with a large number of users quickly.

## How to Import Members

1.  From the Bitcaster Admin sidebar, navigate to **Bitcaster** > **Members**.
2.  On the Member list page, click the **Import Members** button located in the top-right corner.
3.  On the "Import Members" page, you will see two fields:
    -   **File:** Click "Choose File" and select the CSV file you want to upload.
    -   **Group:** Select the Group to which all newly imported members will be assigned. This field is required and defaults to the systems default group.
4.  Click the **Confirm** button to begin the import process.

After the import is complete, you will be redirected back to the Member list, and a message will appear confirming how many members were successfully created (e.g., "Record successfully imported 2/3").

## Supported File Format

The importer has specific requirements for the file format.

-   **File Type:** CSV (Comma-separated values).
-   **Encoding:** The file must be UTF-8 encoded.
-   **Header Row:** The first line of the file must be a header row containing column names.

### Column Mapping

#### `email` (Required)

A column named `email` is **mandatory**. The value from this column is used to set the member's unique `username` and their `email` address.

-   If the `email` column is missing from the header, the import will fail.
-   Any data row with a missing or incorrectly formatted email address will be skipped.

#### Custom Fields (`custom__*`)

You can populate the JSON `custom_fields` for each member during the import. To do this, add columns to your CSV file with a header that starts with the prefix `custom__`.

For example, a column named `custom__department` will populate the `department` key in the `custom_fields` object.

### Example

Here is an example of a valid CSV file:

```csv
email,first_name,last_name,custom__department,custom__employee_id
user1@example.com,John,Doe,Sales,1001
user2@example.com,Jane,Roe,Engineering,2005
invalid-email,,,Human Resources,3003
```

-   The first two rows will be successfully imported. The `first_name` and `last_name` columns will be ignored as they are not standard mapped fields, but the custom fields `department` and `employee_id` will be populated.
-   The third row will be skipped because the email address is invalid.
-   The final success message will report that "2/3" records were imported.

**Note:** The import process is designed to **add new members only**. It uses the email address to identify conflicts. If a member with a given email already exists in the system, that row will be skipped. All successfully imported members will be automatically added to the group you select on the import form.

**Synchronous import:** the import runs synchronously in the browser request. The page redirects back to the Member list only after the file has been fully processed, and the result message reports how many records were imported. Very large files may therefore take a while to complete.

The same CSV import is also available from the command line — see [Command Line Interface](../adm-guide/cli.md) (`bc import users`).
