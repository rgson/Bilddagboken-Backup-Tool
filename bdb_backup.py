#!/usr/bin/env python3

################################################################################
# Imports

from argparse import ArgumentParser, FileType
from base64 import b64encode
from copy import deepcopy
from lxml import etree
from lxml.cssselect import CSSSelector
from lxml.html import html5parser
from operator import itemgetter
from posixpath import basename
from re import match
from sys import exit, stderr
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import urlopen, Request

################################################################################
# Functions

def add_date_and_index(entry):
	pattern = '.+? (\d+?) (.+?) (\d+?)   .+? (\d+?)\/\d+?' #Note: important non-breaking space inbetween two normal spaces.
	matches = match(pattern, entry['title'])
	entry['date'] = '{year:04d}-{month:02d}-{day:02d}'.format(
		year=int(matches.group(3)),
		month=month_number(matches.group(2)),
		day=int(matches.group(1)))
	entry['index'] = int(matches.group(4))

def add_picture_data(pictures, entry):
	entry['img_class'] = make_picture_class(pictures, entry['picture']) or ''
	for comment in entry['comments']:
		comment['img_class'] = make_picture_class(pictures, comment['avatar']) or ''
		for reply in comment['replies']:
			reply['img_class'] = make_picture_class(pictures, reply['avatar']) or ''

def build_comment(comment_elem):
	return {
			'id': find_comment_id(comment_elem),
			'date': find_comment_date(comment_elem),
			'name': find_comment_name(comment_elem),
			'avatar': find_comment_avatar(comment_elem),
			'text': find_comment_text(comment_elem),
			'replies': find_replies(comment_elem),
		}

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

def build_reply(reply_elem):
	return {
			'id': find_reply_id(reply_elem),
			'date': find_reply_date(reply_elem),
			'name': find_reply_name(reply_elem),
			'avatar': find_reply_avatar(reply_elem),
			'text': find_reply_text(reply_elem),
		}

def deep_sort(entries):
	entries.sort(key=itemgetter('date', 'index'))
	for entry in entries:
		entry['comments'].sort(key=itemgetter('id'))
		for comment in entry['comments']:
			comment['replies'].sort(key=itemgetter('id'))

def fetch_dom(url, guestpass=None):
	request = Request(url)
	request.add_header('Accept-Language', 'sv')
	if guestpass != None:
		request.add_header('Cookie', 'dv_guestpass=' + guestpass)
	request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36')
	response = urlopen(request)
	parser = HTMLParserUTF8(namespaceHTMLElements=False)
	parsed = html5parser.parse(response, guess_charset=False, parser=parser)
	return parsed

def find_comment_avatar(comment_elem):
	selector = CSSSelector('.baseCommentDiv > .commentAvatarHolder img')
	return selector(comment_elem)[0].get('src')

def find_comment_date(comment_elem):
	selector = CSSSelector('.baseCommentDiv > .commentTop > .commentDate')
	return selector(comment_elem)[0].text

def find_comment_id(comment_elem):
	return int(comment_elem.get('id').rsplit('_', 1)[-1])

def find_comment_name(comment_elem):
	selector = CSSSelector('.baseCommentDiv > .commentTop > .userLink')
	return selector(comment_elem)[0].text

def find_comment_text(comment_elem):
	selector = CSSSelector('.baseCommentDiv > .commentTextLong > .commentContent, .baseCommentDiv > .commentTextShort > .commentContent')
	return get_full_node_content(selector(comment_elem)[0]).strip()

def find_entry_comments(entry_dom):
	selector = CSSSelector('#showContentHolder #showContentComments .commentHolder')
	return [build_comment(comment_elem) for comment_elem in selector(entry_dom)]

def find_entry_description(entry_dom):
	selector = CSSSelector('#showContentHolder #showContentTextHtml')
	text = get_full_node_content(selector(entry_dom)[0]).strip()
	selector = CSSSelector('#showContentHolder')
	copy = deepcopy(selector(entry_dom)[0])
	selector = CSSSelector('#showContentHolder > div')
	for trash in selector(copy):
		copy.remove(trash)
	text += get_full_node_content(copy).strip()
	return repair_html(text)

