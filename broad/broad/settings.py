from __future__ import absolute_import

BOT_NAME = 'broadspider'

SPIDER_MODULES = ['broad.spiders']
NEWSPIDER_MODULE = 'broad.spiders'

CLOSESPIDER_ITEMCOUNT = 800
RETRY_ENABLED = False
COOKIES_ENABLED = True

LOGSTATS_INTERVAL = 3
LOG_LEVEL = 'INFO'
MEMDEBUG_ENABLED = True
CONCURRENT_REQUESTS = 120

AUTOTHROTTLE_ENABLED = True
REACTOR_THREADPOOL_MAXSIZE = 20

SCHEDULER_PRIORITY_QUEUE = 'scrapy.pqueues.DownloaderAwarePriorityQueue'

SCRAPY_BENCH_RANDOM_PAYLOAD_SIZE = None

EXTENSIONS = {'broad.latencies.latencies.Latencies': 300}
LATENCIES_INTERVAL = 2

MONGODB_URI = 'mongodb://localhost:27017'
MONGODB_DATABASE = 'scrapy'
MONGODB_COLLECTION = 'news'

ITEM_PIPELINES = {
    'broad.mongosync.mongosync.MongoDBPipeline': 300,
    #'broad.asyncpipe.pipelines.mongo.MongoPipeline': 300,
}

SPIDER_MIDDLEWARES = {
    'scrapy_bench.middlewares.RandomPayloadMiddleware': 1000,
}

try:
    from .local_settings import *
except ImportError:
    pass
