from application import db
from application.dirtylist import *
import random
import datetime, pytz
import hashlib

# Table of all users
class user(db.Model):
    id = db.Column(db.Integer, primary_key = True)          
    nickname = db.Column(db.String(60))                 # User's nickname, shown at the top of pages
    email = db.Column(db.String(120), unique = True)    # User's email, an unique key
    password = db.Column(db.String(120))                # Password('s md5)
    icon = db.Column(db.Integer)                        # User's icon's id
    mark = db.Column(db.String(320))                    # the mark list   
    def get_id(self):
        return self.id
    def check_pw(self, pw):
        return self.password == pw
    def __init__(self, nickname, email, password):
        self.nickname = nickname
        self.email = email
        self.password = password
        self.icon = random.randint(1,10)
        self.mark = '[]'
    def __repr__(self):
        return '<User %r>' % self.nickname
    def save(self):
        db.session.add(self)
        db.session.commit()


# Table of all matters (for search & select)
class matterDB(db.Model):
    id = db.Column(db.Integer, primary_key = True)  # Index
    matter_name = db.Column(db.String(120))         # Matter's name
    matter_code = db.Column(db.String(120))         # Matter's in-database code
    def __init__(self, matter_name, matter_code):
        self.matter_name = matter_name
        self.matter_code = matter_code
    def __repr__(self):
        return '<Matter %r>' % self.matter_name
    def save(self):
        db.session.add(self)
        db.session.commit()


# Table of all medium (including matters and concentration information)
class mediumDB(db.Model):
    id = db.Column(db.Integer, primary_key = True)  # Index
    name = db.Column(db.String(100))                # Medium's name
    matters = db.Column(db.String(500))             # Matters included in the medium (With dirty list)
    concentration = db.Column(db.String(500))       # Matters' concentration (With dirty dictionary)
    def __init__(self, name, mattersdict = None):
        self.name = name
        self.matters = '[]'
        self.concentration = '{}'
        if mattersdict:
            for i in mattersdict.keys():
                cur_matter = matterDB.query.filter_by(matter_name = i).first()
                if cur_matter is None:
                    continue
                self.matters = libs_list_insert(self.matters, cur_matter.id)
                self.concentration = libs_dict_insert(self.concentration, cur_matter.id, mattersdict[i])
    def __repr__(self):
        return '<Medium %r>' % self.name
    def save(self):
        db.session.add(self)
        db.session.commit()


# Table of all bacteria
class floraDB(db.Model):
    id = db.Column(db.Integer, primary_key = True)  # Index
    code = db.Column(db.String(100))                # Bacteria's code name in database
    name = db.Column(db.String(100))                # Bacteria's name
    def __init__(self, code, name):
        self.code = code
        self.name = name
    def __repr__(self):
        return '<Flora %r>' % self.name
    def save(self):
        db.session.add(self)
        db.session.commit()

# Table of all plasmid
class plasmidDB(db.Model):
    id = db.Column(db.Integer, primary_key = True)  # Index
    name = db.Column(db.String(60))                 # Plasmid's name
    sequence = db.Column(db.String(5000))           # Plasmid's sequence
    def __init__(self, name, sequence):
        self.name = name
        self.sequence = sequence
    def __repr__(self):
        return '<Plasmid %r>' % self.name
    def save(self):
        db.session.add(self)
        db.session.commit()


# The terminal for sequence
terminalDB = {
    "name": "A 202 Terminator",
    "Introduction": "double terminator (B0010-B0012)",
    "BBa": "BBa_B0015",
    "sequence": 'GAATTCGCGGCCGCTTCTAGAGCCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATCTGTTGTTTGTCGGTGAACGCTCTCTACTAGAGTCACACTGGCTCACCTTCGGGTGGGCCTTTCTGCGTTTATATACTAGTAGCGGCCGCTGCAG'
}


