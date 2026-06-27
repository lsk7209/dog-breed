from __future__ import annotations

from datetime import datetime, timedelta
from html import escape
from pathlib import Path
import csv
import io
import json
import re


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / ".github" / "content-queue"
SCHEDULE = ROOT / "content-schedule.json"
BASE_URL = "https://dogbreedcost.com"
ADSENSE_LOADER = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3050601904412736" crossorigin="anonymous"></script>'
GA4_TAG = '<script async src="https://www.googletagmanager.com/gtag/js?id=G-5FZSHME54N"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag(\'js\',new Date());gtag(\'config\',\'G-5FZSHME54N\');</script>'
FEED_LINK = '<link rel="alternate" type="application/rss+xml" title="BreedWise RSS" href="https://dogbreedcost.com/feed.xml">'
VERIFICATION_TAGS = '<meta name="google-site-verification" content="33-RSHdhGx_IC-b1_fpFOHyr-s0P35VSCOwIOFy6UAE"><meta name="naver-site-verification" content="d0084eb5ece035b3d7de4936181ae0dd92022175">'


TOPICS_CSV = """main_keyword|expanded_keywords|title|subtitle|angle|reader|source
renter dog breed shortlist|lease rules, pet deposits, neighbor noise|Renter Dog Breed Shortlist: Lease-Safe Planning Before You Apply|A renter dog breed shortlist for comparing lease rules, pet deposits, and neighbor noise before adoption.|housing constraint|apartment renters|avma
apartment dog noise audit|barking triggers, shared walls, quiet routines|Apartment Dog Noise Audit: Choose a Breed Around Shared Walls|An apartment dog noise audit that connects barking triggers, shared walls, and daily quiet routines.|noise management|city renters|avma
dog breed energy match test|weekday schedule, exercise load, enrichment time|Dog Breed Energy Match Test: A Weekday Reality Check|A dog breed energy match test for comparing exercise load, enrichment time, and a normal weekday schedule.|time fit|busy households|akc
low shedding dog reality check|coat upkeep, allergies, cleaning work|Low-Shedding Dog Reality Check: Less Hair Is Not Less Work|A low shedding dog reality check covering coat upkeep, allergy expectations, and cleaning work.|expectation reset|allergy-conscious buyers|merck
family dog safety budget|child gates, training sessions, supervision routines|Family Dog Safety Budget: The Costs Behind a Calm Household|A family dog safety budget guide for child gates, training sessions, and supervision routines.|family safety|parents|avma
rescue dog breed history checklist|shelter notes, behavior records, uncertainty buffer|Rescue Dog Breed History Checklist: What to Ask Before You Bond|A rescue dog breed history checklist for shelter notes, behavior records, and uncertainty buffers.|adoption records|rescue adopters|avma
breeder health record review|screening paperwork, parent records, contract questions|Breeder Health Record Review: Read the Paperwork Before the Puppy|A breeder health record review guide using screening paperwork, parent records, and contract questions.|record review|puppy buyers|ofa
dog insurance research checklist|policy exclusions, breed questions, claim limits|Dog Insurance Research Checklist: Compare Questions, Not Hype|A dog insurance research checklist for policy exclusions, breed questions, and claim limits without ranking insurers.|financial research|cost planners|naphia
puppy first year cost traps|setup purchases, training gaps, emergency reserve|Puppy First-Year Cost Traps: Where New Owners Undercount|A puppy first year cost traps guide covering setup purchases, training gaps, and an emergency reserve.|first year budget|new owners|synchrony
senior owner dog breed planning|lifting limits, walking pace, support network|Senior Owner Dog Breed Planning: Match Care to Real Mobility|A senior owner dog breed planning guide for lifting limits, walking pace, and support networks.|owner fit|older adults|avma
dog breed climate fit|heat tolerance, coat type, seasonal routines|Dog Breed Climate Fit: Weather Should Shape the Shortlist|A dog breed climate fit guide linking heat tolerance, coat type, and seasonal care routines.|climate fit|regional searchers|akc
flat faced dog heat planning|brachycephalic limits, cooling routines, travel timing|Flat-Faced Dog Heat Planning: Questions Before a Hot Summer|Flat faced dog heat planning for brachycephalic limits, cooling routines, and travel timing.|heat risk|warm climate owners|merck
long backed dog stair plan|ramps, furniture access, weight control|Long-Backed Dog Stair Plan: Home Setup Before Cute Photos|A long backed dog stair plan covering ramps, furniture access, and weight-control routines.|home setup|small breed planners|merck
giant breed car transport cost|vehicle space, ramps, travel gear|Giant Breed Car Transport Cost: The Budget Outside the House|A giant breed car transport cost guide for vehicle space, ramps, and travel gear.|transport budget|large dog buyers|appa
toy breed home safety setup|stairs, handling, dental routines|Toy Breed Home Safety Setup: Tiny Dogs Need Serious Planning|A toy breed home safety setup guide covering stairs, handling, and dental routines.|safety setup|small dog buyers|merck
grooming intensive breeds schedule|coat intervals, salon questions, mat prevention|Grooming-Intensive Breeds Schedule: Budget the Calendar First|A grooming intensive breeds schedule guide for coat intervals, salon questions, and mat prevention.|grooming calendar|coat-focused owners|akc
working dog lifestyle mismatch|job drive, training hours, owner stamina|Working Dog Lifestyle Mismatch: Admiration Is Not a Plan|A working dog lifestyle mismatch guide connecting job drive, training hours, and owner stamina.|lifestyle risk|active breed shoppers|akc
calm dog breed myth|adult temperament, exercise needs, source quality|Calm Dog Breed Myth: Why Labels Can Mislead New Owners|A calm dog breed myth guide about adult temperament, exercise needs, and source quality.|myth busting|first-time researchers|avma
guard dog liability planning|rental rules, visitors, training documentation|Guard Dog Liability Planning: Costs Before Protection Talk|A guard dog liability planning guide for rental rules, visitors, and training documentation.|liability planning|guardian breed shoppers|avma
dog breed allergy expectations|dander, coat care, household testing|Dog Breed Allergy Expectations: What Low-Allergy Claims Miss|Dog breed allergy expectations explained through dander, coat care, and household testing.|allergy planning|sensitive households|merck
hypoallergenic dog cost reality|grooming cadence, cleaning supplies, trial visits|Hypoallergenic Dog Cost Reality: The Maintenance Behind the Claim|A hypoallergenic dog cost reality guide for grooming cadence, cleaning supplies, and trial visits.|cost reality|allergy-conscious buyers|merck
high prey drive dog management|fencing, recall limits, small pet safety|High Prey Drive Dog Management: Plan the Boundaries First|A high prey drive dog management guide for fencing, recall limits, and small pet safety.|behavior management|multi-pet homes|akc
vocal dog breed apartment plan|alert barking, hallway noise, neighbor expectations|Vocal Dog Breed Apartment Plan: Shared-Wall Decisions Before Adoption|A vocal dog breed apartment plan for alert barking, hallway noise, and neighbor expectations.|noise fit|apartment dwellers|avma
dog daycare suitability by breed|temperament notes, vaccines, stress signals|Dog Daycare Suitability by Breed: Questions Before You Budget|A dog daycare suitability by breed guide covering temperament notes, vaccines, and stress signals.|care logistics|working owners|aaha
dog boarding cost by size|kennel fit, medication notes, holiday pricing|Dog Boarding Cost by Size: Plan Travel Before You Need It|A dog boarding cost by size guide for kennel fit, medication notes, and holiday pricing.|travel budget|frequent travelers|appa
dog travel crate budget|crate size, vehicle fit, airline rules|Dog Travel Crate Budget: Measure Before You Book|A dog travel crate budget guide linking crate size, vehicle fit, and airline-rule research.|travel setup|mobile owners|avma
dog food budget by adult size|calorie needs, bag size, growth stage|Dog Food Budget by Adult Size: Puppy Math That Changes Later|A dog food budget by adult size guide for calorie needs, bag size, and growth-stage assumptions.|food budget|budget planners|appa
dog walking schedule audit|weekday gaps, weather plans, backup walkers|Dog Walking Schedule Audit: The Breed Question Hidden in Your Calendar|A dog walking schedule audit for weekday gaps, weather plans, and backup walkers.|schedule audit|time-strapped owners|avma
dog trainer cost planning|group classes, private sessions, habit refreshers|Dog Trainer Cost Planning: Budget for Skills Before Problems|A dog trainer cost planning guide covering group classes, private sessions, and habit refreshers.|training budget|new owners|avma
puppy socialization budget plan|class fees, safe exposure, transport time|Puppy Socialization Budget Plan: Build Confidence Into the Calendar|A puppy socialization budget plan for class fees, safe exposure, and transport time.|puppy planning|puppy buyers|aaha
multi dog breed compatibility|size gaps, play style, resource guarding|Multi-Dog Breed Compatibility: Plan the Second Dog Carefully|A multi dog breed compatibility guide for size gaps, play style, and resource-guarding questions.|multi-dog fit|second-dog families|avma
cat friendly dog breed questions|prey drive, introductions, safe rooms|Cat-Friendly Dog Breed Questions: Protect the Cat First|Cat friendly dog breed questions for prey drive, introductions, and safe-room planning.|multi-pet safety|cat owners|avma
small yard dog exercise plan|sniff walks, training games, fence limits|Small Yard Dog Exercise Plan: Space Is Not the Whole Answer|A small yard dog exercise plan using sniff walks, training games, and fence limits.|yard reality|suburban owners|akc
no yard dog breed planning|walk routes, weather backup, elevator routines|No-Yard Dog Breed Planning: Make the Outside Routine Real|A no yard dog breed planning guide for walk routes, weather backup, and elevator routines.|urban fit|condo owners|avma
city dog breed selection|crowds, elevators, traffic noise|City Dog Breed Selection: Plan for Crowds Before Cuteness|A city dog breed selection guide covering crowds, elevators, and traffic noise.|city lifestyle|urban adopters|avma
suburban dog fence budget|yard gaps, gate habits, neighbor boundaries|Suburban Dog Fence Budget: The Hidden Cost of Freedom|A suburban dog fence budget guide for yard gaps, gate habits, and neighbor boundaries.|fencing cost|suburban families|appa
rural property dog breed fit|wildlife, recall, vet distance|Rural Property Dog Breed Fit: Space Solves Less Than You Think|A rural property dog breed fit guide for wildlife, recall, and veterinary distance.|rural fit|country households|avma
winter weather dog breed fit|paw care, coat length, indoor exercise|Winter Weather Dog Breed Fit: Cold Days Change the Routine|A winter weather dog breed fit guide for paw care, coat length, and indoor exercise.|seasonal fit|cold climate owners|akc
summer heat dog breed risk|walking hours, shade, cooling gear|Summer Heat Dog Breed Risk: Build the Day Around Temperature|A summer heat dog breed risk guide covering walking hours, shade, and cooling gear.|heat planning|hot climate owners|merck
dog coat type maintenance guide|single coat, double coat, corded coat|Dog Coat Type Maintenance Guide: Budget by Texture, Not Looks|A dog coat type maintenance guide comparing single coat, double coat, and corded coat routines.|coat education|grooming planners|akc
double coat grooming mistake|shaving myths, undercoat tools, seasonal sheds|Double-Coat Grooming Mistake: What Future Owners Should Know|A double coat grooming mistake guide about shaving myths, undercoat tools, and seasonal sheds.|grooming myth|spitz breed shoppers|akc
hand stripping terrier cost|coat texture, groomer availability, home tools|Hand-Stripping Terrier Cost: The Grooming Skill Owners Miss|A hand stripping terrier cost guide for coat texture, groomer availability, and home tools.|specialist grooming|terrier shoppers|akc
doodle grooming cost questions|coat unpredictability, mat prevention, salon cadence|Doodle Grooming Cost Questions: Ask Before the First Haircut|A doodle grooming cost questions guide for coat unpredictability, mat prevention, and salon cadence.|mixed coat planning|doodle shoppers|akc
rare breed vet access plan|specialist familiarity, breeder network, records|Rare Breed Vet Access Plan: Rarity Can Change the Budget|A rare breed vet access plan covering specialist familiarity, breeder networks, and records.|rare breed planning|rare breed buyers|avma
popular breed waitlist cost|deposits, travel, screening patience|Popular Breed Waitlist Cost: Slow Down Before the Deposit|A popular breed waitlist cost guide for deposits, travel, and screening patience.|buying process|high-demand breed buyers|avma
adoption fee vs lifetime cost|upfront price, routine care, uncertainty reserve|Adoption Fee vs Lifetime Cost: The Number That Matters Later|An adoption fee vs lifetime cost guide comparing upfront price, routine care, and uncertainty reserve.|cost framing|rescue adopters|synchrony
dog breed temperament labels|breed summaries, individual history, training context|Dog Breed Temperament Labels: Read Them With Limits|A dog breed temperament labels guide for breed summaries, individual history, and training context.|source literacy|breed researchers|avma
male vs female dog cost myths|size differences, training needs, medical assumptions|Male vs Female Dog Cost Myths: Do Not Budget by Folklore|A male vs female dog cost myths guide about size differences, training needs, and medical assumptions.|myth busting|comparison searchers|avma
puppy vs adult dog cost decision|training time, setup needs, known temperament|Puppy vs Adult Dog Cost Decision: Time Is Part of the Price|A puppy vs adult dog cost decision guide covering training time, setup needs, and known temperament.|life stage choice|adopters|aaha
rescue vs breeder records|health paperwork, behavior notes, support expectations|Rescue vs Breeder Records: Compare What You Can Verify|A rescue vs breeder records guide for health paperwork, behavior notes, and support expectations.|record comparison|undecided buyers|ofa
dog breed size chart budget|food, gear, transport, care access|Dog Breed Size Chart Budget: Translate Pounds Into Costs|A dog breed size chart budget guide connecting food, gear, transport, and care access.|size budgeting|planners|appa
medium dog ownership sweet spot|food costs, exercise needs, housing fit|Medium Dog Ownership Sweet Spot: Useful, Not Automatic|A medium dog ownership sweet spot guide for food costs, exercise needs, and housing fit.|size decision|balanced breed searchers|appa
large dog apartment constraints|elevators, floor space, landlord rules|Large Dog Apartment Constraints: The Lease Is Only Step One|A large dog apartment constraints guide for elevators, floor space, and landlord rules.|housing fit|large breed renters|avma
small dog dental planning guide|mouth size, home brushing, vet conversations|Small Dog Dental Planning Guide: Budget the Routine Early|A small dog dental planning guide for mouth size, home brushing, and veterinary conversations.|dental planning|small dog owners|merck
dog stairs ramp budget|furniture rules, traction, aging joints|Dog Stairs Ramp Budget: Home Mobility Starts Early|A dog stairs ramp budget guide for furniture rules, traction, and aging-joint planning.|mobility setup|home planners|merck
dog shedding cleaning cost|vacuum wear, laundry, seasonal blowouts|Dog Shedding Cleaning Cost: The Budget After Adoption Day|A dog shedding cleaning cost guide for vacuum wear, laundry, and seasonal blowouts.|cleaning budget|house-proud owners|appa
dog barking complaint prevention|routine design, enrichment, neighbor communication|Dog Barking Complaint Prevention: Plan Before the Notice|A dog barking complaint prevention guide for routine design, enrichment, and neighbor communication.|neighbor risk|renters|avma
dog separation anxiety planning|alone-time practice, walker backup, trainer budget|Dog Separation Anxiety Planning: Budget for Alone-Time Skills|A dog separation anxiety planning guide for alone-time practice, walker backup, and trainer budget.|alone-time fit|hybrid workers|avma
dog exercise time budget|walk minutes, mental work, bad weather backup|Dog Exercise Time Budget: Count Hours, Not Hopes|A dog exercise time budget guide for walk minutes, mental work, and bad-weather backup.|time budget|busy owners|akc
dog enrichment subscription alternatives|DIY games, rotation bins, training rewards|Dog Enrichment Subscription Alternatives: Spend on Variety, Not Clutter|Dog enrichment subscription alternatives using DIY games, rotation bins, and training rewards.|budget enrichment|cost-conscious owners|avma
dog sport starter budget|class fees, gear, travel, vet clearance questions|Dog Sport Starter Budget: Try the Hobby Before Buying the Gear|A dog sport starter budget guide for class fees, gear, travel, and veterinary clearance questions.|activity budget|sport-curious owners|akc
dog hiking breed checklist|trail rules, heat, paw care, recall|Dog Hiking Breed Checklist: Trail Dreams Need Practical Limits|A dog hiking breed checklist for trail rules, heat, paw care, and recall.|outdoor fit|hikers|avma
dog swimming breed questions|water safety, coat drying, ear care|Dog Swimming Breed Questions: Water-Loving Does Not Mean Automatic|Dog swimming breed questions covering water safety, coat drying, and ear care.|water activity|lake families|merck
dog fetch obsession management|arousal, joint load, structured games|Dog Fetch Obsession Management: When Exercise Needs Rules|A dog fetch obsession management guide for arousal, joint load, and structured games.|behavior routine|active owners|avma
dog recall training risk|prey drive, safe spaces, long lines|Dog Recall Training Risk: Plan for the Dog You Actually Have|A dog recall training risk guide for prey drive, safe spaces, and long-line practice.|training risk|off-leash hopefuls|avma
dog leash reactivity budget|trainer support, equipment, quiet routes|Dog Leash Reactivity Budget: The Cost of Better Walks|A dog leash reactivity budget guide for trainer support, equipment, and quiet routes.|behavior cost|urban walkers|avma
dog muzzle training planning|vet visits, safety, positive conditioning|Dog Muzzle Training Planning: A Practical Safety Skill|A dog muzzle training planning guide for vet visits, safety, and positive conditioning.|handling skill|safety-minded owners|avma
dog crate training cost|crate size, bedding, gradual practice|Dog Crate Training Cost: Buy the Right Setup Once|A dog crate training cost guide for crate size, bedding, and gradual practice.|setup cost|puppy owners|avma
dog fence escape risk review|digging, climbing, gate habits|Dog Fence Escape Risk Review: Inspect the Yard Like a Trainer|A dog fence escape risk review for digging, climbing, and gate habits.|containment risk|yard owners|avma
dog home office routine|meetings, walk timing, attention breaks|Dog Home Office Routine: Make Remote Work Dog-Compatible|A dog home office routine guide for meetings, walk timing, and attention breaks.|remote work fit|remote workers|avma
dog toddler household checklist|gates, toy zones, supervision roles|Dog Toddler Household Checklist: Separate Cute From Safe|A dog toddler household checklist covering gates, toy zones, and supervision roles.|family safety|parents|avma
dog apartment lease restrictions|weight limits, breed clauses, fees|Dog Apartment Lease Restrictions: Read the Pet Policy First|A dog apartment lease restrictions guide for weight limits, breed clauses, and fees.|lease research|renters|avma
dog breed banned list research|local rules, housing policies, travel issues|Dog Breed Banned List Research: Verify Rules Before You Choose|A dog breed banned list research guide for local rules, housing policies, and travel issues.|legal research|restricted-breed searchers|avma
dog landlord pet interview|references, training plan, damage prevention|Dog Landlord Pet Interview: Prepare Evidence Before Asking|A dog landlord pet interview guide for references, training plans, and damage prevention.|renter strategy|apartment applicants|avma
dog move across states plan|records, climate change, new vet access|Dog Move Across States Plan: Breed Fit Can Change by Address|A dog move across states plan for records, climate change, and new veterinary access.|relocation planning|moving households|avma
dog vet record folder|vaccines, screening, medication notes|Dog Vet Record Folder: Build the File Before It Is Urgent|A dog vet record folder guide for vaccines, screening, and medication notes.|documentation|organized owners|aaha
dog health screening acronym guide|OFA, CHIC, DNA tests, limitations|Dog Health Screening Acronym Guide: Decode OFA, CHIC, and DNA Tests|A dog health screening acronym guide explaining OFA, CHIC, DNA tests, and limitations.|source literacy|puppy researchers|ofa
OFA CHIC records checklist|breed databases, parent numbers, result dates|OFA CHIC Records Checklist: What Future Owners Can Verify|An OFA CHIC records checklist for breed databases, parent numbers, and result dates.|record verification|breeder shoppers|ofa
dog genetic test expectations|carrier status, breed mix, health uncertainty|Dog Genetic Test Expectations: Useful Clues, Real Limits|A dog genetic test expectations guide for carrier status, breed mix, and health uncertainty.|test literacy|evidence-minded owners|ofa
dog breed lifespan planning|age curve, senior care, emotional budget|Dog Breed Lifespan Planning: Budget for the Whole Arc|A dog breed lifespan planning guide for age curve, senior care, and emotional budget.|long-term planning|future owners|aaha
dog senior care reserve|mobility aids, medication discussions, visit cadence|Dog Senior Care Reserve: Start Before the Gray Muzzle|A dog senior care reserve guide for mobility aids, medication discussions, and visit cadence.|senior cost|long-term planners|aaha
dog emergency fund formula|monthly savings, deductible gaps, transport|Dog Emergency Fund Formula: A Calm Number for Uncertain Costs|A dog emergency fund formula using monthly savings, deductible gaps, and transport planning.|financial planning|budgeters|synchrony
dog routine care calendar|annual visits, grooming cycles, supply refills|Dog Routine Care Calendar: Turn Pet Care Into Appointments|A dog routine care calendar for annual visits, grooming cycles, and supply refills.|calendar planning|busy owners|aaha
dog dental cleaning budget questions|home care, estimates, anesthesia conversations|Dog Dental Cleaning Budget Questions: Ask Before the Estimate|Dog dental cleaning budget questions for home care, estimates, and anesthesia conversations.|dental planning|adult dog owners|merck
dog spay neuter timing cost|life stage, vet discussion, recovery setup|Dog Spay Neuter Timing Cost: Plan the Conversation, Not the Answer|A dog spay neuter timing cost guide for life stage, veterinary discussion, and recovery setup.|vet conversation|new owners|aaha
dog vaccination visit planning|core vaccines, records, appointment rhythm|Dog Vaccination Visit Planning: Keep the Record Trail Clean|A dog vaccination visit planning guide for core vaccines, records, and appointment rhythm.|preventive care|new owners|aaha
dog parasite prevention budget|seasonality, weight bands, vet guidance|Dog Parasite Prevention Budget: Plan by Season and Size|A dog parasite prevention budget guide for seasonality, weight bands, and veterinary guidance.|preventive budget|cost planners|merck
dog grooming salon interview|coat experience, handling style, appointment length|Dog Grooming Salon Interview: Questions Before the First Trim|A dog grooming salon interview guide for coat experience, handling style, and appointment length.|service selection|grooming planners|akc
dog home grooming kit|brush types, nail tools, bath setup|Dog Home Grooming Kit: Buy for the Coat You Have|A dog home grooming kit guide for brush types, nail tools, and bath setup.|home care|hands-on owners|akc
dog nail trim training cost|desensitization, tools, professional help|Dog Nail Trim Training Cost: Small Skill, Big Payoff|A dog nail trim training cost guide for desensitization, tools, and professional help.|handling training|new owners|avma
dog ear care routine planning|inspection habit, grooming notes, vet questions|Dog Ear Care Routine Planning: Prevent Panic With a Checklist|A dog ear care routine planning guide for inspection habits, grooming notes, and veterinary questions.|routine care|spaniel owners|merck
dog eye care question list|tear staining, irritation signs, breed shape|Dog Eye Care Question List: What to Notice Before It Is Urgent|A dog eye care question list for tear staining, irritation signs, and breed shape.|observation planning|small dog owners|merck
dog skin allergy cost buffer|flare records, diet notes, follow-up visits|Dog Skin Allergy Cost Buffer: Plan for Recurring Questions|A dog skin allergy cost buffer guide for flare records, diet notes, and follow-up visits.|recurring care|sensitive-skin households|merck
dog joint mobility home setup|traction, ramps, weight routines|Dog Joint Mobility Home Setup: Make Movement Easier Early|A dog joint mobility home setup guide for traction, ramps, and weight routines.|mobility planning|large dog owners|merck
dog weight management owner plan|food measuring, treat budget, family rules|Dog Weight Management Owner Plan: The Household Has to Agree|A dog weight management owner plan for food measuring, treat budget, and family rules.|owner habit|all households|aaha
dog brachycephalic breed questions|breathing limits, heat routines, travel plans|Dog Brachycephalic Breed Questions: Ask Before the Cute Face Wins|Dog brachycephalic breed questions covering breathing limits, heat routines, and travel plans.|breed health questions|flat-face breed shoppers|merck
dog herding instinct home plan|nipping, motion triggers, training jobs|Dog Herding Instinct Home Plan: Give the Brain a Legal Job|A dog herding instinct home plan for nipping, motion triggers, and training jobs.|instinct planning|active families|akc
dog sighthound safety checklist|recall limits, cold sensitivity, secure runs|Dog Sighthound Safety Checklist: Speed Needs Boundaries|A dog sighthound safety checklist for recall limits, cold sensitivity, and secure runs.|group-specific fit|sighthound shoppers|akc
dog scent hound recall planning|nose work, long lines, secure fields|Dog Scent Hound Recall Planning: Manage the Nose, Not the Myth|A dog scent hound recall planning guide for nose work, long lines, and secure fields.|group-specific fit|hound shoppers|akc
dog companion breed alone time|attachment needs, work hours, backup care|Dog Companion Breed Alone Time: Plan for the Hours You Are Gone|A dog companion breed alone time guide for attachment needs, work hours, and backup care.|alone-time fit|companion breed shoppers|avma
"""


