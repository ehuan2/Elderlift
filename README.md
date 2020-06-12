# Elder_Lift
The elderly aid that connects the elderly to volunteers willing to help

Here are the steps to run on your local device:
(0 open terminal)
1. Download Python, at least v3.7 - check by running ```python3 --version```
2. Download the serverside and the clientside folders
3. cd into the serverside then do the following: 
```pip3 install requirements.txt```
(cd means to change directory, so do the following)
```cd {absolute path of directory}```
4. Do the same with the clientside
5. Set up your env. variables needed for the serverside: 
Links on how (Windows: https://www.youtube.com/watch?v=IolxqkL7cD8, Mac/Linux: https://www.youtube.com/watch?v=5iWhQWVXosU)
EMAIL_USER, EMAIL_PASS, SECRET_KEY
Make sure to use an email that has its default security measures deactivated (should be fine, can reenable after test)
The secret key can literally be anything you want, just a string
6. cd into the serverside and run the following -> make sure to keep it running
```python3 run.py```
7. Repeat the same for clientside, but run on a new terminal

Click the link from the clientside running flask application, and enjoy!
