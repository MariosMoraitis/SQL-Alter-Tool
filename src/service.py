import os
from databases import Oracle, MsSQL, DB2

def calculate_n_write(table_name, columns, action, issue, path, include_spool) -> str:

    try:
        ora_sql = Oracle(table_name=table_name, columns=columns, issue=issue, action=action, include_spool=include_spool)
        mssql = MsSQL(table_name=table_name, columns=columns, issue=issue, action=action, include_spool=include_spool)
        db2 = DB2(table_name=table_name, columns=columns, issue=issue, action=action, include_spool=include_spool)

        _path = os.path.join(path, issue)

        # Create a folder to store the generated sqls. Folder_Name = issue
        if not os.path.isdir(_path):
            os.mkdir(_path)


        with open(os.path.join(_path, f'ORA_{issue}.sql'), 'w', encoding='utf-8') as f:
            f.write(str(ora_sql))

        with open(os.path.join(_path, f'MsSQL_{issue}.sql'), 'w', encoding='utf-8') as f:
            f.write(str(mssql))

        with open(os.path.join(_path, f'DB2_{issue}.sql'), 'w', encoding='utf-8') as f:
            f.write(str(db2))

        return 'OK'
    except Exception as e:
        return f'Faced exception:\n{str(e)}'