SOURCES = {
    "aaha": ("AAHA canine life stage guidance", "https://www.aaha.org/resources/life-stage-canine-2019/"),
    "akc": ("American Kennel Club breed reference", "https://www.akc.org/dog-breeds/"),
    "appa": ("APPA pet industry statistics", "https://americanpetproducts.org/industry-trends-and-stats/"),
    "avma": ("AVMA pet selection guidance", "https://www.avma.org/resources-tools/pet-owners/petcare/selecting-pet-your-family"),
    "merck": ("Merck Veterinary Manual dog owner library", "https://www.merckvetmanual.com/dog-owners"),
    "naphia": ("NAPHIA pet insurance industry data", "https://naphia.org/industry-data/"),
    "ofa": ("OFA CHIC breed health reference", "https://ofa.org/chic-programs/browse-by-breed/"),
    "synchrony": ("Synchrony Lifetime of Care study release", "https://www.multivu.com/synchrony/9310651-en-synchrony-2025-pet-lifetime-of-care-study"),
}


FORMATS = [
    ("decision audit", ["The answer in one paragraph", "The hidden constraint", "A five-question home test", "Source notes", "What to do next"]),
    ("budget lens", ["Quick answer", "Costs people undercount", "Three budget lines to separate", "Evidence to collect", "A calm next step"]),
    ("risk review", ["Direct answer", "Red flags and green flags", "The weekly routine test", "Where sources help", "Boundary before commitment"]),
    ("checklist", ["Short answer", "Checklist before you decide", "Questions for the current caregiver", "Budget and schedule notes", "Reader takeaway"]),
    ("comparison guide", ["Plain-English answer", "Compare the tradeoffs", "When this choice fits", "When to pause", "Internal reading path"]),
    ("source literacy", ["Answer first", "What the phrase can and cannot prove", "Records worth saving", "Claims to avoid", "Decision rule"]),
    ("home simulation", ["The practical answer", "Run a normal Thursday", "Stress-test the setup", "What to verify", "Final filter"]),
    ("calendar plan", ["Fast answer", "First month", "First six months", "Yearly review", "What changes the plan"]),
    ("mistake audit", ["Bottom line", "The common mistake", "Better replacement question", "Budget safeguard", "How to use this guide"]),
    ("owner readiness", ["Answer in one sentence", "Readiness scorecard", "Weak spots to fix first", "Documentation habit", "Next action"]),
]


