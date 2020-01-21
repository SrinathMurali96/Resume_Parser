import os
from . import utils
import spacy
import pprint
from spacy.matcher import Matcher
import multiprocessing as mp

class ResumeParser(object):
    def __init__(self, resume):
        nlp = spacy.load('en_core_web_sm')
        self.__matcher = Matcher(nlp.vocab)
        self.__details = {
            'name'              : None,
            'email'             : None,
            'mobile_number'     : None,
            'skills'            : None,
            'education'         : None,
            'experience'        : None,
            'competencies'      : None,
            'measurable_results': None
        }
        self.__resume      = resume
        self.__text_raw    = utils.extract_text(self.__resume, os.path.splitext(self.__resume)[1])
        self.__text        = ' '.join(self.__text_raw.split())
        self.__nlp         = nlp(self.__text)
        self.__noun_chunks = list(self.__nlp.noun_chunks)
        self.__get_basic_details()

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        name       = utils.extract_name(self.__nlp, matcher=self.__matcher)
        email      = utils.extract_email(self.__text)
        mobile     = utils.extract_mobile_number(self.__text)
        skills     = utils.extract_skills(self.__nlp, self.__noun_chunks)
        edu        = utils.extract_education([sent.string.strip() for sent in self.__nlp.sents])
        experience = utils.extract_experience(self.__text)
        entities   = utils.extract_entity_sections(self.__text_raw)
        self.__details['name'] = name
        self.__details['email'] = email
        self.__details['mobile_number'] = mobile
        self.__details['skills'] = skills
        # self.__details['education'] = entities['education']
        self.__details['education'] = edu
        self.__details['experience'] = experience
        try:
            self.__details['competencies'] = utils.extract_competencies(self.__text_raw, entities['experience'])
            self.__details['measurable_results'] = utils.extract_measurable_results(self.__text_raw, entities['experience'])
        except KeyError:
            self.__details['competencies'] = []
            self.__details['measurable_results'] = []
        return

def resume_result_wrapper(resume):
        parser = ResumeParser(resume)
        return parser.get_extracted_data()

if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())

    resumes = []
    data = []
    for root, directories, filenames in os.walk('resumes'):
        for filename in filenames:
            file = os.path.join(root, filename)
            resumes.append(file)

    results = [pool.apply_async(resume_result_wrapper, args=(x,)) for x in resumes]

    results = [p.get() for p in results]

    pprint.pprint(results)
    
 from nltk.corpus import stopwords

# Omkar Pathak
NAME_PATTERN      = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

# Education (Upper Case Mandatory)
EDUCATION         = [
                    'BE','B.E.', 'B.E', 'BS', 'B.S', 'ME', 'M.E', 'M.E.', 'MS', 'M.S', 'BTECH', 'MTECH', 
                    'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
                    ]

NOT_ALPHA_NUMERIC = r'[^a-zA-Z\d]'

NUMBER            = r'\d+'

# For finding date ranges
MONTHS_SHORT      = r'(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)|(aug)|(sep)|(oct)|(nov)|(dec)'
MONTHS_LONG       = r'(january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december)'
MONTH             = r'(' + MONTHS_SHORT + r'|' + MONTHS_LONG + r')'
YEAR              = r'(((20|19)(\d{2})))'

STOPWORDS         = set(stopwords.words('english'))

RESUME_SECTIONS = [
                    'accomplishments',
                    'experience',
                    'education',
                    'interests',
                    'projects',
                    'professional experience',
                    'publications',
                    'skills',
                ]

COMPETENCIES = {
    'teamwork': [
        'supervised',
        'facilitated',
        'planned',
        'plan',
        'served',
        'serve',
        'project lead',
        'managing',
        'managed',
        'lead ',
        'project team',
        'team',
        'conducted',
        'worked',
        'gathered',
        'organized',
        'mentored',
        'assist',
        'review',
        'help',
        'involve',
        'share',
        'support',
        'coordinate',
        'cooperate',
        'contributed'
    ],
    'communication': [
        'addressed',
        'collaborated',
        'conveyed',
        'enlivened',
        'instructed',
        'performed',
        'presented',
        'spoke',
        'trained',
        'author',
        'communicate',
        'define',
        'influence',
        'negotiated',
        'outline',
        'proposed',
        'persuaded',
        'edit',
        'interviewed',
        'summarize',
        'translate',
        'write',
        'wrote',
        'project plan',
        'business case',
        'proposal',
        'writeup'
    ],
    'analytical': [
        'process improvement',
        'competitive analysis',
        'aligned',
        'strategive planning',
        'cost savings',
        'researched ',
        'identified',
        'created',
        'led',
        'measure',
        'program',
        'quantify',
        'forecasr',
        'estimate',
        'analyzed',
        'survey',
        'reduced',
        'cut cost',
        'conserved',
        'budget',
        'balanced',
        'allocate',
        'adjust',
        'lauched',
        'hired',
        'spedup',
        'speedup',
        'ran',
        'run',
        'enchanced',
        'developed'
    ],
    'result_driven': [
        'cut',
        'decrease',
        'eliminate',
        'increase',
        'lower',
        'maximize',
        'rasie',
        'reduce',
        'accelerate',
        'accomplish',
        'advance',
        'boost',
        'change',
        'improve',
        'saved',
        'save',
        'solve',
        'solved',
        'upgrade',
        'fix',
        'fixed',
        'correct',
        'achieve'           
    ],
    'leadership': [
        'advise',
        'coach',
        'guide',
        'influence',
        'inspire',
        'instruct',
        'teach',
        'authorized',
        'chair',
        'control',
        'establish',
        'execute',
        'hire',
        'multi-task',
        'oversee',
        'navigate',
        'prioritize',
        'approve',
        'administer',
        'preside',
        'enforce',
        'delegate',
        'coordinate',
        'streamlined',
        'produce',
        'review',
        'supervise',
        'terminate',
        'found',
        'set up',
        'spearhead',
        'originate',
        'innovate',
        'implement',
        'design',
        'launch',
        'pioneer',
        'institute'
    ]
}

