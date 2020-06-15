# ElderLift
The elderly aid that connects the elderly to volunteers willing to help. 

Here is the client endpoint:
https://elderlift-client.ue.r.appspot.com

Was deployed to GCloud through App Engine, built using Python Flask. Uses GCloud MySQL as a database. 

Functionality:
CRUD on tasks, and own user accounts.
Filtering tasks based on location.

Issues:
Doesn't actually work right now due to too much cost for gcloud.  

If you want to run on your local device, do the following:
1. Download python, at least version 3.7
2. Download the serverside and clientside folders from this repository or simply fork this repository, and run the command of git clone <repository name> (needs git download)
3. Perform pip install on both the requirements.txt in clientside and serverside folders.
4. Run python3 run.py in serverside.
5. Change the location of the API inside the clientside folders to be localhost:8080 instead of the webserver where it's all held. 
6. Set your OS environment variables of SECRET_KEY, EMAIL_USER, etc. to the right ones. For more information, check out Corey Schafer on setting os variables.
7. Run python3 run.py in clientside. 
8. Enjoy!
  
**To run locally, switch to local_version branch and follow the instructions in the READ ME **