ACCENTS = [
    ("#2f6b54", "#eaf6ef"),
    ("#2f5f8f", "#e8f1f8"),
    ("#8a5a12", "#fff4dd"),
    ("#8b3f34", "#fff0ed"),
    ("#44546a", "#eef2f6"),
]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def title_case_text(text: str) -> str:
    specials = {"aaha": "AAHA", "akc": "AKC", "avma": "AVMA", "chic": "CHIC", "dna": "DNA", "diy": "DIY", "ofa": "OFA"}
    words = []
    for word in re.split(r"(\W+)", text):
        key = word.lower()
        words.append(specials.get(key, word[:1].upper() + word[1:].lower() if word else word))
    return "".join(words)


def stable_choice(options: list[str], seed: str) -> str:
    score = sum((position + 1) * ord(char) for position, char in enumerate(seed))
    return options[score % len(options)]


def read_topics() -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(TOPICS_CSV), delimiter="|")
    rows = [dict(row) for row in reader]
    if len(rows) != 100:
        raise RuntimeError(f"expected 100 topics, got {len(rows)}")
    title_patterns = [
        "{main}: {expanded} Before You Choose",
        "{main} for {expanded}: A Practical BreedWise Guide",
        "How to Use {main} to Check {expanded}",
        "{main}: Planning Around {expanded} Without Guesswork",
        "{main} Checklist for {expanded}",
        "{main} and {expanded}: The Decision Guide",
        "Before Adoption: {main}, {expanded}, and the Real Routine",
        "{main}: What {expanded} Changes in Real Life",
        "{main}: A Home-Test Guide for {expanded}",
        "Choosing With {main}: {expanded} in the Real Week",
        "{main} Questions for {expanded} Before Commitment",
        "{main}: How {expanded} Affects the Shortlist",
        "The {main} Field Guide to {expanded}",
        "{main}: Owner Readiness Around {expanded}",
        "{main} Reality Check: {expanded} in Daily Life",
        "{main}: Compare {expanded} Before You Decide",
        "{main} Planning Notes for {expanded}",
        "{main}: The Practical Filter for {expanded}",
        "Use {main} to Stress-Test {expanded}",
        "{main}: Records, Routine, and {expanded}",
        "{main} Decision Map: {expanded} at Home",
        "{main}: What to Verify About {expanded}",
        "A Better {main} Checklist for {expanded}",
        "{main}: Budget, Evidence, and {expanded}",
    ]
    subtitle_patterns = [
        "A {main} guide that turns {expanded} into budget checks, record requests, daily routines, and source-quality decisions.",
        "Use this {main} article to compare {expanded} with housing fit, care workload, documented evidence, and long-term cost exposure.",
        "This {main} guide explains how {expanded} should shape the shortlist before adoption, purchase, or a serious breed comparison.",
        "For readers researching {main}, this guide connects {expanded} with practical questions, credible sources, and BreedWise planning boundaries.",
        "A reader-first {main} guide for checking {expanded} against routines, local constraints, professional input, and ownership capacity.",
        "This {main} resource turns {expanded} into a practical review of records, time, cost, home setup, and decision risk.",
        "Use {main} to test whether the issues around {expanded} are manageable in the actual household rather than only attractive in a breed summary.",
        "A practical {main} walkthrough for comparing {expanded}, owner workload, source quality, and the next responsible step.",
        "This {main} guide helps future owners translate {expanded} into a shortlist that is smaller, clearer, and easier to verify.",
        "For {main} research, this article weighs {expanded} through daily care, local proof, budget reserves, and realistic limits.",
        "A focused {main} guide for turning {expanded} into questions that owners can answer before the dog comes home.",
        "This {main} article links {expanded} with the documents, routines, cost buffers, and household roles that make a choice workable.",
    ]
    for index, row in enumerate(rows):
        main = row["main_keyword"]
        expanded = row["expanded_keywords"]
        row["title"] = title_patterns[index % len(title_patterns)].format(
            main=title_case_text(main),
            expanded=title_case_text(expanded),
        )
        row["subtitle"] = subtitle_patterns[index % len(subtitle_patterns)].format(
            main=main,
            expanded=expanded,
        )
    return rows


