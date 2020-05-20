# rocketCrawler
Python module to download the rocket.Chat history from a particular group on the server. Uploaded files are stored as URLs.



how to use:

palChat = rocketCrawler('MyEmailAdress@hoster.de', 'MyKewlPassword1234')


groups = palChat.getGroups()


#print(groups)


mygroup = 'mbi-pal-fel-schick-202005' #Module is private. When taking it more public, this should be annoymised.

_ = palChat.getHistory(mygroup)


_ = palChat.getFileURLs(mygroup)

palChat.writeHistory2File(mygroup)
