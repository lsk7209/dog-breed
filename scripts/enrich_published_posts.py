from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"


ENRICHMENTS = {
    "beagle-apartment-exercise-plan.html": """
<h2 id="apartment-week-test">Run the apartment week before adoption</h2>
<p>A Beagle can live well in an apartment when the owner plans around scent, sound, and repetition. The useful test is not whether the home has a yard. It is whether the household can repeat a morning sniff walk, a quiet recovery period, a workday enrichment plan, and an evening decompression routine without relying on perfect weather or unlimited free time.</p>
<p>Before adoption, run the schedule for seven days. Put two short scent sessions on the calendar, decide where food puzzles will be used, and write down the hallway or elevator moments that could trigger barking. If the plan already feels too complicated, that is helpful information. It is better to learn that before the dog is waiting at the door.</p>
<h2 id="noise-and-neighbor-plan">Noise and neighbor plan</h2>
<p>Apartment exercise is partly a noise problem. A tired Beagle is not automatically a quiet Beagle, especially if boredom, hallway sounds, or isolation become part of the daily pattern. The owner should plan for curtains, white noise, predictable departures, legal chew options, and a way to reward quiet behavior before complaints appear.</p>
<p>The goal is not to suppress normal dog behavior. The goal is to prevent avoidable conflict. If the building has thin walls, long hallways, shared elevators, or strict pet rules, the routine needs more documentation and a stronger backup plan.</p>
<h2 id="beagle-owner-checklist">Beagle owner checklist</h2>
<ul><li>Choose three scent games that can be done indoors without damaging the apartment.</li><li>Identify the longest workday gap and decide who covers it if the dog struggles.</li><li>Price a walker, trainer, or daycare backup before it becomes urgent.</li><li>Ask shelters, rescues, or breeders what is known about barking, separation history, and food motivation.</li><li>Keep the exercise plan flexible enough for rain, heat, illness, and busy workweeks.</li></ul>
""",
    "boxer-health-costs.html": """
<h2 id="energy-health-budget">Energy and health belong in the same budget</h2>
<p>Boxer ownership costs are not only about veterinary surprises. A realistic plan includes training, safe exercise, heat-aware routines, durable equipment, and a reserve for health conversations that may require follow-up. Owners who budget only for food and annual visits can be caught off guard by the amount of structure an energetic Boxer needs.</p>
<p>The practical question is whether the household can pay with both money and attention. A Boxer may need calm leash work, appropriate play, weight control, and a home routine that prevents overexcitement from becoming the default setting. Those are not extras; they are part of the cost of owning the breed responsibly.</p>
<h2 id="boxer-records">Records to request before commitment</h2>
<p>Ask for available veterinary records, parent or background information where relevant, notes about breathing tolerance, heart conversations, skin issues, previous injuries, and current weight. If the dog is an adult rescue, ask how the dog behaves after exercise, during heat, around other dogs, and after long periods alone.</p>
<p>Missing records do not automatically make the dog a poor choice. They change the budget. A dog with less history needs a larger uncertainty buffer and a slower first-month plan.</p>
<h2 id="boxer-decision-rule">A practical Boxer decision rule</h2>
<p>A Boxer is a better fit when the household can describe the training plan, the exercise rhythm, the heat plan, and the emergency reserve in writing. If those answers are vague, pause before choosing based on personality alone.</p>
""",
    "cavalier-king-charles-health-costs.html": """
<h2 id="cavalier-first-year-plan">First-year Cavalier planning</h2>
<p>The first year should turn uncertainty into records. Keep notes from veterinary visits, dental checks, weight conversations, ear or skin observations, and grooming appointments. A Cavalier owner does not need to panic about every possibility, but the owner should know what has been checked and what still needs monitoring.</p>
<p>This is especially important for a companion breed that can feel easy in daily life. A sweet temperament can hide the fact that recurring care is still work. The budget should include routine appointments, grooming support, dental planning, and a reserve for follow-up conversations when something changes.</p>
<h2 id="cavalier-household-fit">Household fit questions</h2>
<ul><li>Who tracks weight, dental care, and grooming intervals?</li><li>What records will be saved after each veterinary visit?</li><li>Can the household afford follow-up appointments without delaying care?</li><li>Does the dog have a calm routine that avoids overfeeding and under-exercising?</li><li>Who notices small changes in breathing, stamina, appetite, or comfort?</li></ul>
<h2 id="cavalier-cost-boundary">Cost boundary</h2>
<p>The responsible conclusion is not that Cavaliers are too risky or automatically easy. The responsible conclusion is that a future owner should request records, keep a recurring-care budget, and treat warm breed descriptions as only one part of the decision.</p>
""",
    "dachshund-back-problems-cost.html": """
<h2 id="dachshund-home-audit">Home audit before the dog arrives</h2>
<p>Dachshund cost planning starts with the floor plan. Stairs, couches, beds, slippery surfaces, and car access can all become part of the ownership budget. The cheapest setup is not always the safest setup if it encourages jumping or makes daily movement harder to manage.</p>
<p>Future owners should decide household rules before the dog arrives. Will the dog use ramps? Are children allowed to lift the dog? Is furniture access controlled? Who keeps weight management consistent? These questions are practical, not dramatic. They turn a known body-shape concern into a normal home management plan.</p>
<h2 id="dachshund-cost-layers">Cost layers to separate</h2>
<ul><li>Setup: ramps, gates, harnesses, beds, traction, and safe car access.</li><li>Routine: weight checks, nail care, dental care, and exercise that avoids overdoing it.</li><li>Training: teaching the dog to use ramps and accept handling calmly.</li><li>Reserve: money kept aside for veterinary conversations if mobility changes.</li></ul>
<h2 id="dachshund-pause-point">When to pause</h2>
<p>Pause if the plan depends on everyone remembering safety rules without a system. A Dachshund household needs repeatable habits. If the habits are not realistic, choose a different setup before choosing the dog.</p>
""",
    "first-time-dog-owner-breed-questions.html": """
<h2 id="first-time-owner-reality-check">First-time owner reality check</h2>
<p>The first dog often teaches owners what breed summaries leave out. Grooming takes time. Training takes repetition. Veterinary care requires records. Housing rules matter. A good first-time owner decision should reduce the number of surprises that arrive after the dog is already attached to the household.</p>
<p>Before choosing a breed, write the weekly routine in plain language. Include walks, feeding, cleaning, training, grooming, alone time, transport, and emergency coverage. If the schedule only works during a quiet week, the plan is not strong enough yet.</p>
<h2 id="questions-before-breed-list">Questions before the breed list</h2>
<ul><li>What problem would make this breed hard in your actual home?</li><li>What recurring cost are you most likely to underestimate?</li><li>Who handles the dog when work, travel, or illness disrupts the plan?</li><li>Which source supports your assumption about temperament, grooming, or health?</li><li>What would make you remove a breed from the shortlist?</li></ul>
<h2 id="first-time-owner-next-step">Best next step</h2>
<p>Choose one breed and test it against a normal weekday, a bad-weather day, and a month with an unexpected bill. A breed that survives those three checks is more useful than a breed that only looks good in a summary.</p>
""",
    "five-year-dog-ownership-cost-framework.html": """
<h2 id="five-year-cost-categories">Five-year categories that prevent surprise</h2>
<p>A useful five-year dog budget separates costs by behavior. Some costs happen once, some repeat predictably, and some appear only when the plan fails. Food, routine care, parasite prevention, grooming, training, boarding, replacement gear, and emergency reserves should not be blended into one vague monthly number.</p>
<p>This matters because owners often undercount time-sensitive costs. A training class delayed for six months may become private behavior help. A skipped grooming routine may become mat removal. A weak emergency reserve may turn a manageable visit into a financial crisis.</p>
<h2 id="five-year-budget-review">Quarterly budget review</h2>
<ul><li>Update food and routine-care totals with real receipts.</li><li>Track grooming, training, boarding, and replacement equipment separately.</li><li>Write down any health or behavior issue that repeated more than once.</li><li>Adjust the uncertainty buffer before it is needed.</li><li>Compare the budget with the dog's age, size, coat, and activity level.</li></ul>
<h2 id="five-year-framework-limit">Framework limit</h2>
<p>A framework cannot predict the individual dog. Its value is discipline: it gives the owner a place to put uncertainty instead of pretending uncertainty does not exist.</p>
""",
    "french-bulldog-vet-costs.html": """
<h2 id="frenchie-heat-breathing-plan">Heat and breathing planning</h2>
<p>French Bulldog cost planning should include the daily environment. Hot weather, travel, exercise intensity, stairs, and excitement can all change how the owner manages the dog. The budget is not only veterinary. It includes cooling routines, safer transport choices, weight management, and a willingness to change plans when conditions are not suitable.</p>
<p>Owners should avoid articles that turn flat-faced breed concerns into either panic or denial. The practical middle is better: understand the watchlist, ask a veterinarian about the individual dog, and build routines that do not depend on pushing the dog through discomfort.</p>
<h2 id="frenchie-questions">Questions to ask before buying or adopting</h2>
<ul><li>What breathing, heat, skin, dental, and weight notes are available?</li><li>How does the dog handle walks, excitement, car rides, and warm days?</li><li>What routine care has already been done?</li><li>What local veterinary access and emergency transport are available?</li><li>Can the household afford follow-up care without waiting?</li></ul>
<h2 id="frenchie-owner-boundary">Owner boundary</h2>
<p>A French Bulldog can be a loving companion, but the owner must be comfortable saying no to risky heat, overexertion, and vague health claims. That boundary is part of the cost of ownership.</p>
""",
    "german-shepherd-joint-risk-budget.html": """
<h2 id="german-shepherd-training-budget">Training is part of mobility planning</h2>
<p>For a German Shepherd, movement and manners are connected. Pulling, jumping, uncontrolled play, and poor impulse control can make daily life harder for a large dog and the people handling it. Budgeting for training is not separate from budgeting for joint-conscious ownership; it is one of the ways owners keep routines safer and more manageable.</p>
<p>A good plan names the training format, the person responsible for practice, and the equipment that will be used. It also sets realistic expectations. One class is a start, not a finished behavior plan.</p>
<h2 id="german-shepherd-month-one">Month-one owner checks</h2>
<ul><li>Record weight, body condition, and exercise tolerance.</li><li>Check floors, stairs, car access, and resting areas.</li><li>Ask what hip and elbow records or history are available.</li><li>Schedule training before strength becomes a daily conflict.</li><li>Keep an emergency reserve separate from routine food and gear spending.</li></ul>
<h2 id="german-shepherd-decision-boundary">Decision boundary</h2>
<p>The question is not whether a German Shepherd is good or bad. The question is whether the household can support a large, intelligent, active dog with consistent training, source-aware health questions, and a long-term mobility budget.</p>
""",
    "golden-retriever-health-costs.html": """
<h2 id="golden-recurring-care">Recurring care matters more than the headline cost</h2>
<p>Golden Retriever health-cost planning should not focus only on rare expensive events. Many owners feel the budget through recurring care: food, grooming, preventive visits, weight management, training, replacement toys, and the time required to keep an active social dog settled.</p>
<p>The breed's popularity can make the decision feel familiar, but familiarity is not a budget. A future owner should still ask for records, compare local costs, and decide how much uncertainty the household can absorb without delaying care.</p>
<h2 id="golden-owner-checks">Golden owner checks</h2>
<ul><li>Track body condition and food portions from the beginning.</li><li>Ask about hips, elbows, skin, ears, and previous veterinary notes.</li><li>Budget for grooming tools, bathing, and seasonal shedding cleanup.</li><li>Plan training around greeting manners and leash control.</li><li>Keep a reserve for follow-up visits when a concern does not resolve quickly.</li></ul>
<h2 id="golden-useful-conclusion">Useful conclusion</h2>
<p>A Golden Retriever may be a strong family fit, but the strongest decision is the one that combines affection with records, routine, and a realistic five-year cost plan.</p>
""",
    "labrador-retriever-health-costs.html": """
<h2 id="labrador-weight-cost">Weight management is a cost issue</h2>
<p>Labrador Retriever cost planning should include food motivation and weight control. Extra weight can affect routine comfort, activity, training, and veterinary conversations. Owners should budget not only for food but for measured feeding, training rewards, durable enrichment, and family rules that prevent overfeeding.</p>
<p>A Labrador plan works better when everyone in the household understands the same rules. If one person measures meals and another gives frequent extras, the budget and the dog's health routine are working against each other.</p>
<h2 id="labrador-household-system">Household system</h2>
<ul><li>Choose who measures food and who buys it.</li><li>Set a treat budget and training reward plan.</li><li>Track weight and body condition with the veterinarian.</li><li>Plan exercise that fits bad weather and busy workweeks.</li><li>Keep joint, ear, and skin questions in the record folder.</li></ul>
<h2 id="labrador-cost-boundary">Cost boundary</h2>
<p>The safest budget is not the cheapest one. It is the one that makes routine care easy to repeat and keeps enough reserve for the problems a large, food-motivated dog may make more expensive.</p>
""",
    "poodle-health-screening-costs.html": """
<h2 id="poodle-size-specific-plan">Size-specific planning</h2>
<p>Poodle health screening and cost planning changes by size. Toy, Miniature, and Standard Poodles can differ in grooming cadence, handling needs, exercise, dental concerns, and the kinds of questions owners should bring to breeders, rescues, or veterinarians. A single Poodle budget is usually too broad.</p>
<p>The owner should write down which size is being considered before comparing costs. Then the plan can separate grooming, dental care, orthopedic or eye questions, training, food, equipment, and long-term monitoring.</p>
<h2 id="poodle-records">Records and service access</h2>
<ul><li>Ask what screening or parent information is available for the size being considered.</li><li>Price grooming locally before assuming the coat is manageable.</li><li>Decide whether home brushing and maintenance are realistic.</li><li>Ask a veterinarian which routine checks matter most for the individual dog.</li><li>Keep grooming, dental, and screening notes in the same folder.</li></ul>
<h2 id="poodle-decision-rule">Decision rule</h2>
<p>A Poodle plan is strong when the owner can afford the coat, understand the size-specific questions, and keep up with records. Low shedding is useful only when the maintenance behind it is also realistic.</p>
""",
    "afghan-hound-grooming-temperament-cost.html": """
<h2 id="afghan-coat-workflow">Turn coat care into a repeatable workflow</h2>
<p>Afghan Hound coat planning is easier when the owner separates daily maintenance from professional grooming. Ask a local groomer what the current coat condition would require, how long a visit usually takes, and which home tools are realistic for the dog's tolerance. Do not use a generic appointment interval as a promise; coat length, texture, handling history, and the owner's routine can change the actual workload.</p>
<p>Write the workflow before adoption: where brushing happens, who handles the dog, what happens when the coat is wet or tangled, and how a missed session is recovered. A low price estimate that assumes perfect cooperation is not a reliable budget. Save the quote and the questions that produced it so the estimate can be updated after the first month.</p>
<h2 id="afghan-secure-outdoor-plan">Secure outdoor and recall plan</h2>
<p>A sighthound-oriented household should verify fencing, leash rules, transport, and nearby exercise options before treating a yard as a solution. A fenced area is not a substitute for checking escape points or planning what happens when weather, travel, or a repair removes access. The decision is stronger when the owner can name a safe weekday route, a bad-weather alternative, and the person who handles the dog if the primary caregiver is away.</p>
""",
    "airedale-terrier-grooming-exercise.html": """
<h2 id="airedale-grooming-quote">Get a grooming quote that matches the coat plan</h2>
<p>Airedale grooming should be budgeted as a service and a household skill. Ask whether the local groomer recommends stripping, clipping, or a mixed maintenance plan for the individual coat, and record what is included in the quote. The visit price alone may not describe brushing, bathing, drying, handling time, tools, or the work the owner must repeat between appointments.</p>
<p>Exercise planning needs the same specificity. Put walks, training, play, rest, and bad-weather alternatives on a normal-week calendar. A large terrier can make an energetic plan look easy on paper while the daily combination of arousal, leash work, and coat maintenance creates friction. Test the schedule for two weeks and change the plan before adding optional equipment.</p>
<h2 id="airedale-training-boundary">Training and household boundary</h2>
<p>Ask who practices calm greetings, leash skills, handling, and recovery after activity. The responsible conclusion is not that every Airedale needs the same program; it is that the household should budget for repetition and qualified help when its own practice is not enough. Keep local quotes, the weekly schedule, and the records behind the decision together.</p>
""",
    "akita-first-time-owner-risk.html": """
<h2 id="akita-household-management">Write the handling plan for ordinary visitors</h2>
<p>First-time-owner planning becomes concrete when it covers the people who will actually enter the home. Decide where the dog rests, how doors and gates are managed, how guests receive instructions, and who takes over if the owner is tired or absent. This is not a temperament prediction. It is a test of whether the household can create consistent boundaries before a difficult interaction occurs.</p>
<p>Use the same approach outside the home. Check local leash and housing rules, identify a route that allows space from other dogs, and price training support before a problem becomes urgent. If the plan depends on every family member improvising, it is not yet a first-time-owner plan. Put the rules in writing and make the safer choice the easier choice.</p>
<h2 id="akita-records-and-review">Records and review point</h2>
<p>Before commitment, request the available health, behavior, vaccination, training, and ownership-history records. Missing information is not an automatic verdict, but it increases the uncertainty reserve and makes a slower introduction more important. Review the plan after the first month using actual incidents, costs, and questions for a veterinarian or qualified trainer rather than relying on a breed label.</p>
""",
    "alaskan-malamute-food-escape-cost.html": """
<h2 id="malamute-food-budget">Build the food budget from the actual dog</h2>
<p>Food planning should start with the dog's current weight, life stage, activity, feeding instructions, and the product's own label rather than a single breed-wide number. Record the package size, price, measured daily amount, treats, and any change recommended by a veterinarian. Prices vary by retailer and region, while the correct amount can change as the dog grows or its routine changes.</p>
<p>Use a monthly sheet with food, treats, supplements if professionally advised, grooming, equipment, training, boarding, and a separate uncertainty reserve. This makes it clear which amount is a recurring estimate and which amount is only a placeholder. A large-dog budget should be stress-tested against a price increase, a travel week, and a month when exercise or care needs outside help.</p>
<h2 id="malamute-containment-and-climate">Containment and climate checks</h2>
<p>Fencing is a system, not just a purchase. Walk the boundary, check gates and digging points, confirm local rules, and decide how the dog is transported when the yard is unavailable. Coat care and exercise also depend on climate and the dog's individual tolerance. Keep an indoor enrichment option and a cooler or safer-time routine so the plan does not rely on one perfect outdoor window.</p>
""",
    "american-bully-housing-health-cost.html": """
<h2 id="american-bully-housing-check">Verify housing rules before health assumptions</h2>
<p>Housing is an evidence question before it becomes a breed question. Ask the landlord, insurer, homeowners association, or local authority for the current written rule and save the response. A listing, forum comment, or verbal assumption is not enough when a restriction could change the household's ability to keep the dog. Also check pet deposits, liability terms, weight limits, elevator access, and emergency transport.</p>
<p>Keep the health and cost plan equally concrete. Record the dog's current weight and body condition with a veterinarian, ask what routine care is due, and price food, training, equipment, grooming, and local veterinary access. Avoid turning body shape or a label into a diagnosis. The useful result is a list of records, questions, and recurring costs that can be reviewed as the individual dog changes.</p>
<h2 id="american-bully-training-system">Training system and backup owner</h2>
<p>Write down who handles leash practice, calm greetings, exercise, feeding, and care during travel or illness. If a backup person cannot safely manage the routine, include qualified help in the budget before adoption. A strong plan is one the household can repeat on an ordinary weekday, not one that works only when every adult has extra time.</p>
""",
}

