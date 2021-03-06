import os

REDISHOST = os.getenv('REDISHOST', 'localhost')
REDISPORT = os.getenv('REDISPORT', '6379')
REDISDB = os.getenv('REDISDB', 0)
REDISPASSWD = os.getenv('REDISPASSWD', '')
SITEURL = os.getenv('SITEURL', 'http://example.com')
KEYLENGTH = os.getenv('KEYLENGTH', 8)

LISTENHOST = os.getenv('LISTENHOST', '127.0.0.1')
LISTENPORT = os.getenv('LISTENPORT', 5000)
