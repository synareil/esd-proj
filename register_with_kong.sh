#!/bin/bash

# Kong admin URL
KONG_ADMIN_URL=http://localhost:8001

# Service details
SERVICE_NAME="shipping"
SERVICE_URL="http://shipping:5000/shipping"
ROUTE_PATHS="/shipping"

# Register service with Kong
echo "Registering $SERVICE_NAME with Kong..."
curl -i -X POST --url $KONG_ADMIN_URL/services/ --data "name=$SERVICE_NAME" --data "url=$SERVICE_URL"

# Add a route for the service
echo "Adding route for $SERVICE_NAME..."
curl -i -X POST --url $KONG_ADMIN_URL/services/$SERVICE_NAME/routes --data "paths[]=$ROUTE_PATHS"

# Service details
SERVICE_NAME="cart"
SERVICE_URL="http://cart:5000/cart"
ROUTE_PATHS="/cart"

# Register service with Kong
echo "Registering $SERVICE_NAME with Kong..."
curl -i -X POST --url $KONG_ADMIN_URL/services/ --data "name=$SERVICE_NAME" --data "url=$SERVICE_URL"

# Add a route for the service
echo "Adding route for $SERVICE_NAME..."
curl -i -X POST --url $KONG_ADMIN_URL/services/$SERVICE_NAME/routes --data "paths[]=$ROUTE_PATHS"

# Service details
SERVICE_NAME="order"
SERVICE_URL="http://order:5000/order"
ROUTE_PATHS="/order"

# Register service with Kong
echo "Registering $SERVICE_NAME with Kong..."
curl -i -X POST --url $KONG_ADMIN_URL/services/ --data "name=$SERVICE_NAME" --data "url=$SERVICE_URL"

# Add a route for the service
echo "Adding route for $SERVICE_NAME..."
curl -i -X POST --url $KONG_ADMIN_URL/services/$SERVICE_NAME/routes --data "paths[]=$ROUTE_PATHS"

# Service details
SERVICE_NAME="inventory"
SERVICE_URL="http://inventory:5000/item"
ROUTE_PATHS="/item"

# Register service with Kong
echo "Registering $SERVICE_NAME with Kong..."
curl -i -X POST --url $KONG_ADMIN_URL/services/ --data "name=$SERVICE_NAME" --data "url=$SERVICE_URL"

# Add a route for the service
echo "Adding route for $SERVICE_NAME..."
curl -i -X POST --url $KONG_ADMIN_URL/services/$SERVICE_NAME/routes --data "paths[]=$ROUTE_PATHS"

# Service details
SERVICE_NAME="marketing-content"
SERVICE_URL="http://marketing-content:80/"
ROUTE_PATHS="/marketing-content"

# Register service with Kong
echo "Registering $SERVICE_NAME with Kong..."
curl -i -X POST --url $KONG_ADMIN_URL/services/ --data "name=$SERVICE_NAME" --data "url=$SERVICE_URL"

# Add a route for the service
echo "Adding route for $SERVICE_NAME..."
curl -i -X POST --url $KONG_ADMIN_URL/services/$SERVICE_NAME/routes --data "paths[]=$ROUTE_PATHS"

# Service details
SERVICE_NAME="placeorder"
SERVICE_URL="http://placeorder:80/"
ROUTE_PATHS="/placeorder"

# Register service with Kong
echo "Registering $SERVICE_NAME with Kong..."
curl -i -X POST --url $KONG_ADMIN_URL/services/ --data "name=$SERVICE_NAME" --data "url=$SERVICE_URL"

# Add a route for the service
echo "Adding route for $SERVICE_NAME..."
curl -i -X POST --url $KONG_ADMIN_URL/services/$SERVICE_NAME/routes --data "paths[]=$ROUTE_PATHS"


# Service details
SERVICE_NAME="manageproduct"
SERVICE_URL="http://manageproduct:80/"
ROUTE_PATHS="/manageproduct"

# Register service with Kong
echo "Registering $SERVICE_NAME with Kong..."
curl -i -X POST --url $KONG_ADMIN_URL/services/ --data "name=$SERVICE_NAME" --data "url=$SERVICE_URL"

