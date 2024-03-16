#!/bin/sh

# Register service with Consul
curl --request PUT --data @service.json http://consul:8500/v1/agent/service/register

# Execute CMD
exec "$@"
