#!/usr/bin/env python3
"""
Messaging Screenshot Generator API - Template-based Version
Uses Flask templates and Playwright for realistic screenshot rendering
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import json
import random
import base64
import io
import os
from datetime import datetime
import zipfile
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
TEMPLATE_FOLDER = 'templates'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Storage for uploaded data
evidence_images = []
convokit_conversations = []

# Contact names
CONTACT_NAMES = [
    'James Anderson', 'Emma Wilson', 'Michael Brown', 'Sarah Davis',
    'David Miller', 'Jessica Taylor', 'Daniel Thomas', 'Ashley Martinez',
    'Matthew Jackson', 'Emily White', 'Christopher Harris', 'Amanda Clark',
]

# Read the messaging template
MESSAGING_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif;
            -webkit-font-smoothing: antialiased;
        }
        .phone-screen {
            width: 375px;
            height: 812px;
            background: {{ bg_color }};
            position: relative;
            display: flex;
            flex-direction: column;
        }
        .notch {
            width: 165px; height: 30px; background: #000;
            position: absolute; top: 0; left: 50%;
            transform: translateX(-50%); border-radius: 0 0 20px 20px;
            z-index: 10;
        }
        .status-bar {
            height: 47px; background: {{ header_bg }};
            display: flex; justify-content: space-between; align-items: flex-end;
            padding: 0 20px 8px 20px; font-size: 15px; font-weight: 500;
            color: {{ header_text_color }};
            flex-shrink: 0;
        }
        .chat-header {
            height: 56px; background: {{ header_bg }};
            display: flex; align-items: center; padding: 0 8px 0 4px;
            border-bottom: 0.5px solid {{ border_color }};
            color: {{ header_text_color }};
            flex-shrink: 0;
        }
        .back-button { font-size: 28px; padding: 8px; line-height: 1; }
        .avatar {
            width: 36px; height: 36px; border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0 8px; overflow: hidden;
        }
        .avatar img { width: 100%; height: 100%; object-fit: cover; }
        .contact-info { flex: 1; }
        .contact-name { font-size: 17px; font-weight: 600; }
        .contact-status { font-size: 12px; opacity: 0.8; }
        .messages-container {
            padding: 16px;
            background: {{ bg_color }};
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }
        .message {
            display: flex; margin-bottom: 4px; gap: 8px; align-items: flex-end;
        }
        .message.sent { justify-content: flex-end; }
        .message.received { justify-content: flex-start; }
        .message-bubble {
            max-width: 70%; padding: 8px 12px; border-radius: 18px;
            font-size: 16px; line-height: 1.4; word-wrap: break-word;
        }
        .sent .message-bubble {
            background: {{ sent_bg }}; color: {{ sent_text_color }};
            border-bottom-right-radius: 4px;
        }
        .received .message-bubble {
            background: {{ received_bg }}; color: {{ received_text_color }};
            border-bottom-left-radius: 4px;
        }
        .message-bubble img {
            max-width: 100%; max-height: 200px; border-radius: 8px; 
            display: block; margin: 4px 0; object-fit: contain;
        }
        .message-time {
            font-size: 11px; opacity: 0.6; margin-top: 2px;
            display: flex; align-items: center; justify-content: flex-end; gap: 3px;
        }
        .input-bar {
            height: 50px; border-top: 0.5px solid {{ border_color }};
            background: {{ header_bg }}; display: flex; align-items: center;
            padding: 6px 8px; gap: 8px;
            flex-shrink: 0;
        }
        .text-input {
            flex: 1; height: 36px; background: white; border: 1px solid #D1D1D6;
            border-radius: 18px; padding: 0 14px; font-size: 16px; color: #8E8E93;
            display: flex; align-items: center;
        }
        .home-indicator {
            height: 34px; display: flex; align-items: center;
            justify-content: center; background: {{ header_bg }};
            flex-shrink: 0;
        }
        .home-indicator-bar {
            width: 140px; height: 5px; background: #000;
            border-radius: 3px; opacity: 0.3;
        }
    </style>
</head>
<body>
    <div class="phone-screen">
        <div class="notch"></div>
        <div class="status-bar">
            <span>{{ time }}</span>
            <span>78%</span>
        </div>
        <div class="chat-header">
            <div class="back-button">‹</div>
            <div class="avatar">
                <img src="{{ avatar_url }}" alt="{{ contact_name }}">
            </div>
            <div class="contact-info">
                <div class="contact-name">{{ contact_name }}</div>
                <div class="contact-status">{{ status }}</div>
            </div>
        </div>
        <div class="messages-container">
            {% for msg in messages_before %}
            <div class="message {{ msg.sender }}">
                <div class="message-bubble">
                    {{ msg.text }}
                    {% if platform == 'whatsapp' and msg.sender == 'sent' %}
                    <div class="message-time">{{ random_time() }} ✓✓</div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
            
            <div class="message {{ image_sender }}">
                <div class="message-bubble">
                    <img src="data:image/jpeg;base64,{{ evidence_image }}" alt="Evidence">
                </div>
            </div>
            
            {% for msg in messages_after %}
            <div class="message {{ msg.sender }}">
                <div class="message-bubble">
                    {{ msg.text }}
                    {% if platform == 'whatsapp' and msg.sender == 'sent' %}
                    <div class="message-time">{{ random_time() }} ✓✓</div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        <div class="input-bar">
            <div class="text-input">{{ input_placeholder }}</div>
        </div>
        <div class="home-indicator">
            <div class="home-indicator-bar"></div>
        </div>
    </div>
</body>
</html>
"""

