import certifi
from pymongo import MongoClient

from env import env

ca = certifi.where()
client = MongoClient(env.mongo_uri, tlsCAFile=ca)
