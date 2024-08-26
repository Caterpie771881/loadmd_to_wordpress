import time
import base64
import random


def rc4(data: str, key: str) -> str:
    box = list(range(256))
    key = [ord(key[i % len(key)]) for i in range(256)]
    cipher, j = "", 0
    for i in range(256):
        j = (j + box[i] + key[i]) % 256
        box[i], box[j] = box[j], box[i]
    a = j = 0
    for i in range(len(data)):
        a = (a + 1) % 256
        j = (j + box[a]) % 256
        box[a], box[j] = box[j], box[a]
        cipher += chr(ord(data[i]) ^ box[(box[a] + box[j]) % 256])
    return cipher


def encryption_password(password: str) -> tuple[str, str]:
    def base64_encode(string: str) -> str:
        return base64.b64encode(string.encode('latin_1')).decode()
    timestamp = int(time.time())
    password = base64_encode(f"{base64_encode(password)}@{timestamp}")
    key = ''.join(str(i) for i in random.randbytes(8))
    return base64_encode(rc4(password, key)), key
