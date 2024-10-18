import sqlite3
import json

# 数据库路径
DB_FILE_PATH = 'plugins/BiliMart/'

# 数据库文件名
DB_FILE_NANE = 'mart_item.db'


def connect_db():
    """连接到 SQLite 数据库（如果数据库不存在，会自动创建）"""
    return sqlite3.connect(DB_FILE_PATH + DB_FILE_NANE)

def _create_tables():
    """创建表格"""
    conn = connect_db()
    cursor = conn.cursor()

    # 检查 items 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items';")
    items_exists = cursor.fetchone() is not None

    # 检查 details 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='details';")
    details_exists = cursor.fetchone() is not None

    # 如果两个表都存在，直接退出函数
    if items_exists and details_exists:
        conn.close()
        return  # 表格已存在，退出函数

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        c2cItemsId INTEGER NOT NULL UNIQUE,
        type INTEGER,
        c2cItemsName TEXT NOT NULL,
        totalItemsCount INTEGER,
        price INTEGER,
        showPrice TEXT,
        showMarketPrice TEXT,
        uid TEXT,
        paymentTime INTEGER,
        isMyPublish BOOLEAN,
        uname TEXT,
        uspaceJumpUrl TEXT,
        uface TEXT
        create_time TEXT
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blindBoxId INTEGER,
        itemsId INTEGER,
        skuId INTEGER,
        name TEXT NOT NULL,
        img TEXT,
        marketPrice INTEGER,
        type INTEGER,
        isHidden BOOLEAN,
        item_id INTEGER,
        FOREIGN KEY (item_id) REFERENCES items (id)
    );
    ''')

    conn.commit()
    conn.close()

def _insert_one_data_to_items(item_data):
    """插入商品数据"""
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # 插入商品的Item信息
        cursor.execute('''
        INSERT OR REPLACE INTO items (c2cItemsId, type, c2cItemsName, totalItemsCount, price, showPrice, showMarketPrice, uid, paymentTime, isMyPublish, uname, uspaceJumpUrl, uface, create_time) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%S', 'now'))
        ''', (
            item_data['c2cItemsId'],
            item_data['type'],
            item_data['c2cItemsName'],
            item_data['totalItemsCount'],
            item_data['price'],
            item_data['showPrice'],
            item_data['showMarketPrice'],
            item_data['uid'],
            item_data['paymentTime'],
            item_data['isMyPublish'],
            item_data['uname'],
            item_data['uspaceJumpUrl'],
            item_data['uface']
        ))
    except sqlite3.IntegrityError as e:
        print("_insert_one_data_to_items:" + str(e))
    item_id = cursor.lastrowid  # 获取插入的商品 ID
    conn.commit()
    conn.close()

    return item_id

def _insert_one_data_to_details(item_id, data):
    """插入详细信息数据"""
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # 插入商品details信息
        cursor.execute('''
        INSERT INTO details (blindBoxId, itemsId, skuId, name, img, marketPrice, type, isHidden, item_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['blindBoxId'],
            data['itemsId'],
            data['skuId'],
            data['name'],
            data['img'],
            data['marketPrice'],
            data['type'],
            data['isHidden'],
            item_id
        ))
    except sqlite3.IntegrityError as e:
        print("_insert_one_data_to_details:" + str(e))

    conn.commit()
    conn.close()


def insert_item_data(data):
    """解析 JSON 数据并插入到数据库"""
    details_data = data['detailDtoList'][0]

    i = _insert_one_data_to_items(data)  # 插入商品并获取 ID
    _insert_one_data_to_details(i, details_data)  # 插入详细信息


def init():
    # 创建表
    _create_tables()
