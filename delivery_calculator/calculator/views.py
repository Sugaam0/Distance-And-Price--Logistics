from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from decimal import Decimal
from .utils import PriceCalculator
from .models import DeliveryCalculation
import json
import traceback

def calculator_view(request):
    """
    Main calculator view
    """
    context = {
        'geoapify_api_key': getattr(settings, 'GEOAPIFY_API_KEY', '')
    }
    return render(request, 'calculator/calculator.html', context)

@csrf_exempt  # For testing - remove in production
def calculate_price_api(request):
    """
    API endpoint for price calculation
    """
    print(f"=== Request received: {request.method} ===")
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Only POST method is allowed'
        }, status=405)
    
    try:
        # Parse JSON data
        body = request.body.decode('utf-8')
        print(f"Request body: {body}")
        data = json.loads(body)
        print(f"Parsed data: {data}")
        
        # Validate required fields
        required_fields = ['pickup_location', 'delivery_location', 'length', 'width', 'height', 'weight', 'package_type']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return JsonResponse({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)
        
        # Convert to proper types
        try:
            form_data = {
                'pickup_location': str(data['pickup_location']),
                'delivery_location': str(data['delivery_location']),
                'length': Decimal(str(data['length'])),
                'width': Decimal(str(data['width'])),
                'height': Decimal(str(data['height'])),
                'weight': Decimal(str(data['weight'])),
                'package_type': str(data['package_type']),
                'is_fragile': bool(data.get('is_fragile', False)),
                'needs_insurance': bool(data.get('needs_insurance', False)),
            }
            print(f"Form data prepared: {form_data}")
        except (ValueError, TypeError, KeyError) as e:
            print(f"Data conversion error: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Invalid data format: {str(e)}'
            }, status=400)
        
        # Calculate price
        print("Initializing calculator...")
        calculator = PriceCalculator()
        
        print("Calculating price...")
        price_breakdown = calculator.calculate_price(form_data)
        print(f"Price breakdown calculated: {price_breakdown}")
        
        # Save calculation to database
        try:
            calculation = DeliveryCalculation.objects.create(
                pickup_location=form_data['pickup_location'],
                delivery_location=form_data['delivery_location'],
                length=form_data['length'],
                width=form_data['width'],
                height=form_data['height'],
                weight=form_data['weight'],
                package_type=form_data['package_type'],
                is_fragile=form_data['is_fragile'],
                needs_insurance=form_data['needs_insurance'],
                distance=Decimal(str(price_breakdown['distance'])),
                total_price=Decimal(str(price_breakdown['total']))
            )
            print(f"✓ Saved to database with ID: {calculation.id}")
        except Exception as e:
            print(f"⚠ Database save error (non-critical): {e}")
            # Continue even if save fails
        
        print("=== Returning success response ===")
        return JsonResponse({
            'success': True,
            'breakdown': price_breakdown
        })
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format in request'
        }, status=400)
    except Exception as e:
        print(f"!!! Unexpected error: {e}")
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)