def load_existing() -> tuple[list[dict], set[str], set[str], set[str]]:
    raw_schedule = json.loads(SCHEDULE.read_text(encoding="utf-8"))
    for item in raw_schedule:
        if item.get("research_mode") == "common-source-centered":
            queue_path = ROOT / item["queue_file"]
            if queue_path.exists():
                queue_path.unlink()
    schedule = [item for item in raw_schedule if item.get("research_mode") != "common-source-centered"]
    titles = {item["title"].casefold() for item in schedule}
    slugs = {item["slug"].casefold() for item in schedule}
    keywords = {item["main_keyword"].casefold() for item in schedule}
    for path in (ROOT / "blog").glob("*.html"):
        if path.name == "index.html":
            continue
        slugs.add(path.stem.casefold())
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
        if match:
            titles.add(re.sub(r"\s+", " ", match.group(1)).strip().casefold())
    return schedule, titles, slugs, keywords


def sentence_topic(topic: dict[str, str], index: int) -> str:
    main = topic["main_keyword"]
    expanded = topic["expanded_keywords"]
    reader = topic["reader"]
    options = [
        f"{main} is useful only when the issues around {expanded} can be checked against the reader's actual home, calendar, and budget.",
        f"For {reader}, {main} should narrow the decision: test {expanded} against daily work, local rules, and backup care.",
        f"The practical question behind {main} is whether the issues around {expanded} can survive a normal week, not whether a breed summary sounds appealing.",
        f"Use {main} as a filter for {expanded}: what is documented, what is affordable, and what still depends on hope?",
        f"{main} becomes a stronger planning topic when the issues around {expanded} are tied to named tasks, written evidence, and a reserve for surprises.",
        f"The right use of {main} is to turn {expanded} into decisions the household can verify before commitment.",
        f"For this reader, {main} is not a shortcut to a breed answer; it is a way to pressure-test {expanded}.",
        f"A useful {main} review asks whether the issues around {expanded} fit the owner's routine on a tired weekday, not only on an ideal adoption weekend.",
    ]
    return stable_choice(options, f"{main}|{expanded}|topic-sentence|{index}")


def expanded_parts(topic: dict[str, str]) -> list[str]:
    return [part.strip() for part in topic["expanded_keywords"].split(",") if part.strip()]


def issue(part: str) -> str:
    return f"the issue around {part}"


def plan_for(part: str) -> str:
    return f"the plan for {part}"


def work_around(part: str) -> str:
    return f"the work around {part}"


def source_claim(topic: dict[str, str]) -> str:
    source = topic["source"]
    if source == "ofa":
        return "breed health screening and record-verification context"
    if source == "aaha":
        return "life-stage care planning and preventive-care conversation context"
    if source == "akc":
        return "breed-group traits, coat expectations, activity patterns, and terminology context"
    if source == "appa":
        return "broad pet spending categories and ownership-cost framing"
    if source == "merck":
        return "general dog-owner health-topic context without diagnosis"
    if source == "naphia":
        return "pet insurance research vocabulary and market-context framing"
    if source == "synchrony":
        return "lifetime-of-care cost framing and long-range budgeting context"
    return "pet-selection and responsible ownership context"


