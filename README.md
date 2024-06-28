## Web framework: Django

Instagram like application with web interface based on Django and SQLite database.

## Description:

The user can register on the website by email. 
After basic registration, the user will receive an email with unique link to continue registration. 
The user who goes by the link will be redirected to the profile page to add full name, bio and avatar. 
Next, user can create posts with images, see posts of other users via feed of the latest posts. 
Unauthorized guests cannot view the profiles, fullname and avatars of users. Each post may have multiple images and tags. 
Users may like and unlike posts.

## Installation:

Clone a project:
```
git clone https://github.com/ArtemiLapitski/djangogramm-app.git
```

Open project directory:
```
cd djangogramm-app
```

Open djangogramm directory:
```
cd djangogramm
```

Create a virtualenv or skip this point.
Activate virtualenv.

Install the requirements:
```
pip install -r requirements.txt
```

Create the file .env.  Use .env.example file as an example.

Migrate data to database:
```
python manage.py migrate
```

To run on local server:
```
python manage.py runserver
```
Url: http://127.0.0.1:8000/


### To deploy app on remote server using docker:


Make sure you have docker installed and daemon running.

Build docker image:
```
docker build -t djangogramm .
```
If remote server platform is other than 'linux/amd64', then use this command:
```
docker build --build-arg TARGET_PLATFORM=your_remote_server_platform -t djangogramm .
```
Log in to docker:
```
docker login
```

Create docker repository on the hosting service of your choice.

Tag your local image to remote repository:
```
docker tag djangogramm new-repo:tagname  
```
Push image to remote repository:
```
docker push new-repo:tagname
```

### Fulfill the steps below on your remote server:

Make sure docker is installed and running. 

Log in to docker:
```
docker login
```
Pull image to your server:
```
docker pull new-repo:tagname
```
Run docker image:
```
docker run -it -p 8000:8000 your_image_name
```
