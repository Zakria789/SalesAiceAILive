"""
🎯 SIMPLE SOLUTION - Standalone API (No Django Integration)
============================================================

Since Daphne keeps having import issues, use this standalone script
that directly updates HumeAI without Django.

Run: python standalone_agent_api.py
Then test with: python test_agent_apis.py (option 2)
"""

from flask import Flask, request, jsonify
import requests
from decouple import config
import json
import os
from datetime import datetime

app = Flask(__name__)

# Config
HUME_API_KEY = config('HUME_API_KEY')
HUME_API_BASE = "https://api.hume.ai/v0/evi"
LOCAL_DB_PATH = "agents_database.json"


def load_db():
    if os.path.exists(LOCAL_DB_PATH):
        with open(LOCAL_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"agents": []}


def save_db(data):
    with open(LOCAL_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@app.route('/api/agents/update-prompt/', methods=['POST'])
def update_agent_prompt():
    """Update existing HumeAI agent's prompt"""
    try:
        data = request.json
        config_id = data.get('config_id')
        new_prompt = data.get('prompt')
        
        if not config_id or not new_prompt:
            return jsonify({
                'success': False,
                'error': 'config_id and prompt required'
            }), 400
        
        # Update on HumeAI
        url = f"{HUME_API_BASE}/configs/{config_id}"
        headers = {
            "X-Hume-Api-Key": HUME_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "name": "SalesAice.ai Sales Agent (UPDATED)",
            "prompt": {
                "text": new_prompt,
                "version_type": "FIXED"
            }
        }
        
        response = requests.patch(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            # Save to local DB
            db = load_db()
            agent_data = {
                'config_id': config_id,
                'prompt': new_prompt,
                'updated_at': datetime.now().isoformat()
            }
            
            # Update or add
            found = False
            for i, agent in enumerate(db['agents']):
                if agent.get('config_id') == config_id:
                    db['agents'][i] = agent_data
                    found = True
                    break
            
            if not found:
                db['agents'].append(agent_data)
            
            save_db(db)
            
            return jsonify({
                'success': True,
                'message': 'Prompt updated successfully! ✅',
                'config_id': config_id,
                'updated_at': datetime.now().isoformat(),
                'saved_to_local_db': True
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'HumeAI returned {response.status_code}'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/agents/list/', methods=['GET'])
def list_agents():
    """List all agents"""
    try:
        db = load_db()
        return jsonify({
            'success': True,
            'count': len(db['agents']),
            'agents': db['agents']
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n🚀 Starting Standalone Agent API Server")
    print("="*60)
    print(f"📍 Running on: http://localhost:8002")
    print(f"📋 Endpoints:")
    print(f"   POST /api/agents/update-prompt/")
    print(f"   GET  /api/agents/list/")
    print("="*60)
    print("\n✅ Server ready! Test with: python test_agent_apis.py\n")
    
    app.run(host='0.0.0.0', port=8002, debug=True)
