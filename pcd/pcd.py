#!/bin/env python3

class pcd():
    from pcd.add import add, add_usage
    from pcd.db import migrate_db, podcast_list, config_dump, web_list, web_history, web_podcast_detail, get_config, get_nb_users, check_user, user_exists
    from pcd.delete import delete, delete_usage
    from pcd.edit import edit, edit_usage
    from pcd.download import dl, get_file
    from pcd.user import user_add, user_del, user_usage

    def __init__(self, db_file) -> None:
        self.db_file = db_file
