# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 14:09:56 2024

@author: Skanda
"""

import requests
import pandas as pd
import time
from tqdm import tqdm

# Replace with your actual GitHub token
GITHUB_TOKEN = 'xxx'
headers = {'Authorization': f'token {GITHUB_TOKEN}'}


def search_users_in_boston():
    """Search for users in Boston with over 100 followers using pagination."""
    url = "https://api.github.com/search/users"
    params = {'q': 'location:Boston followers:>100', 'per_page': 100}
    all_users = []
    page = 1

    while True:
        response = requests.get(url, headers=headers, params={**params, 'page': page})
        users = response.json().get('items', [])
        
        if not users or response.status_code != 200:
            break
        
        all_users.extend(users)
        page += 1
        time.sleep(1)  # Avoid hitting the rate limit

    return all_users

def get_user_details(username):
    """Fetch detailed information for a given GitHub user."""
    user_url = f"https://api.github.com/users/{username}"
    user_resp = requests.get(user_url, headers=headers,timeout=10)
    return user_resp.json()

def clean_company_name(company_name):
    """Clean up company names as per specifications."""
    if company_name:
        return company_name.strip().lstrip('@').upper()
    return ''

def format_user_data(user):
    """Extract and format user data for users.csv."""
    return {
        'login': user.get('login', ''),  # GitHub user ID (username)
        'id': user.get('id', ''),
        'name': user.get('name', ''),
        'company': clean_company_name(user.get('company', '')),
        'location': user.get('location', ''),
        'email': user.get('email', ''),
        'hireable': user.get('hireable', ''),
        'bio': user.get('bio', ''),
        'public_repos': user.get('public_repos', 0),
        'followers': user.get('followers', 0),
        'following': user.get('following', 0),
        'created_at': user.get('created_at', '')
    }

def fetch_user_repositories(username):
    """Fetch up to 500 most recently pushed repositories for a user."""
    url = f'https://api.github.com/users/{username}/repos'
    params = {'sort': 'pushed', 'per_page': 100}
    all_repos = []
    page = 1

    while len(all_repos) < 500:
        response = requests.get(url, headers=headers, params={**params, 'page': page})
        repos = response.json()
        
        if not repos or response.status_code != 200:
            break
        
        for repo in repos:
            # Safely handle license information
            license_name = repo['license']['key'] if repo.get('license') else ''
            all_repos.append({
                'login': username,  # GitHub user ID
                'full_name': repo.get('full_name', ''),
                'created_at': repo.get('created_at', ''),
                'stargazers_count': repo.get('stargazers_count', 0),
                'watchers_count': repo.get('watchers_count', 0),
                'language': repo.get('language', ''),
                'has_projects': repo.get('has_projects', False),
                'has_wiki': repo.get('has_wiki', False),
                'license_name': license_name  # Use the safe license extraction
            })
        
        if len(repos) < 100:
            break  # No more pages of repos
        
        page += 1
        time.sleep(1)  # Rate limit handling
    
    return all_repos[:500]

# Fetch user and repository data
users_data = []
repos_data = []

for user in tqdm(search_users_in_boston()):
    user_details = get_user_details(user['login'])
    users_data.append(format_user_data(user_details))
    
    # Fetch repositories for the user
    user_repos = fetch_user_repositories(user['login'])
    repos_data.extend(user_repos)

# Convert to DataFrames
users_df = pd.DataFrame(users_data)
repos_df = pd.DataFrame(repos_data)

# Save DataFrames to CSV
path = r'E:\RajC\IIT\IIT Madras\Sep 2024\TDS\Project\\'
users_df.to_csv(path + 'users_1.csv', index=False)
repos_df.to_csv(path + 'repositories_1.csv', index=False)



# Ensure the 'created_at' column is in datetime format
users_df['created_at'] = pd.to_datetime(users_df['created_at'])

# Sort the dataframe by 'created_at' in ascending order
earliest_users = users_df.sort_values(by='created_at').head(5)

# Extract the 'login' values and join them into a comma-separated string
earliest_users_logins = ','.join(earliest_users['login'].tolist())
print(earliest_users_logins)




from collections import Counter

# Assuming repos_data is already populated from previous code
licenses_counter = Counter()

# Iterate through the repository data
for repo in repos_data:
    license_info = repo.get('license', None)
    if license_info and 'name' in license_info:
        licenses_counter[license_info['name']] += 1











