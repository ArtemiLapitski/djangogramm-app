## Technologies and Frameworks Used:

Instagram like application with web interface based on Django and SQLite database. 
AWS S3 along with AWS Lambda services are used to store and process images.
Also, there are Single-Page Application (SPA) elements added to the project, namely 'Like' and 'Follow' buttons are 
updated dynamically using AJAX.
Users are able to log in via third-party services like Google or Github.
The app is currently deployed at http://djangogramm.online/

## User Experience and Features:

The user can register on the website by email or via third-party services like Google or Github.
After basic registration using email, the user will receive an email with unique link to activate the account. 
The user who goes by the link will be redirected to the activation page to add full name, bio and avatar. 
Next, user can create posts with images, follow other users, see posts of other users via feed of the latest posts. 
Unauthorized guests cannot view the profiles, fullname and avatars of users. Each post may have multiple images and tags. 
Users may also like/unlike posts and request password change.

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

Install python requirements:
```
pip install -r requirements.txt
```

Create the file .env.  Use .env.example file as an example.

Migrate data to database:
```
python manage.py migrate
```

Collect static files:
```
python manage.py collectstatic
```

Create superuser if needed:
```
python manage.py createsuperuser
```

To run on local server:
```
python manage.py runserver
```
Url: http://127.0.0.1:8000/


### To deploy app on remote server using docker:

#### Follow steps below on your local server:

Make sure you have docker installed and daemon running.

Build docker image:
```
docker build -t djangogramm .
```
If remote server platform is other than 'linux/amd64', then use this command:
```
docker build --build-arg TARGET_PLATFORM=your_remote_server_platform -t djangogramm .
```
Login to docker:
```
docker login
```

Create docker repository on the hosting service of your choice.

Tag your local image to remote repository. Adding tagname is optional. New repo is the name of new repository:
```
docker tag djangogramm new-repo:tagname  
```
Push image to remote repository:
```
docker push new-repo:tagname
```

#### Follow steps below on your remote server:

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

Register on the website or log in using test account:

Email:
```
jsmith@mail.com
```
Password:
```
8uhb5thm
```

### To run isolated tests use the following commands:
```
python manage.py test --settings=djangogramm.test_settings feed
```
```
python manage.py test --settings=djangogramm.test_settings users
```
