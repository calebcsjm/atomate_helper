### MongoDB Setup:

1. Create an account on MongoDB Atlas.
   - Select the "Cloud" deployment
2. Pick a name for the oganization and for the project
3. Select Python as the preferred langauge. 
4. Create a free shared cluster - the cloud provider and region doesn't matter much
5. Set up the Database users
   - On the left side, under Security, select Database Access.
   - Click "Add a New Database User"
   - Using the Password Authentication method, set a username and password, and then change "Database User Prvileges" to be "Atlas admin"
   - Set up a second user, also using the password method, but with "Only read any database" privileges (I am honestly not sure when atomate ever uses this, but they ask for a second user).
   - Make a note of these usernames and passwords, as they are required in the config files during the atomate setup
6. Add IP addresses
   - Under Security, select Network Access.
   - I found it simplest just to select "Allow Access From Anywhere," which prevents any issues with the connection coming from a new location. If you have skills for it and want a more secure connection, feel free to add individual IP addresses. 
7. Get the connection string
   - Under "Deployment" in the top left, select Databases, and then click on "Connect" next to the name of your cluster. 
   - _NOTE: I highly recommend looking at the tutorials and setting up MongoDB Compass, which is a nice GUI to interact with the database. It is very helpful for troubleshooting and code development._
   - Select "Connect your application"
   - Chose the driver as Python, and select the version matching your atomate environment (I set atomate up with Python 3.8, because the default python for the supercomputer, 3.6, couldn't install the needed update for numpy)
   - Copy the connection string that it provides. As described in the atomate installation notes, you will need to edit that string to match the format atomate wants. 
   - Example: `mongodb+srv://adminuser:<password>@cluster0.mcvql.mongodb.net/myFirstDatabase?retryWrites=true&w=majority` -> `mongodb+srv://cluster0.mcvql.mongodb.net`
8. Do a happy dance 
