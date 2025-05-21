# cse2102-spring25-team3

This is a group project for creating a Pet Adoption Website. All work is contained in this repository.

## Trello Board

[cse2102-spring25-team3-trello-board](https://trello.com/b/TMf0n9g8/cse-2102-group-3-trello-board)

## Prototype Link

[cse2102-spring25-team3-prototype](https://www.figma.com/design/Yxjq3zPTtxVf5x3YweH5u5/Pet-Adoption-Project?node-id=0-1&t=M1CZAgbuuqOmQ3uO-1)

## Team Members

| Name             | NetID    |
| ---------------- | -------- |
| Owen Zheng       | owz22001 |
| Rohit Suresh     | rhs22002 |
| Zachary Demanche | zad22002 |
| Jiawen Chen      | jic22026 |

## Initial Steps (IMPORTANT DON'T SKIP)

Follow the following steps to initialize everything

1. Download all files from the repository
2. Change directory to the directory that contains the backend and frontend folder
3. Inside the backend folder create a file called ".env", ignoring the quotation marks copy the name as is.
    - Create a secret key in the file (Type exactly this or change the secret key if you like): SECRET_KEY = "secretkeyexample123"
4. Initialize the database:
    - (on Mac): python3 initdatabase.py
    - (on Windows): python initdatabase.py
5. Start and open Docker Desktop

## Running Virtual Environment (Recommended)

Follow the following steps to run on Virtual Environment

1. Make sure to be in the root directory which contains the backend/frontend directory and others.
2. run command:
    - (on Mac): python3 venv venv
    - (on Windows): python venv venv
3. run command:
    - (on Mac): source venv/bin/activate
    - (on Windows): .\venv\Scripts\activate

## Run Backend Docker Image

Follow the following steps to dockerize the backend

1. Change directory to backend directory
2. run command(don't forget the .): docker build -t backend .
3. run command: docker run -d -p 5000:5000 backend
4. Go to your web browser: [http://localhost:5000/](http://localhost:5000/)
5. To check swagger: [http://localhost:5000/apidocs](http://localhost:5000/apidocs)

## Run Frontend Docker Image

Follow the following steps to dockerize the frontend

1. Change directory to frontend directory
2. run command(don't forget the .): docker build -t frontend .
3. run command: docker run -d -p 5173:5173 frontend
4. Go to your web browser: [http://localhost:5173/](http://localhost:5173/)

## Features in the Web App
- You can login as an admin:
    - username: admin
    - password: adminpass123
- Or sign up as a normal user
- When adding or editing pets, you might have to refresh the page in order to see the changes.
- If you would like to add a pet, you need to find an image URL from the internet.

## Stop/Clear docker container/image

Follow the following steps to stop and clear docker containers and images(Follow the steps in order)

### Stop Docker Container

1. run command: docker ps -a
    - You should see the container id that contains the frontend and backend
2. run command: docker stop container_id
    - Fill the container id with what you found in step 1

### Remove All Stopped Docker Container

1. run command: docker container prune
    - Enter Y when prompted

### Remove All unused Docker images (Optional)
1. run command: docker image prune -a
    - Optionally you can also delete specific images
    - run command: docker images:
        - You should see image ID
        - run command: docker image rm image_id
