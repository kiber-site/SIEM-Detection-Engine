import requests
import os
import glob
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_URL = os.getenv('QRADAR_URL') 
QRADAR_TOKEN = os.getenv('QRADAR_TOKEN')

def push_to_qradar(rule_data):
    
    endpoint = f"{QRADAR_URL}/api/analytics/rules"
    headers = {
        "SEC": QRADAR_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    rule_name = rule_data.get('rule_name')
    
    check_url = f"{endpoint}?filter=name%3D%22{rule_name}%22"
    response = requests.get(check_url, headers=headers, verify=False)
    
    existing_rules = response.json()
    
    if existing_rules:
        # Update məntiqi (PUT request)
        rule_id = existing_rules[0]['id']
        update_url = f"{endpoint}/{rule_id}"
        # QRadar-da update zamanı bütün obyekti göndərmək lazımdır
        resp = requests.post(update_url, json=rule_data, headers=headers, verify=False)
        if resp.status_code == 200:
            print(f"🔄 Updated QRadar Rule: {rule_name}")
        else:
            print(f"❌ Error Updating {rule_name}: {resp.status_code}")
    else:
        # Yeni yaratma məntiqi (POST request)
        resp = requests.post(endpoint, json=rule_data, headers=headers, verify=False)
        if resp.status_code in [200, 201]:
            print(f"✅ Created QRadar Rule: {rule_name}")
        else:
            print(f"❌ Error Creating {rule_name}: {resp.status_code} - {resp.text}")

# JSON fayllarını tapırıq
rule_files = glob.glob("qradar/rules/*.json")

for file_path in rule_files:
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            rule_content = json.load(f)
            push_to_qradar(rule_content)
        except json.JSONDecodeError:
            print(f"⚠️ Fayl oxuna bilmədi: {file_path}")
