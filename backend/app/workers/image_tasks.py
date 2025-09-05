from app.services.image_generation import generate_images
from app.models import Batch, GeneratedImage, Model, ModelImage, GarmentImage
from app.database import SessionLocal
import os
import time
import asyncio
from typing import Dict, List

def _configure_fal():
    """Configure fal.ai client with API key"""
    try:
        import fal_client as fal
        fal_key = os.getenv("FAL_KEY")
        if not fal_key:
            raise ValueError("FAL_KEY environment variable is not set")
        
        # Set the API key as environment variable for fal
        os.environ["FAL_KEY"] = fal_key
        return fal
    except ImportError:
        raise ImportError("fal package is not installed. Please install it with: pip install fal")
    except Exception as e:
        raise Exception(f"Failed to configure fal.ai client: {str(e)}")

fal = _configure_fal()

def on_queue_update(update):
    if isinstance(update, fal.InProgress):
        for log in update.logs:
           print(log["message"])
           
           
def generate_images_task(batch_id: int):
    """
    Generate fashion try-on images using fal.ai API with long polling
    
    Args:
        batch_id (int): The batch ID to process
        poses (list): List of poses to generate images for
        
    """
    # Configure fal.ai client
    
    
    db = SessionLocal()
    try:
        # Get batch information
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")
        
        # Update batch status to processing
        batch.status = 'processing'
        db.commit()
        
        # Get all garment images from the batch
        if not batch.garment_images:
            raise ValueError("No garment images found for this batch")
        
        # Get the model related to this task
        task = batch.task
        if not task or not task.model_id:
            # Fallback to default model image if no model is associated with the task
            default_model_url = "https://images.easelai.com/tryon/woman.webp"
            print(f"No model associated with this task, using default model image: {default_model_url}")
            models = [{
                "id": None,
                "model_images": [{
                    "url": default_model_url,
                    "pose_label": "default"
                }]
            }]
        else:
            # Get the specific model for this task
            model = db.query(Model).filter(Model.id == task.model_id).first()
            if not model:
                # Fallback to default model image if model not found
                default_model_url = "https://images.easelai.com/tryon/woman.webp"
                print(f"Model {task.model_id} not found, using default model image: {default_model_url}")
                models = [{
                    "id": None,
                    "model_images": [{
                        "url": default_model_url,
                        "pose_label": "default"
                    }]
                }]
            else:
                # Ensure model has at least one model image
                if not model.model_images:
                    print(f"Warning: Model {model.id} has no model images")
                models = [model]
        
        generated_images = {}
        
        # For each garment image, generate images with each model
        for garment_image in batch.garment_images:
            garment_image_url = garment_image.image_url
            
            # Validate garment URL
            if not garment_image_url or garment_image_url.strip() == "":
                print(f"Warning: Garment image {garment_image.id} has empty URL, skipping")
                continue
                
            print(f"Processing garment image: {garment_image_url}")
            
            # For each model, generate images with this garment
            for model in models:
                model_id = getattr(model, 'id', None)
                model_images = getattr(model, 'model_images', [{'url': "https://images.easelai.com/tryon/woman.webp", 'pose_label': 'default'}])
                
                for model_image in model_images:
                    # Check if model_image is a dictionary or an ORM object
                    if isinstance(model_image, dict):
                        model_image_url = model_image['url']
                        pose_label = model_image['pose_label']
                    else:
                        # It's an ORM object, use attribute access
                        model_image_url = model_image.url
                        pose_label = model_image.pose_label
                    
                    # Validate model URL
                    if not model_image_url or model_image_url.strip() == "":
                        print(f"Warning: Model image has empty URL, skipping")
                        continue
                        
                    print(f"Using model image: {model_image_url} with pose: {pose_label}")
                    
                    try:
                        # Prepare the request payload
                        request_payload = {
                            
                                "full_body_image": model_image_url,
                                "clothing_image": garment_image_url
                 
                            }
                            
                        
                        
                        # Debug: Print the request payload
                        print(f"Debug - Request payload: {request_payload}")
                        
                        # Call fal.ai fashion try-on API with long polling
                        # Clean URLs to ensure no extra spaces or backticks
           
                        result = fal.subscribe("easel-ai/fashion-tryon", arguments=request_payload,with_logs=True,on_queue_update=on_queue_update,)
                        print(f"result -  payload: {result}")
                        # For testing, use a mock result
                        # result = {'payload': {'image': {'url': "https://images.easelai.com/tryon/woman.webp"}}}
                        
                        # Extract the generated image URL from the result
                        if 'image' in result and 'url' in result['image']:
                            generated_image_url = result['image']['url'].strip().replace('`', '')
                            key = f"garment_{garment_image.id}_model_{model_id}_pose_{pose_label}"
                            generated_images[key] = generated_image_url
                            
                            # Save to database
                            generated_image = GeneratedImage(
                                garment_image_id=garment_image.id,
                                model_id=model_id,
                                output_url=generated_image_url,
                                pose_label=pose_label
                            )
                            db.add(generated_image)
                            db.commit()
                        
                    except Exception as e:
                        print(f"Error generating image for garment {garment_image.id} with model {model_id} and pose {pose_label}: {str(e)}")
                        # Continue with other combinations even if one fails
                        continue
        
        # Update batch status to done
        batch.status = 'done'
        db.commit()
        
        return generated_images
        
    except Exception as e:
        # Update batch status to failed
        if batch:
            batch.status = 'failed'
            db.commit()
        raise e
    finally:
        db.close()

