# esd-proj
Welcome to our LittleFuzzy's Enterprise Solution Development Project. To test this project yourself, please follow the following instruction.
# 1. Set up of docker & environment
In the ESD-Proj directory, use the following command to create docker containers and get the services up. Note: it may take a while
> docker compose up --build

**Ensure that all microservices are running except for kong-migration**

Run the following commands in git-bash preferably
> ./register_with_kong.sh 
> ./item_dummy.sh

Explaination:
* Register with kong.sh is to register with kong. 
* Item_dummy.sh imports dummy data for you to try. 

# 3. Running the website front-end for users and admin
1. To access **user-end** front-end, Access the webpage via http://localhost:8009

# 4. To bring microservices down
> docker compose down 

To delete all network, databases and containers
> docker compose down -v