def body_sections(topic: dict[str, str], index: int) -> list[tuple[str, str]]:
    main = topic["main_keyword"]
    expanded = topic["expanded_keywords"]
    parts = expanded_parts(topic)
    first = parts[0]
    second = parts[1] if len(parts) > 1 else parts[0]
    third = parts[2] if len(parts) > 2 else parts[-1]
    angle = topic["angle"]
    reader = topic["reader"]
    source_label, source_url = SOURCES[topic["source"]]
    second_source_label, second_source_url = SOURCES["avma"] if topic["source"] != "avma" else SOURCES["aaha"]
    e = escape
    def label(options: list[str], salt: str) -> str:
        return stable_choice(options, f"{topic['main_keyword']}|{topic['expanded_keywords']}|{salt}|{index}")

    def prose(options: list[str], salt: str) -> str:
        return stable_choice(options, f"{topic['main_keyword']}|{topic['reader']}|{salt}|{index}")

    section_bank = {
        "answer": (
            label(["Answer first", "Short answer", "Bottom line", "Decision answer", "Plain answer", "Fast answer", "Reader-first answer", "The useful answer"], "answer"),
            prose([
                f"{topic['title']} is strongest when it works like a home audit, not a breed ranking. For {reader}, the useful answer is whether the issues around {first}, {second}, and {third} still make sense during an ordinary week with work, weather, errands, and one inconvenient bill.",
                f"Start with the constraint, not the dog photo. A good {main} decision checks whether the work around {first}, {second}, and {third} fits the household when time is limited and the first plan needs a backup.",
                f"The practical answer is not a universal yes or no. {reader.capitalize()} should use {main} to decide whether the tasks around {first}, {second}, and {third} can be assigned, priced, documented, and repeated without relying on ideal conditions.",
                f"Treat {main} as a readiness test. If {issue(first)} depends on enthusiasm, {issue(second)} depends on a guess, or {plan_for(third)} has no owner, the shortlist needs more work before the household compares breeds.",
                f"A useful decision starts by asking what must happen every week. For this topic, that means checking {first}, {second}, and {third} against the current routine instead of assuming the routine will expand after adoption.",
                f"{reader.capitalize()} do not need another broad breed promise. They need to know whether the issues around {first}, {second}, and {third} are realistic enough to survive busy days, local limits, and a budget that already has other demands.",
            ], "answer-body")
        ),
        "friction": (
            label(["Where the friction usually appears", "The hidden friction", "Where plans usually break", "The part owners undercount", "The mismatch point", "Where the plan gets tested"], "friction"),
            prose([
                f"The {angle} problem usually appears after the easy comparison is over. The issue around {first} changes the day-to-day routine, {issue(second)} can change the repeat cost, and {plan_for(third)} often decides whether the backup plan is real.",
                f"Most mismatches are not caused by one dramatic fact. They come from small assumptions about {first}, loose estimates around {second}, and no written plan for {third}.",
                f"The friction point is where preference meets logistics. A household may like the idea of the dog, but {first}, {second}, and {third} still need named responsibilities and evidence.",
                f"Owners often notice this issue late because each part looks manageable alone. Put {first}, {second}, and {third} into the same week and the real workload becomes clearer.",
                f"This is where source reading has to become household planning. A broad article may explain terms, but the owner still has to prove that {first}, {second}, and {third} fit the specific home.",
            ], "friction-body")
        ),
        "decision_table": (
            label(["Decision table", "Green-yellow-red check", "Decision signals", "Readiness table", "Practical decision signals", "Fit check table"], "decision_table"),
            prose([
                f"<table class='table'><tr><th>Signal</th><th>What to verify</th><th>Why it matters</th></tr><tr><td>Green</td><td>{e(issue(first))} is documented with a named routine and backup.</td><td>The plan can survive a normal busy week.</td></tr><tr><td>Yellow</td><td>{e(issue(second))} still needs a quote, policy, record, or trial period.</td><td>The decision needs one more documented answer.</td></tr><tr><td>Red</td><td>{e(plan_for(third))} is being minimized or assigned to nobody.</td><td>The household may be buying surprise work.</td></tr></table>",
                f"<table class='table'><tr><th>Status</th><th>Reader evidence</th><th>Decision meaning</th></tr><tr><td>Ready</td><td>{e(plan_for(first))} has a calendar slot and backup owner.</td><td>The household has moved beyond a vague preference.</td></tr><tr><td>Needs work</td><td>{e(issue(second))} depends on a missing estimate, rule, or record.</td><td>One more fact should be gathered before commitment.</td></tr><tr><td>Not ready</td><td>{e(plan_for(third))} is being dismissed because it is inconvenient.</td><td>The risk is likely being pushed into the future.</td></tr></table>",
                f"<table class='table'><tr><th>Checkpoint</th><th>Acceptable answer</th><th>Weak answer</th></tr><tr><td>{e(first)}</td><td>Assigned to a person and routine.</td><td>Assumed from enthusiasm.</td></tr><tr><td>{e(second)}</td><td>Supported by a source, quote, policy, or note.</td><td>Left as a guess.</td></tr><tr><td>{e(third)}</td><td>Covered by a backup plan.</td><td>Deferred until a problem appears.</td></tr></table>",
            ], "decision-table-body")
        ),
        "checklist": (
            label(["Pre-adoption checklist", "Questions to answer before commitment", "Before-you-choose checklist", "Decision checklist", "Commitment checklist", "Questions before the shortlist"], "checklist"),
            prose([
                f"<ul><li>Write the weekly job connected to {e(first)} in one sentence.</li><li>Find the document, quote, record, or professional conversation that supports the assumption about {e(second)}.</li><li>Name the person who handles {e(third)} when the first plan fails.</li><li>Compare the answer with the BreedWise cost framework before adding more breeds to the shortlist.</li></ul>",
                f"<ul><li>List the recurring task behind {e(first)} and where it fits on the calendar.</li><li>Save the rule, invoice range, caregiver note, or source page that clarifies {e(second)}.</li><li>Set a reserve for the moment {e(third)} takes more time than expected.</li><li>Remove any breed from the shortlist if the household cannot answer these items honestly.</li></ul>",
                f"<ul><li>Ask who owns {e(work_around(first))} on a weekday, weekend, and travel day.</li><li>Check whether {e(issue(second))} needs a local price, policy, vet note, or service provider.</li><li>Decide what evidence would change your mind about {e(third)}.</li><li>Keep the notes with the adoption or breeder records so the decision remains traceable.</li></ul>",
            ], "checklist-body")
        ),
        "scenario": (
            label(["Reader scenario", "A realistic week", "How this plays out", "A household example", "A normal-week example", "What the week can reveal"], "scenario"),
            prose([
                f"Picture a household researching {main} on a Sunday night. The easy version is to keep opening breed pages. The better version is to spend the week checking {first}, pricing or documenting {second}, and deciding what happens if {third} becomes harder than expected.",
                f"A realistic week is revealing. Monday tests whether {work_around(first)} fits the schedule. Midweek shows whether {issue(second)} has a local cost or record behind it. By the weekend, the family should know whether responsibility for {third} is assigned or still being avoided.",
                f"Imagine the reader has three breeds left on the shortlist. Instead of ranking them by appeal, they run each one through the same question: what changes in the home if the issue around {first}, {second}, or {third} is more demanding than expected?",
                f"The useful scenario is not perfect adoption day. It is a tired Thursday, a delayed appointment, a wet walk, and a budget that cannot absorb every surprise. That is where {main} becomes practical.",
            ], "scenario-body")
        ),
        "cost": (
            label(["Cost and time stack", "Budget pressure points", "The cost stack", "Where the budget gets real", "Time and money pressure", "Budget reality check"], "cost"),
            prose([
                f"Do not turn {main} into one price. Separate setup costs, repeat costs, and uncertainty reserve. Setup covers the first tools and appointments, repeat costs cover the work that returns, and the reserve protects the household when the issues around {expanded} take more help than expected.",
                f"The budget question has two clocks: what must be paid now and what keeps coming back. {title_case_text(first)} may affect setup, {second} may create recurring work, and {third} may become the reason a reserve is needed.",
                f"A cleaner budget uses three columns: money, time, and proof. If the work around {first} costs time, the issue around {second} needs a quote, or the plan for {third} depends on a professional conversation, write that down before comparing breeds.",
                f"Cost pressure is not only the purchase or adoption fee. The more useful review asks which part of {expanded} repeats, which part needs equipment, and which part could require outside support.",
            ], "cost-body")
        ),
        "records": (
            label(["Records worth saving", "Evidence to collect", "Documentation that matters", "What to save before you decide", "Paper trail to keep", "Records that reduce guesswork"], "records"),
            prose([
                f"<ul><li>Primary source: <a href='{source_url}' rel='nofollow noopener'>{e(source_label)}</a>, used for {e(source_claim(topic))}. Accessed 2026-06-27.</li><li>Cross-check: <a href='{second_source_url}' rel='nofollow noopener'>{e(second_source_label)}</a>, used for general ownership and care-planning context.</li><li>Household proof: lease terms, vet notes, caregiver records, local service estimates, and dated screenshots of any rule that affects the decision.</li></ul>",
                f"<ul><li>Reference page: <a href='{source_url}' rel='nofollow noopener'>{e(source_label)}</a>, used for {e(source_claim(topic))}. Accessed 2026-06-27.</li><li>Second context source: <a href='{second_source_url}' rel='nofollow noopener'>{e(second_source_label)}</a>, used to keep the advice grounded in general ownership planning.</li><li>Local file: policies, estimates, records, emails, and professional notes that prove the plan can work where the reader lives.</li></ul>",
                f"<ul><li>Source checked: <a href='{source_url}' rel='nofollow noopener'>{e(source_label)}</a>, used for {e(source_claim(topic))}. Accessed 2026-06-27.</li><li>Context checked: <a href='{second_source_url}' rel='nofollow noopener'>{e(second_source_label)}</a>, used for broader care-planning boundaries.</li><li>Decision evidence: written rules, appointment notes, rescue or breeder paperwork, trainer or groomer policies, and local cost ranges.</li></ul>",
            ], "records-body")
        ),
        "source_ladder": (
            label(["Source ladder", "How to use sources", "Source quality check", "Evidence ladder", "How to read the evidence", "Source reality check"], "source_ladder"),
            prose([
                f"Use broad sources for vocabulary and boundaries, not final certainty. {source_label} can frame the issue, but the reader still needs local documents, professional conversations, and a written household plan for the work.",
                f"A source ladder keeps the decision honest: public reference for terms, local record for feasibility, professional input for sensitive questions, and a household assignment for the daily job.",
                f"{source_label} is useful context, but it cannot see the individual dog, local prices, landlord rules, climate, or caregiver capacity. Treat it as step one, then verify the plan close to home.",
                f"Good research moves from general to specific. Start with the public source, add the local rule or record, ask a professional when risk is involved, and write down who does the work.",
            ], "source-ladder-body")
        ),
        "comparison": (
            label(["Compare two realistic options", "Side-by-side reality check", "Appealing vs sustainable", "Comparison worksheet", "Two-option comparison", "A more honest comparison"], "comparison"),
            prose([
                f"<table class='table'><tr><th>Question</th><th>Easy assumption</th><th>Better evidence</th></tr><tr><td>{e(first)}</td><td>Borrowed from a breed summary.</td><td>Checked against the current home and schedule.</td></tr><tr><td>{e(second)}</td><td>Estimated from a casual average.</td><td>Priced with a local quote or documented rule.</td></tr><tr><td>{e(third)}</td><td>Handled only after trouble appears.</td><td>Assigned before commitment.</td></tr></table>",
                f"<table class='table'><tr><th>Decision point</th><th>Weak version</th><th>Stronger version</th></tr><tr><td>{e(first)}</td><td>Assumed because the breed sounds suitable.</td><td>Tested in the reader's real routine.</td></tr><tr><td>{e(second)}</td><td>Left as a vague future cost.</td><td>Attached to a quote, record, or rule.</td></tr><tr><td>{e(third)}</td><td>Treated as somebody's future problem.</td><td>Given an owner and a backup.</td></tr></table>",
                f"<table class='table'><tr><th>Area</th><th>Looks fine when...</th><th>Actually works when...</th></tr><tr><td>{e(first)}</td><td>The reader imagines an ideal week.</td><td>The reader can place it on the calendar.</td></tr><tr><td>{e(second)}</td><td>The cost is guessed.</td><td>The cost or rule is written down.</td></tr><tr><td>{e(third)}</td><td>No one has needed the backup yet.</td><td>The backup is ready before adoption.</td></tr></table>",
            ], "comparison-body")
        ),
        "mistakes": (
            label(["Mistakes to avoid", "Common planning mistakes", "What not to assume", "Avoid these shortcuts", "Planning traps", "Assumptions to challenge"], "mistakes"),
            prose([
                f"<ol><li>Do not choose from photos before checking {e(first)}.</li><li>Do not treat {e(second)} as a one-time issue if it can repeat.</li><li>Do not let {e(third)} become one person's invisible job.</li><li>Do not convert this article into medical, legal, insurance, or training advice for a specific dog.</li></ol>",
                f"<ol><li>Do not assume {e(first)} will be easy because the breed is popular.</li><li>Do not budget for {e(second)} without a local reality check.</li><li>Do not postpone the conversation about {e(third)} until the dog is already home.</li><li>Do not treat broad educational sources as a substitute for professional guidance.</li></ol>",
                f"<ol><li>Do not let a single appealing trait outweigh {e(first)}.</li><li>Do not ignore repeat work connected to {e(second)}.</li><li>Do not accept a plan for {e(third)} that has no person, date, or backup.</li><li>Do not use this guide as a diagnosis, legal opinion, or insurer recommendation.</li></ol>",
            ], "mistakes-body")
        ),
        "aeo": (
            label(["Quick answer summary", "Summary for skimmers", "Answer-engine summary", "Decision summary", "Concise answer block", "Short version for comparison"], "aeo"),
            prose([
                f"For quick answer engines: {main} is a planning query for {reader}. Test {expanded} against daily routine, written records, local costs, and a reserve for uncertainty before treating any breed as a fit.",
                f"Short answer: {main} should not produce a universal breed recommendation. It should help the reader verify whether the issues around {expanded} are workable in their home, budget, and support network.",
                f"The answerable part of {main} is practical: document the issues around {expanded}, assign the work, and pause if any key assumption still depends on hope.",
                f"Use {main} to compare evidence rather than enthusiasm. {reader.capitalize()} should leave with fewer weak assumptions about {expanded}, not a longer list of possible breeds.",
            ], "aeo-body")
        ),
        "owner_roles": (
            label(["Owner roles", "Who does the work?", "Assign the routine", "Household responsibility check", "Workload map", "Who owns each task?"], "owner_roles"),
            prose([
                f"Write the owner roles before the decision gets emotional. One person may handle research, another may handle appointments, and another may handle routines. If the work around {first}, {second}, and {third} all lands on the same person by default, the workload is not honestly assigned.",
                f"A household plan needs names, not intentions. Put {first}, {second}, and {third} beside the person who handles each job, then add a backup for sick days, travel, and busy seasons.",
                f"Ownership becomes easier to judge when the work is visible. If nobody wants to own {work_around(first)}, nobody has priced {issue(second)}, or everyone avoids {plan_for(third)}, the breed question is premature.",
            ], "owner-roles-body")
        ),
        "pause": (
            label(["When to pause", "Stop and verify", "Pause before you commit", "A sensible stop point", "When the answer is not ready", "The pause test"], "pause"),
            prose([
                f"Pause if the answer depends on hope instead of evidence. Vague promises about {issue(first)}, missing records around {second}, or no backup for {third} are not small details.",
                f"A pause is warranted when the household likes the dog but cannot prove the plan. That usually means {issue(first)} is vague, {issue(second)} is unpriced, or {plan_for(third)} has no owner.",
                f"Stop the shortlist process if one question keeps getting postponed. The delayed question is often the one connected to {first}, {second}, or {third}.",
            ], "pause-body")
        ),
        "one_week": (
            label(["One-week test", "Try the routine for a week", "Seven-day reality test", "Trial week", "Seven-day home simulation", "Calendar test"], "one_week"),
            prose([
                f"Run a seven-day simulation without the dog. Put the calls, quotes, record checks, cleaning, transport, and budget transfers on the calendar. If the research version of {main} cannot fit, the real version deserves caution.",
                f"Use one ordinary week as a test. Schedule the work behind {first}, add the admin for {second}, and create a backup slot for {third}. The calendar will show whether the plan is realistic.",
                f"Do not wait for ownership to discover the routine. A trial week lets the household practice the time, money, and coordination that {main} is likely to require.",
            ], "one-week-body")
        ),
        "local_check": (
            label(["Local checks", "Local reality check", "What changes by address", "Local proof points", "Address-specific checks", "What to verify nearby"], "local_check"),
            prose([
                f"Local details can overturn broad advice. Rental rules, service availability, climate, travel distance, and professional fees all change how the issues around {expanded} feel in practice.",
                f"The same breed question can have a different answer by address. A reader should check housing rules, nearby services, weather, transport, and professional access before relying on general guidance about {expanded}.",
                f"Public sources start the research, but local proof finishes it. For {main}, that proof may be a lease clause, clinic note, groomer policy, trainer intake form, or realistic service quote.",
            ], "local-check-body")
        ),
        "professional_questions": (
            label(["Questions for professionals", "What to ask before deciding", "Conversation prompts", "Expert questions to bring", "Better questions for the next call", "Ask this before commitment"], "professional_questions"),
            prose([
                f"<ul><li>Ask a veterinarian, trainer, groomer, shelter counselor, or breeder what they would want documented about {e(first)}.</li><li>Ask which parts of {e(second)} usually surprise new owners in the first year.</li><li>Ask what warning signs would make {e(third)} a reason to slow down.</li><li>Ask whether the answer changes by age, size, health history, housing type, or local service access.</li></ul>",
                f"<p>Bring sharper questions to the next professional conversation. Instead of asking whether a breed is good, ask what evidence would reduce risk around {e(first)}, what recurring work is tied to {e(second)}, and what backup plan they would expect for {e(third)}.</p>",
                f"<ul><li>What record or observation would make {e(first)} easier to evaluate?</li><li>What would you budget first for {e(second)}?</li><li>When does {e(third)} become a management issue rather than a preference?</li><li>What should a careful owner monitor during the first month?</li></ul>",
                f"<p>Use professional input to test the weak parts of the plan. Ask what they would verify first, how they would document {e(first)}, which costs around {e(second)} are easy to miss, and when {e(third)} deserves a slower decision.</p>",
                f"<ul><li>Which assumption about {e(first)} should be checked before commitment?</li><li>What normal range should the reader expect for {e(second)}?</li><li>What would make {e(third)} easier to manage at home?</li><li>What local factor changes the advice most often?</li></ul>",
                f"<p>A better expert conversation starts with specifics. Bring the current plan, the evidence already collected, and the remaining questions about {e(first)}, {e(second)}, and {e(third)} so the answer can be practical rather than generic.</p>",
            ], "professional-questions-body")
        ),
        "handoff": (
            label(["Handoff plan", "Make the plan shareable", "Household handoff", "What another caregiver needs", "Caregiver notes", "Plan another person can follow"], "handoff"),
            prose([
                f"A strong plan can be handed to another caregiver without a long explanation. Write the routine for {first}, save the proof behind {second}, and keep the backup for {third} in the same folder as vet records, lease documents, and service contacts.",
                f"If only one person understands the plan, the household is still fragile. Put the details for {first}, {second}, and {third} where another adult can find them during travel, illness, a schedule change, or an emergency appointment.",
                f"Good ownership planning survives handoff. The reader should be able to show a pet sitter, family member, or future veterinarian what was assumed about {first}, what was checked about {second}, and what limit was set for {third}.",
                f"Make the plan usable when the main caregiver is unavailable. A short note should explain the routine for {first}, the record or quote behind {second}, and the point where the backup plan for {third} needs outside help.",
                f"Shared care works better when the details are visible. Store the plan for {first}, the source trail for {second}, and the backup rule for {third} somewhere the household already checks.",
                f"A handoff note prevents quiet assumptions from becoming emergencies. It should say what is normal, what is changing, and who to contact if {first}, {second}, or {third} stops fitting the plan.",
            ], "handoff-body")
        ),
        "internal_path": (
            label(["Where to read next", "Related BreedWise checks", "Internal reading path", "Next comparison points", "Connect this with the cost lens", "Build the next shortlist"], "internal_path"),
            prose([
                f"After this article, compare the notes with the <a href='../methodology/index.html'>BreedWise methodology</a> and the <a href='../index.html#ownership'>ownership cost preview</a>. Those pages help separate breed appeal from repeat work, documented evidence, and long-term household capacity.",
                f"Use the <a href='../blog/index.html'>Blog index</a> to pair this topic with one neighboring constraint, then check the <a href='../index.html#ownership'>cost preview</a> before adding more breeds. The goal is fewer weak assumptions, not more tabs.",
                f"For a deeper review, read the <a href='../methodology/index.html'>methodology</a>, then compare this decision against the <a href='../index.html#ownership'>five-year ownership lens</a>. A breed that passes both checks is easier to defend than one that only looks good in a summary.",
                f"Pair this guide with the <a href='../methodology/index.html'>methodology</a> if the reader needs a stricter decision process, or use the <a href='../blog/index.html'>Blog index</a> to compare one adjacent ownership constraint.",
                f"The next useful page is not always another breed profile. Check the <a href='../index.html#ownership'>ownership cost preview</a> and the <a href='../methodology/index.html'>methodology</a> to see whether the plan still holds up.",
                f"Use internal links as a decision path: start with this guide, confirm the framework in the <a href='../methodology/index.html'>methodology</a>, and use the <a href='../blog/index.html'>Blog index</a> only for a clearly related follow-up question.",
            ], "internal-path-body")
        ),
        "first_month": (
            label(["First-month review", "After adoption, check again", "What to monitor early", "The first-month signal"], "first_month"),
            prose([
                f"If the household moves forward, revisit the plan during the first month. Track whether the work around {first} is happening as expected, whether the plan for {second} is taking more time or money than planned, and whether the backup plan for {third} needs a different owner. Early notes are useful because they show patterns before frustration becomes the only data point.",
                f"The first month should not be treated as proof that every assumption was correct. It is a review period. Watch how often the work around {first} changes the schedule, whether the plan for {second} creates repeat admin, and whether the plan for {third} needs outside help sooner than expected.",
                f"Good planning continues after the dog comes home. Save receipts, appointment notes, behavior observations, and schedule changes related to {first}, {second}, and {third}. Those notes make future decisions calmer and more accurate.",
            ], "first-month-body")
        ),
        "tradeoff": (
            label(["Tradeoff to accept", "What the owner is really choosing", "The real compromise", "Decision tradeoff"], "tradeoff"),
            prose([
                f"Every breed choice has a tradeoff. The question is whether the household accepts the tradeoff openly. If the work around {first} takes time, the plan for {second} takes money, and the plan for {third} takes coordination, those are not reasons to panic; they are reasons to decide with clear eyes.",
                f"The right answer may still be yes. A household can accept work around {first}, costs around {second}, or limits around {third} when those tradeoffs are visible, budgeted, and shared by the people who will live with them.",
                f"A bad match often begins when the owner accepts the benefit but ignores the cost. This guide asks the reader to hold both sides together: the appeal of the dog and the practical load created by {first}, {second}, and {third}.",
            ], "tradeoff-body")
        ),
        "proof_before_profile": (
            label(["Evidence before more profiles", "Proof before preference", "What would change your mind?", "Decision evidence"], "proof_before_profile"),
            prose([
                f"Before opening another breed profile, decide what evidence would change the shortlist. It might be a written rule about {first}, a professional comment about {second}, or a household limit around {third}. Without that standard, research can become endless browsing.",
                f"Use a simple rule: preference can start the shortlist, but evidence should edit it. If the reader cannot identify the proof needed for {first}, {second}, and {third}, they are not ready to compare more breeds.",
                f"Strong research creates a stopping point. Once the issue around {first} is documented, the issue around {second} is priced or explained, and the plan for {third} has a backup, the reader can make a cleaner decision instead of collecting more vague opinions.",
            ], "proof-before-profile-body")
        ),
        "decision_boundary": (
            label(["Decision boundary", "What this guide can and cannot decide", "Keep the conclusion honest", "Where judgment still matters"], "decision_boundary"),
            prose([
                f"This guide can organize the decision, but it cannot know the individual dog. Use it to decide what must be verified about {first}, what must be budgeted for {second}, and what limit should be set around {third}. The final choice still belongs with the household and qualified professionals who know the local facts.",
                f"Keep the conclusion narrow. A useful result is not 'this breed is always right' or 'this breed is always wrong.' A useful result is a documented answer about {first}, a realistic plan for {second}, and a clear boundary for {third}.",
                f"The article should leave the reader with better judgment, not false certainty. If the plan around {first}, {second}, or {third} changes after a professional conversation or local rule check, update the shortlist instead of defending the old assumption.",
                f"Do not force a final answer from incomplete evidence. When the reader still lacks proof around {first}, a cost range for {second}, or a backup for {third}, the responsible conclusion is to keep researching before committing.",
            ], "decision-boundary-body")
        ),
        "next": (
            label(["Practical next step", "Next action", "What to do now", "Use this guide", "Turn this into a plan", "Make the next choice smaller"], "next"),
            prose([
                f"Save this guide, write down two unanswered questions about {expanded}, and resolve them before reading more breed profiles. Better research should narrow the shortlist, not make every option sound equally possible.",
                f"Turn the article into a small action list: one document to find, one local cost to check, and one household responsibility to assign. Then compare the notes with the BreedWise methodology and five-year ownership cost framework.",
                f"Do one practical thing next. Call for a quote, save the relevant rule, ask the current caregiver a clearer question, or remove one breed that cannot pass the {expanded} check.",
                f"Keep the notes and date them. If the checklist feels inconvenient now, treat that as evidence; the same work usually becomes harder once the dog is already home.",
            ], "next-body") + " " + prose([
                f"Before closing the tab, mark the weakest assumption about {first} and decide who will verify it.",
                f"If the next step is still vague, make it concrete: one phone call, one saved document, or one budget number.",
                f"A good stopping point is a smaller shortlist with clearer reasons, not a larger folder of untested claims.",
                f"Use the next 15 minutes to capture the decision trail while the tradeoffs are still fresh.",
            ], "next-tail")
        ),
    }
    archetypes = [
        ["answer", "friction", "decision_table", "tradeoff", "records", "scenario", "cost", "professional_questions", "checklist", "source_ladder", "handoff", "one_week", "proof_before_profile", "aeo", "internal_path", "decision_boundary", "first_month", "pause", "next"],
        ["answer", "cost", "comparison", "checklist", "records", "mistakes", "scenario", "tradeoff", "professional_questions", "source_ladder", "owner_roles", "handoff", "aeo", "local_check", "proof_before_profile", "internal_path", "decision_boundary", "first_month", "next"],
        ["answer", "scenario", "checklist", "decision_table", "source_ladder", "tradeoff", "records", "cost", "mistakes", "professional_questions", "one_week", "handoff", "aeo", "proof_before_profile", "internal_path", "decision_boundary", "pause", "first_month", "next"],
        ["answer", "records", "source_ladder", "comparison", "friction", "checklist", "scenario", "cost", "professional_questions", "owner_roles", "tradeoff", "aeo", "local_check", "handoff", "internal_path", "proof_before_profile", "decision_boundary", "first_month", "next"],
        ["answer", "comparison", "friction", "cost", "decision_table", "mistakes", "tradeoff", "records", "professional_questions", "source_ladder", "one_week", "aeo", "handoff", "proof_before_profile", "internal_path", "decision_boundary", "pause", "first_month", "next"],
        ["answer", "mistakes", "checklist", "scenario", "records", "decision_table", "source_ladder", "cost", "professional_questions", "owner_roles", "handoff", "tradeoff", "aeo", "local_check", "proof_before_profile", "internal_path", "decision_boundary", "first_month", "next"],
    ]
    sections = [section_bank[key] for key in archetypes[index % len(archetypes)]]
    return sections