# Platform color schemes
PLATFORM_STYLES = {
    'imessage': {
        'bg_color': '#FFFFFF',
        'header_bg': '#F2F2F7',
        'header_text_color': '#000000',
        'border_color': '#C6C6C8',
        'sent_bg': '#007AFF',
        'sent_text_color': '#FFFFFF',
        'received_bg': '#E8E8ED',
        'received_text_color': '#000000',
        'input_placeholder': 'iMessage',
        'status': ''
    },
    'whatsapp': {
        'bg_color': '#EFEAE2',
        'header_bg': '#008069',
        'header_text_color': '#FFFFFF',
        'border_color': '#008069',
        'sent_bg': '#D9FDD3',
        'sent_text_color': '#000000',
        'received_bg': '#FFFFFF',
        'received_text_color': '#000000',
        'input_placeholder': 'Message',
        'status': 'online'
    },
    'messenger': {
        'bg_color': '#FFFFFF',
        'header_bg': '#FFFFFF',
        'header_text_color': '#000000',
        'border_color': '#E4E6EB',
        'sent_bg': 'linear-gradient(135deg, #0099FF 0%, #0084FF 100%)',
        'sent_text_color': '#FFFFFF',
        'received_bg': '#E4E6EB',
        'received_text_color': '#050505',
        'input_placeholder': 'Aa',
        'status': ''
    },
    'signal': {
        'bg_color': '#FFFFFF',
        'header_bg': '#F2F2F7',
        'header_text_color': '#000000',
        'border_color': '#D1D1D6',
        'sent_bg': '#5E5CE6',
        'sent_text_color': '#FFFFFF',
        'received_bg': '#E5E5EA',
        'received_text_color': '#000000',
        'input_placeholder': 'Signal message',
        'status': ''
    }
}


