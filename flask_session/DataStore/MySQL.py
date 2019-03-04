import mysql.connector

class MySQL:
    def __init__(self, **dns):
        self.dns = dns
        self.dbh = None

    def _open(self):
        self.dbh = mysql.connector.MySQLConnection(**self.dns)

    def _close(self):
        self.dbh.close()

    def query(self, stmt, *args, **kwargs):
        self._open()
        if kwargs.get('prepared', False):
            cursor = self.dbh.cursor(prepared=True)
            cursor.execute(stmt, args)
        else:
            cursor = self.dbh.cursor()
            cursor.execute(stmt)
        data = cursor.fetchall()
        cursor.close()
        self._close()
        return data