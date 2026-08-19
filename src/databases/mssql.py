from .database_syntax import DatabaseSyntax

class MsSQL(DatabaseSyntax):

    def __init__(self, table_name, columns, action, issue, include_spool):
        super().__init__(table_name, columns, action, issue, include_spool)

        self.data_types["TIMESTAMP"] = "DATETIME2"

    def __str__(self):
        defs = self.column_definition()
        col_list = ',\n     '.join(defs)

        if self.action == "ADD":
            sql = f"ADD\n   {col_list}"
        else:
            sql = f"DROP COLUMN\n   {col_list}"

        spool_str = f"--SPOOL MsSQL_{self.issue}.INFO" if self.include_spool else ""
        return f"""{spool_str}
BEGIN TRAN;
    ALTER TABLE {self.table_name} {sql}
    COMMIT TRAN;
GO
"""