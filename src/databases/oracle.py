from .database_syntax import DatabaseSyntax

class Oracle(DatabaseSyntax):

    def __init__(self, table_name, columns, action, issue, include_spool):
        super().__init__(table_name, columns, action, issue, include_spool)

    def __str__(self):
        defs = self.column_definition()

        if len(defs) == 1:
            sql = f'{self.action} {defs[0]};'
        else:
            items = ',\n'.join(f'  {d}' for d in defs)
            sql = f'{self.action} (\n{items}\n);' 

        spool_str = f"SPOOL Oracle_{self.issue}.INFO" if self.include_spool else ""    
        return f"""{spool_str}
ALTER TABLE {self.table_name}
{sql}
COMMIT;{self.spool_off}
EXIT;
"""