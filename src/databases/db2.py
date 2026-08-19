from .database_syntax import DatabaseSyntax

class DB2(DatabaseSyntax):

    def __init__(self, table_name, columns, action, issue, include_spool):
        super().__init__(table_name, columns, action, issue, include_spool)

    def quote_identifier(self, name: str) -> str:
        return f'"{name}"'

    def __str__(self):
        defs = self.column_definition()

        sql = '\n'.join(f'{self.action} COLUMN {d}' for d in defs)
        spool_str = f"SPOOL DB2_{self.issue}.INFO" if self.include_spool else ""

        return f"""{spool_str}
ALTER TABLE "{self.table_name}"
{sql};
COMMIT;{self.spool_off}
EXIT;
"""