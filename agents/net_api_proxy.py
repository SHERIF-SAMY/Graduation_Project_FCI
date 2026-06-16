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
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
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
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
            response = await client.put(url, headers=headers)

        if response.status_code in (200, 201, 204):
            return {"success": True, "error": None, "status_code": response.status_code}
        else:
            return {"success": False, "error": f"API Error {response.status_code}: {response.text}", "status_code": response.status_code}
    except Exception as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}


async def get_my_orders(auth_token: str, status_filter: Optional[int] = None) -> dict:
    """
    Calls BOTH:
      - GET /api/UserDashboard/renter/recent-activities
      - GET /api/UserDashboard/renter/recent-rentals
    Merges the results (deduplicates by orderId) and returns the combined list.
    No user_id needed — uses Bearer token only.

    status_filter: if set, filters to only orders with this status
                   (0=Pending, 1=Accepted, 2=Rejected, 3=Completed, 4=InProgress, 6=Cancelled)
    """
    urls = [
        f"{DOTNET_API_BASE}/api/UserDashboard/renter/recent-activities",
        f"{DOTNET_API_BASE}/api/UserDashboard/renter/recent-rentals",
    ]
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    all_orders: list[dict] = []
    seen_ids: set = set()

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
            for url in urls:
                try:
                    response = await client.get(url, headers=headers)
                    endpoint_name = url.split("/")[-1]
                    print(f"[NetAPI] GET {endpoint_name} status: {response.status_code}")
                    print(f"[NetAPI] GET {endpoint_name} snippet: {response.text[:500]}")

                    if response.status_code == 200:
                        data = response.json()
                        # Extract list from response
                        if isinstance(data, list):
                            items = data
                        else:
                            items = (
                                data.get("recentActivities")
                                or data.get("recentRentals")
                                or data.get("activities")
                                or data.get("rentals")
                                or data.get("items")
                                or data.get("orders")
                                or data.get("data")
                                or []
                            )

                        for item in items:
                            oid = item.get("orderId") or item.get("id") or item.get("Id")
                            prod_name = item.get("productName") or item.get("ProductName") or (
                                isinstance(item.get("product"), dict) and item["product"].get("name")
                            )
                            if oid and prod_name:
                                is_valid_id = False
                                try:
                                    if int(oid) > 0:
                                        is_valid_id = True
                                except (ValueError, TypeError):
                                    if isinstance(oid, str) and oid.strip() and oid.strip().lower() not in ("none", "null", "0", ""):
                                        is_valid_id = True
                                
                                if is_valid_id and oid not in seen_ids:
                                    seen_ids.add(oid)
                                    all_orders.append(item)
                    elif response.status_code == 401:
                        return {"success": False, "orders": [], "error": "unauthorized", "status_code": 401}
                    else:
                        print(f"[NetAPI] {endpoint_name} non-200: {response.status_code} {response.text[:200]}")
                except Exception as inner_e:
                    print(f"[NetAPI] Error calling {url}: {inner_e}")

        # Apply status filter if requested
        if status_filter is not None and all_orders:
            def _matches(o):
                val = o.get("status") if o.get("status") is not None else o.get("Status")
                if val is None:
                    return False
                norm_val = str(val).strip().lower().replace(" ", "")
                filter_map = {
                    0: ["pending", "0"],
                    1: ["accepted", "1"],
                    2: ["rejected", "2"],
                    3: ["completed", "3"],
                    4: ["inprogress", "4"],
                    5: ["returned", "5"],
                    6: ["cancelled", "6"]
                }
                allowed = filter_map.get(status_filter, [])
                return norm_val == str(status_filter) or norm_val in allowed

            all_orders = [o for o in all_orders if _matches(o)]

        return {"success": True, "orders": all_orders, "error": None, "status_code": 200}

    except Exception as e:
        return {"success": False, "orders": [], "error": f"Request failed: {str(e)}"}


async def get_wallet_balance(auth_token: str) -> dict:
    """
    GET /api/Wallet/balance
    Returns: {"success": bool, "balance": float, "currency": str, "error": str|None}
    """
    url = f"{DOTNET_API_BASE}/api/Wallet/balance"
    headers = {"Authorization": f"Bearer {auth_token}"}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "balance": float(data.get("balance", 0)),
                "currency": data.get("currency", "EGP"),
                "error": None,
                "status_code": 200
            }
        else:
            return {"success": False, "balance": 0.0, "currency": "EGP",
                    "error": f"HTTP {response.status_code}", "status_code": response.status_code}
    except Exception as e:
        return {"success": False, "balance": 0.0, "currency": "EGP", "error": str(e)}


async def get_product_insurance(product_id: int) -> dict:
    """
    GET /api/Product/{id}  (no auth required — public endpoint)
    Returns: {"success": bool, "insurance_amount": float, "error": str|None}
    """
    url = f"{DOTNET_API_BASE}/api/Product/{product_id}"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
            response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "insurance_amount": float(data.get("insuranceAmount", 0)),
                "error": None
            }
        else:
            return {"success": False, "insurance_amount": 0.0,
                    "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "insurance_amount": 0.0, "error": str(e)}