def find_entry_id(entry_dom):
	selector = CSSSelector('#imagetagsToolbar input[name="imageid"]')
	return int(selector(entry_dom)[0].get('value'))

def find_entry_picture(entry_dom):
	selector = CSSSelector('#showContentHolder img#picture')
	return selector(entry_dom)[0].get('src')

def find_entry_title(entry_dom):
	selector = CSSSelector('#showContentHolder #showContentTitle')
	return selector(entry_dom)[0].text.strip()

def find_newest_picture(profile_dom):
	selector = CSSSelector('.contentImageList > div:first-of-type > a.openImage')
	try:
		return selector(profile_dom)[0].get('href')
	except:
		return None

def find_prev_entry_url(entry_dom):
	selector = CSSSelector('.prevDayHref a')
	url = selector(entry_dom)[0].get('href')
	return url if url[-2:] != '//' else None

def find_replies(comment_elem):
	selector = CSSSelector('.commentDiscussionHolder .commentDiscussionReply')
	return [build_reply(reply_elem) for reply_elem in selector(comment_elem)]

def find_reply_avatar(reply_elem):
	selector = CSSSelector('.userLink > .commentDiscussionAvatar')
	return selector(reply_elem)[0].get('src')

def find_reply_date(reply_elem):
	selector = CSSSelector('.commentDiscussionTop > .commentDate')
	return selector(reply_elem)[0].text

def find_reply_id(reply_elem):
	return int(reply_elem.get('id').rsplit('_', 1)[-1])

def find_reply_name(reply_elem):
	selector = CSSSelector('.commentDiscussionTop > .userLink')
	return selector(reply_elem)[0].text

def find_reply_text(reply_elem):
	selector = CSSSelector('.commentTextLong > .commentDiscussionContent, .commentTextShort > .commentDiscussionContent')
	return get_full_node_content(selector(reply_elem)[0]).strip()

def format_html(username, entries, pictures):
	return (
	'<!DOCTYPE html>'
	'<html>'
	'<head>'
		'<title>Bilddagboken - {username}</title>'
		'<meta charset=\'utf-8\'>'
		'<style>{normal_css}{picture_css}</style>'
	'</head>'
	'<body>'
		'<h1>Bilddagboken - {username}</h1>'
		'{entries}'
	'</body>'
	'</html>'
	).format(username=username, picture_css=format_html_picture_css(pictures),
				normal_css=format_html_normal_css(), entries=format_html_entries(entries))

def format_html_comment(comment):
	replies_html = format_html_replies(comment['replies'])
	return (
	'<div class="c">'
		'<img class="{img_class}">'
		'<span>{name}</span>'
		'<span class="d">{date}</span>'
		'<div>{text}</div>'
		'<div class="rs">{replies_html}</div>'
	'</div>'
	).format(replies_html=replies_html, **comment)

def format_html_comments(comments):
	return ''.join([format_html_comment(comment) for comment in comments])

def format_html_entries(entries):
	return ''.join([format_html_entry(entry) for entry in entries])

def format_html_entry(entry):
	comments_html = format_html_comments(entry['comments'])
	return (
	'<div class="e">'
		'<h2>{title}</h2>'
		'<img class="{img_class}">'
		'<div class="t">{text}</div>'
		'<div class="cs">{comments_html}</div>'
	'</div>'
	).format(comments_html=comments_html, **entry)

def format_html_normal_css():
	return (
		'body{'
			'width:45em;'
			'margin:auto;'
			'font-family:sans-serif;'
			'color:#333;'
			'line-height:1.6;'
			'word-wrap:break-word}'
		'p{'
			'margin-top:0}'
		'.e{'
			'border:1px solid #ddd;'
			'padding:0 30px;'
			'margin-bottom:1em}'
		'.e>img{'
			'display:block;'
			'margin:0 auto 1em;'
			'max-width:100%}'
		'.cs{'
			'border-top:1px solid #ddd;'
			'padding-top:1em}'
		'.rs{'
			'margin-left:25px}'
		'.c{'
			'margin-bottom:1em}'
		'.r{'
			'margin-top:1em}'
		'.c>img,.r>img{'
			'float:left;'
			'margin-right:1em;'
			'width:50px;'
			'height:50px}'
		'.d{'
			'color:#777;'
			'float:right}'
		'.e>.t,h1,h2{'
			'text-align:center}'
		)

