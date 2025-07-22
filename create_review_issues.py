import json
import os
import requests

OWNER = "Michael-Baudeur"
REPO = "SU_Determination_Attitude_LEO"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

print("Working directory:", os.getcwd())
print("Files in directory:", os.listdir())

print("Creating review tasks...")
#Load JSON
with open("current_review_items.json") as file:
  data = json.load(file)

#parcours des cartes du project
for item in data["data"]["node"]["items"]["nodes"]:
  title = item["content"]["title"]
  print(f"Processing issue: {title}")
  status = None
  #parcours des custom fields
  for field in item["fieldValues"]["nodes"]:
    print(f"check field {field.get("field", {}).get("name")}")
    #check du custom field status
    if field.get("field", {}).get("name") == "Status":
      print(f"Detected status field for {title}")
      options = field["field"]["options"]
      option_id = field.get("OptionId")
      #Match de l'option avec l'option Id
      for opt in options:
        if opt["id"] == option_id:
          status = opt["name"]
          print(f"Issue status: {status}")
          break
    
    if status == "Review":
      issue_title = f"Review {title}"
      print(f"Creating issue: {issue_title}")
      r = requests.post(
        f"https://api.github.com/repos/{OWNER}/{REPO}/issues",
        headers={
          "Authorization": f"Bearer {TOKEN}",
          "Accept": "application/vnd.github+json"
        },
        json={
          "title": issue_title,
          "body": f"Issue reveiw auto-created for '{title}'"
        }
      )
      if r.status_code == 201:
        print(f"✅ Created: {r.json()['html_url']}")
      else:
        print(f"❌ Error: {r.status_code} {r.text}")
        
    
      
