So this is the serverside API:

Here are the necessary endpoints: Always has /v1/api


Users Endpoint:

POST Register: /register - Needs password, user_role, name, email, address, city and country
GET Register Token: /register/<token> 
POST Login: /login - Needs Email, Password and Remember
GET, PUT, DELETE Account: /account - Login required, All fields for PUT
GET Logout: /logout
GET User Info: /user/<int:user_id> - Gets the info based on user
POST Reset Password Request: /reset_password - Needs Email
POST Reset Password: /reset_password/<token> - Needs Password

Tasks Endpoint:

POST New Task: /elderly/new_task - Needs Title, Content
GET, PUT, DELETE Task: /elderly/<int:task_id> - Login required
