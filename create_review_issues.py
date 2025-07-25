import json
import os
import requests

GITHUB_API = "https://api.github.com/graphql"
OWNER = "Michael-Baudeur"
REPO = "SU_Determination_Attitude_LEO"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
CLASSIC_TOKEN = os.environ.get("CLASSIC_GITHUB_TOKEN", "")
PROJECT_ID = os.environ.get("PROJECT_ID","")

def review_issue_exists(owner, repo, issue_title,token):
  url = f"https://api.github.com/repos/{owner}/{repo}/issues"
  headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
  }
  params = {"state": "open", "per_page": 100}
  r = requests.get(url, headers=headers, params=params)
  if r.status_code == 200:
    issues = r.json()
    for issue in issues:
      if issue["title"] == issue_title:
        return True
  return False


print("Working directory:", os.getcwd())
print("Files in directory:", os.listdir())

def create_review_issues(filename = "current_review_items.json"):
  print("Creating review tasks...")
  #Load JSON
  with open(filename) as file:
    data = json.load(file)
    
  issue_nodes_ids = []
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
          issue_nodes_ids.append(r.json()["node_id"])
        else:
          print(f"❌ Error: {r.status_code} {r.text}")
      else:
        print("Review issue already exist")
  return issue_nodes_ids

def get_field_and_option_id(option = "Todo", field = "Status", filename = "current_review_items.json"):
  field_id = None
  option_id = None
  with open(filename) as file:
    data = json.load(file)
  for item in data["data"]["node"]["items"]["nodes"]:
    title = item["content"]["title"]
    #parcours des custom fields
    for f_field in item["fieldValues"]["nodes"]:
      #check du custom field status
      if f_field.get("field", {}).get("name") == field:
        field_id = f_field.get("field", {}).get("id")
        print(f"field id: {field_id}")
        options = f_field["field"]["options"]
        #Match de l'option avec l'option Id
        for opt in options:
          print(f"option name: {opt["name"]}")
          if opt["name"] == option:
            option_id = opt["id"]
            print(f"option id: {option_id}")
            break
        break
            
    return field_id, option_id
  

def run_gql(query, variables=None):
    headers = {
        "Authorization": f"Bearer {CLASSIC_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    payload = {"query": query, "variables": variables}
    if variables:
        payload["variables"] = variables
    response = requests.post(GITHUB_API, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
  
def add_issue_to_project(issue_node_id, project_id, status_field_id, option_id):
    # Step 1: Add item to project
    add_item_query = """
    mutation($projectId:ID!, $contentId:ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item { 
          id 
        }
      }
    }
    """
    response = run_gql(add_item_query, {"projectId": project_id, "contentId": issue_node_id})
    if(response.get("data")
       and response["data"].get("addProjectV2ItemById")
       and response["data"]["addProjectV2ItemById"].get("item")
    ):
      project_item_id = response["data"]["addProjectV2ItemById"]["item"]["id"]
    else:
      print(f"Error in API response: {response}")
      return None
    
    # Step 2: Set Status to 'Todo'
    update_status_query = """
    mutation($projectId:ID!, $itemId:ID!, $fieldId:ID!, $optionId:String!) {
      updateProjectV2ItemFieldValue(
      input: {
        projectId: $projectId,
        itemId: $itemId,
        fieldId: $fieldId,
        value: { singleSelectOptionId: $optionId }
      }
    ) {
        projectV2Item { id }
      }
    }
    """
    run_gql(update_status_query, {
        "projectId": project_id,
        "itemId": project_item_id,
        "fieldId": status_field_id,
        "optionId": option_id
    })
    print("✅ Issue added to ProjectV2 and set to 'Todo'.")

def add_issues_to_project(nodes_ids, column = 'Todo'):
  field_id, option_id = get_field_and_option_id(column)
  for id in nodes_ids:
    print(f"Adding Issue: {id} to project")
    add_issue_to_project(id, PROJECT_ID, field_id, option_id)

nodes_IDs = create_review_issues()
print(f"nodes IDs: {nodes_IDs}")
add_issues_to_project(nodes_IDs)
    
  
