import requests
import os

# ==== CONFIGURATION UTILISATEUR ====
OWNER = "Michael-Baudeur"
REPOSITORY = "SU_Determination_Attitude_LEO"
PROJECT = "SU_Determination_Attitude_LEO"
GITHUB_FINEGRAINED_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_CLASSIC_TOKEN = os.environ.get("CLASSIC_GITHUB_TOKEN", "")
PROJECT_ID = os.environ.get("PROJECT_ID","")

DEBUG = 2 #DEBUG detail level from 0 (no debug prints) to 2 (detailed debug prints)
# ====================================

# ==== Variables globales ====
GITHUB_API_URL = "https://api.github.com/graphql"
# ============================

def setup_config(debug, owner, repository, project, github_finegrained_token, github_classic_token, project_id):
  """
  Setup global variables of github_utils library

  Args:
    owner (str): The name of the owner of the repository. Default to configurated.
    repository (str): The name of the repository. Default to configurated.
    project (str): The name of the Project associated with the repository. Default to configurated.
    github_finegrained_token (str): GitHub authentication fine grained token.
    github_classic_token (str): Github authentication classic token.
    project_id (str): The ProjectV2_ID ("PVT_xx...")
  """
  DEBUG=debug
  OWNER=owner
  REPOSITORY=repository
  PROJECT=project
  GITHUB_FINEGRAINED_TOKEN=github_finegrained_token
  GITHUB_CLASSIC_TOKEN=github_classic_token
  PROJECT_ID=project_id
  if DEBUG:
    print(f"Owner: {OWNER}")
    print(f"Repository: {REPOSITORY}")
    print(f"PROJECT: {PROJECT}")
    print(f"Fine grained token: {GITHUB_FINEGRAINED_TOKEN}")
    print(f"Classic toke: {GITHUB_CLASSIC_TOKEN}")
    print(f"Project Id: {PROJECT_ID}")

