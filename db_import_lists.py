from application import db, dataLibs
from application.model import *
import os
nowdir = os.path.abspath(os.path.dirname(__file__))

def upcase(s):
	for x in s:
		if x

f = open(os.path.join(nowdir, 'mar_total.txt'), 'r')
while True:
	line = f.readline()
	if line:
		new_matter = matterDB(line[0:line.find('|')], line[line.find('|') + 1:])
		new_matter.save()
	else:
		break
f.close()

fr = open(os.path.join(nowdir, 'all_names.txt'), 'r')
while True:
	line = fr.readline()
	if line:
		line2 = fr.readline()
		new_flora = floraDB(line[2 : len(line) - 1], line2)
		new_flora.save()
	else:
		break
fr.close()

medium_list = ['Escherichia coli-2.0.txt']
for filename in medium_list:
	file = open(os.path.join(nowdir, filename), 'r')
	new_medium = mediumDB(filename[0 : filename.rfind('.')])
	while True:
		line = file.readline()
		if line:
			new_matter = matterDB.query.filter_by(matter_code = line[line.rfind(' ') + 1 : ]).first()
			if new_matter:
				new_medium.matters = libs_list_insert(new_medium.matters, new_matter.id)
				new_medium.concentration = libs_dict_insert(new_medium.concentration, new_matter.id, line[0 : line.find(' ')])
		else:
			break
	new_medium.save()
	file.close()

plasmid_list = ['pSB1AK3.txt', 'pSB1AT3.txt', 'pSB1C3.txt', 'pSB1K3.txt', 'pSB1T3.txt']
plasmid_path = os.path.join(nowdir, 'plasmid')
for filename in plasmid_list:
	file = open(os.path.join(plasmid_path, filename), 'r')
	sequence = ''
	while True:
		line = file.readline()
		if line:
			sequence += line.upper()
		else:
			break
	new_plasmid = plasmidDB(filename[0 : filename.rfind('.')], sequence)
	new_plasmid.save()
	file.close()
