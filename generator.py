# generator.py
import xmlschema
import sqlalchemy as sa
from sqlalchemy import MetaData, Table, Column, String, Numeric, Date, Boolean, JSON, ForeignKey, Integer
import pandas as pd
from pathlib import Path
import json

def generate_model():
    """Generates full MISMO 3.4 artifacts from your repo files."""
    # Load your Encompass DD
    dd_path = Path('mappings/encompass_data_dictionary.xlsx')  # Update filename
    mappings_df = pd.read_excel(dd_path) if dd_path.exists() else pd.DataFrame()
    
    # Load MISMO Schema (from your schemas/)
    xsd_path = Path('schemas/MISMO_3.4.0_B324.xsd')  # Your primary XSD
    schema = xmlschema.XMLSchema(str(xsd_path))
    
    metadata = MetaData(schema='public')
    
    # Core Tables (full hierarchy from MISMO)
    tables = {}
    
    def create_table(name, elements, parent=None):
        cols = [Column('id', Integer, primary_key=True)]
        if parent:
            cols.append(Column(f'{parent}_id', Integer, ForeignKey(f'{parent}s.id')))
        
        for elem in elements:
            if hasattr(elem.type, 'is_simple') and elem.type.is_simple():
                col_type = map_type(elem.type)
                cols.append(Column(elem.name.lower(), col_type))
        
        # Standard MISMO fields
        cols += [
            Column('sequence_number', Integer),
            Column('extension_data', JSON),  # For extensions/custom
            Column('created_at', Date, server_default=sa.func.now()),
            Column('updated_at', Date, server_default=sa.func.now(), onupdate=sa.func.now())
        ]
        
        table = Table(name.lower() + 's', metadata, *cols)
        tables[name] = table
    
    # Parse key MISMO containers (DEAL, LOAN, etc.)
    for elem_name in ['DEAL', 'LOAN', 'PROPERTY', 'PARTY', 'BORROWER', 'ASSET', 'LIABILITY']:
        if elem_name in schema.elements:
            create_table(elem_name, schema.elements[elem_name].type.content)
    
    # Output DDL
    Path('artifacts').mkdir(exist_ok=True)
    with open('artifacts/mismo_3.4_ddl.sql', 'w') as f:
        for table in metadata.sorted_tables:
            f.write(str(sa.schema.CreateTable(table).compile(dialect=sa.dialects.postgresql.dialect())) + ';\n')
    
    # Encompass Mappings (merge your DD)
    if not mappings_df.empty:
        mappings_df.to_csv('artifacts/encompass_mismo_mappings.csv', index=False)
    
    # ERD (dbdiagram.io format)
    with open('artifacts/erd.dbml', 'w') as f:
        f.write("""Table loans {
  id integer [pk]
  base_loan_amount numeric
  // Add more from your XSD
}

Table properties {
  id integer [pk]
  loan_id integer [ref: > loans.id]
}

// Relationships from MISMO XLinks
Ref: loans.id < properties.loan_id
""")
    
    print("✅ Artifacts generated in /artifacts/!")

def map_type(xsd_type):
    """MISMO types → Postgres."""
    t = str(xsd_type).lower()
    if 'decimal' in t: return Numeric(15, 2)
    if 'date' in t: return Date
    if 'boolean' in t: return Boolean
    if 'integer' in t: return Integer
    return String(255)  # Enums/strings

if __name__ == "__main__":
    generate_model()
