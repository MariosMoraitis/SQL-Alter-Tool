class DatabaseSyntax:

    def __init__(self, table_name:str, columns, action:str, issue:str):
        self.table_name = table_name
        self.columns = columns
        self.action = action
        self.issue = issue

        self.data_types: dict[str,str] = {
            "TEXT": "CHAR",
            "DATE": "DATE",
            "TIMESTAMP": "TIMESTAMP",
            "NUMBER": "NUMERIC"
        }

        # Generic types that do NOT take a length/precision in the DDL
        self.fixed_types = {"DATE", "TIMESTAMP"}

    def resolve_type(self, generic_type: str) -> str:
        """Translate a generic type (TEXT/DATE/TIMESTAMP/NUMBER) into the
        dialect-specific SQL type name, using self.data_types."""
        try:
            return self.data_types[generic_type]
        except KeyError:
            raise ValueError(f'Unsupported data type "{generic_type}".')

    def quote_identifier(self, name: str) -> str:
        """Override in a subclass if the dialect needs quoted identifiers
        (e.g. DB2 uses double quotes). Default = no quoting."""
        return name

    def build_column_definition(self, column: dict) -> str:
        """
        Turn one column dict into a DDL fragment:
            ADD  -> 'AGE NUMERIC(5)'  or  'CREATED_AT DATE'  (no length for fixed types)
            DROP -> 'AGE'
        """
        col_name = self.quote_identifier(column["column_name"]).upper()

        if self.action == 'DROP':
            return col_name

        generic_type = column["data_type"]
        sql_type = self.resolve_type(generic_type)

        if generic_type in self.fixed_types:
            return f"{col_name} {sql_type}"

        length = str(column["length"]).replace(".", ",")

        return f"{col_name} {sql_type}({length})"

    def column_definition(self) -> list[str]:
        """Build the DDL fragment for every column."""
        return [self.build_column_definition(c) for c in self.columns]