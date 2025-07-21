import json
import os
import requests

OWNER = "Michael-Baudeur"
REPO = "SU_Determination_Attitude_LEO"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

#Load JSON
with open("current_review_items.json") as file:
  data = json.load(file)

#parcours des cartes du project
for item in data["data"]["node"]["items"]["nodes"]:
  title = item["content"]["title"]
  status = None
  #parcours des custom fields
  for field in item["fieldValues"]["nodes"]:
    if field.get("field", {}).get("name") == "Status":
      options = field["field"]["options"]
      option_id = field.get("OptionId")
    
