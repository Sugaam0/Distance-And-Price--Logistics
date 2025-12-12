"""
Run this script to test your Geoapify API key
Usage: python test_geoapify.py
"""

import requests
import json

# Your API key
API_KEY = 'fdd1cc8280464a8f91fa18d317ae53d6'

print("=" * 60)
print("TESTING GEOAPIFY API")
print("=" * 60)

# Test 1: Geocode Kathmandu
print("\n1. Testing Geocoding - Kathmandu")
print("-" * 60)
geocode_url = "https://api.geoapify.com/v1/geocode/search"
params = {
    'text': 'Kathmandu, Nepal',
    'apiKey': API_KEY,
    'limit': 1,
    'filter': 'countrycode:np'
}

try:
    response = requests.get(geocode_url, params=params, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('features'):
            coords = data['features'][0]['geometry']['coordinates']
            print(f"✓ SUCCESS: Kathmandu geocoded to [{coords[1]}, {coords[0]}]")
            kathmandu_coords = coords
        else:
            print("✗ FAILED: No results found")
            kathmandu_coords = None
    else:
        print(f"✗ FAILED: {response.text}")
        kathmandu_coords = None
except Exception as e:
    print(f"✗ ERROR: {e}")
    kathmandu_coords = None

# Test 2: Geocode Pokhara
print("\n2. Testing Geocoding - Pokhara")
print("-" * 60)
params['text'] = 'Pokhara, Nepal'

try:
    response = requests.get(geocode_url, params=params, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('features'):
            coords = data['features'][0]['geometry']['coordinates']
            print(f"✓ SUCCESS: Pokhara geocoded to [{coords[1]}, {coords[0]}]")
            pokhara_coords = coords
        else:
            print("✗ FAILED: No results found")
            pokhara_coords = None
    else:
        print(f"✗ FAILED: {response.text}")
        pokhara_coords = None
except Exception as e:
    print(f"✗ ERROR: {e}")
    pokhara_coords = None

# Test 3: Calculate route
if kathmandu_coords and pokhara_coords:
    print("\n3. Testing Routing - Kathmandu to Pokhara")
    print("-" * 60)
    
    waypoints = f"{kathmandu_coords[1]},{kathmandu_coords[0]}|{pokhara_coords[1]},{pokhara_coords[0]}"
    routing_url = "https://api.geoapify.com/v1/routing"
    
    params = {
        'waypoints': waypoints,
        'mode': 'drive',
        'apiKey': API_KEY
    }
    
    try:
        response = requests.get(routing_url, params=params, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('features'):
                distance_meters = data['features'][0]['properties']['distance']
                distance_km = distance_meters / 1000
                time_seconds = data['features'][0]['properties']['time']
                time_hours = time_seconds / 3600
                
                print(f"✓ SUCCESS!")
                print(f"  Distance: {distance_km:.2f} km")
                print(f"  Estimated Time: {time_hours:.2f} hours")
            else:
                print("✗ FAILED: No route found")
                print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"✗ FAILED: {response.text}")
    except Exception as e:
        print(f"✗ ERROR: {e}")
else:
    print("\n3. Skipping routing test (geocoding failed)")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

# Check if API key is valid
print("\n4. API Key Check")
print("-" * 60)
if kathmandu_coords or pokhara_coords:
    print("✓ API Key appears to be VALID")
    print("\nNext steps:")
    print("1. Make sure GEOAPIFY_API_KEY is set in settings.py")
    print("2. Restart your Django server")
    print("3. Try the calculator again")
else:
    print("✗ API Key appears to be INVALID or EXPIRED")
    print("\nPlease:")
    print("1. Check your API key at https://myprojects.geoapify.com")
    print("2. Generate a new API key if needed")
    print("3. Update API_KEY in this script and in settings.py")