def clean_reddit_text(text):
    """Remove Reddit-specific formatting and clean up text"""
    import re
    
    # Remove [deleted] and [removed]
    if text.lower().strip() in ['[deleted]', '[removed]', 'deleted', 'removed']:
        return None
    
    # Remove Reddit markdown formatting
    # Remove bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # Remove italic: *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # Remove strikethrough: ~~text~~
    text = re.sub(r'~~(.+?)~~', r'\1', text)
    
    # Remove quotes: > text
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    
    # Remove code blocks: `code` or ```code```
    text = re.sub(r'`{1,3}(.+?)`{1,3}', r'\1', text)
    
    # Remove links: [text](url)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    # Remove Reddit-specific mentions: /r/subreddit, u/username
    text = re.sub(r'/r/\w+', '', text)
    text = re.sub(r'u/\w+', '', text)
    
    # Remove excessive newlines
    text = re.sub(r'\n+', ' ', text)
    
    # Remove excessive spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Trim
    text = text.strip()
    
    # Return None if empty after cleaning
    if not text or len(text) < 3:
        return None
    
    return text


def get_random_time():
    """Generate random timestamp"""
    hour = random.randint(1, 12)
    minute = f"{random.randint(0, 59):02d}"
    return f"{hour}:{minute}"


def get_avatar_url(seed):
    """Get avatar URL"""
    return f"https://ui-avatars.com/api/?name={seed}&size=150&background=random&color=fff&bold=true"


@app.route('/api/upload-images', methods=['POST'])
def upload_images():
    """Upload evidence images"""
    global evidence_images
    
    if 'images' not in request.files:
        return jsonify({'error': 'No images provided'}), 400
    
    files = request.files.getlist('images')
    evidence_images = []
    
    for file in files:
        img_data = base64.b64encode(file.read()).decode('utf-8')
        evidence_images.append(img_data)
    
    return jsonify({
        'success': True,
        'count': len(evidence_images),
        'message': f'Uploaded {len(evidence_images)} images'
    })


@app.route('/api/upload-conversations', methods=['POST'])
def upload_conversations():
    """Upload ConvoKit JSON conversations"""
    global convokit_conversations
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    data = json.load(file)
    
    convokit_conversations = data.get('conversations', [])
    
    return jsonify({
        'success': True,
        'count': len(convokit_conversations),
        'message': f'Loaded {len(convokit_conversations)} conversations'
    })


@app.route('/api/generate-screenshots', methods=['POST'])
def generate_screenshots():
    """Generate screenshots using Playwright and return as ZIP"""
    
    data = request.get_json()
    platform = data.get('platform', 'imessage')
    num_screenshots = int(data.get('num_screenshots', 10))
    messages_before = int(data.get('messages_before_image', 2))
    messages_after = int(data.get('messages_after_image', 2))
    
    if not evidence_images:
        return jsonify({'error': 'No evidence images uploaded'}), 400
    
    # Run async screenshot generation
    zip_path = asyncio.run(generate_screenshots_async(
        platform, num_screenshots, messages_before, messages_after
    ))
    
    return send_file(
        zip_path,
        mimetype='application/zip',
        as_attachment=True,
        download_name=os.path.basename(zip_path)
    )


