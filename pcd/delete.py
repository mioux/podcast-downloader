#!/bin/env python3
import sys, os, sqlite3

argc = len(sys.argv)
exe_name = os.path.basename(sys.argv[0])

def delete_usage(self):
    print ("Usage: " + exe_name + " delete --id=<uuid>")
    print ("       --id=<uuid> : ID of podcast to delete")

def delete(self, id):
    con = sqlite3.connect(self.db_file)
    curs = con.cursor()

    curs.execute("DELETE FROM podcast WHERE id = :id OR uuid = id", { 'id': id })
    if curs.rowcount > 0:
        print (id + " deleted successfully")
    else:
        print (id + " not found")
    con.commit()
    con.close()
