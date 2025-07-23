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
    print(f"Checking field {field.get("field", {}).get("name")}...")
    #check du custom field status
    if field.get("field", {}).get("name") == "Status":
      print(f"Checking status...")
      options = field["field"]["options"]
      option_id = field.get("optionId")
      print(f"Options: {options}")
      print(f"Option Id: {option_id}")
      #Match de l'option avec l'option Id
      for opt in options:
        if opt["id"] == option_id:
          status = opt["name"]
          print(f"Issue status: {status}")
          break
    
    if status == "Review":
      issue_title = f"Review {title}"
      if not review_issue_exists(OWNER, REPO, issue_title, TOKEN):
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
      else:
        print("Issue already exist")


def review_issue_exists(owner, repo, issue_title,token):
  url = f"https://api.github.com/repos/{owner}/{repo}/issues"
  headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
  }
  params = {"state": "all", "per_page": 100}
  r = requests.get(url, headers=headers, params=params)
  if r.status_code == 200:
    issues = r.json()
    for issue in issues:
      if issue["title"] == issue_title:
        return True
  return False


    
      
