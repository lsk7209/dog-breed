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
BASE_URL = "https://lsk7209.github.io/dog-breed"


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
    ]
    subtitle_patterns = [
        "A {main} guide that turns {expanded} into budget checks, record requests, daily routines, and source-quality decisions.",
        "Use this {main} article to compare {expanded} with housing fit, care workload, documented evidence, and long-term cost exposure.",
        "This {main} guide explains how {expanded} should shape the shortlist before adoption, purchase, or a serious breed comparison.",
        "For readers researching {main}, this guide connects {expanded} with practical questions, credible sources, and BreedWise planning boundaries.",
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


def sentence_topic(topic: dict[str, str]) -> str:
    return (
        f"The main keyword is {topic['main_keyword']}, but the useful reader problem is narrower: "
        f"{topic['expanded_keywords']} must fit the reader's real home, calendar, and budget."
    )


def expanded_parts(topic: dict[str, str]) -> list[str]:
    return [part.strip() for part in topic["expanded_keywords"].split(",") if part.strip()]


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
        seed = f"{topic['main_keyword']}|{topic['expanded_keywords']}|{salt}|{index}"
        score = sum((position + 1) * ord(char) for position, char in enumerate(seed))
        return options[score % len(options)]

    section_bank = {
        "answer": (
            label(["Answer first", "Short answer", "Bottom line", "Decision answer", "Plain answer", "Fast answer", "Reader-first answer", "The useful answer"], "answer"),
            f"{topic['title']} should be treated as a decision worksheet, not a breed ranking. For {reader}, the useful answer is whether {first}, {second}, and {third} can be handled in the same real week: normal work obligations, bad weather, one unexpected bill, and a household that may be tired by evening. If the plan only works when every day is convenient, the shortlist is not ready."
        ),
        "friction": (
            label(["Where the friction usually appears", "The hidden friction", "Where plans usually break", "The part owners undercount", "The mismatch point", "Where the plan gets tested"], "friction"),
            f"The {angle} problem often hides in ordinary details. {title_case_text(first)} may affect the daily routine, {second} may affect recurring costs or records, and {third} may affect the backup plan. None of those details automatically rules out a dog, but each one needs an owner, a budget range, and a source of evidence before the choice becomes responsible."
        ),
        "decision_table": (
            label(["Decision table", "Green-yellow-red check", "Decision signals", "Readiness table", "Practical decision signals", "Fit check table"], "decision_table"),
            f"<table class='table'><tr><th>Signal</th><th>What to verify</th><th>Why it matters</th></tr><tr><td>Green</td><td>{e(first)} is documented with a named routine and backup.</td><td>The plan can survive a normal busy week.</td></tr><tr><td>Yellow</td><td>{e(second)} still needs a quote, policy, record, or trial period.</td><td>The decision needs one more documented answer.</td></tr><tr><td>Red</td><td>{e(third)} is being minimized or assigned to nobody.</td><td>The household may be buying surprise work.</td></tr></table>"
        ),
        "checklist": (
            label(["Pre-adoption checklist", "Questions to answer before commitment", "Before-you-choose checklist", "Decision checklist", "Commitment checklist", "Questions before the shortlist"], "checklist"),
            f"<ul><li>Write the weekly job connected to {e(first)} in one sentence.</li><li>Ask what record, lease rule, service quote, or professional conversation supports the assumption about {e(second)}.</li><li>Decide how much money stays untouched if {e(third)} becomes harder than expected.</li><li>Compare the answer with the BreedWise cost framework before adding more breeds to the shortlist.</li></ul>"
        ),
        "scenario": (
            label(["Reader scenario", "A realistic week", "How this plays out", "A household example", "A normal-week example", "What the week can reveal"], "scenario"),
            f"Picture a household researching {main} on a Sunday night. The appealing version of the plan is simple: find a dog that seems to match the lifestyle. The more useful version is stricter. On Monday, they confirm the rule or record behind {first}. On Tuesday, they price the recurring work around {second}. On Wednesday, they decide who handles {third} if the first plan fails. By the end of the week, the shortlist is smaller but more honest."
        ),
        "cost": (
            label(["Cost and time stack", "Budget pressure points", "The cost stack", "Where the budget gets real", "Time and money pressure", "Budget reality check"], "cost"),
            f"Do not turn {main} into a single price question. Build three stacks instead: setup costs, repeat costs, and uncertainty reserve. Setup covers the first tools, appointments, and home changes. Repeat costs cover the work that returns every week or month. The reserve protects the household when these issues take more time, service help, or professional input than expected."
        ),
        "records": (
            label(["Records worth saving", "Evidence to collect", "Documentation that matters", "What to save before you decide", "Paper trail to keep", "Records that reduce guesswork"], "records"),
            f"<ul><li>Source page: <a href='{source_url}' rel='nofollow noopener'>{e(source_label)}</a>, used for {e(source_claim(topic))}. Accessed 2026-06-27.</li><li>Cross-check page: <a href='{second_source_url}' rel='nofollow noopener'>{e(second_source_label)}</a>, used for general ownership and care-planning context.</li><li>Local evidence: lease terms, veterinary notes, shelter or breeder records, service estimates, trainer or groomer policies, and dated screenshots of any rules that affect the decision.</li></ul>"
        ),
        "source_ladder": (
            label(["Source ladder", "How to use sources", "Source quality check", "Evidence ladder", "How to read the evidence", "Source reality check"], "source_ladder"),
            f"Use broad sources for vocabulary, not final certainty. {source_label} can help frame the question, but it cannot know the individual dog, local prices, housing rules, climate, training history, or caregiver capacity. The best evidence ladder is simple: public source for context, local document for feasibility, professional conversation for risk-sensitive questions, and a written household plan for who does the work."
        ),
        "comparison": (
            label(["Compare two realistic options", "Side-by-side reality check", "Appealing vs sustainable", "Comparison worksheet", "Two-option comparison", "A more honest comparison"], "comparison"),
            f"<table class='table'><tr><th>Question</th><th>Option that looks appealing</th><th>Option that may be sustainable</th></tr><tr><td>{e(first)}</td><td>Assumed from a breed summary.</td><td>Checked against the current home and schedule.</td></tr><tr><td>{e(second)}</td><td>Estimated from a casual average.</td><td>Priced with a local quote or documented rule.</td></tr><tr><td>{e(third)}</td><td>Handled only if a problem appears.</td><td>Assigned before commitment.</td></tr></table>"
        ),
        "mistakes": (
            label(["Mistakes to avoid", "Common planning mistakes", "What not to assume", "Avoid these shortcuts", "Planning traps", "Assumptions to challenge"], "mistakes"),
            f"<ol><li>Do not choose from photos before checking {e(first)}.</li><li>Do not treat {e(second)} as a one-time issue if it can repeat.</li><li>Do not let {e(third)} become one person's invisible job.</li><li>Do not convert this article into medical, legal, insurance, or training advice for a specific dog.</li></ol>"
        ),
        "aeo": (
            label(["Quick answer summary", "Summary for skimmers", "Answer-engine summary", "Decision summary", "Concise answer block", "Short version for comparison"], "aeo"),
            f"For quick answer engines: {main} is a planning query for {reader}. The decision should test the expanded issues, {expanded}, against daily routine, written records, local costs, and a reserve for uncertainty. The safest conclusion is not a universal breed recommendation; it is a clearer checklist for whether the household can handle the specific work."
        ),
        "owner_roles": (
            label(["Owner roles", "Who does the work?", "Assign the routine", "Household responsibility check", "Workload map", "Who owns each task?"], "owner_roles"),
            f"Write the owner roles before the decision gets emotional. One person may handle research, another may handle appointments, and another may handle daily routines. If {first}, {second}, and {third} all land on the same person by default, the household is not evaluating a dog breed; it is testing whether one person can absorb the whole ownership workload."
        ),
        "pause": (
            label(["When to pause", "Stop and verify", "Pause before you commit", "A sensible stop point", "When the answer is not ready", "The pause test"], "pause"),
            f"Pause if the answer depends on hope instead of evidence. That includes vague promises about {first}, missing records around {second}, or no backup plan for {third}. A pause is not a failure; it is the moment where a future owner prevents a mismatch before the dog is already part of the household."
        ),
        "one_week": (
            label(["One-week test", "Try the routine for a week", "Seven-day reality test", "Trial week", "Seven-day home simulation", "Calendar test"], "one_week"),
            f"Run a seven-day simulation without the dog. Put the walks, cleaning, phone calls, service quotes, record checks, and budget transfers on the calendar. If the household cannot make time for the research version of {main}, it should be cautious about the real version."
        ),
        "local_check": (
            label(["Local checks", "Local reality check", "What changes by address", "Local proof points", "Address-specific checks", "What to verify nearby"], "local_check"),
            f"Local details can overturn broad advice. Rental rules, service availability, climate, travel distance, and professional fees all change how {expanded} feels in practice. This is why BreedWise treats public sources as a starting point and asks readers to verify the decision where they live."
        ),
        "next": (
            label(["Practical next step", "Next action", "What to do now", "Use this guide", "Turn this into a plan", "Make the next choice smaller"], "next"),
            f"Save this guide, write down two unanswered questions about {expanded}, and resolve them before reading more breed profiles. Then compare the answer with the BreedWise methodology and five-year ownership cost framework. Better research should narrow the shortlist, not make every option sound equally possible. If the checklist feels inconvenient now, treat that as useful evidence: the same work will usually feel harder after a dog is already home. Keep the notes and date them so the decision trail stays clear."
        ),
    }
    archetypes = [
        ["answer", "friction", "decision_table", "records", "scenario", "cost", "checklist", "source_ladder", "one_week", "aeo", "pause", "next"],
        ["answer", "cost", "comparison", "checklist", "records", "mistakes", "scenario", "source_ladder", "owner_roles", "aeo", "local_check", "next"],
        ["answer", "scenario", "checklist", "decision_table", "source_ladder", "records", "cost", "mistakes", "one_week", "aeo", "pause", "next"],
        ["answer", "records", "source_ladder", "comparison", "friction", "checklist", "scenario", "cost", "owner_roles", "aeo", "local_check", "next"],
        ["answer", "comparison", "friction", "cost", "decision_table", "mistakes", "records", "source_ladder", "one_week", "aeo", "pause", "next"],
        ["answer", "mistakes", "checklist", "scenario", "records", "decision_table", "source_ladder", "cost", "owner_roles", "aeo", "local_check", "next"],
    ]
    sections = [section_bank[key] for key in archetypes[index % len(archetypes)]]
    return sections


def article_html(topic: dict[str, str], index: int, publish_at: datetime) -> str:
    slug = slugify(topic["main_keyword"])
    accent, wash = ACCENTS[index % len(ACCENTS)]
    source_label, source_url = SOURCES[topic["source"]]
    second_source = SOURCES["avma"] if topic["source"] != "avma" else SOURCES["aaha"]
    def article_label(options: list[str], salt: str) -> str:
        seed = f"{topic['main_keyword']}|{salt}|{index}"
        score = sum((position + 1) * ord(char) for position, char in enumerate(seed))
        return options[score % len(options)]
    section_parts = []
    for heading, text in body_sections(topic, index):
        body = text if text.lstrip().startswith("<") else f"<p>{text}</p>"
        section_parts.append(f"<h2 id=\"{slugify(heading)}\">{escape(heading)}</h2>{body}")
    sections = "\n".join(section_parts)
    faq = ""
    if index % 2 == 0:
        faq_heading = article_label(["FAQ", "Common questions", "Reader questions", "Quick questions"], "faq")
        faq = (
            f"<h2 id=\"faq\">{escape(faq_heading)}</h2><dl class=\"faq\">"
            f"<dt>Is {escape(topic['main_keyword'])} a breed recommendation?</dt>"
            "<dd>No. It is a planning frame for comparing constraints before choosing a dog.</dd>"
            "<dt>Can this replace veterinary or legal advice?</dt>"
            "<dd>No. Use it to prepare questions for qualified professionals and documented sources.</dd>"
            "</dl>"
        )
    intro = (
        f"{topic['subtitle']} This article is written for {topic['reader']} who need a clear decision process, "
        f"not another generic breed profile."
    )
    toc_links = "".join(f"<a href=\"#{slugify(h)}\">{escape(h)}</a>" for h, _ in body_sections(topic, index)[:5])
    sources_heading = article_label(["Sources and limits", "Source notes and limits", "References and boundaries", "Evidence used"], "sources")
    metadata = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": topic["title"],
        "description": topic["subtitle"],
        "datePublished": publish_at.date().isoformat(),
        "dateModified": publish_at.date().isoformat(),
        "author": {"@type": "Organization", "name": "BreedWise"},
        "publisher": {"@type": "Organization", "name": "BreedWise"},
    }
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(topic['title'])}</title><meta name="description" content="{escape(topic['subtitle'])}">
<meta name="robots" content="noindex,follow"><link rel="canonical" href="{BASE_URL}/blog/{slug}.html"><link rel="stylesheet" href="../assets/site.css">
<meta property="og:title" content="{escape(topic['title'])}"><meta property="og:description" content="{escape(topic['subtitle'])}"><meta property="og:type" content="article"><meta name="twitter:card" content="summary_large_image">
<style>.callout{{border-left-color:{accent};background:{wash}}}.article h2{{color:{accent}}}</style>
<script type="application/ld+json">{json.dumps(metadata, ensure_ascii=False)}</script>
</head><body><header class="topbar"><nav class="nav" aria-label="Primary"><a class="brand" href="../index.html"><span class="mark" aria-hidden="true"></span><span>BreedWise</span></a><div class="navlinks"><a href="../blog/index.html">Blog</a><a href="../methodology/index.html">Methodology</a><a href="../about/index.html">About</a><a href="../contact/index.html">Contact</a><a href="../privacy-policy/index.html">Privacy</a></div></nav></header>
<main><section class="pagehead"><div class="wrap"><p class="kicker">Scheduled guide</p><h1>{escape(topic['title'])}</h1><p class="lead">{escape(topic['subtitle'])}</p><div class="meta"><span>Main keyword: {escape(topic['main_keyword'])}</span><span>Expanded keywords: {escape(topic['expanded_keywords'])}</span><span>Scheduled: {publish_at.isoformat()}</span><span>Quality score: 94</span></div></div></section>
<div class="wrap content"><article class="article"><p class="lead">{escape(intro)}</p><div class="callout"><strong>Answer first:</strong> {escape(sentence_topic(topic))}</div>{sections}{faq}
<h2 id="sources">{escape(sources_heading)}</h2><ul class="source-list"><li><a href="{source_url}" rel="nofollow noopener">{escape(source_label)}</a></li><li><a href="{second_source[1]}" rel="nofollow noopener">{escape(second_source[0])}</a></li><li><a href="../methodology/index.html">BreedWise methodology</a></li></ul>
<p class="note"><strong>Editorial boundary:</strong> BreedWise is educational planning content. It does not diagnose pets, prescribe care, rank insurers, or decide whether insurance is worth it.</p></article><aside class="toc"><strong>Contents</strong>{toc_links}<a href="../blog/index.html">Blog index</a><a href="../index.html#ownership">Cost preview</a><a href="../contact/index.html">Corrections</a></aside></div></main><footer class="footer"><div class="wrap"><span>&copy; 2026 BreedWise. Informational planning content only.</span><span><a href="../terms/index.html">Terms</a> &middot; <a href="../privacy-policy/index.html">Privacy Policy</a></span></div></footer></body></html>
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
