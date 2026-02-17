import requests
import json

api_key = "b159e4c1a255d8fc5a52dd90018c8d4b94bc45e91481ad2a7a9705e2b9fbf674"
company = "amazon"

url = "https://serpapi.com/search"
params = {
    'q': f'{company} top competitors alternatives',
    'api_key': api_key,
    'engine': 'google',
    'num': 10
}

print(f"Searching for: {company} competitors\n")

response = requests.get(url, params=params, timeout=10)
data = response.json()

print("=== SERP API Response ===\n")
print(f"Status: {response.status_code}\n")

if 'error' in data:
    print(f"ERROR: {data['error']}")
else:
    print(f"Found {len(data.get('organic_results', []))} organic results\n")
    
    for i, result in enumerate(data.get('organic_results', [])[:5], 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Link: {result.get('link', 'N/A')}")
        print(f"Snippet: {result.get('snippet', 'N/A')[:200]}...")

print("\n\n=== Full JSON Response ===")
print(json.dumps(data, indent=2)[:2000])
