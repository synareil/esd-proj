# esd-proj
Welcome to our LittleFuzzy's Enterprise Solution Development Project. To test this project yourself, please follow the following instruction.
# 1. Set up of docker & environment
In the ESD-Proj directory, use the following command to create docker containers and get the services up. Note: it may take a while
> docker compose up --build

**<p style='red'>Ensure that all microservices are running except for kong-migration<p>**

Run the following commands in git-bash preferably
> ./register_with_kong.sh  <br>
> ./item_dummy.sh

register_with_kong.sh can be found in the root folder, item_dummy.sh can be found in Scripts.

Explanation:
* Register with kong.sh is to register with kong.
* Item_dummy.sh imports dummy data for you to try. 

# 3.Accessing website UI for users and admin
1. Access the users webpage via http://localhost:8008
2. Access the admin webpage via http://localhost:8009


# 4. To bring microservices down
> docker compose down 

To delete all network, databases and containers
> docker compose down -v