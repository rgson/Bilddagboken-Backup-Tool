#!/usr/bin/env python3

################################################################################
# Imports

from base64 import b64encode
from html5lib import HTMLParser
from html5lib.treebuilders.etree_lxml import TreeBuilder
from lxml import html, etree
from lxml.cssselect import CSSSelector
from lxml.html import html5parser
from operator import itemgetter
from posixpath import basename
from re import match
from sys import stderr
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


################################################################################
# Functions

def fetch_dom(url, guestpass=None):
	request = Request(url)
	request.add_header('Accept-Language', 'sv')
	if guestpass != None:
		request.add_header('Cookie', 'dv_guestpass=' + guestpass)
	request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36')
	response = urlopen(request)
	parsed = html5parser.parse(response, parser=HTMLParser(strict=False, tree=TreeBuilder, namespaceHTMLElements=False))
	return parsed

def find_newest_picture(profile_dom):
	selector = CSSSelector('.contentImageList > div:first-of-type > a.openImage')
	return selector(profile_dom)[0].get('href')

def find_prev_entry_url(entry_dom):
	selector = CSSSelector('.prevDayHref a')
	url = selector(entry_dom)[0].get('href')
	return url if url[-2:] != '//' else None

def build_entry(entry_dom):
	entry = {
		'id': find_entry_id(entry_dom),
		'title': find_entry_title(entry_dom),
		'text': find_entry_description(entry_dom),
		'picture': find_entry_picture(entry_dom),
		'comments': find_entry_comments(entry_dom),
	}
	add_date_and_index(entry)
	return entry

def find_entry_id(entry_dom):
	selector = CSSSelector('#imagetagsToolbar input[name="imageid"]')
	return int(selector(entry_dom)[0].get('value'))

def find_entry_title(entry_dom):
	selector = CSSSelector('#showContentHolder #showContentTitle')
	return selector(entry_dom)[0].text.strip()

def find_entry_description(entry_dom):
	selector = CSSSelector('#showContentHolder #showContentTextHtml')
	return get_full_node_content(selector(entry_dom)[0]).strip()

def find_entry_picture(entry_dom):
	selector = CSSSelector('#showContentHolder img#picture')
	return selector(entry_dom)[0].get('src')

def find_entry_comments(entry_dom):
	selector = CSSSelector('#showContentHolder #showContentComments .commentHolder')
	return [build_comment(comment_elem) for comment_elem in selector(entry_dom)]

def build_comment(comment_elem):
	return {
			'id': find_comment_id(comment_elem),
			'date': find_comment_date(comment_elem),
			'name': find_comment_name(comment_elem),
			'avatar': find_comment_avatar(comment_elem),
			'text': find_comment_text(comment_elem),
			'replies': find_replies(comment_elem),
		}

def find_comment_id(comment_elem):
	return int(comment_elem.get('id').rsplit('_', 1)[-1])

def find_comment_date(comment_elem):
	selector = CSSSelector('.baseCommentDiv > .commentTop > .commentDate')
	return selector(comment_elem)[0].text

def find_comment_name(comment_elem):
	selector = CSSSelector('.baseCommentDiv > .commentTop > .userLink')
	return selector(comment_elem)[0].text

def find_comment_avatar(comment_elem):
	selector = CSSSelector('.baseCommentDiv > .commentAvatarHolder img')
	return selector(comment_elem)[0].get('src')

def find_comment_text(comment_elem):
	selector = CSSSelector('.baseCommentDiv > .commentTextLong > .commentContent, .baseCommentDiv > .commentTextShort > .commentContent')
	return get_full_node_content(selector(comment_elem)[0]).strip()

def find_replies(comment_elem):
	selector = CSSSelector('.commentDiscussionHolder .commentDiscussionReply')
	return [build_reply(reply_elem) for reply_elem in selector(comment_elem)]

def build_reply(reply_elem):
	return {
			'id': find_reply_id(reply_elem),
			'date': find_reply_date(reply_elem),
			'name': find_reply_name(reply_elem),
			'avatar': find_reply_avatar(reply_elem),
			'text': find_reply_text(reply_elem),
		}

def find_reply_id(reply_elem):
	return int(reply_elem.get('id').rsplit('_', 1)[-1])

def find_reply_date(reply_elem):
	selector = CSSSelector('.commentDiscussionTop > .commentDate')
	return selector(reply_elem)[0].text

