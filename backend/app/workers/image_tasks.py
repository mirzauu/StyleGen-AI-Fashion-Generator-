from app.services.image_generation import generate_images
from app.models import Batch, GeneratedImage
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

def generate_images_task(batch_id: int, poses: list):
    """
    Generate fashion try-on images using fal.ai API with long polling
    
    Args:
        batch_id (int): The batch ID to process
        poses (list): List of pose labels (e.g., ["front", "side", "back"])
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
        
        # Get the garment image URL from the batch
        if not batch.garment_images:
            raise ValueError("No garment images found for this batch")
        
        # Get the first garment image URL
        garment_image_url = batch.garment_images[0].image_url
        
        # For each pose, we need a full body image of a person
        # In a real implementation, you might have different model images for different poses
        # For now, we'll use a default model image
        model_image_url = "https://images.easelai.com/tryon/woman.webp"  # Default model image
        
        # Debug: Print the URLs to see what we're getting
        print(f"Debug - Garment image URL: {garment_image_url}")
        print(f"Debug - Model image URL: {model_image_url}")
        
        # Validate URLs
        if not garment_image_url or garment_image_url.strip() == "":
            raise ValueError("Garment image URL is empty or None")
        
        if not model_image_url or model_image_url.strip() == "":
            raise ValueError("Model image URL is empty or None")
        
        generated_images = {}
        
        for pose in poses:
            try:
                # Prepare the request payload
                request_payload = {
                    "input": {
                        "full_body_image": model_image_url,
                        "clothing_image": garment_image_url,
                        "gender": "female"  # Default to female, can be made configurable
                    },
                    "logs": True
                }
                
                # Debug: Print the request payload
                print(f"Debug - Request payload: {request_payload}")
                
                # Call fal.ai fashion try-on API with long polling
                result = fal.subscribe("easel-ai/fashion-tryon", request_payload)
                
                # Extract the generated image URL from the result
                if result.data and result.data.image:
                    generated_image_url = result.data.image.url
                    generated_images[pose] = generated_image_url
                    
                    # Save to database
                    generated_image = GeneratedImage(
                        batch_id=batch.id, 
                        output_url=generated_image_url, 
                        pose_label=pose
                    )
                    db.add(generated_image)
                
            except Exception as e:
                print(f"Error generating image for pose {pose}: {str(e)}")
                # Continue with other poses even if one fails
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

def generate_images_task_with_queue(batch_id: int, poses: list):
    """
    Generate fashion try-on images using fal.ai API with queue and long polling
    """
    # Configure fal.ai client
    fal = _configure_fal()
    
    db = SessionLocal()
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise ValueError("Batch not found")
        
        batch.status = 'processing'
        db.commit()
        
        # Get the garment image URL from the batch
        if not batch.garment_images:
            raise ValueError("No garment images found for this batch")
        
        # Get the first garment image URL
        garment_image_url = batch.garment_images[0].image_url
        model_image_url = "https://images.easelai.com/tryon/woman.webp"
        
        # Debug: Print the URLs to see what we're getting
        print(f"Debug - Garment image URL: {garment_image_url}")
        print(f"Debug - Model image URL: {model_image_url}")
        
        # Validate URLs
        if not garment_image_url or garment_image_url.strip() == "":
            raise ValueError("Garment image URL is empty or None")
        
        if not model_image_url or model_image_url.strip() == "":
            raise ValueError("Model image URL is empty or None")
        
        generated_images = {}
        
        for pose in poses:
            try:
                # Prepare the request payload
                request_payload = {
                    "input": {
                        "full_body_image": model_image_url,
                        "clothing_image": garment_image_url,
                        "gender": "female"
                    }
                }
                
                # Debug: Print the request payload
                print(f"Debug - Queue request payload: {request_payload}")
                
                # Submit request to queue
                queue_result = fal.queue.submit("easel-ai/fashion-tryon", request_payload)
                
                request_id = queue_result.request_id
                
                # Long polling to wait for completion
                max_attempts = 1  # Maximum 5 minutes (60 * 5 seconds)
                attempt = 0
                
                while attempt < max_attempts:
                    # Check status
                    status = fal.queue.status("easel-ai/fashion-tryon", {
                        "requestId": request_id,
                        "logs": True
                    })
                    
                    if status.status == "COMPLETED":
                        # Get the result
                        result = fal.queue.result("easel-ai/fashion-tryon", {
                            "requestId": request_id
                        })
                        
                        if result.data and result.data.image:
                            generated_image_url = result.data.image.url
                            generated_images[pose] = generated_image_url
                            
                            # Save to database
                            generated_image = GeneratedImage(
                                batch_id=batch.id, 
                                output_url=generated_image_url, 
                                pose_label=pose
                            )
                            db.add(generated_image)
                        
                        break
                    elif status.status == "FAILED":
                        print(f"Request failed for pose {pose}: {status}")
                        break
                    else:
                        # Wait 5 seconds before checking again
                        time.sleep(5)
                        attempt += 1
                
                if attempt >= max_attempts:
                    print(f"Timeout waiting for pose {pose} to complete")
                
            except Exception as e:
                print(f"Error generating image for pose {pose}: {str(e)}")
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