FOLLOWUPS = {
    "boxer-health-costs.html": """
<h2 id="boxer-first-month-review">First-month review for a Boxer</h2>
<p>Use the first month to confirm whether the budget matches the dog in front of you. Track how often exercise needs extra structure, whether heat changes the walking schedule, which training behaviors need repetition, and whether skin, digestion, breathing, or weight questions should be documented for the veterinarian.</p>
<p>This review should be written down, not kept as a vague impression. A Boxer plan gets stronger when the owner can say what is normal, what changed, and what support would be needed if the same issue repeats next month.</p>
""",
    "cavalier-king-charles-health-costs.html": """
<h2 id="cavalier-first-month-review">First-month review for a Cavalier</h2>
<p>During the first month, the owner should create a simple care record. Save the first veterinary notes, food amounts, weight, grooming needs, dental observations, and any comments about stamina or comfort. This record is not for diagnosing the dog. It is for noticing patterns early and making future conversations clearer.</p>
<p>A Cavalier budget works best when the household treats gentle daily life and serious care planning as the same project. The dog may be easy to love, but the owner still needs a routine that catches small changes before they become expensive surprises.</p>
""",
    "dachshund-back-problems-cost.html": """
<h2 id="dachshund-first-month-review">First-month review for a Dachshund</h2>
<p>The first month should test whether the home rules actually work. Watch whether the dog uses ramps, whether furniture access is controlled, whether children or guests lift the dog safely, and whether the walking routine keeps weight and confidence in balance.</p>
<p>If the household keeps breaking its own rules, change the setup instead of blaming the dog. Add gates, move furniture, improve traction, or simplify the routine. Dachshund planning is strongest when safe habits are easier than unsafe habits.</p>
""",
    "first-time-dog-owner-breed-questions.html": """
<h2 id="first-time-owner-first-month">First-month review for first-time owners</h2>
<p>The first month should be treated as a learning period. Keep a short log of feeding, walks, training, sleep, grooming, alone time, and the questions that required outside help. The point is not to grade the owner. The point is to see which assumptions were accurate and which ones need a better system.</p>
<p>At the end of the month, update the budget and the routine. If training takes more time, put it on the calendar. If grooming is harder than expected, price help. If the dog struggles alone, adjust the plan before frustration becomes normal.</p>
""",
    "five-year-dog-ownership-cost-framework.html": """
<h2 id="five-year-framework-first-review">First review after adoption</h2>
<p>A five-year framework becomes useful only when it is updated with real numbers. After the first month, replace guesses with receipts: food, routine care, equipment, grooming, training, travel supplies, and any service help. Then mark which costs were one-time and which are likely to repeat.</p>
<p>This early review helps prevent quiet budget drift. Owners often notice that small recurring costs matter more than one dramatic purchase. Capturing them early makes the five-year range more honest and easier to maintain.</p>
""",
    "french-bulldog-vet-costs.html": """
<h2 id="frenchie-first-month-review">First-month review for a French Bulldog</h2>
<p>During the first month, track heat tolerance, walking recovery, skin or ear observations, dental notes, weight, breathing comfort, and how the dog handles excitement. These notes are not a diagnosis; they are a practical record to bring to a veterinarian if a question repeats.</p>
<p>The owner should also review the environment. Check cooling options, stairs, transport, sleeping areas, and the plan for warm days. A French Bulldog budget is stronger when daily routines reduce avoidable strain instead of waiting for a problem to become urgent.</p>
""",
    "german-shepherd-joint-risk-budget.html": """
<h2 id="german-shepherd-first-month-review">First-month review for a German Shepherd</h2>
<p>During the first month, record exercise tolerance, leash control, surfaces in the home, car access, resting areas, weight, and any movement questions that should be discussed with a veterinarian. These notes help separate normal adjustment from patterns that deserve follow-up.</p>
<p>The training plan should be reviewed at the same time. A large intelligent dog needs consistent handling before problems become expensive. If the household cannot practice daily, budget for help earlier rather than waiting for strength and frustration to grow together.</p>
""",
    "golden-retriever-health-costs.html": """
<h2 id="golden-first-month-review">First-month review for a Golden Retriever</h2>
<p>In the first month, track food amounts, body condition, exercise, grooming, ear observations, skin changes, training needs, and the dog's ability to settle after excitement. Golden Retriever costs often become visible through repeated routines rather than one dramatic bill.</p>
<p>The household should also decide who owns each routine. One person may handle food measurement, another grooming, and another training practice. If no one owns the task, the budget plan is only a wish list.</p>
""",
    "labrador-retriever-health-costs.html": """
<h2 id="labrador-first-month-review">First-month review for a Labrador</h2>
<p>The first month should test food rules and activity routines. Record meal amounts, treats, training rewards, weight, exercise, and any ear, skin, joint, or digestion questions. A Labrador's budget often changes when food motivation and family habits are not managed consistently.</p>
<p>Make the rules visible. Put food measurements where everyone can see them, decide which treats count as training rewards, and schedule exercise that works during bad weather. Consistency is cheaper than correcting drift later.</p>
""",
    "poodle-health-screening-costs.html": """
<h2 id="poodle-first-month-review">First-month review for a Poodle</h2>
<p>The first month should confirm whether the coat plan is realistic. Track brushing, bathing, mat-prone areas, grooming appointment length, dental care, ear observations, and how the dog handles handling. A low-shedding reputation does not remove maintenance; it changes where the maintenance appears.</p>
<p>Owners should also compare the chosen Poodle size with the actual routine. Toy, Miniature, and Standard Poodles can create different equipment, exercise, grooming, and screening questions. The budget should reflect the dog in the home, not only the breed name.</p>
""",
}


