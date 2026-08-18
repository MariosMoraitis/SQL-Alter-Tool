from .database_syntax import DatabaseSyntax

class Oracle(DatabaseSyntax):

    def __init__(self, table_name, columns, action, issue):
          super().__init__(table_name, columns, action, issue)

    def __str__(self):
        defs = self.column_definition()

        if len(defs) == 1:
            sql = f'{self.action} {defs[0]};'
        else:
            items = ',\n'.join(f'  {d}' for d in defs)
            sql = f'{self.action} (\n{items}\n);' 

        return f"""
SPOOL ORA_{self.issue}.INFO
ALTER TABLE {self.table_name}
{sql}
COMMIT;
SPOOL OFF
EXIT;
"""