import os
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DOTNET_API_BASE = os.environ.get("DOTNET_API_BASE", "http://rentalplatform.runaspnet")
TIMEOUT_SECONDS = int(os.environ.get("DOTNET_API_TIMEOUT", "10"))

async def create_rental_order(
    auth_token: str,
    product_id: int,
    start_date: str,
    end_date: str,
    delivery_method: str,
    street: str,
    city: str,
    governorate: str,
    terms_agreed: bool = True
) -> dict:
    """
    Calls POST /api/RentalOrder on the .NET API.
    """
    url = f"{DOTNET_API_BASE}/api/RentalOrder"
    
    # Format dates as ISO strings (the prompt already gives them as YYYY-MM-DD, 
    # but the API might prefer ISO with time. We'll send as is, or append time if needed).
    if len(start_date) == 10:
        start_date += "T00:00:00.000Z"
    if len(end_date) == 10:
        end_date += "T23:59:59.000Z"

    payload = {
        "productId": product_id,
        "startDate": start_date,
        "endDate": end_date,
        "deliveryMethod": delivery_method,
        "street": street or "",
        "city": city or "",
        "governorate": governorate or "",
        "termsAgreed": terms_agreed
    }

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code in (200, 201):
                data = response.json() if response.text else {}
                return {
                    "success": True, 
                    "order_id": data.get("id") or data.get("orderId") or "Success",
                    "error": None,
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "order_id": None,
                    "error": f"API Error {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
    except Exception as e:
        return {
            "success": False,
            "order_id": None,
            "error": f"Request failed: {str(e)}"
        }


async def cancel_rental_order(auth_token: str, order_id: int) -> dict:
    """
    Calls PUT /api/RentalOrder/{id}/cancel on the .NET API.
    Requires a valid Bearer token.
    """
    url = f"{DOTNET_API_BASE}/api/RentalOrder/{order_id}/cancel"

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.put(url, headers=headers)

        if response.status_code in (200, 201, 204):
            return {"success": True, "error": None, "status_code": response.status_code}
        else:
            return {
                "success": False,
                "error": f"API Error {response.status_code}: {response.text}",
                "status_code": response.status_code
            }
    except Exception as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
