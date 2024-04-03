# esd-proj
# 1. Set up of docker

# 2. Set up of environment
To get the services up use the following command
> docker compose up --build

Go to docker desktop and make sure that 19/20 microservices are running. Everything but kong-migration must be running.
After that, register with kong in git bash 
> ./register_with_kong.sh

To add in dummy data, go to the scripts folder:
> ./item_dummy.sh

# 3. Running the website front-end for users and admin
1. To access **user-end** front-end, cd to the userfrontend folder and type the following:
> python -m http.server 8008

Access the webpage via http://localhost:8008

# 4. To bring microservices down
> docker compose down 

To delete all network and database
> docker compose down -v