def format_html_picture_css(pictures):
	return ''.join(['.{class}{{content:url({data})}}'.format_map(p) for p in pictures.values() if p['class'] != None and p['data'] != None])

def format_html_replies(replies):
	return ''.join([format_html_reply(reply) for reply in replies])

def format_html_reply(reply):
	return (
		'<div class="r">'
			'<img class="{img_class}">'
			'<span>{name}</span>'
			'<span class="d">{date}</span>'
			'<div>{text}</div>'
		'</div>'
		).format_map(reply)

def get_filename(url):
	return basename(urlsplit(url)[2])

def get_filetype(url):
	return get_filename(url).rsplit('.', 1)[-1]

def get_full_node_content(node):
	s = node.text or ''
	s += ''.join([etree.tostring(child, encoding='unicode') for child in node])
	return s

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

def picture_to_base64_data(url):
	try:
		filetype = get_filetype(url)
		base64_data = b64encode(urlopen(url).read()).decode('utf-8').replace('\n', '')
		return 'data:image/' + filetype + ';base64,' + base64_data
	except (HTTPError, ValueError) as err:
		print(err, '(URL: {0})'.format(url), file=stderr)

def repair_html(html_str):
	parser = html5parser.HTMLParser(namespaceHTMLElements=False)
	parsed = html5parser.fromstring(html_str, guess_charset=False, parser=parser)
	result = etree.tostring(parsed, encoding='unicode')
	result = result.replace('<b/>', '').replace('<i/>', '')
	return result

################################################################################
# Classes

class HTMLParserUTF8(html5parser.HTMLParser):
	"""
	This class is a hack to force the use of utf8 when parsing the response.
	The charset determination used by lxml.html5parser gets it wrong occasionally.
	"""
	def parse(self, stream, useChardet=False): # Note: useChardet is not respected.
		return html5parser.HTMLParser.parse(self, stream, encoding='utf8', useChardet=False)

################################################################################
# Script

parser = ArgumentParser()
parser.add_argument('-u', '--username',  dest='username',  help='The username, as seen in the profile URL.', required=True)
parser.add_argument('-p', '--guestpass', dest='guestpass', help='The guest password to the user\'s profile.')
parser.add_argument('-o', '--output',    dest='output',    help='The output file where the dump is to be saved.', default='bilddagboken_dump.htm', type=FileType('w'))
parser.add_argument('-l', '--limit',     dest='limit',     help='Limits the number of entries saved.', type=int)
args = parser.parse_args()

entries = []
pictures = {}
counter = 0

profile_url = 'http://dayviews.com/' + args.username + '/'
print('Starting! (URL: {0})'.format(profile_url))
profile_dom = fetch_dom(profile_url, args.guestpass)
url = find_newest_picture(profile_dom)

if url == None:
	print('Not a single pictures was found on the user\'s profile.', file=stderr)
	if args.guestpass == None:
		print('  Perhaps a guest password is needed?', file=stderr)
	else:
		print('  Perhaps the guest password is incorrect?', file=stderr)
	exit(1)

while url != None and (args.limit == None or counter < args.limit):
	counter += 1
	print('Downloading entry #{0} (URL: {1})'.format(counter, url))
	entry_dom = fetch_dom(url, args.guestpass)
	entry = build_entry(entry_dom)
	entries.append(entry)
	add_picture_data(pictures, entry)
	url = find_prev_entry_url(entry_dom)

deep_sort(entries)

print('Generating HTML output...')
output_html = format_html(args.username, entries, pictures)
print(output_html, file=args.output)

print('Done!')
