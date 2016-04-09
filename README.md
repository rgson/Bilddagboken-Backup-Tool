# Bilddagboken Backup Tool

Bilddagboken Backup Tool (`bdb_backup`) is a command-line tool for saving the content of a profile from the Swedish website [bilddagboken.se](http://bilddagboken.se) (now [dayviews.com](http://dayviews.com)).

At its prime, Bilddagboken attracted a significant number of users, including myself and a large share of the people in my surroundings. Due to its nature (the name's literal meaning being _"the picture diary"_), many of these users' profiles contain large amounts of photos, write-ups and discussions related to revered memories and old friends. However, due to the fickle nature of the online social media scene, these memorabilia are at risk of being lost.

`bdb_backup` alleviates the risk by allowing the user to download a copy of the content on their profile; the copy includes all of their pictures as well as the associated descriptions and comments. Everything is neatly stored in a single HTML document that can be viewed, stored and backed up at the user's discretion.


## Usage

	usage: bdb_backup.py [-h] -u USERNAME [-p GUESTPASS] [-o OUTPUT] [-l LIMIT]

	optional arguments:
	  -h, --help            show this help message and exit
	  -u USERNAME, --username USERNAME
	                        The username, as seen in the profile URL.
	  -p GUESTPASS, --guestpass GUESTPASS
	                        The guest password to the user's profile.
	  -o OUTPUT, --output OUTPUT
	                        The output file where the dump is to be saved.
	  -l LIMIT, --limit LIMIT
	                        Limits the number of entries saved.


## Dependencies

* Python 3.4.3 (or similar)


## Notes

### Legal information

_I am not a lawyer_, but as far as I can tell, using `bdb_backup` does not violate any of [Dayview's terms of use](http://dayviews.com/p/termsNew/) (Swedish version, 2016-04-07).

In fact, the terms of use clearly state that each user owns the content of their profile ("På dayviews.com äger användarna sina bilder") and that the user is personally responsible for making sure the content is backed up elsewhere ("Det är ditt ansvar att säkerställa att dina Dayviews-bilder är fullgott back-uppade annorstädes").

However, `bdb_backup` must obviously __not__ be used to download the content of another user's profile without their permission! Each user's content belongs to them. Hence you must have the user's explicit permission before downloading any material from their profile.

### Broken HTML

Many changes have been made to Bilddagboken/Dayviews throughout its lifetime, including several changes to the formatting capabilities etc. As a result, many picture descriptions contain incredibly broken HTML. In fact, the descriptions are occasionally so broken that they manage to break the layout of the original page and escape the elements where they are expected to reside.

Overall, the HTML parser usually does a pretty good job cleaning up the mess. Additionally, the script takes a few extra steps in an attempt to clean up some more of it and to include runaway text. Even still, the result is not always quite what one would expect. You are therefore strongly recommended to look through the resulting file to make sure that it is acceptable before considering it a complete backup.

If you happen upon a case which the script fails to handle, please consider reporting it as an issue. If possible, include the URL to the identified example or at least a toy example that reproduces the issue. The tool will obviously never be able to handle all of the infinite ways in which HTML can break, but solutions can possibly be incorporated to solve some of them.