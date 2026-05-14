from sql.executor import execute_query

# .NET RentalOrder Status enum values
STATUS_MAP = {
    0: "Pending",
    1: "Accepted",
    2: "Rejected",
    3: "Completed",
    4: "In Progress",
    5: "Returned",
    6: "CANCELLED",
}

def check_orders():
    print("Fetching Rental Orders...\n")
    query = """
    SELECT 
        o.Id         AS OrderId,
        p.Name       AS ProductName,
        u.FullName   AS RenterName,
        o.Status,
        o.TotalAmount,
        o.CreatedAt,
        d.StartDate,
        d.EndDate,
        d.City
    FROM RentalOrders o
    JOIN Products p      ON o.ProductId = p.Id
    JOIN AspNetUsers u   ON o.RenterId  = u.Id
    LEFT JOIN RentalOrderDetails d ON d.RentalOrderId = o.Id
    ORDER BY o.CreatedAt DESC
    """

    try:
        orders = execute_query(query)
        if not orders:
            print("No orders found in the database.")
            return

        print(f"Found {len(orders)} order(s):\n")
        for order in orders:
            status_label = STATUS_MAP.get(order['Status'], f"Unknown ({order['Status']})")
            print(f"Order #{order['OrderId']}")
            print(f"  Product:  {order['ProductName']}")
            print(f"  Renter:   {order['RenterName']}")
            print(f"  Status:   {status_label}")
            print(f"  Amount:   {order['TotalAmount']} EGP")
            print(f"  Dates:    {order['StartDate']} to {order['EndDate']}")
            print(f"  City:     {order['City']}")
            print(f"  Created:  {order['CreatedAt']}")
            print("-" * 40)

    except Exception as e:
        print(f"Error fetching orders: {e}")

if __name__ == "__main__":
    check_orders()
