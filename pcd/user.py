#!/bin/env python3
from pcd.db import set_user_password, delete_user
from getpass import getpass
import os, sys

def user_add(self, username: str, password: str):
    if username is None or username.rstrip() == "":
        user_usage()
        return

    while password is None or password.rstrip() == "":
        getpwd = getpass("New password for {username}: ")
        confirm = getpass("Confirm password: ")
        if getpwd == confirm:
            password = getpwd
        else:
            print("Password do not match !")

    set_user_password(self, username, password)

def user_del(self, username):
    if username is None or username.rstrip() == "":
        user_usage()
        return
    delete_user(self, username)

def user_usage(self):
    exe_name = os.path.basename(sys.argv[0])

    print ("Usage: " + exe_name + " user --username=<username> [--password=<password>] [--delete]")
    print ("       --username=<username> : Username to create/modify/delete (update password if exists, create user if not)")
    print ("       --password=<password> : Optionnal password. Prompted if ommited. Cannot be used with --delete")
    print ("       --delete              : Delete username. Cannot be used with --password")
