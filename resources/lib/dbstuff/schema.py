# -*- coding: utf-8 -*-

class Schema():

    sql_contents = '''
    CREATE TABLE IF NOT EXISTS contents(
        cstatus INTEGER,
        station TEXT,
        title TEXT,
        start TEXT,
        end TEXT,
        filename TEXT,
        duration INTEGER,
        act TEXT,
        info TEXT,
        desc TEXT,
        description TEXT,
        site TEXT,
        cid INTEGER PRIMARY KEY AUTOINCREMENT,
        sid INTEGER,
        kid INTEGER,
        version TEXT,
        modified TEXT,
        UNIQUE(sid, start, kid)
    )'''

    # cstatus
    # -2: failed
    # -1: downloaded
    # 0: pass
    # 1: scheduled
    # 2: threaded
    # 3: downloading

    sql_trigger = '''
    CREATE TRIGGER IF NOT EXISTS update_modified AFTER UPDATE OF cstatus ON contents
    BEGIN
        UPDATE contents SET modified = DATETIME('now', '+9 hours') WHERE cid = NEW.cid;
    END'''

    sql_stations = '''
    CREATE TABLE IF NOT EXISTS stations(
        sid INTEGER PRIMARY KEY AUTOINCREMENT,
        top INTEGER,
        vis INTEGER,
        station TEXT,
        protocol TEXT,
        key TEXT,
        code TEXT,
        region TEXT,
        pref TEXT,
        city TEXT,
        logo TEXT,
        description TEXT,
        site TEXT,
        direct TEXT,
        delay INTEGER,
        scheduled INTEGER,
        nextaired0 TEXT,
        nextaired1 TEXT,
        version TEXT,
        modified TEXT
    )'''

    sql_keywords = '''
    CREATE TABLE IF NOT EXISTS keywords(
        kid INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT,
        match INTEGER,
        weekday INTEGER,
        station TEXT,
        dirname TEXT UNIQUE,
        kstatus INTEGER,
        version TEXT,
        modified TEXT
    )'''

    # kstatus
    # 0: inactive
    # 1: active

    sql_cities = '''
    CREATE TABLE IF NOT EXISTS cities(
        code TEXT,
        region TEXT,
        pref TEXT,
        city TEXT,
        area_id TEXT
    )'''

    sql_holidays = '''
    CREATE TABLE IF NOT EXISTS holidays(
        date TEXT,
        name TEXT
    )'''

    sql_master = '''
    CREATE TABLE IF NOT EXISTS master(
        mid INTEGER PRIMARY KEY AUTOINCREMENT,
        station TEXT UNIQUE,
        region TEXT,
        pref TEXT,
        city TEXT,
        code TEXT,
        site TEXT,
        SJ TEXT,
        LR TEXT,
        SR TEXT,
        SP TEXT,
        SD TEXT,
        mstatus INTEGER,
        version TEXT,
        modified TEXT
    )'''

    sql_auth = '''
    CREATE TABLE IF NOT EXISTS auth(
        auth_key TEXT,
        auth_token TEXT,
        area_id TEXT,
        authed INTEGER,
        key_offset INTEGER,
        key_length INTEGER,
        partial_key TEXT
    )'''

    sql_auth_init = '''
    DELETE FROM auth;
    INSERT INTO auth VALUES ('', '', '', 0, 0, 0, '');
    '''

    sql_status = '''
    CREATE TABLE IF NOT EXISTS status(
        front TEXT
    )'''

    sql_status_init = '''
    DELETE FROM status;
    INSERT INTO status VALUES('[]');
    '''
