#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
import datetime
import pickle
import uuid
import binascii
import json
import zlib
#import gzip
import hashlib
import random
import string

import __init__ as nomagic

from setting import conn


def get_activities_by_user_id(user_id, activity_offset=0, activity_start_id=None):
    user = nomagic._get_entity_by_id(user_id)
    activity_ids = user.get("activity", []) if user else []
    if user:
        activities = [dict(activity, id=activity_id) for activity_id, activity in nomagic._get_entities_by_ids(activity_ids)]
        return [dict(activity, comments = [dict(comment, id=comment_id) \
                for comment_id, comment in nomagic._get_entities_by_ids(activity["comment_ids"])]) \
            for activity in activities]
    return []


def new_status(user_id, data):
    now = datetime.datetime.now()
    data["type"] = "status"
    data["user_id"] = user_id
    data["datetime"] = now.isoformat()
    data["likes"] = []
    data["comment_ids"] = []
    assert data.get("content")

    new_id = nomagic._new_key()
    assert nomagic._node(new_id).execute_rowcount("INSERT INTO entities (id, body) VALUES(%s, %s)", new_id, nomagic._pack(data))

    user = nomagic._get_entity_by_id(user_id)
    activity = user.get("activity", [])
    activity.append(new_id)
    user["activity"] = activity
    nomagic._update_entity_by_id(user_id, user)

    data["user"] = user
    data["like_count"] = 0
    data["like"] = False
    data["comment_count"] = 0

    assert conn.execute_rowcount("INSERT INTO index_posts (user_id, entity_id) VALUES(%s, %s)", user_id, new_id)
    return new_id, data


def get_public_news_feed(activity_offset=10, activity_start_id=None):
    if activity_start_id:
        pass
    else:
        posts = conn.query("SELECT * FROM index_posts ORDER BY id DESC LIMIT 0, %s", activity_offset)
    activity_ids = [i["entity_id"] for i in posts]

    if posts:
        activities = [dict(activity, id=activity_id)
                        for activity_id, activity in nomagic._get_entities_by_ids(activity_ids)]
        return [dict(activity,
                     like_count = len(activity.get("likes", [])),
                     comment_count = len(activity.get("comment_ids", [])),
                     ) for activity in activities]
    return []

def get_news_by_id(activity_id):
    activity = nomagic._get_entity_by_id(activity_id)
    activity["id"] = activity_id
    comments, user_ids = get_comments(activity)

    return dict(activity,
                id = activity_id,
                like_count = len(activity.get("likes", [])),
                comment_count = 0, #len(activity.get("comment_ids", [])),
                comments = comments), user_ids


def get_fileinfo_by_rev(rev):
    fileinfo = conn.get("SELECT * FROM index_dropbox WHERE rev=%s", rev)
    if not fileinfo:
        return

    entity = nomagic._get_entity_by_id(fileinfo["entity_id"])
    return dict(entity, md5=fileinfo["entity_id"]) if entity else None

def update_fileinfo(filehash, user_id, id3info = None, title = None, rev = None):
    if rev:
        if not conn.get("SELECT * FROM index_dropbox WHERE rev=%s", rev):
            assert conn.execute_rowcount("INSERT INTO index_dropbox (rev, entity_id) VALUES (%s, %s)", rev, filehash)

    fileinfo = nomagic._get_entity_by_id(filehash)
    if fileinfo:
        changed = False

        owners = fileinfo.get("owners", [])
        if user_id not in owners:
            owners.append(user_id)
            fileinfo["owners"] = owners
            changed = True

        if id3info and id3info != fileinfo.get("id3info"):
            fileinfo["id3info"] = id3info
            changed = True

        if title and title != fileinfo.get("title"):
            fileinfo["title"] = title
            changed = True

        if changed:
            nomagic._update_entity_by_id(filehash, fileinfo)

    else:
        fileinfo = {"owners":[user_id]}
        if id3info:
            fileinfo["id3info"] = id3info
        if title:
            fileinfo["title"] = title
        assert nomagic._node(filehash).execute_rowcount("INSERT INTO entities (id, body) VALUES(%s, %s)",\
                                                                filehash, nomagic._pack(fileinfo))

    user = nomagic._get_entity_by_id(user_id)
    if user:
        files = user.get("files", [])
        if filehash not in files:
            files.append(filehash)
            user["files"] = files
            nomagic._update_entity_by_id(user_id, user)

    return fileinfo, user


def is_apns_token(token):
    if len(token) == 64:
        return True
    return False