def find_reply_name(reply_elem):
	selector = CSSSelector('.commentDiscussionTop > .userLink')
	return selector(reply_elem)[0].text

def find_reply_avatar(reply_elem):
	selector = CSSSelector('.userLink > .commentDiscussionAvatar')
	return selector(reply_elem)[0].get('src')

def find_reply_text(reply_elem):
	selector = CSSSelector('.commentTextLong > .commentDiscussionContent, .commentTextShort > .commentDiscussionContent')
	return get_full_node_content(selector(reply_elem)[0]).strip()

def get_full_node_content(node):
	s = node.text
	if s is None:
		s = ''
	for child in node:
		s += etree.tostring(child, encoding='unicode')
	return s

def picture_to_base64_data(url):
	try:
		filetype = get_filetype(url)
		base64_data = b64encode(urlopen(url).read()).decode('utf-8').replace('\n', '')
		return 'data:image/' + filetype + ';base64,' + base64_data
	except (HTTPError, ValueError) as err:
		print(err, '(URL: {0})'.format(url), file=stderr)

def get_filename(url):
	return basename(urlsplit(url)[2])

def get_filetype(url):
	return get_filename(url).rsplit('.', 1)[-1]

def add_picture_data(pictures, entry):
	entry['img_class'] = make_picture_class(pictures, entry['picture']) or ''
	for comment in entry['comments']:
		comment['img_class'] = make_picture_class(pictures, comment['avatar']) or ''
		for reply in comment['replies']:
			reply['img_class'] = make_picture_class(pictures, reply['avatar']) or ''

def make_picture_class(pictures, url):
	this = make_picture_class
	if 'class_counter' not in this.__dict__:
		this.class_counter = 0
	if url not in pictures:
		data = picture_to_base64_data(url)
		if data == None:
			return None
		for k, v in pictures.items():
			if v['data'] == data:
				pictures[url] = { 'class': v['class'], 'data': None }
				break
		else:
			pictures[url] = { 'class': 'p' + str(this.class_counter), 'data': data }
			this.class_counter += 1
	return pictures[url]['class']

def month_number(month_str):
	months = ['januari', 'februari', 'mars', 'april', 'maj', 'juni', 'juli',
		'augusti', 'september', 'oktober', 'november', 'december']
	return months.index(month_str) + 1

def add_date_and_index(entry):
	print(entry['title'])
	pattern = '.+? (\d+?) (.+?) (\d+?)   .+? (\d+?)\/\d+?' #Note: important non-breaking space inbetween two normal spaces.
	matches = match(pattern, entry['title'])
	entry['date'] = '{year:04d}-{month:02d}-{day:02d}'.format(
		year=int(matches.group(3)),
		month=month_number(matches.group(2)),
		day=int(matches.group(1)))
	entry['index'] = int(matches.group(4))

def deep_sort(entries):
	entries.sort(key=itemgetter('date', 'index'))
	for entry in entries:
		entry['comments'].sort(key=itemgetter('id'))
		for comment in entry['comments']:
			comment['replies'].sort(key=itemgetter('id'))

def format_html(username, entries, pictures):
	return '''
	<!DOCTYPE html>
	<html>
	<head>
		<title>Bilddagboken - {username}</title>
		<meta charset='utf-8'>
		<style type='text/css'>
			{picture_css}
		</style>
		<style type='text/css'>
			{normal_css}
		</style>
	</head>
	<body>
		<header>
			<h1>Bilddagboken - {username}</h1>
		</header>
		<main>
			{entries}
		</main>
	</body>
	</html>
	'''.format(username=USERNAME, picture_css=format_html_picture_css(pictures),
				normal_css=format_html_normal_css(), entries=format_html_entries(entries))

def format_html_picture_css(pictures):
	return ''.join(['.{class}{{content:url({data});}}'.format_map(p) for p in pictures.values() if p['class'] != None and p['data'] != None])

def format_html_normal_css():
	return '''
		body {
			width: 45em;
			margin: auto;
			font-family: sans-serif;
			color: #333;
			line-height: 1.6;
			word-wrap: break-word
		}
		p {
			margin-top: 0
		}
		.entry {
			border: 1px solid #ddd;
			padding: 0 30px;
			margin-bottom: 1em
		}
		.entry>img {
			display: block;
			margin: 0 auto 1em;
			max-width: 100%
		}
		.comments {
			border-top: 1px solid #ddd;
			padding-top: 1em
		}
		.replies {
			margin-left: 25px
		}
		.comment>img, .reply>img {
			float: left;
			margin-right: 1em;
			width: 50px;
			height: 50px
		}
		.date {
			color: #777
		}
		.entry>p, h1, h2 {
			text-align: center
		}
		'''

