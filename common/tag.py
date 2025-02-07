import random
import string
import time
import logging

import common.config as config
import common.api as api


def random_tag(gen_tag, size=1, *args, **kwargs):
    tags = []

    for index in range(0, size):
        address, type, attribute, n_byte = gen_tag(*args, **kwargs)
        tag = {
            "name": api.random_tag_name(),
            "address": address,
            "attribute": attribute,
            "type": type,
            "length": n_byte
        }

        tags.append(tag)
    return tags


def random_type(types):
    return types[random.randint(0, len(types) - 1)]


def random_value(tag, length=0):
    value = None
    if tag['type'] == config.NEU_TYPE_BIT:
        value = random.randint(0, 1)
    elif tag['type'] == config.NEU_TYPE_BOOL:
        tmp = random.randint(0, 1)
        value = True if tmp == 1 else False
    elif tag['type'] == config.NEU_TYPE_INT8:
        value = random.randint(-128, 127)
    elif tag['type'] == config.NEU_TYPE_UINT8:
        value = random.randint(0, 255)
    elif tag['type'] == config.NEU_TYPE_INT16:
        value = random.randint(-32768, 32767)
    elif tag['type'] == config.NEU_TYPE_UINT16:
        value = random.randint(0, 65535)
    elif tag['type'] == config.NEU_TYPE_WORD:
        value = random.randint(0, 65535)
    elif tag['type'] == config.NEU_TYPE_INT32:
        value = random.randint(-2147483648, 2147483647)
    elif tag['type'] == config.NEU_TYPE_UINT32:
        value = random.randint(0, 4294967295)
    elif tag['type'] == config.NEU_TYPE_DWORD:
        value = random.randint(0, 4294967295)
    elif tag['type'] == config.NEU_TYPE_INT64:
        value = random.randint(-9223372036854775808, 9223372036854775807)
    elif tag['type'] == config.NEU_TYPE_UINT64:
        value = random.randint(0, 18446744073709551615)
    elif tag['type'] == config.NEU_TYPE_LWORD:
        value = random.randint(0, 18446744073709551615)
    elif tag['type'] == config.NEU_TYPE_FLOAT:
        value = random.uniform(-1000000, 1000000)
    elif tag['type'] == config.NEU_TYPE_DOUBLE:
        value = random.uniform(-1000000, 1000000)
    elif tag['type'] == config.NEU_TYPE_STRING:
        value = api.random_string(length)
    elif tag['type'] == config.NEU_TYPE_BYTES:
        for i in range(0, length):
            tmp = random.randint(0, 255)
            value.append(tmp)
    return value


def tag_value_compare(tag, value):
    if tag['type'] == config.NEU_TYPE_BIT:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_BOOL:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_INT8:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_UINT8:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_INT16:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_UINT16:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_WORD:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_INT32:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_UINT32:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_DWORD:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_INT64:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_UINT64:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_LWORD:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_FLOAT:
        return abs(value - tag['value']) < 0.1
    elif tag['type'] == config.NEU_TYPE_DOUBLE:
        return abs(value - tag['value']) < 0.1
    elif tag['type'] == config.NEU_TYPE_STRING:
        return value == tag['value']
    elif tag['type'] == config.NEU_TYPE_BYTES:
        return value == tag['value']
    return value


def get_write_tags(tags, n=1):
    tv = []
    ttags = list(
        filter(lambda tag: tag['attribute'] == config.NEU_TAG_ATTRIBUTE_RW, tags))
    for index in range(0, n):
        t = ttags[random.randint(0, len(ttags) - 1)]
        v = random_value(t, t['length'])
        tv.append((t, v))

    return tv


def get_write_tag(tags):
    tv = get_write_tags(tags)
    return tv[0][0], tv[0][1]


def read_and_check(c, request_name, node_name, group_name):
    with c.read_tags(node_name, group_name) as response:
        response.request_meta['name'] = request_name
        if response.status_code == 200:
            tags = response.json()['tags']
            result = list(
                filter(lambda tag: tag.get('value') is None, tags))
            if len(result) == 0:
                response.success()
            else:
                response.failure("read tags error")
        else:
            response.failure("Failed to read tags")


def write_and_check(c, tags, map_tags, request_name, node_name, group_name):
    tag, value = get_write_tag(tags)
    with c.write_tag(node_name, group_name, tag['name'], value) as response:
        response.request_meta['name'] = request_name
        if response.status_code == 200:
            time.sleep(0.15)  # 0.15-0.2
            c.read_and_update_tags(
                node_name, group_name, map_tags)
            if tag_value_compare(map_tags[tag['name']], value):
                response.success()
            else:
                logging.warning("write %s %s tag %s %s value %s(%s) error", node_name, group_name,
                                tag['name'], tag['address'], value, map_tags[tag['name']]['value'])
                response.failure("write tag error")
        else:
            logging.warning("write error %s %s %s %s %s", node_name, group_name, tags['name'],
                            response.status_code, response.json())
            response.failure("Failed to write tags")