def generate_images_task_with_queue(batch_id: int):
    """
    Generate fashion try-on images using fal.ai API with queue and long polling
    
    Args:
        batch_id (int): The batch ID to process
        poses (list): List of poses to generate images for
    """
    # Configure fal.ai client
    fal = _configure_fal()
    
    db = SessionLocal()
    try:
        # Get batch information
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")
        
        # Update batch status to processing
        batch.status = 'processing'
        db.commit()
        
        # Get all garment images from the batch
        if not batch.garment_images:
            raise ValueError("No garment images found for this batch")
        
        # Get the model related to this task
        task = batch.task
        if not task or not task.model_id:
            # Fallback to default model image if no model is associated with the task
            default_model_url = "https://images.easelai.com/tryon/woman.webp"
            print(f"No model associated with this task, using default model image: {default_model_url}")
            models = [{
                "id": None,
                "model_images": [{
                    "url": default_model_url,
                    "pose_label": "default"
                }]
            }]
        else:
            # Get the specific model for this task
            model = db.query(Model).filter(Model.id == task.model_id).first()
            if not model:
                # Fallback to default model image if model not found
                default_model_url = "https://images.easelai.com/tryon/woman.webp"
                print(f"Model {task.model_id} not found, using default model image: {default_model_url}")
                models = [{
                    "id": None,
                    "model_images": [{
                        "url": default_model_url,
                        "pose_label": "default"
                    }]
                }]
            else:
                # Ensure model has at least one model image
                if not model.model_images:
                    print(f"Warning: Model {model.id} has no model images")
                models = [model]
        
        generated_images = {}
        
        # For each garment image, generate images with each model
        for garment_image in batch.garment_images:
            garment_image_url = garment_image.image_url
            
            # Validate garment URL
            if not garment_image_url or garment_image_url.strip() == "":
                print(f"Warning: Garment image {garment_image.id} has empty URL, skipping")
                continue
                
            print(f"Processing garment image: {garment_image_url}")
            
            # For each model, generate images with this garment
            for model in models:
                model_id = getattr(model, 'id', None)
                model_images = getattr(model, 'model_images', [{'url': "https://images.easelai.com/tryon/woman.webp", 'pose_label': 'default'}])
                
                for model_image in model_images:
                    # Check if model_image is a dictionary or an ORM object
                    if isinstance(model_image, dict):
                        model_image_url = model_image['url']
                        pose_label = model_image['pose_label']
                    else:
                        # It's an ORM object, use attribute access
                        model_image_url = model_image.url
                        pose_label = model_image.pose_label
                    
                    # Validate model URL
                    if not model_image_url or model_image_url.strip() == "":
                        print(f"Warning: Model image has empty URL, skipping")
                        continue
                        
                    print(f"Using model image: {model_image_url} with pose: {pose_label}")
                    
                    try:
                        # Prepare the request payload
                        request_payload = {
                            "input": {
                                "full_body_image": model_image_url,
                                "clothing_image": garment_image_url,
                                "gender": "female"  # Default to female, can be made configurable
                            }
                        }
                        
                        # Debug: Print the request payload
                        print(f"Debug - Queue request payload: {request_payload}")
                        
                        # Clean URLs to ensure no extra spaces or backticks
                        request_payload['input']['full_body_image'] = request_payload['input']['full_body_image'].strip().replace('`', '')
                        request_payload['input']['clothing_image'] = request_payload['input']['clothing_image'].strip().replace('`', '')
                        
                        # Submit request to queue
                        queue_result = fal.queue.submit("easel-ai/fashion-tryon", request_payload)
                        
                        request_id = queue_result.request_id
                        
                        # Long polling to wait for completion
                        max_attempts = 12  # Maximum 1 minute (12 * 5 seconds)
                        attempt = 0
                        
                        while attempt < max_attempts:
                            # Check status
                            status = fal.queue.status("easel-ai/fashion-tryon", {
                                "requestId": request_id,
                                "logs": True
                            })
                            
                            if status['status'] == "COMPLETED":
                                # Get the result
                                result = fal.queue.result("easel-ai/fashion-tryon", {
                                    "requestId": request_id
                                })
                                
                                if 'payload' in result and 'image' in result['payload'] and 'url' in result['payload']['image']:
                                    # Clean the URL by removing backticks and extra spaces
                                    generated_image_url = result['payload']['image']['url'].strip().replace('`', '')
                                    key = f"garment_{garment_image.id}_model_{model_id}_pose_{pose_label}"
                                    generated_images[key] = generated_image_url
                                    
                                    # Save to database
                                    generated_image = GeneratedImage(
                                        garment_image_id=garment_image.id,
                                        model_id=model_id,
                                        output_url=generated_image_url,
                                        pose_label=pose_label
                                    )
                                    db.add(generated_image)
                                    db.commit()
                                
                                break
                            elif status['status'] == "FAILED":
                                print(f"Request failed for garment {garment_image.id} with model {model_id} and pose {pose_label}: {status}")
                                break
                            else:
                                # Wait 5 seconds before checking again
                                time.sleep(5)
                                attempt += 1
                        
                        if attempt >= max_attempts:
                            print(f"Timeout waiting for garment {garment_image.id} with model {model_id} and pose {pose_label} to complete")
                        
                    except Exception as e:
                        print(f"Error generating image for garment {garment_image.id} with model {model_id} and pose {pose_label}: {str(e)}")
                        continue
        
        # Update batch status to done
        batch.status = 'done'
        db.commit()
        
        return generated_images
        
    except Exception as e:
        if batch:
            batch.status = 'failed'
            db.commit()
        raise e
    finally:
        db.close()

def start_fashion_tryon_task(batch_id: int, poses: list):
    """
    Start the fashion try-on task with long polling
    """
    return generate_images_task(batch_id, poses)

def start_fashion_tryon_task_with_queue(batch_id: int, poses: list):
    """
    Start the fashion try-on task with queue and long polling
    """
    return generate_images_task_with_queue(batch_id, poses)