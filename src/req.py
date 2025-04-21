import requests
import json

# Replace with the actual username
username = "heisjoel0x"

# Define the URL
url = f"http://services.baxus.co/api/bar/user/{username}"

# Set headers
headers = {
    "Content-Type": "application/json"
}

# Send GET request
response = requests.get(url, headers=headers)

# Check response
if response.status_code == 200:
    data = response.json()
    
    # Save to file
    with open("bar_data.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Bar data saved to bar_data.json")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
    print(response.text)
