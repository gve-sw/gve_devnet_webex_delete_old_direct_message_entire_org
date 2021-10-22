# Webex Delete Old Direct Messages Entire Org Sample

Cisco Webex Messaging allows organizations to define a retention period after which messages are deleted and purged from Spaces, but at the moment that retention period is the same 
for all users. 

If an organization would like to have all messages in direct or '1-1' available to users for a shorter period of time, this sample code uses the [Compliance and Events](https://developer.webex.com/docs/api/guides/compliance) 
related APIs to delete them. This will not completely purge them until the organization-wide retention period is met, but they will not be retrievable by anyone 
other than software utilizing credentials for a compliance officer role you can enable in your organization. More information in this [Control Hub Compliance Data Sheet](https://www.cisco.com/c/en/us/products/collateral/conferencing/webex-control-hub/datasheet-c78-740772.html)


## Contacts
* Gerardo Chaves (gchaves@cisco.com)

## Solution Components
* Webex REST API
* Webex Control Hub
* Webex Messaging

## Coding Guides and resources
 
Downgrading the requests-oauthlib library to version 0.0.0 to avoid the OAuth error I was getting:  
https://github.com/requests/requests-oauthlib/issues/324  

Example Oauth with Webex Teams:  
https://github.com/CiscoDevNet/webex-teams-auth-sample  

Walkthrough including how to refresh tokens:  
https://developer.webex.com/blog/real-world-walkthrough-of-building-an-oauth-webex-integration  

Refresh token example:  
https://stackoverflow.com/questions/27771324/google-api-getting-credentials-from-refresh-token-with-oauth2client-client  

Compliance and Events guide:  
https://developer.webex.com/docs/api/guides/compliance  

Cisco Webex Teams Python SDK User API Docs, events:  
https://webexteamssdk.readthedocs.io/en/latest/user/api.html#events  



## Installation/Configuration

Once you clone the repository, edit the .env file to fill out the following configuration variables:

**CLIENT_ID**     
Set this constant to the Client ID from your integration. See the [Webex Integrations](https://developer.webex.com/docs/integrations) documentation for more details.

**CLIENT_SECRET**
Set this constant to the Client Secret from your integration. See the [Webex Integrations](https://developer.webex.com/docs/integrations)  documentation for more details.

**TARGET_MSG_AGE**
Set this constant to the number seconds for the maximum age of direct or 1-1 messages to keep in the organization. All messages older than this 
that have been retrieved in the list of created events will be deleted in direct spaces. 

**CHECK_EVENTS_FROM_AGE**
Set this constant to age in number seconds for the oldest message create event to start checking from. This prevents the script from retrieving too 
many events from the past if the script has been run before. The script does handle errors related to messages already been deleted 
gracefully, but no point in retrieving events so far back in time if you know you already ran the script to delete them. 

Also, in the `authenticate.py` file, configure the following variable:

**PUBLIC_URL**
Set PUBLIC_URL to the URL where your instance of this Flask application will run. If you do not change the parameters 
of app.run() at the end of the main.py file, this should be the same value of 'http://0.0.0.0:5000' that is set by default 
in the sample code.  
NOTE: This URL does not actually have to map to a public IP address out on the internet.  

To run the sample, you will need to create a user with Compliance Officer role in Webex Control hub for the organization.  
Full administrators can assign the compliance officer role to any person within their organization. 
Full administrators can't assign the compliance officer role to themselves, another full administrator must assign the role to them.  
More details on how to assign roles to users can be found here: https://help.webex.com/en-US/article/fs78p5/Assign-Organization-Account-Roles-in-Control-Hub  

This sample also requires that you create a Webex Integration in your organization with the proper Scopes so that the `authenticate.py` script can provide 
an oAuth flow so you can log in using Webex credentials for a Webex user that has the Compliance Officer role. Instructions on how to create integrations can 
be found here: https://developer.webex.com/docs/integrations  
Please note that when you are creating the integration, you need to assign to it the following scopes: 
'spark:all','spark-compliance:events_read', 'spark-compliance:messages_read','spark-compliance:messages_write'   
More details on the scopes used for Compliance Officers can be found in the [Compliance and Events guide](https://developer.webex.com/docs/api/guides/compliance) 
mentioned above.

## Usage


The sample has two main python scripts:

1) `authenticate.py`  
This script allows the Compliance Officer to authenticate and shows how to use a [Webex Integration](https://developer.webex.com/docs/integrations) to implement an oAuth flow with refresh tokens 
for Webex Teams. 
The script allows a user to authenticate with Webex teams if they had not done so previously. If they have, it will look for a locally stored auth token and refresh it with 
the refresh token if needed. If the refresh token has also expired, it will launch the full oAuth flow from the beginning.  

Once the user is authenticated, it displays the name and id of the logged in Compliance Officer user  in a generated HTML page.  
Tu run it, execute the script:  

    $ python authenticate.py

Once the flask app is running, use a browser to go to value you used for PUBLIC_URL (i.e. http://0.0.0.0:5000) which will re-direct to a Webex Teams 
authentication page if the first time using it so you can log in using your Webex Teams account credentials.  

Since the authentication and refresh tokens are stored locally in the **tokens.json** file, the `delete_old_direct_messages.py` script will 
be able to run without requiring any further login.  
You should be able to run `delete_old_direct_messages.py` without having to 
re-authenticate for as long as you want as long as you refresh any expired tokens at least once every 60 days. This refresh is done 
automatically whenever you run `delete_old_direct_messages.py` since it checks for expired tokens that are less than 60 days old. 
If more than 60 days have passed since you ran `delete_old_direct_messages.py` , it will print an error prompting you to manually re-run 
`authenticate.py`
NOTE: clear out the **tokens.json** file when you are done using the sample so they are not left insecured in the test server. 
When creating production code using this sample as a reference, be sure to store in a more secure manner and fully encrypted. 


2) `delete_old_direct_messages.py`  
This script when run will check for all message created events in the organization that are newer than the **CHECK_EVENTS_FROM_AGE** constant but 
older than the **TARGET_MSG_AGE** constant described above and add them to a list of messages to delete if they belong to a 'direct' Space.  
Once the list is compiled, it will be printed out to console and the person executing the script will be prompted to confirm they want to 
delete all of those messages:  

```Procced? (y/n): ```  

If confirmation is provided by typing in the 'y' character, all those messages will be deleted from the various 'direct' spaces.  

To remove the confirmation check in the code, look for the the following line in the `delete_old_direct_messages.py` script and delete it:   
```
if not input("Procced? (y/n): ").lower().strip()[:1] == "y": sys.exit(1)   
```   

To manually start the script, just execute it:

    $ python delete_old_direct_messages.py  

You can also schedule it using CRON or some other mechanism to run every day, for example, but remember to remove the validation check 
if you do so.  

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.