def insert_before_sources(html: str, addition: str) -> str:
    marker = '<h2 id="sources">'
    if marker not in html:
        raise RuntimeError("sources marker not found")
    if addition.strip() in html:
        return html
    return html.replace(marker, addition.strip() + "\n\n" + marker, 1)


def clean_beagle(html: str) -> str:
    replacements = {
        '<span>Quality target: 90+</span>': '<span>Educational planning guide</span>',
        "Researching Beagle Apartment Exercise Plan as a budget map is more useful than asking whether the breed is simply expensive or cheap.": "A Beagle apartment exercise plan should start with scent work, noise management, and a schedule the owner can repeat in a small home.",
        "Use the checklist below to compare the breed or ownership scenario without treating the article as veterinary advice.": "Use the checklist below to compare apartment routines without treating this article as veterinary advice.",
        "AEO summary": "Short answer for comparison",
        "Pre-publish quality check": "Why this guide is useful",
        "This guide earns its place only if it gives the reader a distinct decision angle. For Beagle Apartment Exercise Plan, that angle is not a generic breed profile; it is the link between beagle apartment exercise plan, the expanded keyword set, and the owner's next action. If a paragraph does not help that decision, it should be removed or rewritten before publication.": "This guide is useful because it treats apartment life as a routine design problem. Beagle owners need to plan scent outlets, barking triggers, alone time, and backup help before the dog is already restless in a small space.",
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    return html


def main() -> int:
    for filename, addition in ENRICHMENTS.items():
        path = BLOG / filename
        html = path.read_text(encoding="utf-8")
        if filename == "beagle-apartment-exercise-plan.html":
            html = clean_beagle(html)
        html = insert_before_sources(html, addition)
        if filename in FOLLOWUPS:
            html = insert_before_sources(html, FOLLOWUPS[filename])
        path.write_text(html, encoding="utf-8")
    print(f"enriched={len(ENRICHMENTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
