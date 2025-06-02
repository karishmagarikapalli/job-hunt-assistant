import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json

client = ApiClient()

# Get LinkedIn profile data
linkedin_username = "karishma-garikapalli"
profile_data = client.call_api('LinkedIn/get_user_profile_by_username', query={'username': linkedin_username})

# Save the data to a JSON file
with open('/home/ubuntu/job_hunt_ecosystem/linkedin_profile_data.json', 'w') as f:
    json.dump(profile_data, f, indent=4)

print("LinkedIn profile data has been retrieved and saved to linkedin_profile_data.json")
