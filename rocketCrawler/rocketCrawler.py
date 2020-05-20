from numpy import *
import datetime
import requests as req

class rocketCrawler(object):

    def __init__(self, email, password, server = 'https://chat.gwdg.de'):
        """Initialize the class, connect to the server and store the credentials.

        Args:
            email (str)     : RocketChat email
            password (str)  : RocketChat password
            password (str)  : RocketChat password
            server (str)    : Server URL, default = https://chat.gwdg.de
        """
        self.baseUrl = server + '/api/v1'
        
        self.email = email
        self.password = password
        self.token = ''
        self.hds = {}
        
        
        self.history = {}
        self.files =  {}
        
        self.login(verbose = True)
        
        
    def login(self, verbose = True):
        data = {
            'user': self.email,
            'password': self.password,
        }
        
        login = req.post(self.baseUrl+'/login', data=data)
        if login.json()['status'] == 'success':
            #getting login credentials
            self.name = login.json()['data']['me']['_id']
            self.token = login.json()['data']['authToken']
            self.hds = {
                'X-Auth-Token': self.token,
                'X-User-Id': self.name,
            }
            if verbose:
                print('Login did work :) \n')
        else:
            if verbose:
                print('Login did not work :( \n')
        
    def getGroups(self):
        '''
        Prints your group names
        Within this class you can use the Name or the ID as input.
        Avoid having groups with identical names, but most servers won't let
        you do that anyway. Use the ID to access data manually outside this class.

        returns :
            a dict with: {Group name : unique group ID}
        '''
        # Getting your personal groups
        grouplist = req.get(self.baseUrl+'/groups.list', headers=self.hds).json()
        self.groups = {group['fname']:group['_id'] for group in grouplist['groups']}
        print('Your groups are:')
        for key in self.groups.keys():
            print(key)
        print()
        return self.groups

    def getHistory(self, nameOrID, getGroups = False, entries = 10000):
        '''
        nameOrID  : Clear text room name or ID
        getGroups : Calls self.getGroups to update the group dict with stored
                    credentials. Not needed if function has already been
                    executed manually.
        entries   : Number of most recent history entries to be requested.
                    Default is 10000. Could be limited by server!
                    If so, you need to implement your own loop
                    functionality as done in getFileUrls...

        returns:
            list of dict of history entries
        '''
        if getGroups:
            _ = self.getGroups()

        try:
            # Try if a name is given, which exists in your groups
            ID = self.groups[nameOrID]
        except KeyError:
            ID = nameOrID

        pars = {
            'roomId': ID,
            'count': entries,
        }

        # History is sorted by date and can accept `count` to arbitrary number
        # (tested up to 4000 only, depends on server.)
        hist = req.get(self.baseUrl+'/groups.history', headers=self.hds, params=pars)
        if hist.json()['success']:
            self.history[ID] = hist.json()['messages']
        else:
            raise ValueError('Could not connect to group.'
                             'Either nameOrId or login credentials is incorrect.')

        return self.history[ID]


    def getFileURLs(self, nameOrID, getGroups = False, entries = 100, cap = True):
        '''
        nameOrID        : Clear text room name or ID
        getGroups       : Calls self.getGroups to update the group dict with stored
                          credentials. Not needed if function has already been
                          executed manually.
        historyEntries  : Number of most recent URLs to be requested. Default is
                          100. Could be limited by server for some reason...
                          => See moreThanAllowed if you get less than expected!
        cap             : If you want to request more than the allowed cap of
                          entries, setting this to True and entries to the less
                          than or equal to the maximum will loop and concatenate
                          over all available files.
        returns:
            list of dict of fileURLs
        '''

        if getGroups:
            _ = self.getGroups()
        try:
            # Try if a name is given, which exists in your groups
            ID = self.groups[nameOrID]
        except KeyError:
            ID = nameOrID


        # Aparently some servers have `API_Upper_Count_Limit` set to
        # e.g. 100...why??? It's just text.
        # Setting count to e.g. >100 will still only give 100 file URLs!
        # Looping via `offset` give a workaround
        files = []
        remaining = entries
        offset = 0
        while remaining == entries:
            
            pars = {
                'roomId': ID,
                'count': entries, 
                'offset': offset,
            }
            #files are sorted by the `name` attribute for some reason.
            files_part = req.get(self.baseUrl+'/groups.files', headers=self.hds, params=pars)
            files = files + files_part.json()['files']
            if cap:
                remaining = len(files_part.json()['files'])
            else:
                remaining = -1
            offset += entries
        self.files[ID] = files
        return files

    def _getURL(self, messagetime, ID):

        '''
        Get the URL for a given messagetime.
        Only to be automatically called by writeHistory2File!
        '''
        # messagetime has format
        # YYYY-MM-DDTHH:MM:SS:MMMZ
        # and we only want
        # YYYY-MM-DDTHH:MM:SS
        messagetime = messagetime[:-5]
        for file in self.files[ID]:
            #same for filetime
            filetime = file['uploadedAt'][:-5]
            a = datetime.datetime.strptime(filetime,    "%Y-%m-%dT%H:%M:%S")
            b = datetime.datetime.strptime(messagetime, "%Y-%m-%dT%H:%M:%S")
            # We want that the message and the file are posted <2s of one another
            c = b - a
            
            if abs(c.days * 86400 + c.seconds)< 2:
                # if so, we return (and later write to file) the first URL we can find
                # ideally one would check if there is more than one match and write both...
                return file['url']

    def writeHistory2File(self, groupName, saveName = None, verbose = True):
        '''
            Creates text file with messages and URLs to photos posted like:

            Alice 2020-01-01 09:41:00:
            Hello World

            Bob 2020-01-01 09:41:20:
            Who is Alice?
            Charlie, do you know them?

            Charlie 2020-01-01 09:41:40:
            They are in this picture with you!
            https://myserver.de/fileSystem:Uploads/1S2S2P3S3P4S/Christmas_Party.jpg

            input:

            groupName : A string with the group name or ID

            saveName  : Save name (optionally including path) for created file.
                        If left to None groupName.txt will be used.
            verbose   : If True, it prints:
                            number of file URLs written to file
                            number of file URLs total = len(files)
                                => Ideally the two would be equal.
                            number of empty lines written to file
                                => coming either from deleted messages or
                                   non-assignable files due to the file not
                                   being uploaded within 2s of its message
            returns:
                used saveName as string
        '''
        
        # Is groupName a valid name or was an ID given?
        if groupName in self.groups.keys():
            ID = self.groups[groupName]
        else:
            ID = groupName
        # Was a saveName provided?
        if saveName == None:
            saveName = '%s.txt'%groupName

        # Open File
        f = open(saveName,'w')
        f.write('Chat export for group %s.\n'%ID)

        # Defining some variables
        last_sender = 'Nobody'
        counter = 0
        counter_del = 0
        counter_char = 0

        for message in self.history[ID][::-1]:
            name = message['u']['name']
            content = message['msg']
            dateAndTime = '%s %s'%(message['ts'][:10],message['ts'][11:-5])
            # We want to summarise the consecutive messages per person
            # under one name (like in Rocket.Chat)
            if last_sender != name:                  
                f.write('\n%s %s: \n'%(name,dateAndTime))
            # Is the message empty?
            # Then an image was posted or the message was deleted.
            if len(content) == 0:
                messagetime = message['ts']
                URL = self._getURL(messagetime, ID)
                # Did we sucessfully find a image URL matching
                # the time of the message?
                if URL == None:
                    f.write('[Message deleted or file not found!]\n')
                    counter_del += 1
                else:
                    f.write(URL+'\n')
                    counter += 1
            # If there is a message we write it to file
            else:
                try:
                    f.write(content+'\n')
                except Exception as e:
                    # Rocket.Chat emojis are encoded by :EMOJI_NAME:,
                    # others can't be written to file:
                    print('There was a message, which could not be written:'
                          '\n %s \n because %s \n'%(content,e))
            last_sender = name
        if verbose:
            print('There were %d files in the chat.'
                  'A file was assigned to %d messages'%(len(self.files[ID]),counter))
            print('For %d messages no file could be assigned.'
                  ' Probably the message was deleted.'%counter_del)
        f.close()
        return(saveName)
