# pylint: disable=unused-argument

import sqlite3 as sql
import json


class DBConnection:
    def __init__(self, dbname):
        self.conn = sql.connect(dbname)

    def __del__(self):
        self.conn.close()

    def get_user_char(self, user_id, char_name):
        res = self.conn.cursor().execute(
            "SELECT OBJ FROM u%(user_id)s WHERE NAME='%(char_name)s'" % locals()
        ).fetchone()
        if res is None:
            return None
        return json.loads(res[0])

    def update_user_char(self, user_id, char_name, char):
        char = json.dumps(char)
        res = self.conn.cursor().execute(
            "UPDATE OR IGNORE u%(user_id)s SET OBJ='%(char)s' WHERE NAME='%(char_name)s'" % locals()
        )
        if res.rowcount == 0:
            return False
        self.conn.commit()
        return True

    def set_user_char(self, user_id, char_name, char):
        char = json.dumps(char)
        res = self.conn.cursor().execute(
            "INSERT OR IGNORE INTO u%(user_id)s (NAME, OBJ) VALUES ('%(char_name)s', '%(char)s')"
            % locals()
        )
        if res.rowcount == 0:
            return False
        self.conn.commit()
        return True
