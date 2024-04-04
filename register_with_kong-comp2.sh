#!/bin/bash

# Kong admin URL
KONG_ADMIN_URL=http://192.168.202.53:8001

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

#Service details
SERVICE_NAME="order"
SERVICE_URL="http://order:5000/order"
ROUTE_PATHS="/order"

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

#Adding Cors
curl -i -X POST http://localhost:8001/services/order/plugins \
    --data "name=cors" \
    --data "config.origins=*" \
    --data "config.headers=Accept, Authorization, Content-Type" \
    --data "config.exposed_headers=Authorization" \
    --data "config.credentials=true" \
    --data "config.max_age=3600"