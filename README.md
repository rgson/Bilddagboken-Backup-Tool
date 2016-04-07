#`bdb_dumper`

`bdb_dumper` is a command-line tool for saving the content of a profile from the Swedish website [bilddagboken.se](http://bilddagboken.se) (now [dayviews.com](http://dayviews.com)).

At its prime, Bilddagboken attracted a significant number of user, including myself and a large share of the people in my surroundings. Due to its nature (literally being named "the picture diary"), many of these users' profiles contain large amounts of photos, write-ups and discussions related to revered memories and old friends. However, due to the fickle nature of the online social media scene, these memorabilia are constantly at risk of being lost.

`bdb_dumper` alleviates the problem by allowing the user to download a copy of the content on their profile; including all of their pictures as well as the associated descriptions and comments. Everything is neatly stored in a single HTML document that can be viewed, stored and backed up at the user's discretion.


## Legal information

_I am not a lawyer_, but as far as I can tell, `bdb_dumper` does not violate any of [Dayview's terms of use](http://dayviews.com/p/termsNew/) at the time of writing (2016-04-07).

In fact, the terms of use clearly state that each user owns the content of their profile ("På dayviews.com äger användarna sina bilder") and that the user is personally responsible for making sure the content is backed up elsewhere ("Det är ditt ansvar att säkerställa att dina Dayviews-bilder är fullgott back-uppade annorstädes").

However, `bdb_dumper` must obviously __not__ be used to download the content of another user's profile without their permission! Each user's content belongs to them. Hence you must have the user's explicit permission before downloading any material from their profile.


## Usage

	usage: bdb_dumper.py [-h] -u USERNAME [-p GUESTPASS] [-o OUTPUT] [-l LIMIT]

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