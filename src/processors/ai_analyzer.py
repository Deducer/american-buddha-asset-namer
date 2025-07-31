"""
AI-powered content analyzer for images and videos
"""

import base64
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import cv2
from PIL import Image
import io
import requests
from utils.logger import get_logger

logger = get_logger("AIAnalyzer")

class AIAnalyzer:
    """Analyzes media content using OpenAI Vision API"""
    
    def __init__(self, api_key: str = None):
        """Initialize the AI analyzer"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if self.api_key and self.api_key != "your-api-key-here":
            # Store API key for direct use
            self.client = None
            logger.info("API key stored for direct API calls")
        else:
            logger.warning("No valid OpenAI API key provided")
    
    def analyze_image(self, image_path: Path, custom_prompt: str = None) -> Dict[str, Any]:
        """Analyze an image and return content description"""
        if not self.api_key or self.api_key == "your-api-key-here":
            return self._fallback_analysis(image_path, is_video=False)
        
        try:
            # Read and encode the image
            image_data = self._encode_image(image_path)
            
            # Prepare the prompt
            prompt = custom_prompt or self._get_default_prompt()
            
            # Call OpenAI Vision API directly using requests
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                payload = {
                    "model": "gpt-4o",  # Updated model that supports vision
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}",
                                        "detail": "auto"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 150,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code != 200:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    return self._fallback_analysis(image_path, is_video=False)
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                logger.info("Successfully analyzed image with OpenAI Vision API")
                return self._parse_ai_response(content)
                
            except Exception as api_error:
                logger.error(f"API call error: {api_error}")
                return self._fallback_analysis(image_path, is_video=False)
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return self._fallback_analysis(image_path, is_video=False)
    
    def analyze_video(self, video_path: Path, custom_prompt: str = None) -> Dict[str, Any]:
        """Analyze a video by extracting key frames"""
        if not self.client:
            return self._fallback_analysis(video_path, is_video=True)
        
        try:
            # Extract key frames from video
            frames = self._extract_video_frames(video_path)
            
            if not frames:
                return self._fallback_analysis(video_path, is_video=True)
            
            # Analyze the most representative frame (middle one)
            middle_frame = frames[len(frames) // 2]
            
            # Convert frame to image
            temp_image_path = Path("temp") / f"frame_{video_path.stem}.jpg"
            temp_image_path.parent.mkdir(exist_ok=True)
            cv2.imwrite(str(temp_image_path), middle_frame)
            
            # Analyze the frame
            result = self.analyze_image(temp_image_path, custom_prompt)
            result["is_video"] = True
            result["duration"] = self._get_video_duration(video_path)
            
            # Clean up
            temp_image_path.unlink(missing_ok=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing video {video_path}: {e}")
            return self._fallback_analysis(video_path, is_video=True)
    
    def _encode_image(self, image_path: Path) -> str:
        """Encode image to base64"""
        # Open and resize if needed
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large
            max_size = 1024
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Save to bytes
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            
            return base64.b64encode(buffer.read()).decode('utf-8')
    
    def _extract_video_frames(self, video_path: Path, num_frames: int = 5) -> List:
        """Extract key frames from video"""
        frames = []
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames > 0:
                # Calculate frame indices to extract
                indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
                
                for idx in indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                    ret, frame = cap.read()
                    if ret:
                        frames.append(frame)
            
            cap.release()
            
        except Exception as e:
            logger.error(f"Error extracting frames from {video_path}: {e}")
        
        return frames
    
    def _get_video_duration(self, video_path: Path) -> float:
        """Get video duration in seconds"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            
            if fps > 0:
                return frame_count / fps
        except:
            pass
        
        return 0.0
    
    def _get_default_prompt(self) -> str:
        """Get the default analysis prompt"""
        return """Analyze this image and provide a structured description in JSON format with the following fields:
        - description: A brief, descriptive summary (2-5 words) suitable for a filename
        - scene_type: The type of scene (e.g., interview, b-roll, landscape, closeup)
        - subjects: Main subjects or objects in the image
        - location: Location or setting if identifiable
        - action: What's happening in the image
        - mood: The overall mood or atmosphere
        - technical: Technical aspects (e.g., lighting, composition)
        
        Keep the description concise and filename-friendly. Return only valid JSON."""
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                data = json.loads(response)
                return {
                    "description": data.get("description", "untitled"),
                    "scene_type": data.get("scene_type", "general"),
                    "subjects": data.get("subjects", []),
                    "location": data.get("location", "unknown"),
                    "action": data.get("action", "static"),
                    "mood": data.get("mood", "neutral"),
                    "technical": data.get("technical", {}),
                    "ai_analyzed": True
                }
        except:
            pass
        
        # Fallback to text parsing
        return {
            "description": self._extract_description(response),
            "scene_type": "general",
            "subjects": [],
            "location": "unknown",
            "action": "static",
            "mood": "neutral",
            "technical": {},
            "ai_analyzed": True
        }
    
    def _extract_description(self, text: str) -> str:
        """Extract a filename-friendly description from text"""
        # Take first few words and clean them
        words = text.split()[:5]
        description = "_".join(words)
        
        # Remove special characters
        description = "".join(c for c in description if c.isalnum() or c in "_-")
        
        return description.lower() or "untitled"
    
    def _fallback_analysis(self, file_path: Path, is_video: bool) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        return {
            "description": file_path.stem,
            "scene_type": "video" if is_video else "image",
            "subjects": [],
            "location": "unknown",
            "action": "unknown",
            "mood": "unknown",
            "technical": {},
            "ai_analyzed": False,
            "is_video": is_video
        }