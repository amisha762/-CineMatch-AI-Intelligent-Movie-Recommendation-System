import requests

API_KEY = "3122f5f88b8b0f31282f2af4e9ec16da"

url = "https://api.themoviedb.org/3/search/movie"

params = {
    "api_key": API_KEY,
    "query": "Titanic"
}

response = requests.get(url, params=params, timeout=20)

print("Status Code:", response.status_code)
print(response.text)