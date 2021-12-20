import json

import pytest

from app import crud
from app.google import delete_file

# https://testdriven.io/blog/fastapi-crud/
# https://github.com/testdrivenio/fastapi-crud-async/blob/master/src/tests/test_notes.py


def test_ping(test_app):
    response = test_app.get("/healthcheck/")
    assert response.status_code == 200
    assert response.json() == True


def test_create_asset(test_app, monkeypatch):
    test_response_payload = {
        "_id": "dsasadas",
        "name": None,
        "webContentLink": "sdafasdfsadfsadf",
        "webViewLink": "asdlfksdlflñsadf",
        "thumbnailLink": None,
        "version": None,
        "mimeType": None,
        "size": None,
        "iconLink": None,
        "createdTime": None,
        "modifiedTime": None,

    }

    async def mock_create(payload):
        # Google file has been created (delete it)
        google_id = payload["id"]
        delete_file(google_id)
        return {
            "_id": "dsasadas",
            "webContentLink": "sdafasdfsadfsadf",
            "webViewLink": "asdlfksdlflñsadf"
        }

    monkeypatch.setattr(crud, "create", mock_create)
    files_data = {'file': ("demoooo.docx", open("./app/tests/demo.docx", "rb"))}
    response = test_app.post("/api/v1/assets/", files=files_data)

    assert response.status_code == 201
    assert response.json() == test_response_payload


"""
def test_create_asset_invalid_json(test_app):
    response = test_app.post("/api/v1/assets/", data=json.dumps({"title": "something"}))
    assert response.status_code == 422

    response = test_app.post("/api/v1/assets/", data=json.dumps({"title": "1", "description": "2"}))
    assert response.status_code == 422


def test_read_asset(test_app, monkeypatch):
    test_data = {"id": 1, "title": "something", "description": "something else"}

    async def mock_get(id):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/api/v1/assets/1")
    assert response.status_code == 200
    assert response.json() == test_data


def test_read_asset_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/api/v1/assets/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Asset not found"

    response = test_app.get("/api/v1/assets/0")
    assert response.status_code == 422


def test_read_all_assets(test_app, monkeypatch):
    test_data = [
        {"title": "something", "description": "something else", "id": 1},
        {"title": "someone", "description": "someone else", "id": 2},
    ]

    async def mock_get_all():
        return test_data

    monkeypatch.setattr(crud, "get_all", mock_get_all)

    response = test_app.get("/api/v1/assets/")
    assert response.status_code == 200
    assert response.json() == test_data


def test_update_asset(test_app, monkeypatch):
    test_update_data = {"title": "someone", "description": "someone else", "id": 1}

    async def mock_get(id):
        return True

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(id, payload):
        return 1

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put("/api/v1/assets/1/", data=json.dumps(test_update_data))
    assert response.status_code == 200
    assert response.json() == test_update_data


@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"description": "bar"}, 422],
        [999, {"title": "foo", "description": "bar"}, 404],
        [1, {"title": "1", "description": "bar"}, 422],
        [1, {"title": "foo", "description": "1"}, 422],
        [0, {"title": "foo", "description": "bar"}, 422],
    ],
)
def test_update_asset_invalid(test_app, monkeypatch, id, payload, status_code):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.put(f"/api/v1/assets/{id}/", data=json.dumps(payload),)
    assert response.status_code == status_code


def test_remove_asset(test_app, monkeypatch):
    test_data = {"title": "something", "description": "something else", "id": 1}

    async def mock_get(id):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_delete(id):
        return id

    monkeypatch.setattr(crud, "delete", mock_delete)

    response = test_app.delete("/api/v1/assets/1/")
    assert response.status_code == 200
    assert response.json() == test_data


def test_remove_asset_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.delete("/api/v1/assets/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Asset not found"

    response = test_app.delete("/api/v1/assets/0/")
    assert response.status_code == 422
"""
