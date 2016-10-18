#include "input_utils.h"

namespace mol {

substance :: substance() {
}

substance :: ~substance() {
}

reaction :: reaction() {
}

reaction :: ~reaction() {
}

mol_file :: mol_file() {
}

mol_file :: ~mol_file() {
}

void substance :: clear() {
	atom.clear(); name = ""; ID=""; types.clear(); comm.clear();
}

int to_int(string x) {
	stringstream sin(x);
	int res; sin >> res;
	return res;
}

string get_element(string str, string x) {
	stringstream sin(str); string s;
	sin >> s; sin >> s; sin >> s;
	return s;
}

bool check_element(string str, string x) {
	for (size_t i = 0; i < x.size(); ++ i)
		if (str[i] != x[i])
			return false;
	return true;
}

bool drop_test(string x) {
	set <char> forbid_list;

	for (char i = 'a'; i <= 'z'; ++ i)
		forbid_list.insert(i);
	forbid_list.insert('|');

	for (size_t i = 0; i < x.size(); ++ i)
		if (forbid_list.count(x[i]))
			return true;

	return false;
}

void reaction :: clear() {
	sub.clear(); pdt.clear(); enr.clear();
	ec_name = "";
}

string first_useful(ifstream & fin) {
	string str;
	do {
		getline(fin, str);
		if (spc == "")
			if (str.find("# Species: ") != string :: npos)
				spc = str.substr(11);
	} while ('#' == str[0] && fin.eof() == false);
	return str;
}

string all_caps(string x) {
	for (size_t i = 0; i < x.size(); ++ i)
		if ('a' <= x[i] && x[i] <= 'z')
			x[i] = x[i] - 'a' + 'A';
	return x;
}

vector <string> split(const string & x) {
	string s = all_caps(x); vector <string> ret;
	while (s.find(' ') != string :: npos) {
		ret.push_back(s.substr(0, s.find(' ')));
		s = s.substr(s.find(' ') + 1);
	}
	ret.push_back(s);
	return ret;
}

bool input_initial(vector <reaction>& reaction_list,
	map <string, substance>& substance_list) {
	
	std :: ios :: sync_with_stdio(false);
	
	map <string, int> ec_check;

	ifstream react("reactions.dat");
	ifstream comp("compounds.dat");
	ofstream log("log.txt");

	if (false == react.is_open() || false == comp.is_open() ||
		false == log.is_open())
		return false;

	string str, dir, name;
	substance current_subs;

	str = first_useful(comp);
	do {
		if (check_element(str, "UNIQUE-ID"))
			current_subs.name = get_element(str, "UNIQUE-ID");
		if (check_element(str, "CHEMICAL-FORMULA")) {
			size_t pos = str.find('(');
			string n_str(str, pos + 1);
			stringstream sin(n_str);
			string atom_name; int atom_count;
			sin >> atom_name >> atom_count;
			//log << atom_name << ' ' << atom_count << endl;
			current_subs.atom.insert(make_pair(atom_name, atom_count));
		}

		if (check_element(str, "DBLINKS - (CHEBI \"")) {
			size_t pos = str.find('\"');
			string n_str(str, pos + 1);
			stringstream sin(n_str);
			sin >> current_subs.ID;
			current_subs.ID.pop_back();
		}
	
		if (check_element(str, "TYPES")) {
			string s = all_caps(get_element(str, "TYPES"));
			current_subs.types.insert(s);
		}

		if (check_element(str, "COMMON-NAME")) {
			string s = all_caps(get_element(str, "COMMON-NAME"));
			current_subs.comm.insert(s);
		}

		if ("//" == str) {
			if (substance_list.count(current_subs.name))
				log << "ERROR " << current_subs.name << endl;
			if (current_subs.name == "")
				log << "ERROR EMPTY C" << endl;
			substance_list.insert(make_pair(current_subs.name, current_subs));
			current_subs.clear();
		}
	} while (getline(comp, str));

	str = first_useful(react);
	bool flag_drop = false;
	reaction current_react;

	do {
		if (check_element(str, "EC-NUMBER"))
			current_react.ec_name = get_element(str, "EC-NUMBER");
		if (check_element(str , "REACTION-DIRECTION"))
			dir = get_element(str, "REACTION-DIRECTION");
		if (check_element(str, "UNIQUE-ID")) {
			if (check_element(get_element(str, "UNIQUE-ID"), "TRANS-"))
				flag_drop = true;
			if (current_react.ec_name != "")
				continue;
			current_react.ec_name = get_element(str, "UNIQUE-ID");
		}

		if (check_element(str, "ENZYMATIC-REACTION")) {
			string ecr_sdtr = get_element(str, "ENZYMATIC-REACTION");
			current_react.enr.insert(ecr_sdtr);
		}

		if (check_element(str , "LEFT")) {
			name = get_element(str, "LEFT");
			flag_drop |= drop_test(name);
			if (false == flag_drop && false == substance_list.count(name)) {
				log << "ERROR " << name << endl;
				flag_drop = true;
			}
			current_react.sub[name] = 1;
		}

		if (check_element(str , "RIGHT")) {
			name = get_element(str, "RIGHT");
			flag_drop |= drop_test(name);
			if (false == flag_drop && false == substance_list.count(name)) {
				log << "ERROR " << name << endl;
				flag_drop = true;
			}
			current_react.pdt[name] = 1;
		}

		if (check_element(str , "^COEFFICIENT")) {
			int coeff = to_int(get_element(str, "^COEFFICIENT"));
			current_react.sub[name] = coeff;
		}

		if ("//" == str) {
			if (flag_drop) {
				flag_drop = false;
				current_react.clear();
				continue;
			}

			string ec_name = current_react.ec_name;
			
			string p_num = "_pum_" + std :: to_string(ec_check[ec_name] ++);
			
			if ("REVERSIBLE" == dir || "LEFT-TO-RIGHT" == dir) {
				current_react.ec_name = ec_name + "_0" + p_num;
				reaction_list.push_back(current_react);
			}
			swap(current_react.sub, current_react.pdt);
			if ("REVERSIBLE" == dir || "RIGHT-TO-LEFT" == dir) {
				current_react.ec_name = ec_name + "_1" + p_num;
				reaction_list.push_back(current_react);
			}

			current_react.clear();
		}
	} while (getline(react, str));
	
	react.close();
	comp.close();

	log << reaction_list.size() << endl;
	for (size_t i = 0; i < reaction_list.size(); ++ i) {
		log << reaction_list[i].ec_name << endl;
		for (auto j = reaction_list[i].sub.begin();
			j != reaction_list[i].sub.end(); ++ j)
			log << "    SUB " << j -> first << ' ' << j -> second << endl;
		for (auto j = reaction_list[i].pdt.begin();
			j != reaction_list[i].pdt.end(); ++ j)
			log << "    PDT " << j -> first << ' ' << j -> second << endl;
	}

	log << substance_list.size() << endl;
	for (auto i = substance_list.begin(); i != substance_list.end(); ++ i) {
		log << (i -> second.name) << '|' << (i -> second.ID) << endl;
		for (auto j = i -> second.atom.begin(); j != i -> second.atom.end(); ++ j)
			log << "    ATOM " << j -> first << ' ' << j -> second << endl;
	}

	log.close();
	
	spc = all_caps(spc); bool dang_flag = false;
	for (size_t i = 0; i < forbid_org.size(); ++ i) {
		vector <string> s = split(forbid_org[i]); int cnt = 0;
		for (size_t j = 0; j < min((size_t)2, s.size()) ; ++ j) {
			if (spc.find(s[j]) != string :: npos)
				++ cnt;
			//cout << s[j] << endl;
		}
		if (cnt >= 2) {
			dang_flag = true;
			cout << spc << '|' << forbid_org[i] << endl;
			break;
		}
	}
	
	cout << spc << endl;

	assert(dang_flag == false);

	return true;
}

};