def format_html_entries(entries):
	return '\n'.join([format_html_entry(entry) for entry in entries])

def format_html_entry(entry):
	comments_html = format_html_comments(entry['comments'])
	return '''
	<div id='entry-{id}' class='entry'>
		<h2>{title}</h2>
		<img class='{img_class}'>
		<p>{text}</p>
		<div class='comments'>{comments_html}</div>
	</div>
	'''.format(comments_html=comments_html, **entry)

def format_html_comments(comments):
	return '\n'.join([format_html_comment(comment) for comment in comments])

def format_html_comment(comment):
	replies_html = format_html_replies(comment['replies'])
	return '''
	<div id='comment-{id}' class='comment'>
		<img class='{img_class}'>
		<span class='name'>{name}</span>
		<span class='date'>{date}</span>
		<p class='text'>{text}</p>
		<div class='replies'>{replies_html}</div>
	</div>
	'''.format(replies_html=replies_html, **comment)

def format_html_replies(replies):
	return '\n'.join([format_html_reply(reply) for reply in replies])

def format_html_reply(reply):
	return '''
		<div id='reply-{id}' class='reply'>
			<img class='{img_class}'>
			<span class='name'>{name}</span>
			<span class='date'>{date}</span>
			<p class='text'>{text}</p>
		</div>
		'''.format_map(reply)


################################################################################
# Script

# TODO parameterize
USERNAME = 'robin93'
GUESTPASS = 'torsklever'
OUTPUT = 'bdb_' + USERNAME + '.htm'

profile_url = 'http://dayviews.com/' + USERNAME + '/'
print('Starting! (URL: {0})'.format(profile_url))
profile_dom = fetch_dom(profile_url, GUESTPASS)

entries = []
pictures = {}
url = find_newest_picture(profile_dom)
counter = 0

#while url != None:
for i in range(3):
	counter += 1
	print('Downloading entry #{0} (URL: {1})'.format(counter, url))
	entry_dom = fetch_dom(url, GUESTPASS)
	entry = build_entry(entry_dom)
	entries.append(entry)
	add_picture_data(pictures, entry)
	url = find_prev_entry_url(entry_dom)

deep_sort(entries)

print('Generating HTML output...')
output_html = format_html(USERNAME, entries, pictures)
with open(OUTPUT, 'w') as output_file:
	print(output_html, file=output_file)

print('Done!')


##########
# Issues
#
# SOLVED:
# * Issue with some pictures being replaced by the one next to them (lower index is incorrectly same as higher index).
#    Examples: onsdag 16 april 2008   bild 2/3  -->  onsdag 16 april 2008   bild 3/3
#              fredag 18 april 2008   bild 7/28 -->  fredag 18 april 2008   bild 8/28
#              torsdag 21 augusti 2008   bild 1/1 - tisdag 26 augusti 2008   bild 1/1 --> onsdag 27 augusti 2008   bild 1/1
#              tisdag 14 augusti 2007   bild 1/9 - tisdag 14 augusti 2007   bild 8/9 --> tisdag 14 augusti 2007   bild 9/9
#    Cause: Some pictures have titles based on the description
#           (i.e. Ditt_namn_Ditt_efternamn_Din_gata_Namnet_pa_den_du_gillar_Komunen_du_bor_i_Namnet_pa_personen_du.jpg)
#           in which case this is shared by other pictures with the same description.
# * {content:url(None);} for some pictures. Could be omitted entirely instead.
# * Certain pieces of text are lost for comments and replies, e.g. "<3"
#    Examples: söndag 2 mars 2008   bild 1/2
#              söndag 6 april 2008   bild 2/6
#    Cause: Probably caused by the extraction of text incl. subcomments. > and < seem to fuck shit up.
# * Duplicated comment replies for different comments.
#    Example: lördag 10 maj 2008   bild 2/3
#    Cause: Probably also related to the extraction of text.
# * Sorting by ID is insufficient for entries. Must be sorted by date and index.
#
# REMAINING:
# * Entire HTML file should be minified to remove indentation, spaces, etc.
#