async def generate_screenshots_async(platform, num_screenshots, messages_before, messages_after):
    """Generate screenshots using Playwright"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'{platform}_screenshots_{timestamp}.zip'
    zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 375, 'height': 812})
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i in range(num_screenshots):
                # Get conversation messages
                messages_pre, messages_post = get_conversation_messages(messages_before, messages_after)
                
                # Get random evidence image
                evidence_img_b64 = random.choice(evidence_images)
                
                # Get random contact
                contact_name = random.choice(CONTACT_NAMES)
                avatar_seed = random.randint(1, 100)
                avatar_url = get_avatar_url(avatar_seed)
                
                # Render HTML
                html_content = render_messaging_html(
                    platform, contact_name, avatar_url,
                    messages_pre, evidence_img_b64, messages_post
                )
                
                # Load and screenshot
                await page.set_content(html_content)
                await page.wait_for_timeout(500)  # Wait for images to load
                
                screenshot_bytes = await page.screenshot(type='jpeg', quality=95)
                
                # Add to ZIP
                zipf.writestr(f'{platform}_screenshot_{i+1}.jpg', screenshot_bytes)
                
                print(f"Generated {i+1}/{num_screenshots}")
        
        await browser.close()
    
    return zip_path


def get_conversation_messages(num_before, num_after):
    """Get conversation messages from ConvoKit or generate generic ones"""
    
    if convokit_conversations:
        # Try up to 10 times to get a good conversation
        for attempt in range(10):
            convo = random.choice(convokit_conversations)
            all_messages = convo['messages']
            
            # Clean messages and filter out deleted/invalid ones
            cleaned_messages = []
            for msg in all_messages:
                cleaned_text = clean_reddit_text(msg['text'])
                if cleaned_text:
                    # Limit message length for better display
                    if len(cleaned_text) > 150:
                        cleaned_text = cleaned_text[:147] + '...'
                    
                    cleaned_messages.append({
                        'sender': msg['sender'],
                        'text': cleaned_text
                    })
            
            # Need enough valid messages
            total_needed = num_before + num_after
            if len(cleaned_messages) >= total_needed:
                # Get random slice from conversation
                if len(cleaned_messages) > total_needed:
                    start_idx = random.randint(0, len(cleaned_messages) - total_needed)
                    selected_messages = cleaned_messages[start_idx:start_idx + total_needed]
                else:
                    selected_messages = cleaned_messages[:total_needed]
                
                messages_pre = selected_messages[:num_before]
                messages_post = selected_messages[num_before:num_before + num_after]
                
                return messages_pre, messages_post
        
        # If we couldn't find a good conversation after 10 tries, fall through to generic
    
    # Generate generic messages as fallback
    generic = [
        {'sender': 'received', 'text': 'Hey, check this out'},
        {'sender': 'sent', 'text': 'What is it?'},
        {'sender': 'received', 'text': 'Look at this'},
        {'sender': 'sent', 'text': 'Interesting'},
        {'sender': 'received', 'text': 'What do you think?'},
        {'sender': 'sent', 'text': 'Thanks for sharing'},
        {'sender': 'received', 'text': 'Let me know what you think'},
        {'sender': 'sent', 'text': 'Will do'},
    ]
    
    messages_pre = generic[:num_before]
    messages_post = generic[num_before:num_before + num_after]
    
    return messages_pre, messages_post


def render_messaging_html(platform, contact_name, avatar_url, messages_before, evidence_image_b64, messages_after):
    """Render the messaging HTML template"""
    
    styles = PLATFORM_STYLES[platform]
    current_time = datetime.now().strftime('%H:%M')
    image_sender = random.choice(['sent', 'received'])
    
    # Build template context
    context = {
        'platform': platform,
        'contact_name': contact_name,
        'avatar_url': avatar_url,
        'time': current_time,
        'status': styles['status'],
        'messages_before': messages_before,
        'messages_after': messages_after,
        'evidence_image': evidence_image_b64,
        'image_sender': image_sender,
        'input_placeholder': styles['input_placeholder'],
        'random_time': get_random_time,
        **styles
    }
    
    # Render template
    from jinja2 import Template
    template = Template(MESSAGING_TEMPLATE)
    return template.render(**context)


@app.route('/api/status', methods=['GET'])
def status():
    """Check API status"""
    return jsonify({
        'status': 'online',
        'evidence_images': len(evidence_images),
        'conversations': len(convokit_conversations)
    })


@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Clear uploaded data"""
    global evidence_images, convokit_conversations
    evidence_images = []
    convokit_conversations = []
    return jsonify({'success': True, 'message': 'Data cleared'})


if __name__ == '__main__':
    print("="*60)
    print("Messaging Screenshot Generator API")
    print("Template-based rendering with Playwright")
    print("="*60)
    print("\nStarting server on http://localhost:5000")
    print("\nMake sure Playwright is installed:")
    print("  pip install playwright")
    print("  playwright install chromium")
    print("\n" + "="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)