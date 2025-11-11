"""
Setup Ngrok Authtoken - Interactive Script
"""
import subprocess
import sys
import os
from colorama import Fore, Style, init

init(autoreset=True)

print(f"\n{Fore.CYAN}{'='*70}")
print(f"{Fore.YELLOW}🔑 NGROK AUTHTOKEN SETUP")
print(f"{Fore.CYAN}{'='*70}\n")

print(f"{Fore.CYAN}Browser me ngrok dashboard khul gaya hai?\n")
print(f"{Fore.WHITE}Steps:")
print(f"{Fore.WHITE}1. Login/Signup on ngrok dashboard")
print(f"{Fore.WHITE}2. Copy your authtoken (looks like: 2abc123def456...)")
print(f"{Fore.WHITE}3. Paste it here\n")

print(f"{Fore.YELLOW}{'='*70}\n")

authtoken = input(f"{Fore.CYAN}Paste your ngrok authtoken here: {Fore.WHITE}").strip()

if not authtoken:
    print(f"\n{Fore.RED}❌ No token provided!")
    sys.exit(1)

if len(authtoken) < 20:
    print(f"\n{Fore.RED}❌ Token seems too short. Please copy the complete token.")
    sys.exit(1)

print(f"\n{Fore.CYAN}Adding authtoken to ngrok config...\n")

try:
    # Add authtoken
    result = subprocess.run(
        ['ngrok', 'config', 'add-authtoken', authtoken],
        capture_output=True,
        text=True,
        check=True
    )
    
    print(f"{Fore.GREEN}✅ Authtoken added successfully!")
    print(f"{Fore.WHITE}{result.stdout}")
    
    print(f"\n{Fore.CYAN}Starting ngrok on port 8002...\n")
    
    # Start ngrok in new window
    subprocess.Popen(
        ['powershell', '-NoExit', '-Command', 'ngrok http 8002'],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    print(f"{Fore.GREEN}✅ Ngrok started in new window!")
    print(f"{Fore.YELLOW}⏳ Waiting 5 seconds for ngrok to initialize...\n")
    
    import time
    time.sleep(5)
    
    # Get ngrok URL
    import requests
    try:
        response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=5)
        tunnels = response.json()
        
        if tunnels.get('tunnels'):
            for tunnel in tunnels['tunnels']:
                if tunnel['proto'] == 'https':
                    public_url = tunnel['public_url']
                    
                    print(f"{Fore.GREEN}✅ Ngrok URL: {Fore.WHITE}{public_url}\n")
                    
                    # Update .env
                    env_path = '.env'
                    if os.path.exists(env_path):
                        with open(env_path, 'r') as f:
                            lines = f.readlines()
                        
                        with open(env_path, 'w') as f:
                            for line in lines:
                                if line.startswith('BASE_URL='):
                                    f.write(f'BASE_URL={public_url}\n')
                                else:
                                    f.write(line)
                        
                        print(f"{Fore.GREEN}✅ Updated .env with: BASE_URL={public_url}\n")
                    
                    print(f"{Fore.CYAN}{'='*70}")
                    print(f"{Fore.YELLOW}📋 TWILIO WEBHOOK URLS:")
                    print(f"{Fore.CYAN}{'='*70}\n")
                    print(f"{Fore.WHITE}Voice Webhook:")
                    print(f"{Fore.GREEN}{public_url}/api/hume-twilio/voice-webhook-fixed/\n")
                    print(f"{Fore.WHITE}Status Callback:")
                    print(f"{Fore.GREEN}{public_url}/api/hume-twilio/status-callback-fixed/\n")
                    print(f"{Fore.CYAN}{'='*70}\n")
                    
                    print(f"{Fore.GREEN}🎉 Setup complete! Ready to test calls!\n")
                    break
        else:
            print(f"{Fore.YELLOW}⚠️  Could not get ngrok URL automatically")
            print(f"{Fore.CYAN}Check the ngrok window for your URL\n")
            
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️  Could not connect to ngrok API")
        print(f"{Fore.CYAN}Check the ngrok window for your URL manually\n")
    
except subprocess.CalledProcessError as e:
    print(f"{Fore.RED}❌ Error adding authtoken:")
    print(f"{Fore.WHITE}{e.stderr}")
    sys.exit(1)
except Exception as e:
    print(f"{Fore.RED}❌ Error: {str(e)}")
    sys.exit(1)
