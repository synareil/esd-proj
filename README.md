# esd-proj
Welcome to our LittleFuzzy's Enterprise Solution Development Project. To test this project yourself, please follow the following instruction.
# 1. Set up of docker & environment
1. In the ESD-Proj directory, use the following command to create docker containers and get the services up. Note: it may take a while
> docker compose up --build

**Ensure that all microservices are running except for kong-migration<p>**

2. You may edit ./user_dummy.sql in Scripts, by changing 'youremail@example.com' to your email

3. Run the following commands in git-bash
> source ./register_with_kong.sh  <br>
> source ./item_dummy.sh

register_with_kong.sh can be found in the root folder, item_dummy.sh can be found in Scripts.

Explanation:
* Register with kong.sh is to register with kong.
* Item_dummy.sh imports dummy data for you to try. 

# 2.Ensure you have env_files folder
1. Unzip and place in root directory
2. you may request the file from julian.maximal@gmail.com

# 3.Accessing website UI for users and admin
1. Access the users webpage via http://localhost:8008
2. Access the admin webpage via http://localhost:8009


# 4. To bring microservices down
> docker compose down 

To delete all network, databases and containers
> docker compose down -v