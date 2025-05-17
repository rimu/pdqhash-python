You need redis and python 3.9+ installed.

git clone the files into a directory somewhere:

`git clone --recurse-submodules https://github.com/rimu/pdqhash-python.git`

then change into the directory:

`cd pdqhash-python`

create a python virtual environment:

`python3 -m venv venv`

activate the environment:

`source venv/bin/activate`


install all the dependencies:

`pip install -r requirements.txt`

compile some dependencies:

`pip install -e .`

set an environment variable:

`export QUART_APP=app.py`

boot up the web server:

`quart run`

If all goes to plan then you will see messages on the screen indicating the IP and port where the API is running. Most likely it
will be http://127.0.0.1:5000 so try http://127.0.0.1:5000/pdq-hash?image_url=something in your browser and see if you see JSON. "Something" can be the url to any image.

If that's working fine then use Ctrl + C to stop the test server. For production you need to use uvicorn instead of 'quart run'.

There are a lot of ways you could do that. If you're into docker and have redis running on the host (not in a container) try
`docker-compose up --build` and it might just work. If you'd like to run a redis instance in a container then edit docker-compose.yml and add the container and tweak the REDIS_URI environment variable.
