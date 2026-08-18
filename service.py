import os
from databases import Oracle, MsSQL, DB2

def calculate_n_write(table_name, columns, action, issue, path=None):
    try:
        ora_sql = Oracle(table_name=table_name, columns=columns, issue=issue, action=action)
        mssql = MsSQL(table_name=table_name, columns=columns, issue=issue, action=action)
        db2 = DB2(table_name=table_name, columns=columns, issue=issue, action=action)

        # Create a folder to store the generated sqls. Folder_Name = issue
        if not os.path.isdir(issue):
            os.mkdir(issue)


        with open(os.path.join(issue, f'ORA_{issue}.sql'), 'w', encoding='utf-8') as f:
            f.write(str(ora_sql))

        with open(os.path.join(issue, f'MsSQL_{issue}.sql'), 'w', encoding='utf-8') as f:
            f.write(str(mssql))

        with open(os.path.join(issue, f'DB2_{issue}.sql'), 'w', encoding='utf-8') as f:
            f.write(str(db2))

        return 'OK'
    except Exception as e:
        return f'Faced exception:\n{str(e)}'