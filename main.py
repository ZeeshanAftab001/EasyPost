import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from requests.auth import HTTPBasicAuth
import base64

app = Flask(__name__)

# Your Twilio credentials
TWILIO_ACCOUNT_SID = "ACfacc70a6d5c2bd964d785762340381c7"  # Your Account SID from the logs
TWILIO_AUTH_TOKEN = "55da26003908c39fefae2b10628f0a0f"  # ⚠️ Replace with your actual Auth Token

MEDIA_DIR = "user_media"
os.makedirs(MEDIA_DIR, exist_ok=True)

def download_media_with_auth(media_url, media_type, message_sid):
    """Download media from Twilio with authentication"""
    try:
        print(f"📥 Downloading: {media_type} from {media_url}")
        
        # Use HTTP Basic Auth with Twilio credentials
        auth = HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # For videos, use streaming to handle larger files
        response = requests.get(media_url, auth=auth, timeout=60, stream=True)
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            # Enhanced file extension mapping for videos
            extension_map = {
                # Images
                'image/jpeg': '.jpg', 'image/png': '.png', 'image/gif': '.gif',
                'image/webp': '.webp',
                
                # Videos
                'video/mp4': '.mp4', 'video/3gpp': '.3gp', 'video/quicktime': '.mov',
                'video/x-msvideo': '.avi', 'video/x-matroska': '.mkv', 'video/webm': '.webm',
                
                # Audio
                'audio/ogg': '.ogg', 'audio/aac': '.aac', 'audio/mpeg': '.mp3',
                'audio/wav': '.wav', 'audio/x-m4a': '.m4a',
                
                # Documents
                'application/pdf': '.pdf', 'text/plain': '.txt',
                'application/msword': '.doc',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
                'application/vnd.ms-excel': '.xls',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            }
            
            extension = extension_map.get(media_type, '.bin')
            filename = f"{message_sid}{extension}"
            filepath = os.path.join(MEDIA_DIR, filename)
            
            # Get file size from headers
            content_length = int(response.headers.get('content-length', 0))
            print(f"📦 File size: {content_length} bytes ({content_length/1024/1024:.2f} MB)")
            
            # Download with progress for large files
            downloaded_size = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        # Show progress for files larger than 1MB
                        if content_length > 1024 * 1024:
                            progress = (downloaded_size / content_length) * 100
                            if int(progress) % 25 == 0:  # Log every 25%
                                print(f"📊 Download progress: {progress:.1f}%")
            
            # Verify download
            if os.path.exists(filepath):
                actual_size = os.path.getsize(filepath)
                print(f"✅ Successfully saved: {filename} ({actual_size} bytes)")
                
                # Additional video-specific info
                if media_type.startswith('video/'):
                    print(f"🎥 Video file saved: {filename}")
                    if actual_size != content_length:
                        print(f"⚠️ Size mismatch: expected {content_length}, got {actual_size}")
                
                return filepath
            else:
                print("❌ File was not created")
                return None
        else:
            print(f"❌ Download failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ Download timeout - video might be too large")
        return None
    except Exception as e:
        print(f"💥 Error: {e}")
        return None

def get_media_info(media_type, filepath):
    """Get specific information about different media types"""
    if media_type.startswith('video/'):
        return {
            'type': 'video',
            'icon': '🎥',
            'message': 'video',
            'max_size_mb': 16  # WhatsApp video size limit
        }
    elif media_type.startswith('image/'):
        return {
            'type': 'image', 
            'icon': '📸',
            'message': 'image',
            'max_size_mb': 5
        }
    elif media_type.startswith('audio/'):
        return {
            'type': 'audio',
            'icon': '🎵',
            'message': 'audio message',
            'max_size_mb': 16
        }
    elif media_type == 'application/pdf':
        return {
            'type': 'document',
            'icon': '📄',
            'message': 'PDF document',
            'max_size_mb': 100
        }
    else:
        return {
            'type': 'file',
            'icon': '📎',
            'message': 'file',
            'max_size_mb': 100
        }

