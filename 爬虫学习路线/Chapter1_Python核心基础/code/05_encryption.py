"""
Python加密库实战

学习目标:
1. 理解常见哈希算法（MD5/SHA）的用途
2. 理解HMAC消息认证的原理
3. 理解AES对称加密的使用场景
4. 理解RSA非对称加密的基本原理
5. 为Chapter6的JS逆向打基础

运行方式:
    python code/05_encryption.py

重要提示:
- MD5/SHA1: 不安全，已被淘汰，仅用于学习
- AES: 对称加密，加密解密用同一密钥
- RSA: 非对称加密，公钥加密，私钥解密
- HMAC: 消息认证，防止篡改
"""

import hashlib
import hmac
import base64
import time
import rsa


def hash_demo():
    """哈希算法演示"""
    print("=" * 50)
    print("哈希算法 (MD5/SHA)")
    print("=" * 50)

    data = "Hello World"

    # MD5 (不安全，但常见于老旧系统)
    md5 = hashlib.md5(data.encode()).hexdigest()
    print(f"MD5: {md5}")

    # SHA-1 (不安全，逐渐被淘汰)
    sha1 = hashlib.sha1(data.encode()).hexdigest()
    print(f"SHA-1: {sha1}")

    # SHA-256 (推荐)
    sha256 = hashlib.sha256(data.encode()).hexdigest()
    print(f"SHA-256: {sha256}")

    # SHA-512
    sha512 = hashlib.sha512(data.encode()).hexdigest()
    print(f"SHA-512: {sha512}")

    print("\n💡 哈希特点:")
    print("  - 不可逆：不能从哈希反推原文")
    print("  - 固定长度：无论输入多长，输出长度固定")
    print("  - 唯一性：不同输入大概率产生不同哈希")


def hmac_demo():
    """HMAC演示 - 消息认证码"""
    print("\n" + "=" * 50)
    print("HMAC (消息认证)")
    print("=" * 50)

    key = b"secret_key_12345"
    message = "Hello World"

    # HMAC-SHA256
    h = hmac.new(key, message.encode(), hashlib.sha256)
    print(f"HMAC-SHA256: {h.hexdigest()}")

    # 验证HMAC（篡改消息后会不匹配）
    h_verify = hmac.new(key, message.encode(), hashlib.sha256)
    print(f"验证结果: {h_verify.hexdigest() == h.hexdigest()}")

    # 实际应用：API签名
    def generate_signature(params, secret):
        """
        生成API签名

        流程:
        1. 按字典序排序参数
        2. 拼接成 k1=v1&k2=v2 格式
        3. 用HMAC签名
        """
        sorted_params = sorted(params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        signature = hmac.new(
            secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    params = {
        "user_id": "12345",
        "action": "login",
        "timestamp": str(int(time.time())),
    }

    signature = generate_signature(params, "your_secret_key")
    print(f"\n📝 API签名示例:")
    print(f"  参数: {params}")
    print(f"  签名: {signature}")

    print("\n💡 HMAC用途:")
    print("  - 验证消息完整性（是否被篡改）")
    print("  - 很多网站的API请求都需要sign参数")


def aes_demo():
    """AES对称加密演示"""
    print("\n" + "=" * 50)
    print("AES对称加密")
    print("=" * 50)

    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad, unpad
        from Crypto.Random import get_random_bytes
    except ImportError:
        print("需要安装: pip install pycryptodome")
        return

    key = b"1234567890123456"  # 16字节密钥（AES-128）
    plaintext = "Hello World!"

    # AES-CBC模式（推荐）
    def encrypt_aes_cbc(plaintext, key):
        """AES-CBC加密"""
        iv = get_random_bytes(AES.block_size)  # 随机初始向量
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded = pad(plaintext.encode(), AES.block_size)
        encrypted = cipher.encrypt(padded)
        return base64.b64encode(iv + encrypted).decode()

    def decrypt_aes_cbc(ciphertext, key):
        """AES-CBC解密"""
        data = base64.b64decode(ciphertext)
        iv = data[:AES.block_size]
        encrypted = data[AES.block_size:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted)
        return unpad(decrypted, AES.block_size).decode()

    encrypted = encrypt_aes_cbc(plaintext, key)
    decrypted = decrypt_aes_cbc(encrypted, key)

    print(f"原文: {plaintext}")
    print(f"加密: {encrypted[:50]}...")
    print(f"解密: {decrypted}")

    print("\n💡 AES对称加密特点:")
    print("  - 加密解密用同一密钥")
    print("  - 速度快，适合大量数据")
    print("  - 密钥传输是难题（用RSA解决）")

    print("\n⚠️  注意事项:")
    print("  - ECB模式不安全，不推荐使用")
    print("  - CBC模式需要IV（初始向量）")
    print("  - 密钥必须是16/24/32字节")


def rsa_demo():
    """RSA非对称加密演示"""
    print("\n" + "=" * 50)
    print("RSA非对称加密")
    print("=" * 50)

    # 生成密钥对
    (public_key, private_key) = rsa.newkeys(2048)

    message = "Hello World"

    # 用公钥加密
    encrypted = rsa.encrypt(message.encode(), public_key)
    encrypted_b64 = base64.b64encode(encrypted).decode()
    print(f"原文: {message}")
    print(f"加密(base64): {encrypted_b64[:50]}...")

    # 用私钥解密
    decrypted = rsa.decrypt(base64.b64decode(encrypted_b64), private_key)
    print(f"解密: {decrypted.decode()}")

    # 签名
    signature = rsa.sign(message.encode(), rsa.PrivateKey.load_pkcs1(private_key.save_pkcs1()), "SHA-256")
    print(f"\n签名: {base64.b64encode(signature).decode()[:50]}...")

    # 验证签名
    verify = rsa.verify(message.encode(), signature, public_key)
    print(f"验证结果: {'✅ 有效' if verify else '❌ 无效'}")

    print("\n💡 RSA特点:")
    print("  - 公钥加密，私钥解密（加密）")
    print("  - 私钥签名，公钥验证（认证）")
    print("  - 速度慢，只适合少量数据")
    print("  - 常用于传输对称加密的密钥")


def sign_params_demo():
    """
    实际场景：生成签名参数

    很多网站的API请求都需要sign参数
    这个函数展示常见的签名生成逻辑
    """
    print("\n" + "=" * 50)
    print("实战: API签名生成")
    print("=" * 50)

    def generate_sign(params: dict, secret_key: str) -> str:
        """
        常见签名算法

        流程:
        1. 按key字典序排序
        2. 拼接成 k1=v1&k2=v2 格式
        3. 拼接上secret_key
        4. MD5/SHA256计算摘要
        """
        sorted_items = sorted(params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_items])
        sign_string = query_string + secret_key
        sign = hashlib.md5(sign_string.encode()).hexdigest()
        return sign

    params = {
        "app_id": "wx1234567890",
        "user_id": "user_001",
        "action": "get_user_info",
        "timestamp": str(int(time.time())),
        "nonce": "random_string_xyz",
    }

    secret_key = "your_secret_key"

    sign = generate_sign(params, secret_key)

    print("原始参数:")
    for k, v in params.items():
        print(f"  {k}: {v}")
    print(f"签名: {sign}")

    print("\n💡 这个模式在很多网站的API中都能看到:")
    print("  - 微信支付")
    print("  - 支付宝")
    print("  - 各种开放平台")


if __name__ == "__main__":
    hash_demo()
    hmac_demo()
    aes_demo()
    rsa_demo()
    sign_params_demo()