# Add a route for the service
echo "Adding route for $SERVICE_NAME..."
curl -i -X POST --url $KONG_ADMIN_URL/services/$SERVICE_NAME/routes --data "paths[]=$ROUTE_PATHS"

# Service details
SERVICE_NAME="search"
SERVICE_URL="http://search:80/"
ROUTE_PATHS="/search"

# Register service with Kong
echo "Registering $SERVICE_NAME with Kong..."
curl -i -X POST --url $KONG_ADMIN_URL/services/ --data "name=$SERVICE_NAME" --data "url=$SERVICE_URL"

# Add a route for the service
echo "Adding route for $SERVICE_NAME..."
curl -i -X POST --url $KONG_ADMIN_URL/services/$SERVICE_NAME/routes --data "paths[]=$ROUTE_PATHS"

# Service details
SERVICE_NAME="recommendation"
SERVICE_URL="http://recommendation:80/"
ROUTE_PATHS="/recommendation"

# Register service with Kong
echo "Registering $SERVICE_NAME with Kong..."
curl -i -X POST --url $KONG_ADMIN_URL/services/ --data "name=$SERVICE_NAME" --data "url=$SERVICE_URL"

# Add a route for the service
echo "Adding route for $SERVICE_NAME..."
curl -i -X POST --url $KONG_ADMIN_URL/services/$SERVICE_NAME/routes --data "paths[]=$ROUTE_PATHS"

#Adding Cors
curl -i -X POST http://localhost:8001/services/shipping/plugins \
    --data "name=cors" \
    --data "config.origins=*" \
    --data "config.headers=Accept, Authorization, Content-Type" \
    --data "config.exposed_headers=Authorization" \
    --data "config.credentials=true" \
    --data "config.max_age=3600"

curl -i -X POST http://localhost:8001/services/cart/plugins \
    --data "name=cors" \
    --data "config.origins=*" \
    --data "config.headers=Accept, Authorization, Content-Type" \
    --data "config.exposed_headers=Authorization" \
    --data "config.credentials=true" \
    --data "config.max_age=3600"

curl -i -X POST http://localhost:8001/services/order/plugins \
    --data "name=cors" \
    --data "config.origins=*" \
    --data "config.headers=Accept, Authorization, Content-Type" \
    --data "config.exposed_headers=Authorization" \
    --data "config.credentials=true" \
    --data "config.max_age=3600"

curl -i -X POST http://localhost:8001/services/inventory/plugins \
    --data "name=cors" \
    --data "config.origins=*" \
    --data "config.headers=Accept, Authorization, Content-Type" \
    --data "config.exposed_headers=Authorization" \
    --data "config.credentials=true" \
    --data "config.max_age=3600"

curl -i -X POST http://localhost:8001/services/marketing-content/plugins \
    --data "name=cors" \
    --data "config.origins=*" \
    --data "config.headers=Accept, Authorization, Content-Type" \
    --data "config.exposed_headers=Authorization" \
    --data "config.credentials=true" \
    --data "config.max_age=3600"

curl -i -X POST http://localhost:8001/services/placeorder/plugins \
    --data "name=cors" \
    --data "config.origins=*" \
    --data "config.headers=Accept, Authorization, Content-Type" \
    --data "config.exposed_headers=Authorization" \
    --data "config.credentials=true" \
    --data "config.max_age=3600"

curl -i -X POST http://localhost:8001/services/manageproduct/plugins \
    --data "name=cors" \
    --data "config.origins=*" \
    --data "config.headers=Accept, Authorization, Content-Type" \
    --data "config.exposed_headers=Authorization" \
    --data "config.credentials=true" \
    --data "config.max_age=3600"

curl -i -X POST http://localhost:8001/services/search/plugins \
    --data "name=cors" \
    --data "config.origins=*" \
    --data "config.headers=Accept, Authorization, Content-Type" \
    --data "config.exposed_headers=Authorization" \
    --data "config.credentials=true" \
    --data "config.max_age=3600"

curl -i -X POST http://localhost:8001/services/recommendation/plugins \
    --data "name=cors" \
    --data "config.origins=*" \
    --data "config.headers=Accept, Authorization, Content-Type" \
    --data "config.exposed_headers=Authorization" \
    --data "config.credentials=true" \
    --data "config.max_age=3600"