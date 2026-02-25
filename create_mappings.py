import pandas as pd
from pathlib import Path

def create_comprehensive_mapping():
    # Load Your Files (update paths if needed)
    encompass_path = Path('mappings/encompass_data_dictionary.xlsx')
    mismo_ldd_path = Path('mappings/mismo_ldd.xlsx')  # After download

    if not encompass_path.exists():
        print("Encompass DD not found - using sample structure.")
        encompass_df = pd.DataFrame({  # Sample if not found
            'Field ID': ['LoanAmount', '1401', '353'],
            'Field Name': ['Loan Amount', 'BorrowerFirstName', 'PropertyStreetAddress'],
            'Description': ['Base loan amount', 'Borrower's first name', 'Property street'],
            'Data Type': ['Numeric', 'String', 'String']
        })
    else:
        encompass_df = pd.read_excel(encompass_path)

    if not mismo_ldd_path.exists():
        print("MISMO LDD not found - using sample data points from XML.")
        mismo_df = pd.DataFrame({  # From XML sample
            'Data Point Name': ['BaseLoanAmount', 'FirstName', 'StreetAddress'],
            'Definition': ['Original principal balance', 'Individual's first name', 'Street address'],
            'Type': ['Amount', 'String', 'String'],
            'Container/Path': ['LOAN/LOAN_DETAIL', 'PARTY/ROLE/BORROWER/INDIVIDUAL/NAME', 'PROPERTY/ADDRESS']
        })
    else:
        mismo_df = pd.read_excel(mismo_ldd_path, sheet_name='Data Points')

    # Merge (simple left join on approximate names; customize with fuzzy matching if needed)
    merged = pd.merge(encompass_df, mismo_df, left_on='Field Name', right_on='Data Point Name', how='outer')

    # Add Custom Columns (from your model)
    merged['Source System'] = 'Encompass'
    merged['MISMO Version'] = '3.4.0'
    merged['Target Table'] = merged['Container/Path'].apply(lambda x: str(x).split('/')[0].lower() if pd.notnull(x) else 'unknown')  # e.g., 'loan' -> 'loans'
    merged['Target Column'] = merged['Data Point Name'].apply(lambda x: str(x).lower() if pd.notnull(x) else '')
    merged['Transformation Rule'] = ''  # Fill manually, e.g., 'Cast to NUMERIC'
    merged['Validation/Check'] = ''  # e.g., '>0'
    merged['Notes/Edge Cases'] = ''  # e.g., 'Repeatable'
    merged['Status'] = 'Mapped' if pd.notnull(merged['Data Point Name']) else 'Pending'

    # Reorder Columns
    columns = ['Source System', 'Field ID', 'Field Name', 'Description', 'Data Type', 'Length/Format', 'MISMO Version', 'Data Point Name', 'Container/Path', 'Definition', 'Enumerations', 'Target Table', 'Target Column', 'Transformation Rule', 'Validation/Check', 'Notes/Edge Cases', 'Status']
    merged = merged.reindex(columns=columns, fill_value='')

    # Output to Excel with Multiple Sheets
    output_path = Path('mappings/comprehensive_mismo_encompass_mapping.xlsx')
    with pd.ExcelWriter(output_path) as writer:
        merged.to_excel(writer, sheet_name='Core Mappings', index=False)
        # Add Enums Sheet (sample)
        enums_df = pd.DataFrame({'MISMO Data Point': ['LoanPurposeType'], 'MISMO Enum': ['Purchase,Refinance'], 'Encompass Enum': ['1,2'], 'Mapping Note': ['Code to string']})
        enums_df.to_excel(writer, sheet_name='Enums', index=False)

    print(f"File created at {output_path}! Commit to repo.")

if __name__ == "__main__":
    create_comprehensive_mapping()
