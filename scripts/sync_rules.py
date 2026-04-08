import requests
import os
import glob


SPLUNK_URL = os.getenv('SPLUNK_URL')
SPLUNK_TOKEN = os.getenv('SPLUNK_TOKEN')

def push_to_splunk(rule_name, query):
    
    
    endpoint = f"{SPLUNK_URL}/servicesNS/nobody/search/saved/searches"
    headers = {"Authorization": f"Bearer {SPLUNK_TOKEN}"}
    
    
    data = {
        "name": rule_name,
        "search": query,
        "is_visible": "1",
        "disabled": "0",
        "action.email": "1"
    }
    
    
    response = requests.post(endpoint, data=data, headers=headers, verify=False)
    
    if response.status_code == 409: 
        update_url = f"{endpoint}/{rule_name}"
        response = requests.post(update_url, data={"search": query}, headers=headers, verify=False)
        print(f"🔄 {rule_name} yenilendi (Update).")
    elif response.status_code in [200, 201]:
        print(f"✅ {rule_name} yeni yaradıldı (Created).")
    else:
        print(f"❌ Xəta: {rule_name} - {response.status_code} - {response.text}")


rule_files = glob.glob("splunk/rules/**/*.spl", recursive=True)
for file_path in rule_files:
    rule_id = os.path.basename(file_path).replace(".spl", "")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        push_to_splunk(rule_id, content)
