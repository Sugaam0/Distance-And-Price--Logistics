import requests
from django.conf import settings
from decimal import Decimal

class PriceCalculator:
    """
    Comprehensive price calculator for Nepal delivery service
    """
    
    # Base rates
    BASE_RATE_PER_KM = Decimal('50.00')  # NPR per km
    
    # Package type multipliers
    PACKAGE_TYPE_MULTIPLIERS = {
        'document': Decimal('1.0'),
        'standard': Decimal('1.3'),
        'fragile': Decimal('1.6'),
        'heavy': Decimal('1.8'),
    }
    
    # Additional charges
    FUEL_CHARGE_PERCENTAGE = Decimal('0.15')  # 15%
    SERVICE_CHARGE = Decimal('100.00')  # NPR
    FRAGILE_CHARGE = Decimal('200.00')  # NPR
    INSURANCE_CHARGE = Decimal('300.00')  # NPR
    
    # Weight and volume thresholds
    WEIGHT_THRESHOLD = Decimal('5.0')  # kg
    WEIGHT_CHARGE_PER_KG = Decimal('20.00')  # NPR per kg above threshold
    VOLUME_THRESHOLD = Decimal('0.01')  # cubic meters
    VOLUME_CHARGE_PER_CBM = Decimal('5000.00')  # NPR per cubic meter
    
    # Nepal road multiplier (accounting for terrain difficulty)
    ROAD_MULTIPLIER = Decimal('1.25')
    
    def __init__(self):
        self.api_key = getattr(settings, 'GEOAPIFY_API_KEY', None)
        if not self.api_key:
            print("⚠ WARNING: No GEOAPIFY_API_KEY found in settings!")
        else:
            print(f"✓ API Key loaded: {self.api_key[:10]}...")
    
    def geocode_address(self, address):
        """
        Convert address to coordinates using Geoapify Geocoding API
        Returns (latitude, longitude) tuple or None
        """
        if not self.api_key:
            print("⚠ WARNING: No Geoapify API key configured")
            return None
        
        try:
            url = "https://api.geoapify.com/v1/geocode/search"
            params = {
                'text': address,
                'apiKey': self.api_key,
                'limit': 5,  # Get top 5 results to filter
                'filter': 'countrycode:np',
                'bias': 'countrycode:np'  # Strongly prefer Nepal results
            }
            
            headers = {
                'Accept': 'application/json'
            }
            
            print(f"Geocoding address: {address}")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            print(f"Geocoding response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Geocoding API error: {response.text}")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('features') and len(data['features']) > 0:
                # Filter to only include results actually in Nepal
                nepal_results = []
                for feature in data['features']:
                    country = feature['properties'].get('country', '')
                    country_code = feature['properties'].get('country_code', '')
                    
                    if country_code == 'np' or country.lower() == 'nepal':
                        nepal_results.append(feature)
                
                if not nepal_results:
                    print(f"⚠ No Nepal results found for: {address}")
                    return None
                
                # Use the first Nepal result
                coords = nepal_results[0]['geometry']['coordinates']
                lat, lon = coords[1], coords[0]
                formatted_address = nepal_results[0]['properties'].get('formatted', address)
                print(f"✓ Geocoded to: ({lat}, {lon}) - {formatted_address}")
                return (lat, lon)
            
            print(f"⚠ No geocoding results for: {address}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"⚠ Error geocoding address '{address}': {e}")
            return None
        except Exception as e:
            print(f"⚠ Unexpected error in geocoding: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_distance(self, origin, destination):
        """
        Get distance between two locations using Geoapify Routing API
        Returns distance in kilometers
        """
        if not self.api_key:
            print("⚠ WARNING: Using fallback distance (15 km) - No API key")
            return Decimal('15.0')
        
        try:
            # Geocode both addresses
            print(f"=== Getting distance from '{origin}' to '{destination}' ===")
            origin_coords = self.geocode_address(origin)
            destination_coords = self.geocode_address(destination)
            
            if not origin_coords:
                print(f"⚠ Could not geocode origin: {origin}")
                return Decimal('15.0')
            
            if not destination_coords:
                print(f"⚠ Could not geocode destination: {destination}")
                return Decimal('15.0')
            
            # Get route between coordinates
            # IMPORTANT: Geoapify Routing API expects lat,lon format (not lon,lat)
            waypoints = f"{origin_coords[0]},{origin_coords[1]}|{destination_coords[0]},{destination_coords[1]}"
            
            url = "https://api.geoapify.com/v1/routing"
            params = {
                'waypoints': waypoints,
                'mode': 'drive',
                'apiKey': self.api_key
            }
            
            headers = {
                'Accept': 'application/json'
            }
            
            print(f"Fetching route with waypoints: {waypoints}")
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            print(f"Routing response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Routing API error: {response.text[:500]}")
                return Decimal('15.0')
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('features') and len(data['features']) > 0:
                # Distance is in meters
                distance_meters = data['features'][0]['properties']['distance']
                distance_km = Decimal(str(distance_meters / 1000))
                print(f"✓ Calculated distance: {distance_km} km")
                return distance_km
            else:
                print(f"⚠ No route found in API response")
                print(f"API Response: {data}")
                return Decimal('15.0')
                
        except requests.exceptions.RequestException as e:
            print(f"⚠ Error getting distance: {e}")
            return Decimal('15.0')
        except Exception as e:
            print(f"⚠ Unexpected error in get_distance: {e}")
            import traceback
            traceback.print_exc()
            return Decimal('15.0')
    
    def calculate_volume(self, length, width, height):
        """
        Calculate volume in cubic meters
        Input dimensions are in centimeters
        """
        volume_cm3 = length * width * height
        volume_m3 = volume_cm3 / Decimal('1000000')
        return volume_m3
    
    def calculate_price(self, form_data):
        """
        Calculate comprehensive delivery price
        Returns dictionary with detailed breakdown
        """
        # Extract data
        pickup = form_data['pickup_location']
        delivery = form_data['delivery_location']
        length = form_data['length']
        width = form_data['width']
        height = form_data['height']
        weight = form_data['weight']
        package_type = form_data['package_type']
        is_fragile = form_data.get('is_fragile', False)
        needs_insurance = form_data.get('needs_insurance', False)
        
        print(f"Calculating price from {pickup} to {delivery}")
        
        # Calculate distance
        distance = self.get_distance(pickup, delivery)
        
        # Calculate base price
        base_price = self.BASE_RATE_PER_KM * distance
        
        # Calculate weight charge (if over threshold)
        weight_charge = Decimal('0')
        if weight > self.WEIGHT_THRESHOLD:
            excess_weight = weight - self.WEIGHT_THRESHOLD
            weight_charge = excess_weight * self.WEIGHT_CHARGE_PER_KG
        
        # Calculate volume charge
        volume = self.calculate_volume(length, width, height)
        volume_charge = Decimal('0')
        if volume > self.VOLUME_THRESHOLD:
            volume_charge = volume * self.VOLUME_CHARGE_PER_CBM
        
        # Apply package type multiplier
        type_multiplier = self.PACKAGE_TYPE_MULTIPLIERS.get(
            package_type, 
            Decimal('1.3')
        )
        
        # Calculate subtotal with multipliers
        subtotal = (base_price + weight_charge + volume_charge) * type_multiplier * self.ROAD_MULTIPLIER
        
        # Additional charges
        fuel_charge = base_price * self.FUEL_CHARGE_PERCENTAGE
        service_charge = self.SERVICE_CHARGE
        fragility_charge = self.FRAGILE_CHARGE if is_fragile else Decimal('0')
        insurance_charge = self.INSURANCE_CHARGE if needs_insurance else Decimal('0')
        
        # Calculate total
        total = subtotal + fuel_charge + service_charge + fragility_charge + insurance_charge
        
        breakdown = {
            'distance': float(distance),
            'base_price': float(base_price),
            'weight_charge': float(weight_charge),
            'volume_charge': float(volume_charge),
            'volume': float(volume),
            'type_multiplier': float(type_multiplier),
            'road_multiplier': float(self.ROAD_MULTIPLIER),
            'subtotal': float(subtotal),
            'fuel_charge': float(fuel_charge),
            'service_charge': float(service_charge),
            'fragility_charge': float(fragility_charge),
            'insurance_charge': float(insurance_charge),
            'total': float(total),
        }
        
        print(f"Price breakdown: Total = NPR {total}")
        return breakdown