#!/bin/env python3

class pcd():
    from pcd.add import add, add_usage
    from pcd.db import migrate_db, podcast_list, config_dump
    from pcd.delete import delete, delete_usage
    from pcd.edit import edit, edit_usage
    from pcd.download import dl
    
    def __init__(self, config_file, db_file) -> None:
        self.config_file = config_file
        self.db_file = db_file