# ==== GraphQL Utility ====
def run_gql(query, variables=None, token=None):
  """
  Runs a GraphQL query or mutation through the Github API.

  Args:
    query (str): The GraphQL query or mutation string to execute.
    variables (dict, optional): A dictionary of variables to pass to the query. Defaults to None.
    token (str, optional): GitHub authentication token. If None, reads the GITHUB_CLASSIC_TOKEN environment variable.

  Returns:
    dict: The decoded JSON response from the API.

  Raises:
    requests.HTTPError: if the HTTP request fails (status code 4xx or 5xx).
  """
    headers = {
        "Authorization": f"Bearer {token or GITHUB_CLASSIC_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(GITHUB_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    if DEBUG == 2:
      print(f"GraphQL response JSON: {response.json()}")
    return response.json()
# =========================================================

# ==== Getters ====
def get_ProjectV2_ID(owner=OWNER, repository=REPOSITORY, project=PROJECT, token=None):
  """
  Returns the repository associated ProjectV2 ID from the repository owner and name and the name of the ProjectV2.

  Args:
    owner (str, optional): The name of the owner of the repository. Default to configurated.
    repository (str, optional): The name of the repository. Default to configurated.
    project (str, optional): The name of the Project associated with the repository. Default to configurated.
    token (str, optional): GitHub authentication token. If None, reads the GITHUB_CLASSIC_TOKEN environment variable.

  Returns:
    str: The ProjectV2_ID string ("PVT_..."), or None if not found.
  """
  query = """
  query($owner: String!, $name: String!) {
    repository(owner: $owner, name: $name) {
      projectsV2(first: 10) {
        nodes {
          id
          title
          number
        }
      }
    }
  }
  """
  response = run_gql(query, {"owner": owner, "name": repository}, token)
  for project in response["data"]["repository"]["projectsV2"]["nodes"]:
    if project["title"] == project:
      if DEBUG:
        print(f"ProjectV2 ID: {project["id"]}")
      return project["id"]
  return None
    
def get_repository_id(owner=OWNER, repository=REPOSITORY, token=None):
  """
  Returns the repository node ID from its owner and name.

  Args:
      owner (str, optional): The name of the owner of the repository
      repository (str, optional): The name of the repository
      token (str, optional): GitHub authentication token. If None, reads the GITHUB_CLASSIC_TOKEN environment variable.

  Returns:
        str: The repository node ID
  """
  query = """
  query($owner: String!, $name: String!) {
    repository(owner: $owner, name: $name) {
      id
    }
  }
  """
  response = run_gql(query, {"owner": owner, "name": repo}, token)
  repository_id = response["data"]["repository"]["id"]
  if DEBUG:
    print(f"Repository ID: {repository_id}")
  return repository_id

def get_issue_id(number, owner=OWNER, repository=REPOSITORY, token=None):
  """
  Returns the node ID of an issue given its number.

  Args:
      number (int): Issue number.
      owner (str, optional): GitHub user or organization.
      repository (str, optional): Repository name.
      token (str, optional): GitHub authentication token. If None, reads the GITHUB_CLASSIC_TOKEN environment variable.

  Returns:
      str: The issue node ID.
  """
  query = """
  query($ownerr: String!, $name: String!, $number: Int!) {
    repository(owner: $owner, name: $name) {
      issue(number: $number) {
        id
      }
    }
  }
  """
  reponse = run_gql(query, {"owner": owner, "name": repository, "number": number}, token)
  issue_id = response["data"]["respository"]["issue"]["id"]
  if DEBUG:
    print(f"Issue ID: {issue_id}")
  return issue_id

def get_issue_info(issue_id, token=None):
  """
  Returns issue details (number, title) given its node ID.

  Args:
      issue_id (str): Node ID of the issue.
      token (str, optional): GitHub API token.

  Returns:
      dict: Issue info including number and title.
  """
  query = """
  query($id: ID!) {
    node(id: $id) {
      ... on Issue {
        number
        title
      }
    }
  }
  """
  response = run_gql(query, {"id": issue_id}, token)
  issue_info = response["data"]["node"]
  if DEBUG:
    print(f"Issue info: {issue_info}")
  return issue_info

def get_field_id(field_name, project_id=PROJECT_ID, token=None):
  """
  Returns the field ID for a ProjectV2 field given its name.

  Args:
      field_name (str): The name of the field.
      project_id (str, optional): The ProjectV2 node ID (PVT_...).
      token (str, optional): Github API token.

  Returns:
      str: The field node ID, or None if not found.
  """
  query = """
  query($project: ID!) {
    node(id: $project) {
      ... on ProjectV2 {
        fields(first: 50) {
          nodes {
            ... on ProjectV2Field {
              id
              name
            }
          }
        }
      }
    }
  }
  """
  response = run_gql(query, {"project": project_id}, token)
  fields = response["data"]["node"]["fields"]["nodes"]
  for field in fields:
    if field["name"] == field_name:
      if DEBUG:
        print(f"Field ID: {field["id"]}")
      return field["id"]
  if DEBUG:
    print("Field ID not found.")
  return None

def get_field_name(field_id, project_id=PROJECT_ID, token=None):
  """
  Returns the field name for a ProjectV2 field given its node ID.

  Args:
      field_id (str): The field node ID.
      project_id (str, optional): The ProjectV2 node ID (PVT_...).

  Returns:
      str: The field name, or None if not found.
  """
  query = """
  query($project: ID!) {
    node(id: $project) {
      ... on ProjectV2 {
        fields(first: 50) {
          nodes {
            ... on ProjectV2Field {
              id
              name
            }
          }
        }
      }
    }
  }
  """
  response = run_gql(query, {"project": project_id}, token)
  fields = response["data"]["node"]["fields"]["nodes"]
  for field in fields:
    if field["id"] == field_id:
      if DEBUG:
        print(f"Field name: {field["name"]}")
      return field["name"]
  if DEBUG:
    print("Field name not found.")
  return None

def get_option_id(option_name, field_name, project_id=PROJECT_ID, token=None):
    """
    Returns the option ID for a single-select ProjectV2 field by name.

    Args:
        option_name (str): The option name.
        field_name (str): The field name.
        project_id (str, optional): The ProjectV2 node ID.

    Returns:
        str: The option ID, or None if not found.
    """  
    query = """
    query($project: ID!) {
      node(id: $project) {
        ... on ProjectV2 {
          fields(first: 50) {
            nodes {
              ... on ProjectV2SingleSelectField {
                name
                options {
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    response = run_gql(query, {"project": project_id}, token)
    fields = response["data"]["node"]["fields"]["nodes"]
    for field in fields:
      if field["name"] == field_name:
        for opt in field["options"]:
          if opt["name"] == option_name:
            if DEBUG:
              print(f"Option ID: {opt["id"]}")
            return opt["id"]
    if DEBUG:
      print("Option ID not found.")
    return None

def get_option_name(option_id, field_name, project_id=PROJECT_ID, token=None):
    """
    Returns the option name for a single-select ProjectV2 field by option ID.

    Args:
        option_id (str): The option ID.
        field_name (str): The field name.
        project_id (str, optional): The ProjectV2 node ID.
        

    Returns:
        str: The option name, or None if not found.
    """
    query = """
    query($project: ID!) {
      node(id: $project) {
        ... on ProjectV2 {
          fields(first: 50) {
            nodes {
              ... on ProjectV2SingleSelectField {
                name
                options { id name }
              }
            }
          }
        }
      }
    }
    """
    response = run_gql(query, {"project": project_id}, token)
    fields = response["data"]["node"]["fields"]["nodes"]
    for field in fields:
        if field["name"] == field_name:
            for opt in field["options"]:
                if opt["id"] == option_id:
                    if DEBUG:
                      print(f"Option name: {opt["name"]}")
                    return opt["name"]
    if DEBUG:
      print("Option name not found.")
    return None

def get_pull_request_id(number, owner=OWNER, repository=REPOSITORY, token=None):
    """
    Returns the node ID of a pull request given its number.

    Args:
        number (int): Pull request number.
        owner (str, optional): GitHub user or organization.
        repository (str, optional): Repository name.

    Returns:
        str: The pull request node ID.
    """
    query = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) {
        pullRequest(number: $number) { id }
      }
    }
    """
    response = run_gql(query, {"owner": owner, "name": repository, "number": number}, token)
    pull_request_id = response["data"]["repository"]["pullRequest"]["id"]
    if DEBUG:
      print(f"Pull request ID: {pull_request_id}")
    return pull_request_id

def get_pull_request_info(pull_request_id, token=None):
    """
    Returns PR details (number, title) given its node ID.

    Args:
        pull_request_id (str): Node ID of the pull request.
        token (str, optional): GitHub API token.

    Returns:
        dict: PR info including number and title.
    """
    query = """
    query($id: ID!) {
      node(id: $id) {
        ... on PullRequest { number title }
      }
    }
    """
    response = run_gql(query, {"id": pull_request_id}, token)
    pull_request_info = response["data"]["node"]
    if DEBUG:
      print(f"Pull request infos: {pull_request_info}")
    return pull_request_info

def get_project_item_id_by_issue_title(title, project_id=PROJECT_ID, token=None):
    """
    Returns the ProjectV2 item ID for a card whose linked issue or PR has the given title.
    WARNING: Issue/PR titles are not unique! Returns the first match.

    Args:
        title (str): The title of the issue associated to the projectV2 item.
        project_id (str) The ProjectV2 ID (PVT_xxx).
        token (str): GitHub token.

    Returns:
        str: The ProjectV2 item ID, or None if not found.
    """
    query = """
    query($project: ID!) {
      node(id: $project) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              id
              content {
                ... on Issue { title }
              }
            }
          }
        }
      }
    }
    """
    response = run_gql(query, {"project": project_id}, token)
    items = response["data"]["node"]["items"]["nodes"]
    for item in items:
        c = item.get("content")
        if c and c.get("title") == title:
            if DEBUG:
              print(f"Item ID of issue \"{title}\": {item["id"]}")
            return item["id"]
    return None

def get_project_item_id_by_pull_request_title(title, project_id=PROJECT_ID, token=None):
    """
    Returns the ProjectV2 item ID for a card whose linked issue or PR has the given title.
    WARNING: Issue/PR titles are not unique! Returns the first match.

    Args:
        title (str): The title of the pull request associated to the projectV2 item.
        project_id (str) The ProjectV2 ID (PVT_xxx).
        token (str): GitHub token.

    Returns:
        str: The ProjectV2 item ID, or None if not found.
    """
    query = """
    query($project: ID!) {
      node(id: $project) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              id
              content {
                ... on PullRequest { title }
              }
            }
          }
        }
      }
    }
    """
    response = run_gql(query, {"project": project_id}, token)
    items = response["data"]["node"]["items"]["nodes"]
    for item in items:
        c = item.get("content")
        if c and c.get("title") == title:
            return item["id"]
    return None

def get_project_item_id_by_issue_number(issue_number, project_id=PROJECT_ID, token=None):
    """
    Returns the ProjectV2 item ID (PVTI_xxx) for an issue number in the project.

    Args:
        project_id (str): The ProjectV2 ID (PVT_xxx).
        issue_number (int): The issue number.
        token (str): GitHub token.

    Returns:
        str: The ProjectV2 item ID, or None if not found.
    """
    query = """
    query($project: ID!) {
      node(id: $project) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              id
              content {
                ... on Issue { number }
              }
            }
          }
        }
      }
    }
    """
    response = run_gql(query, {"project": project_id}, token)
    items = response["data"]["node"]["items"]["nodes"]
    for item in items:
        c = item.get("content")
        if c and c.get("number") == issue_number:
            return item["id"]
    return None

def get_project_item_id_by_pull_request_number(pull_request_number, project_id=PROJECT_ID, token=None):
    """
    Returns the ProjectV2 item ID for a card whose linked PR has the given number.

    Args:
        project_id (str): The ProjectV2 ID (PVT_xxx).
        pull_request_number (int): The pull request number.
        token (str): GitHub token.

    Returns:
        str: The ProjectV2 item ID, or None if not found.
    """
    query = """
    query($project: ID!) {
      node(id: $project) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              id
              content {
                ... on PullRequest { number }
              }
            }
          }
        }
      }
    }
    """
    response = run_gql(query, {"project": project_id}, token)
    items = response["data"]["node"]["items"]["nodes"]
    for item in items:
        c = item.get("content")
        if c and c.get("number") == pull_request_number:
            return item["id"]
    return None

# ======================================================

# ==== Setters ====
def update_project_item_field(item_id, field_id, value_dict, project_id=PROJECT_ID, token=None):
    """
    Updates a ProjectV2 field for a given item (e.g., set status, text, or date).

    Args:
        project_id (str): ProjectV2 node ID.
        item_id (str): ProjectV2 item node ID.
        field_id (str): Field node ID.
        value_dict (dict): Dict describing the value to set (singleSelectOptionId, text, or date).
        token (str): GitHub API token.

    Returns:
        dict: The API response.
    """
    query = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId,
        itemId: $itemId,
        fieldId: $fieldId,
        value: $value
      }) {
        projectV2Item { id }
      }
    }
    """
    vars = {
        "projectId": project_id,
        "itemId": item_id,
        "fieldId": field_id,
        "value": value_dict
    }
    response = run_gql(query, vars, token)
    return response

def create_issue(title, body, owner=OWNER, repository=REPOSITORY, token=None):
  """
  Creates a new Github issue.

  Args:
      title (str): Issue title.
      body (str): Issue body.
      owner (str): Github user or organization.
      repository (str): Repository name.
      token (str): Github API token.

  Returns:
      dict: The API response with issue data.
  """
  url = f"https://api.github.com/repos/{owner}/{repository}/issues"
  headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
  }
  response = requests.post(url, headers=headers, json={"title": title, "body": body})
  response.raise_for_status()
  return response.json()



  
