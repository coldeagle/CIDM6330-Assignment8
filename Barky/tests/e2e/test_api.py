import json
import os
from pathlib import Path

import pytest
import requests
from barkylib import config
from barkylib.domain.models import Bookmark


def test_api_works(test_client):
    url = config.get_api_url()+'/api/'
    r = test_client.get(f"{url}")

    assert r.status_code == 200
    assert b"Barky API" in r.data


def test_api_add(test_client):
    cleanup(test_client, 1)
    url = config.get_api_url()+'/api/add'
    r = add_bookmark(test_client, 1)

    cleanup(test_client, 1)

    assert r.status_code == 201


def test_get_all(test_client):
    cleanup(test_client, 1)
    cleanup(test_client, 2)

    add_bookmark(test_client, 1)
    add_bookmark(test_client, 2)

    url = config.get_api_url()+'/api/all'

    r = test_client.get(f'{url}')

    data = json.loads(r.data)

    assert len(data) == 2

    cleanup(test_client, 1)
    cleanup(test_client, 2)


def test_edit(test_client):
    index = 1
    cleanup(test_client, index)
    add_bookmark(test_client, index)
    bmark = get_test_bookmark(test_client, index)
    url = config.get_api_url()+'/api/edit/'+str(bmark['id'])
    index = 2

    r = test_client.post(f"{url}", json=json.loads('{"title":"'+str(index)+'", "url":"http://test'+str(index)+'.com", "notes":"test'+str(index)+'"}'))
    assert r.status_code == 201

    bmark = get_test_bookmark(test_client, index)

    assert str(bmark['title']) == str(index)

    cleanup(test_client, index)


def test_get_one(test_client):
    index = 1
    cleanup(test_client, index)
    add_bookmark(test_client, index)
    bmark = get_test_bookmark(test_client, index)

    url = config.get_api_url()+'/api/one/'+str(bmark['id'])

    r = test_client.get(f'{url}')

    assert bmark['title'] == json.loads(r.data)['title']


def add_bookmark(test_client, index):
    url = config.get_api_url()+'/api/add'
    r = test_client.post(f"{url}", json=json.loads('{"title":"'+str(index)+'", "url":"http://test'+str(index)+'.com", "notes":"test'+str(index)+'"}'))
    return r


def get_test_bookmark(test_client, index) -> Bookmark:
    url = config.get_api_url()+'/api/first/title/'+str(index)+'/title'
    r = test_client.get(f'{url}')

    if r.data is not None:
        try:
            return json.loads(r.data)
        except Exception as e:
            print(e)
    else:
        return None


def cleanup(test_client, index):
    bmark = get_test_bookmark(test_client, index)
    try:
        url = config.get_api_url()+'/api/delete/'+str(bmark['id'])
        r = test_client.get(f'{url}')
    except Exception as e:
        print(e)


def delete_db():
    path = Path(__file__).parent.parent.parent

    try:
        os.remove(path / "src/barkylib/bookmarks_test.db")
    except Exception as e:
        print(e)
    try:
        os.remove(path / "src/barkylib/bookmarks.db")
    except Exception as e:
        print(e)

    path = Path(__file__).parent.parent
    try:
        os.remove(path/ "bookmarks.db")
    except Exception as e:
        print(e)