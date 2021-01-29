import sqlite3
import urllib3
import os
import json
import sys
import base64
import xlrd
from urllib.parse import unquote

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def dpapi_decrypt(encrypted):
    import ctypes
    import ctypes.wintypes
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [('cbData', ctypes.wintypes.DWORD),
                    ('pbData', ctypes.POINTER(ctypes.c_char))]
    p = ctypes.create_string_buffer(encrypted, len(encrypted))
    blobin = DATA_BLOB(ctypes.sizeof(p), p)
    blobout = DATA_BLOB()
    retval = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blobin), None, None, None, None, 0, ctypes.byref(blobout))
    if not retval:
        raise ctypes.WinError()
    result = ctypes.string_at(blobout.pbData, blobout.cbData)
    ctypes.windll.kernel32.LocalFree(blobout.pbData)
    return result
def aes_decrypt(encrypted_txt):
    with open(os.path.join(os.environ['LOCALAPPDATA'],
                           r"Google\Chrome\User Data\Local State"), encoding='utf-8', mode="r") as f:
        jsn = json.loads(str(f.readline()))
    encoded_key = jsn["os_crypt"]["encrypted_key"]
    encrypted_key = base64.b64decode(encoded_key.encode())
    encrypted_key = encrypted_key[5:]
    key = dpapi_decrypt(encrypted_key)
    nonce = encrypted_txt[3:15]
    cipher = Cipher(algorithms.AES(key), None, backend=default_backend())
    cipher.mode = modes.GCM(nonce)
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_txt[15:])
def chrome_decrypt(encrypted_txt):
    if sys.platform == 'win32':
        try:
            if encrypted_txt[:4] == b'x01x00x00x00':
                decrypted_txt = dpapi_decrypt(encrypted_txt)
                return decrypted_txt.decode()
            elif encrypted_txt[:3] == b'v10':
                decrypted_txt = aes_decrypt(encrypted_txt)
                return decrypted_txt[:-16].decode()
        except WindowsError:
            return None
    else:
        raise WindowsError
def get_cookies_from_chrome(domain):
    sql = f'SELECT name, encrypted_value as value FROM cookies where host_key like "%{domain}%"'
    filename = os.path.join(
        os.environ['USERPROFILE'], r'AppData\Local\Google\Chrome\User Data\default\Cookies'
        # os.environ['USERPROFILE'], r'AppData\Local\Microsoft\Edge\User Data\Default\Cookies'
    )
    con = sqlite3.connect(filename)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(sql)
    cookie = ''
    for row in cur:
        if row['value'] is not None:
            name = row['name']
            value = chrome_decrypt(row['value'])
            if value is not None:
                cookie += name + '=' + value + ';'
    return cookie

def get_config():
    file_path = r'.\config.xlsx'
    open_xls_file = xlrd.open_workbook(file_path)
    table = open_xls_file.sheet_by_index(0)
    nrows = table.nrows
    domain_list = []
    for i in range(1, nrows):
        domain_len = {}
        domain = table.cell_value(i, 0)
        isSign = table.cell_value(i, 1)
        if 'https' in domain:
            domain_len['http'] = 'https'
        else:
            domain_len['http'] = 'http'
        domain_len['domain'] = domain.replace('https://', '').replace('http://', '').replace('/', '')
        try:
            domain_len['isSign'] = str(int(isSign))
        except Exception as e:
            domain_len['isSign'] = '0'
        domain_list.append(domain_len)
    return domain_list

def set_config(domain_list):
    import configparser
    filename = './cookies/cookies.ini'
    if not os.path.exists(filename):
        fd = open(filename, mode="w", encoding="utf-8")
        fd.close()
    conf = configparser.ConfigParser()
    conf.read(filename)
    for i in domain_list:
        sections = conf.sections()

        try:
            if '' == i['cookie']:
                pass
            else:
                conf.options(i['domain'])
                # conf.add_section(i['domain'])
                conf.set(i['domain'], "domain", i['domain'])
                conf.set(i['domain'], "isSign", i['isSign'])
                conf.set(i['domain'], "http", i['http'])
                conf.set(i['domain'], "cookie", unquote(i['cookie']))
        except Exception as e:
            conf.add_section(i['domain'])
            conf.set(i['domain'], "domain", i['domain'])
            conf.set(i['domain'], "isSign", i['isSign'])
            conf.set(i['domain'], "http", i['http'])
            conf.set(i['domain'], "cookie", unquote(i['cookie']))
        # write to file
    with open(filename, "w+") as f:
        conf.write(f)



if __name__ == '__main__':
    # domain = 'hdatmos.club'   # 目标网站域名
    # cookie = get_cookies_from_chrome(domain)
    # print(cookie)

    domain_list = get_config()
    for i in domain_list:
        print(i['domain'])
        cookie = get_cookies_from_chrome(i['domain'])
        print(cookie)
        i['cookie'] = cookie
    for i in domain_list:
        print(i)
    set_config(domain_list)