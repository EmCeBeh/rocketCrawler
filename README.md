# rocketCrawler
Python module to download the rocket.Chat history from a particular group on the server. Uploaded files are stored as URLs.

## Use GUI python script
You can either execute the python file rocketCrawler_gui.py in your Terminal (python rocketCrawler_gui.py) and Windows will appear asking for your log in credentials and the groups you want to download. It will then save a Textfile in Markdown syntax which you can compile to a nice, readeable PDF.

## Use the functions by yourself
palChat = rocketCrawler('MyEmailAdress@hoster.de', 'MyKewlPassword1234')

groups = palChat.getGroups()

print(groups)

mygroup = 'mbi-pal-fel-schick-202005' #Module is private. When taking it more public, this should be annoymised.

_ = palChat.getHistory(mygroup)

_ = palChat.getFileURLs(mygroup)

palChat.writeHistory2File(mygroup)
