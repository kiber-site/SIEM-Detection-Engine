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
    if not rule_name:
        print("⚠️ Faylda 'rule_name' tapılmadı, keçilir...")
        return

    try:
        check_url = f"{endpoint}?filter=name%3D%22{rule_name}%22"
        response = requests.get(check_url, headers=headers, verify=False, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API Xətası ({rule_name}): {response.status_code}")
            return

        existing_rules = response.json()
        
        if existing_rules:
            rule_id = existing_rules[0]['id']
            update_url = f"{endpoint}/{rule_id}"
            resp = requests.post(update_url, json=rule_data, headers=headers, verify=False)
            if resp.status_code == 200:
                print(f"🔄 Updated QRadar Rule: {rule_name}")
            else:
                print(f"❌ Update Xətası {rule_name}: {resp.status_code}")
        else:
            resp = requests.post(endpoint, json=rule_data, headers=headers, verify=False)
            if resp.status_code in [200, 201]:
                print(f"✅ Created QRadar Rule: {rule_name}")
            else:
                print(f"❌ Yaradılma Xətası {rule_name}: {resp.status_code} - {resp.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"🌐 Bağlantı xətası: {e}")

rule_files = glob.glob("qradar/rules/*.json")

if not rule_files:
    print("⚠️ Heç bir JSON faylı tapılmadı! Qovluq yolunu yoxlayın: qradar/rules/*.json")

for file_path in rule_files:
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            rule_content = json.load(f)
            push_to_qradar(rule_content)
        except json.JSONDecodeError:
            print(f"⚠️ JSON formatı səhvdir: {file_path}")
