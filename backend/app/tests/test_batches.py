# from fastapi.testclient import TestClient
# from app.main import app
# from app.models.batch import Batch
# from app.models.task import Task
# from app.models.generated_image import GeneratedImage
# from app.models.model import Model
# from app.models.model_image import ModelImage
# from app.models.user import User
# from app.models.subscription import Subscription
# from app.models.plan import Plan

# client = TestClient(app)

# def test_create_batch():
#     # Assuming a user is already authenticated and a task exists
#     response = client.post("/tasks/1/batches/", json={"garment_image_url": "http://example.com/garment.jpg"})
#     assert response.status_code == 201
#     assert "id" in response.json()

# def test_get_batch_status():
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

# def test_batch_creation_invalid_data():
#     response = client.post("/tasks/1/batches/", json={"garment_image_url": ""})
#     assert response.status_code == 422  # Unprocessable Entity for invalid data

# def test_get_nonexistent_batch():
#     response = client.get("/batches/999")
#     assert response.status_code == 404  # Not Found for nonexistent batch