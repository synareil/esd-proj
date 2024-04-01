# Kong admin URL
$KONG_ADMIN_URL = "http://localhost:8001"

# Function to register service and add a route in Kong
Function Register-ServiceAndRoute {
    param (
        [string]$serviceName,
        [string]$serviceUrl,
        [string]$routePaths
    )

    # Register service with Kong
    Write-Host "Registering $serviceName with Kong..."
    curl -Method POST -Uri "$KONG_ADMIN_URL/services/" -Body "name=$serviceName&url=$serviceUrl"

    # Add a route for the service
    Write-Host "Adding route for $serviceName..."
    curl -Method POST -Uri "$KONG_ADMIN_URL/services/$serviceName/routes" -Body "paths[]=$routePaths"
}

# Service details and registration
Register-ServiceAndRoute -serviceName "shipping" -serviceUrl "http://shipping:5000/shipping" -routePaths "/shipping"
Register-ServiceAndRoute -serviceName "cart" -serviceUrl "http://cart:5000/cart" -routePaths "/cart"
Register-ServiceAndRoute -serviceName "order" -serviceUrl "http://order:5000/order" -routePaths "/order"
Register-ServiceAndRoute -serviceName "inventory" -serviceUrl "http://inventory:5000/item" -routePaths "/item"
Register-ServiceAndRoute -serviceName "marketing-content" -serviceUrl "http://marketing-content:80/" -routePaths "/marketing-content"
Register-ServiceAndRoute -serviceName "placeorder" -serviceUrl "http://placeorder:80/" -routePaths "/placeorder"
Register-ServiceAndRoute -serviceName "manageproduct" -serviceUrl "http://manageproduct:80/" -routePaths "/manageproduct"