# Table for design's information
class design(db.Model):
    id = db.Column(db.Integer, primary_key = True)              # Index
    design_name = db.Column(db.String(60))                      # Name of the design
    design_mode = db.Column(db.String(30))                      # Mode of the design (Should be "synthetic" or "decompose")
    description = db.Column(db.String(300))                     # Description of the design
    state = db.Column(db.Integer)                               # State that the design is now in (1 to 5)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Owner's user id 
    owner = db.relationship('user', backref = db.backref('design_set', lazy = 'dynamic'))
    liked_by = db.Column(db.String(320))                        # List of the users like the design
    design_time = db.Column(db.DateTime)                        # Design's created time
    shared = db.Column(db.Boolean)                              # If the design is shared
    needHelp = db.Column(db.Boolean)                            # If the design's owner need help
    # state1 data region
    state1_data_id = db.Column(db.Integer, db.ForeignKey("state1_data.id"))
    state1_data = db.relationship('state1_data', backref = db.backref('owners', lazy = 'dynamic'))
    state1_upload_file = db.Column(db.Boolean)
    # state2 data region
    state2_data_id = db.Column(db.Integer, db.ForeignKey("state2_data.id"))
    state2_data = db.relationship('state2_data', backref = db.backref('owners', lazy = 'dynamic'))
    # state3 data region
    enzyme_info_id = db.Column(db.Integer, db.ForeignKey('enzyme_info.id'))
    enzyme_info = db.relationship('enzyme_info', backref = db.backref('all_s2data', lazy = 'dynamic'))
    # state5 data region
    state5_saved_data = db.Column(db.String(5000))
    state5_upload_file = db.Column(db.Boolean)
    state5_file_path = db.Column(db.String(100))
    def get_id(self):
        return self.id
    def __init__(self, owner):
        self.owner = owner
        self.state = 1
        self.liked_by = '[]'
        self.design_name = None
        self.design_mode = ''
        self.design_time = datetime.datetime.now(pytz.timezone('America/New_York'))
        self.shared = False
        self.needHelp = False
        self.state1_upload_file = False
        self.state5_saved_data = '{}'
        self.state5_upload_file = False
    def __repr__(self):
        return '<Design %r> %s' % (self.id, self.design_name)
    def save(self):
        db.session.add(self)
        db.session.commit()


class state1_data(db.Model):
    id = db.Column(db.Integer, primary_key = True)                  # Mode of the design (Should be "synthetic" or "decompose")
    reaction_time = db.Column(db.Float)                             # Total time of the reaction
    medium_id = db.Column(db.Integer, db.ForeignKey('mediumDB.id')) # Used medium's id
    medium = db.relationship('mediumDB', backref = 'all_design')
    flora = db.Column(db.String(320))                               # All flora set (With dirty list)
    make_matter = db.Column(db.String(320))                         # All matters for synthetic (With dirty list)
    resolve_matter = db.Column(db.String(320))                      # All matters for decomposing (With dirty list)
    md5 = db.Column(db.String(60))                                  # All data's md5 (For multi used of the calculating result)
    def refresh_md5(self):                                          # Refresh the md5 hash with all the data
        src = str(self.reaction_time) + str(self.medium_id) + self.flora + self.make_matter + self.resolve_matter
        m = hashlib.md5()
        m.update(src)
        self.md5 = m.hexdigest()
    def __init__(self):
        self.md5 = ''
        self.flora = '[]'
        self.make_matter = '[]'
        self.resolve_matter = '[]'
    def __repr__(self):
        return '<State 1 data %r>' % self.md5
    def save(self):
        self.refresh_md5()
        db.session.add(self)
        db.session.commit()


class make_matter(db.Model):
    id = db.Column(db.Integer, primary_key = True)                      # Index
    matter_id = db.Column(db.Integer, db.ForeignKey('matterDB.id'))     # Based on which matter
    matter = db.relationship('matterDB', backref = db.backref('maked_set', lazy = 'dynamic'))
    lower = db.Column(db.Float)                                         # Lower bound 
    upper = db.Column(db.Float)                                         # Upper bound
    maxim = db.Column(db.Boolean)                                       # Is maximum bound exists
    def __init__(self, matter, lower, upper, maxim):
        self.matter = matter
        self.lower = lower
        self.upper = upper
        self.maxim = maxim
    def __repr__(self):
        return '<Make mode matter %r>' % self.id
    def save(self):
        db.session.add(self)
        db.session.commit()


class resolve_matter(db.Model):
    id = db.Column(db.Integer, primary_key = True)                      # Index
    matter_id = db.Column(db.Integer, db.ForeignKey('matterDB.id'))     # Based on which matter
    matter = db.relationship('matterDB', backref = db.backref('resolved_set', lazy = 'dynamic'))
    begin = db.Column(db.Float)                                         # Beginning concentration
    def __init__(self, matter, begin):
        self.matter = matter
        self.begin = begin
    def __repr__(self):
        return '<Resolve mode matter %r>' % self.id
    def save(self):
        db.session.add(self)
        db.session.commit()


class state2_data(db.Model):
    id = db.Column(db.Integer, primary_key = True)  # Index
    state1_md5 = db.Column(db.String(60))           # Source data's md5
    bacteria = db.Column(db.String(320))            # All used bacteria (With dirty list)
    def refresh_md5(self):
        src = bacteria
        m = hashlib.md5()
        m.update(src)
        self.md5 = m.hexdigest()
    def __init__(self):
        self.state1_md5 = ''
        self.bacteria = '[]'
    def __repr__(self):
        return '<State 2 data %r>' % self.id
    def save(self):
        self.refresh_md5()
        db.session.add(self)
        db.session.commit()