MEASURABLE_RESULTS = {
    'metrics': [
        'saved',
        'increased',
        '$ ',
        '%',
        'percent',
        'upgraded',
        'fundraised ',
        'millions',
        'thousands',
        'hundreds',
        'reduced annual expenses ',
        'profits',
        'growth',
        'sales',
        'volume',
        'revenue',
        'reduce cost',
        'cut cost',
        'forecast',
        'increase in page views',
        'user engagement',
        'donations',
        'number of cases closed',
        'customer ratings',
        'client retention',
        'tickets closed',
        'response time',
        'average',
        'reduced customer complaints',
        'managed budget',
        'numeric_value'
    ],
    'action_words': [
        'developed',
        'led',
        'analyzed',
        'collaborated',
        'conducted',
        'performed',
        'recruited',
        'improved',
        'founded',
        'transformed',
        'composed',
        'conceived',
        'designed',
        'devised',
        'established',
        'generated',
        'implemented',
        'initiated',
        'instituted',
        'introduced',
        'launched',
        'opened',
        'originated',
        'pioneered',
        'planned',
        'prepared',
        'produced',
        'promoted',
        'started',
        'released',
        'administered',
        'assigned',
        'chaired',
        'consolidated',
        'contracted',
        'co-ordinated',
        'delegated',
        'directed',
        'evaluated',
        'executed',
        'organized',
        'oversaw',
        'prioritized',
        'recommended',
        'reorganized',
        'reviewed',
        'scheduled',
        'supervised',
        'guided',
        'advised',
        'coached',
        'demonstrated',
        'illustrated',
        'presented',
        'taught',
        'trained',
        'mentored',
        'spearheaded',
        'authored',
        'accelerated',
        'achieved',
        'allocated',
        'completed',
        'awarded',
        'persuaded',
        'revamped',
        'influenced',
        'assessed',
        'clarified',
        'counseled',
        'diagnosed',
        'educated',
        'facilitated',
        'familiarized',
        'motivated',
        'participated',
        'provided',
        'referred',
        'rehabilitated',
        'reinforced',
        'represented',
        'moderated',
        'verified',
        'adapted',
        'coordinated',
        'enabled',
        'encouraged',
        'explained',
        'informed',
        'instructed',
        'lectured',
        'stimulated',
        'classified',
        'collated',
        'defined',
        'forecasted',
        'identified',
        'interviewed',
        'investigated',
        'researched',
        'tested',
        'traced',
        'interpreted',
        'uncovered',
        'collected',
        'critiqued',
        'examined',
        'extracted',
        'inspected',
        'inspired',
        'summarized',
        'surveyed',
        'systemized',
        'arranged',
        'budgeted',
        'controlled',
        'eliminated',
        'itemised',
        'modernised',
        'operated',
        'organised',
        'processed',
        'redesigned',
        'reduced',
        'refined',
        'resolved',
        'revised',
        'simplified',
        'solved',
        'streamlined',
        'appraised',
        'audited',
        'balanced',
        'calculated',
        'computed',
        'projected',
        'restructured',
        'modelled',
        'customized',
        'fashioned',
        'integrated',
        'proved',
        'revitalized',
        'set up',
        'shaped',
        'structured',
        'tabulated',
        'validated',
        'approved',
        'catalogued',
        'compiled',
        'dispatched',
        'filed',
        'monitored',
        'ordered',
        'purchased',
        'recorded',
        'retrieved',
        'screened',
        'specified',
        'systematized',
        'conceptualized',
        'brainstomed',
        'tasked',
        'supported',
        'proposed',
        'boosted',
        'earned',
        'negotiated',
        'navigated',
        'updated',
        'utilized'
    ],
    'weak_words': [
        'i',
        'got',
        'i\'ve',
        'because',
        'our',
        'me',
        'he',
        'her',
        'him',
        'she',
        'helped',
        'familiar',
        'asssisted',
        'like',
        'enjoy',
        'love',
        'did',
        'tried',
        'attempted',
        'worked',
        'approximately',
        'managed',
        'manage',
        'create',
        'created'
    ]
}