@app.route("/", methods=["GET", "POST"])
def chatbot():
    if request.method == "GET":
        return "🤖 WhatsApp Bot is running! Send POST requests from Twilio."
    
    # Print incoming data for debugging
    print("=== INCOMING DATA ===")
    for key in request.form:
        if any(x in key for x in ['Media', 'Body', 'From', 'MessageType']):
            print(f"{key}: {request.form[key]}")
    
    num_media = int(request.form.get('NumMedia', 0))
    user_message = request.form.get('Body', '')
    message_sid = request.form.get('MessageSid', 'unknown')
    sender = request.form.get('From', '')
    message_type = request.form.get('MessageType', 'text')
    
    response = MessagingResponse()
    
    print(f"📨 Message type: {message_type}, Media files: {num_media}")
    
    if num_media > 0:
        print(f"📎 Found {num_media} media files")
        
        downloaded_files = []
        for i in range(num_media):
            media_url = request.form.get(f'MediaUrl{i}')
            media_type = request.form.get(f'MediaContentType{i}')
            
            print(f"Media {i}: {media_type}")
            
            if media_url and media_url != 'None':
                filepath = download_media_with_auth(media_url, media_type, f"{message_sid}_{i}")
                if filepath:
                    media_info = get_media_info(media_type, filepath)
                    downloaded_files.append(media_info)
        
        # Send appropriate responses
        if downloaded_files:
            for media_info in downloaded_files:
                response.message(f"{media_info['icon']} Thanks for the {media_info['message']}! I've saved it successfully.")
            
            # Add caption if provided
            if user_message:
                response.message(f"📝 Your caption: \"{user_message}\"")
                
            # Add specific tips based on media type
            main_media = downloaded_files[0]
            if main_media['type'] == 'video':
                response.message("💡 Videos are great! I can process video content if you enable that feature.")
            elif main_media['type'] == 'image':
                response.message("💡 I can analyze images for content recognition if you need!")
                
        else:
            response.message("❌ Sorry, I couldn't download your media file. It might be too large or there was an error.")
            
    else:
        # Text message handling
        if not user_message:
            response.message("""
👋 Hello! I can handle:
🎥 Videos (MP4, 3GP, etc.)
📸 Images (JPEG, PNG, GIF)
🎵 Audio messages
📄 Documents (PDF, etc.)

Just send me any media file!
            """)
        elif user_message.lower() in ['hi', 'hello', 'hey']:
            response.message("""
🎥 Welcome! I'm your media bot!

I can receive and save:
• Videos (up to 16MB)
• Images (up to 5MB) 
• Audio messages
• Documents

Send me any media file to get started!
            """)
        elif 'video' in user_message.lower():
            response.message("""
🎥 Video Support:
• Formats: MP4, 3GP, MOV, AVI
• Max size: 16MB
• I'll save and acknowledge all videos

Just send me a video file!
            """)
        else:
            response.message(f"📝 You said: {user_message}")
    
    return str(response)

@app.route("/videos", methods=["GET"])
def list_videos():
    """List all downloaded videos"""
    video_extensions = ['.mp4', '.3gp', '.mov', '.avi', '.mkv', '.webm']
    
    videos = []
    if os.path.exists(MEDIA_DIR):
        for filename in os.listdir(MEDIA_DIR):
            if any(filename.lower().endswith(ext) for ext in video_extensions):
                filepath = os.path.join(MEDIA_DIR, filename)
                size = os.path.getsize(filepath)
                videos.append({
                    'name': filename,
                    'size_mb': round(size / 1024 / 1024, 2),
                    'type': 'video'
                })
    
    return {
        "total_videos": len(videos),
        "videos": videos
    }

@app.route("/media-stats", methods=["GET"])
def media_stats():
    """Get statistics about all media types"""
    stats = {
        'videos': [], 'images': [], 'audio': [], 'documents': [], 'other': []
    }
    
    if os.path.exists(MEDIA_DIR):
        for filename in os.listdir(MEDIA_DIR):
            filepath = os.path.join(MEDIA_DIR, filename)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                file_info = {
                    'name': filename,
                    'size_mb': round(size / 1024 / 1024, 2)
                }
                
                if filename.lower().endswith(('.mp4', '.3gp', '.mov', '.avi', '.mkv', '.webm')):
                    stats['videos'].append(file_info)
                elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    stats['images'].append(file_info)
                elif filename.lower().endswith(('.ogg', '.aac', '.mp3', '.wav', '.m4a')):
                    stats['audio'].append(file_info)
                elif filename.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt')):
                    stats['documents'].append(file_info)
                else:
                    stats['other'].append(file_info)
    
    # Add counts
    for category in stats:
        stats[f'{category}_count'] = len(stats[category])
    
    return stats

if __name__ == '__main__':
    print("🚀 Starting WhatsApp Media Bot on http://127.0.0.1:5000/")
    print(f"📁 Media storage: {os.path.abspath(MEDIA_DIR)}")
    print("🎥 Video endpoint: http://127.0.0.1:5000/videos")
    print("📊 Stats endpoint: http://127.0.0.1:5000/media-stats")
    app.run(host='0.0.0.0', port=5000, debug=True)