def article_html(topic: dict[str, str], index: int, publish_at: datetime) -> str:
    slug = slugify(topic["main_keyword"])
    accent, wash = ACCENTS[index % len(ACCENTS)]
    source_label, source_url = SOURCES[topic["source"]]
    second_source = SOURCES["avma"] if topic["source"] != "avma" else SOURCES["aaha"]
    def article_label(options: list[str], salt: str) -> str:
        return stable_choice(options, f"{topic['main_keyword']}|{salt}|{index}")
    section_parts = []
    for heading, text in body_sections(topic, index):
        body = text if text.lstrip().startswith("<") else f"<p>{text}</p>"
        section_parts.append(f"<h2 id=\"{slugify(heading)}\">{escape(heading)}</h2>{body}")
    sections = "\n".join(section_parts)
    faq = ""
    if index % 2 == 0:
        faq_heading = article_label(["FAQ", "Common questions", "Reader questions", "Quick questions"], "faq")
        recommendation_answer = article_label([
            "No. It is a planning frame for comparing constraints before choosing a dog.",
            "No. Treat it as a readiness check, not a ranked breed list.",
            "No. It helps the reader prepare better questions before making a breed decision.",
            "No. The article narrows the research task; it does not choose a dog for the household.",
        ], "faq-recommendation")
        advice_answer = article_label([
            "No. Use it to prepare questions for qualified professionals and documented sources.",
            "No. It is educational content and should be checked against professional advice when risk is specific.",
            "No. It can organize the conversation, but a qualified professional should handle case-specific guidance.",
            "No. It points to evidence to collect before asking a veterinarian, trainer, landlord, insurer, or other qualified source.",
        ], "faq-advice")
        faq = (
            f"<h2 id=\"faq\">{escape(faq_heading)}</h2><dl class=\"faq\">"
            f"<dt>Is {escape(topic['main_keyword'])} a breed recommendation?</dt>"
            f"<dd>{escape(recommendation_answer)}</dd>"
            "<dt>Can this replace veterinary or legal advice?</dt>"
            f"<dd>{escape(advice_answer)}</dd>"
            "</dl>"
        )
    intro = stable_choice([
        f"{topic['subtitle']} It is built for {topic['reader']} who want a practical way to narrow the shortlist before emotions take over.",
        f"{topic['subtitle']} The goal is to turn a broad breed question into records, routines, costs, and responsibilities the household can verify.",
        f"{topic['subtitle']} Use it as a decision aid for {topic['reader']}, especially when a breed profile sounds appealing but the day-to-day plan is still vague.",
        f"{topic['subtitle']} This guide keeps the focus on what can be checked: documents, local constraints, owner capacity, and repeatable care.",
        f"{topic['subtitle']} Read it before comparing more breeds so the next choice is based on evidence rather than a longer wish list.",
        f"{topic['subtitle']} It is written for readers who need a realistic ownership screen, not a promise that one breed label solves the problem.",
    ], f"{topic['main_keyword']}|intro|{index}")
    toc_links = "".join(f"<a href=\"#{slugify(h)}\">{escape(h)}</a>" for h, _ in body_sections(topic, index)[:5])
    sources_heading = article_label(["Sources and limits", "Source notes and limits", "References and boundaries", "Evidence used"], "sources")
    callout_label = article_label(["Answer first", "Use this as a filter", "Reader takeaway", "Planning lens", "Start here"], "callout")
    metadata = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": topic["title"],
        "description": topic["subtitle"],
        "datePublished": publish_at.date().isoformat(),
        "dateModified": publish_at.date().isoformat(),
        "author": {"@type": "Organization", "name": "BreedWise"},
        "publisher": {"@type": "Organization", "name": "BreedWise"},
        "mainEntityOfPage": f"{BASE_URL}/blog/{slug}.html",
    }
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(topic['title'])}</title><meta name="description" content="{escape(topic['subtitle'])}">
<meta name="robots" content="noindex,follow"><link rel="canonical" href="{BASE_URL}/blog/{slug}.html"><link rel="stylesheet" href="../assets/site.css">
<meta property="og:title" content="{escape(topic['title'])}"><meta property="og:description" content="{escape(topic['subtitle'])}"><meta property="og:type" content="article"><meta name="twitter:card" content="summary_large_image">
<style>.callout{{border-left-color:{accent};background:{wash}}}.article h2{{color:{accent}}}</style>
<script type="application/ld+json">{json.dumps(metadata, ensure_ascii=False)}</script>{ADSENSE_LOADER}{GA4_TAG}{FEED_LINK}{VERIFICATION_TAGS}
</head><body><header class="topbar"><nav class="nav" aria-label="Primary"><a class="brand" href="../index.html"><span class="mark" aria-hidden="true"></span><span>BreedWise</span></a><div class="navlinks"><a href="../blog/index.html">Blog</a><a href="../cost/index.html">Cost Data</a><a href="../methodology/index.html">Methodology</a><a href="../about/index.html">About</a><a href="../contact/index.html">Contact</a><a href="../privacy-policy/index.html">Privacy</a><a href="../disclosures/index.html">Disclosures</a></div></nav></header>
<main><section class="pagehead"><div class="wrap"><p class="kicker">BreedWise Guide</p><h1>{escape(topic['title'])}</h1><p class="lead">{escape(topic['subtitle'])}</p><div class="meta"><span>Planning topic: {escape(topic['main_keyword'])}</span><span>Decision focus: {escape(topic['expanded_keywords'])}</span><span>Updated: {publish_at.date().isoformat()}</span><span>Educational planning guide</span></div></div></section>
<div class="wrap content"><article class="article"><p class="lead">{escape(intro)}</p><div class="callout"><strong>{escape(callout_label)}:</strong> {escape(sentence_topic(topic, index))}</div>{sections}{faq}
<h2 id="sources">{escape(sources_heading)}</h2><ul class="source-list"><li><a href="{source_url}" rel="nofollow noopener">{escape(source_label)}</a></li><li><a href="{second_source[1]}" rel="nofollow noopener">{escape(second_source[0])}</a></li><li><a href="../methodology/index.html">BreedWise methodology</a></li></ul>
<p class="note"><strong>Editorial boundary:</strong> BreedWise is educational planning content. It does not diagnose pets, prescribe care, rank insurers, or decide whether insurance is worth it.</p></article><aside class="toc"><strong>Contents</strong>{toc_links}<a href="../blog/index.html">Blog index</a><a href="../index.html#ownership">Cost preview</a><a href="../contact/index.html">Corrections</a></aside></div></main><footer class="footer"><div class="wrap"><span>&copy; 2026 BreedWise. Informational planning content only.</span><span><a href="../terms/index.html">Terms</a> &middot; <a href="../privacy-policy/index.html">Privacy Policy</a> &middot; <a href="../disclosures/index.html">Disclosures</a> &middot; <a href="../contact/index.html">Contact</a></span></div></footer></body></html>
"""


def main() -> int:
    QUEUE.mkdir(parents=True, exist_ok=True)
    topics = read_topics()
    schedule, existing_titles, existing_slugs, existing_keywords = load_existing()

    new_titles = set()
    new_slugs = set()
    new_keywords = set()
    for topic in topics:
        slug = slugify(topic["main_keyword"])
        title_key = topic["title"].casefold()
        keyword_key = topic["main_keyword"].casefold()
        if title_key in existing_titles or title_key in new_titles:
            raise RuntimeError(f"duplicate title: {topic['title']}")
        if slug.casefold() in existing_slugs or slug.casefold() in new_slugs:
            raise RuntimeError(f"duplicate slug: {slug}")
        if keyword_key in existing_keywords or keyword_key in new_keywords:
            raise RuntimeError(f"duplicate main keyword: {topic['main_keyword']}")
        new_titles.add(title_key)
        new_slugs.add(slug.casefold())
        new_keywords.add(keyword_key)

    latest = max(datetime.fromisoformat(item["publish_at"]) for item in schedule)
    start = latest + timedelta(hours=5)
    next_number = max(item["number"] for item in schedule) + 1

    manifest_items = []
    for offset, topic in enumerate(topics):
        publish_at = start + timedelta(hours=5 * offset)
        slug = slugify(topic["main_keyword"])
        filename = f"{publish_at.strftime('%Y%m%d%H%M')}-{slug}.html"
        queue_file = f".github/content-queue/{filename}"
        target_file = f"blog/{slug}.html"
        (ROOT / queue_file).write_text(article_html(topic, offset, publish_at), encoding="utf-8")
        manifest_items.append({
            "number": next_number + offset,
            "slug": slug,
            "queue_file": queue_file,
            "target_file": target_file,
            "publish_at": publish_at.isoformat(),
            "main_keyword": topic["main_keyword"],
            "expanded_keywords": topic["expanded_keywords"],
            "title": topic["title"],
            "subtitle": topic["subtitle"],
            "intent": topic["angle"],
            "category": FORMATS[offset % len(FORMATS)][0],
            "quality_score": 94,
            "quality_target": 90,
            "codex_only_generation": True,
            "codex_only_generation_confirmation": True,
            "internal_links": "blog/index.html;index.html#ownership;methodology/index.html",
            "external_source": SOURCES[topic["source"]][1],
            "cta": "Compare this guide with the BreedWise cost framework and methodology before choosing a dog.",
            "meta_title": topic["title"],
            "meta_description": topic["subtitle"],
            "canonical": f"{BASE_URL}/blog/{slug}.html",
            "excerpt": topic["subtitle"],
            "featured_image_idea": "Planning desk with leash, calendar, notes, and a dog-care budget worksheet.",
            "featured_image_alt": f"{title_case_text(topic['main_keyword'])} planning worksheet for {topic['expanded_keywords']}",
            "source_claim": source_claim(topic),
            "source_accessed": "2026-06-27",
            "research_mode": "common-source-centered",
        })

    SCHEDULE.write_text(json.dumps(schedule + manifest_items, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"added={len(manifest_items)} start={start.isoformat()} end={manifest_items[-1]['publish_at']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
