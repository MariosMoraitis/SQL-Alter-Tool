from .database_syntax import DatabaseSyntax

class DB2(DatabaseSyntax):

    def __init__(self, table_name, columns, action, issue):
          super().__init__(table_name, columns, action, issue)

    def quote_identifier(self, name: str) -> str:
        return f'"{name}"'

    def __str__(self):
        defs = self.column_definition()

        sql = '\n'.join(f'{self.action} COLUMN {d}' for d in defs)

        return f"""
SPOOL DB2_{self.issue}.INFO;
ALTER TABLE "{self.table_name}"
{sql};
COMMIT;
SPOOL OFF;
EXIT;
"""