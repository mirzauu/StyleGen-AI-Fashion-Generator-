# from fastapi.testclient import TestClient
# from app.main import app
# from app.models.task import Task
# from app.models.batch import Batch
# from app.models.generated_image import GeneratedImage
# from app.models.model import Model
# from app.models.user import User
# from app.schemas.task import TaskCreate
# from app.schemas.batch import BatchCreate
# from app.schemas.generated_image import GeneratedImageCreate

# client = TestClient(app)

# def test_create_task():
#     response = client.post("/tasks/", json={"model_id": 1, "name": "Test Task"})
#     assert response.status_code == 201
#     assert response.json()["name"] == "Test Task"

# def test_get_task():
#     response = client.get("/tasks/1")
#     assert response.status_code == 200
#     assert "name" in response.json()

# def test_create_batch():
#     response = client.post("/tasks/1/batches/", json={"garment_image_url": "http://example.com/garment.jpg"})
#     assert response.status_code == 201
#     assert response.json()["garment_image_url"] == "http://example.com/garment.jpg"

# def test_get_batch():
#     response = client.get("/batches/1")
#     assert response.status_code == 200
#     assert "status" in response.json()

# def test_generate_images():
#     response = client.post("/batches/1/generate")
#     assert response.status_code == 202
#     assert "task_id" in response.json()

# def test_delete_task():
#     response = client.delete("/tasks/1")
#     assert response.status_code == 204
#     assert response.json() == {}