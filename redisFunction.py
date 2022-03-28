import redis


POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)


def set_redis_connection(curr_pool=POOL) -> redis.Redis:
    """
    need to close manually
    :param curr_pool:
    :return:
    """
    r = redis.Redis(connection_pool=curr_pool)
    return r


def shut_all_redis_connection(curr_pool=POOL) -> int:
    try:
        curr_pool.disconnect()
        return 0
    except Exception as e:
        print(e)
        return -1