class used_bacteria(db.Model):
    id = db.Column(db.Integer, primary_key = True)                      # Index
    flora_id = db.Column(db.Integer, db.ForeignKey('floraDB.id'))       # Prototype bacteria
    flora = db.relationship('floraDB', backref = db.backref('used_bacteria', lazy = 'dynamic'))
    enzyme = db.Column(db.String(320))                                  # Enzyme list (With dirty list)
    def __init__(self, flora):
        self.flora = flora
        self.enzyme = '[]'
    def __repr__(self):
        return '<Edited bacteria based on %r>' % self.flora_id
    def save(self):
        db.session.add(self)
        db.session.commit()


class enzyme(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60))                 # Enzyme's name
    sequence = db.Column(db.String(500))            # Enzyme's CDS sequence
    promoter = db.Column(db.String(320))            # Enzyme's adapted promot
    rbs = db.Column(db.String(320))                 # Enzyme's adapted rbs (With dirty list)
    from_bact_id = db.Column(db.Integer, db.ForeignKey('floraDB.id'))
    from_bact = db.relationship('floraDB', backref = db.backref('used_enzyme', lazy = 'dynamic'))   # Where the enzyme from
    def __init__(self, sequence, name, from_bact):
        self.sequence = sequence
        self.name = name
        self.promoter = '[]'
        self.rbs = '[]'
        self.from_bact = from_bact
        self.detected_promoter = 0
        self.detected_rbs = 0
        self.mRNA_s = 6.7
        self.protein_s = 1.4
    def __repr__(self):
        return '<Enzyme %r>' % self.name
    def save(self):
        db.session.add(self)
        db.session.commit()

class enzyme_info(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    detected_dict = db.Column(db.String(1000))                  # Every enzyme's detected promoter and RBS's ID dict (With dirty dict)
    md5 = db.Column(db.String(60))
    state3_matter_plot = db.Column(db.String(1000))             # Diagram's 20 points for each Matters (With dirty dict)
    def insert_info(self, enzyme_id, detected_promoter, detected_rbs, mRNA_s, protein_s):
        tmpdict = libs_dict_insert(self.detected_dict, enzyme_id,
            {
                "detected_promoter": detected_promoter,
                "detected_rbs": detected_rbs,
                "mRNA_s": mRNA_s,
                "protein_s": protein_s
            })
        if tmpdict:
            self.detected_dict = tmpdict
    def value(self):
        return libs_dict_query_all(self.detected_dict)
    def refresh_md5(self):
        m = hashlib.md5()
        m.update(self.detected_dict)
        self.md5 = m.hexdigest()
    def __init__(self):
        self.detected_dict = '{}'
        self.state3_matter_plot = '{}'
    def save(self):
        db.session.add(self)
        db.session.commit()

class promoter(db.Model):
    id = db.Column(db.Integer, primary_key = True)  # Index
    sequence = db.Column(db.String(300))            # Promoter's sequence
    strength = db.Column(db.Float)                  # Promoter's strength
    name = db.Column(db.String(60))
    type_ = db.Column(db.String(60))
    BBa = db.Column(db.String(60))
    Introduction = db.Column(db.String(60))
    NCBI = db.Column(db.String(60))
    FASTA = db.Column(db.String(60))
    def __init__(self, sequence, strength):
        self.sequence = sequence
        self.strength = strength
    def __repr__(self):
        return '<Promoter with strength %r>' % self.strength
    def save(self):
        db.session.add(self)
        db.session.commit()

class rbs(db.Model):
    id = db.Column(db.Integer, primary_key = True)  # Index
    sequence = db.Column(db.String(300))            # Promoter's sequence
    strength = db.Column(db.Float)                  # Promoter's strength
    name = db.Column(db.String(60))
    type_ = db.Column(db.String(60))
    BBa = db.Column(db.String(60))
    Introduction = db.Column(db.String(60))
    NCBI = db.Column(db.String(60))
    FASTA = db.Column(db.String(60))
    def __init__(self, sequence, strength):
        self.sequence = sequence
        self.strength = strength
    def __repr__(self):
        return '<RBS with strength %r>' % self.strength
    def save(self):
        db.session.add(self)
        db.session.commit()

# tip off
class report(db.Model):
    id = db.Column(db.Integer, primary_key = True)  # Index
    design_id = db.Column(db.Integer)               # Which design was reported
    # by_user_id = db.Column(db.Integer)              # By whom the design was reported
    reason = db.Column(db.String(300))
    def __init__(self, design, reason):
        self.design_id = design
        self.reason = reason
    def __repr__(self):
        return '<Report of design %r>: %r' % (self.design_id, self.reason)
    def save(self):
        db.session.add(self)
        db.session.commit()
