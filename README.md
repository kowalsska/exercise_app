# Coding Exercise


## To run the app

Make sure Docker is running.
Run this in the root directory of the project:

`bash start.sh`

And follow the prompts. Leave the input empty to access the host's root directory.

(When running the app for the first time macOS will prompt you for allowing access to directories. Click Allow on all the prompts.)


### Instructions
Use query param `q` to traverse the current directory. For example:

`http://0.0.0.0:8000/?q=Users`

`http://0.0.0.0:8000/?q=sys/kernel/irq`


### Documentation
When the app is running you can access the automatically generated documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)


## Testing
Use following commands to create a virtual environment and install the packages using following commands, then run the tests.
```
python3 -m venv venv
. venv/bin/activate
make setup
make test
```

## Notes
1.
I installed [this](https://chrome.google.com/webstore/detail/jsonview/chklaanhfefbnpoihckbnefhakgolnmc) Chrome plugin that automatically formats JSON data in the browser and makes it look more readable

2.
The application accesses the host's root directory. I wasn't able to access folders like Users or System until I changed this Docker configuration. It has something to do with latest macOS security features. If you encounter the same issue go to Docker's Preferences -> Experimental Features and disable `Use gRPC FUSE for file sharing`
![alt text](https://i.imgur.com/aRoLWOe.png)


## What it looks like

![alt text](https://i.imgur.com/Y4CDopf.png)


![alt text](https://i.imgur.com/iue2D4m.png)


