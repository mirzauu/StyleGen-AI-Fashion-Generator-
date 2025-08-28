# from fastapi.testclient import TestClient
# from app.main import app
# from app.models.model import Model
# from app.models.model_image import ModelImage
# from app.schemas.model import ModelCreate, ModelUpdate
# from sqlalchemy.orm import Session
# from app.database import get_db

# client = TestClient(app)

# def test_create_model(db: Session):
#     model_data = ModelCreate(name="Test Model", description="A test model.")
#     response = client.post("/models/", json=model_data.dict())
#     assert response.status_code == 201
#     assert response.json()["name"] == model_data.name

# def test_get_model(db: Session):
#     model = Model(name="Test Model", description="A test model.")
#     db.add(model)
#     db.commit()
#     db.refresh(model)

#     response = client.get(f"/models/{model.id}")
#     assert response.status_code == 200
#     assert response.json()["name"] == model.name

# def test_list_models(db: Session):
#     response = client.get("/models/")
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)

# def test_update_model(db: Session):
#     model = Model(name="Test Model", description="A test model.")
#     db.add(model)
#     db.commit()
#     db.refresh(model)

#     update_data = ModelUpdate(name="Updated Model", description="An updated test model.")
#     response = client.put(f"/models/{model.id}", json=update_data.dict())
#     assert response.status_code == 200
#     assert response.json()["name"] == update_data.name

# def test_delete_model(db: Session):
#     model = Model(name="Test Model", description="A test model.")
#     db.add(model)
#     db.commit()
#     db.refresh(model)

#     response = client.delete(f"/models/{model.id}")
#     assert response.status_code == 204

#     response = client.get(f"/models/{model.id}")
#     assert response.status_code == 404