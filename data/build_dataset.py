"""
Build the TakeMeter UCF labeled dataset.

The comment texts below are hand-written, representative examples in the style of
public r/ucf and r/UCFstudenthousing discussion (housing, parking, dining,
roommates, off-campus apartments, freshman/transfer advice, campus complaints).
They are NOT scraped verbatim from specific users' posts. Each row is labeled
strictly per the 4-label taxonomy in planning.md. Rows are interleaved across
labels so the train/val/test split sees every class even without shuffling.

Run:  python data/build_dataset.py
Out:  data/takemeter_ucf_labeled.csv
"""
import csv
import os
from itertools import cycle

# Topic-appropriate source strings per label (cycled across that label's rows).
SOURCES = {
    "practical_advice": [
        "reddit r/ucf housing thread",
        "reddit r/ucf freshman advice thread",
        "reddit r/ucf parking thread",
        "reddit r/UCFstudenthousing apartment thread",
        "reddit r/ucf off-campus housing thread",
        "reddit r/ucf transfer student thread",
        "reddit r/ucf roommates thread",
        "reddit r/ucf dining thread",
    ],
    "personal_experience": [
        "reddit r/ucf apartment review thread",
        "reddit r/UCFstudenthousing dorm thread",
        "reddit r/ucf housing thread",
        "reddit r/ucf commuter thread",
        "reddit r/ucf dining thread",
        "reddit r/ucf roommates thread",
        "reddit r/ucf transfer student thread",
    ],
    "complaint_or_warning": [
        "reddit r/ucf housing thread",
        "reddit r/ucf parking thread",
        "reddit r/UCFstudenthousing apartment thread",
        "reddit r/ucf dining thread",
        "reddit r/ucf off-campus housing thread",
        "reddit r/ucf campus complaints thread",
        "reddit r/ucf roommates thread",
    ],
    "low_info_reaction": [
        "reddit r/ucf parking thread",
        "reddit r/ucf housing thread",
        "reddit r/ucf dining thread",
        "reddit r/ucf campus complaints thread",
        "reddit r/UCFstudenthousing thread",
    ],
}

NOTES = {
    "practical_advice": "actionable guidance another student could use",
    "personal_experience": "describes writer's own experience, no clear recommendation",
    "complaint_or_warning": "negative opinion, frustration, or warning",
    "low_info_reaction": "short, joking, or low-detail reaction",
}

practical_advice = [
    "If you're looking off campus, tour the unit in person before signing and ask if the AC and water heater were recently serviced.",
    "Apply for on-campus housing the day applications open; the good dorms like Towers fill up within hours.",
    "Check whether your lease is individual or joint before signing. Joint leases mean you're on the hook if a roommate bails.",
    "Buy a parking permit early and just use Garage A or H, they almost never fill up like the ones near Engineering.",
    "For freshmen, get the unlimited meal plan first semester and downgrade later once you know your eating habits.",
    "Always read recent Google reviews for any complex; management can change completely from one year to the next.",
    "If you have an 8am, park in Garage I and take the shuttle, it's way less stressful than circling the main lots.",
    "Ask the apartment whether utilities are capped or fully included; some places bill you for overage at the end of the semester.",
    "Set up renters insurance. Most off-campus places require it and it's only like 12 bucks a month.",
    "Transfer students should meet with their academic advisor before registering; a lot of credits don't map the way you'd expect.",
    "Don't sign a lease without seeing the actual unit, not just the model. The model is always nicer than what you get.",
    "Use the Knight Lynx free shuttle at night instead of walking back from the library alone.",
    "If you want a quiet dorm, request Hercules or Libra over Towers; the towers area is way more social and loud.",
    "Take photos of your unit's condition the day you move in so you don't get charged for damage later.",
    "Hit campus dining at off-peak times; the Union food court is packed between 12 and 1.",
    "Look into the Pointe or NorthView if you want a pool and gym, but budget for the higher rent.",
    "Freshman tip: go to office hours early in the semester, professors remember the students who show up.",
    "Split groceries with roommates and cook; the meal plan gets expensive fast if you eat out every day.",
    "If your AC breaks, submit a maintenance ticket in writing and keep a copy. Verbal requests get ignored.",
    "Sublease in the summer if you're going home; you can usually find someone in the UCF housing Facebook groups.",
    "Park at the Research Park lots and take the shuttle if you can't find anything near class, it saves a ton of time.",
    "Double check the shuttle actually stops at your complex; some apartments advertise it but the stop is a 15 minute walk away.",
    "Buy a bike or scooter, campus is huge and you'll save yourself the parking headache entirely.",
    "For roommates, write up a basic agreement about cleaning and quiet hours before you move in; it prevents a lot of fights.",
    "If you're on a budget, the dorms are actually cheaper than most off-campus places once you factor in utilities and the shuttle.",
    "Rent or buy textbooks online, the bookstore prices are a scam.",
    "Check the crime map for the area around any off-campus complex before signing; some spots near Alafaya have more break-ins.",
    "Get to campus 30 minutes early the first week if you're driving, parking is a nightmare until things settle down.",
    "Email housing directly if you want a specific roommate; you can request each other before assignments go out.",
    "If you commute, look into the carpool permit, it's cheaper and you get better lot access.",
    "Don't take the first apartment you tour; compare at least three before deciding, prices vary a lot for the same thing.",
    "Keep your renters insurance and lease in a folder, you'll need them if you ever dispute a charge.",
    "For dining, the 63 South spot is your best on-campus option if you're tired of the Union.",
    "Freshmen, don't bring a car your first semester if you live on campus, it's not worth the permit cost and the parking stress.",
    "Ask about the guest and parking policy at off-campus places; some charge guests to park or tow aggressively.",
    "If you're pre-med or engineering, live close to campus, you'll be there late and the commute will wear you down.",
    "Walk your class schedule the week before to figure out the timing between buildings.",
    "Look at Tivoli or Boardwalk if you want something walkable to campus without paying luxury prices.",
    "Set rent reminders; a lot of off-campus places charge steep late fees after the 3rd.",
    "Join the UCF subreddit and your class Discord before the semester, you'll get answers way faster than email.",
    "If maintenance is slow, escalate to the property manager in person, calling rarely works.",
    "Get your financial aid sorted before housing deposits are due so you don't lose your spot.",
    "Bring a surge protector and a fan for the dorms; the outlets are limited and the AC is inconsistent.",
    "Tour during a weekday so you can see how loud the complex actually is, weekends can be misleading.",
    "If you're transferring from Valencia, use DirectConnect advising, they'll tell you exactly what credits count.",
    "Check whether parking is included in your off-campus rent; some complexes charge a separate monthly fee for a spot.",
    "Use the library reservable study rooms during finals and book them a few days ahead because they go fast.",
    "For roommates you don't know, do a video call first and ask about sleep schedules and how clean they keep things.",
    "If safety worries you, only take a ground floor unit if it has good lighting, otherwise go higher up.",
    "Always get your move-out inspection in writing, that's how you protect your deposit.",
    "Sign up for UCF Alert notifications so you know about closures, weather, and safety stuff on campus.",
    "Set up the laundry app early; the dorm machines are app-only and lines build up on weekends.",
    "If you can, choose a complex with individual leases so a roommate moving out doesn't blow up your rent.",
    "Use mobile ordering at the Union or eat before the lunch rush, it cuts the wait dramatically.",
    "Don't rule out small claims if a landlord keeps your deposit unfairly; document everything from day one.",
    "Get involved in a club your first semester, it's the easiest way to actually meet people if you commute.",
    "Ask current residents, not the leasing office, what maintenance is really like before you sign.",
    "If you have early classes, live on the shuttle line or within walking distance, parking before 10am is brutal.",
]

personal_experience = [
    "I lived at Knights Circle last year and the location was convenient, but maintenance took forever when our AC broke.",
    "My freshman year in Towers was honestly a great time, super social and I made most of my friends there.",
    "I stayed at the Pointe at Central and the unit was fine, the pool area was the best part.",
    "We had a joint lease at NorthView and it was okay until one roommate moved out mid-year.",
    "I commuted from Oviedo my first two years and the drive wasn't bad outside of rush hour.",
    "My experience with the meal plan was that I barely used half of it by the end of the semester.",
    "I transferred from Valencia and most of my credits came over without issues.",
    "I lived at the Lofts and the walls were thin, I could hear my neighbor's TV most nights.",
    "I had a single in Libra and it was quiet, which is exactly what I wanted as an introvert.",
    "My roommate and I got randomly matched and it actually worked out great, we still hang out.",
    "I parked in Garage A every day and never really had trouble finding a spot.",
    "The first week of parking was rough for me but after that it calmed down a lot.",
    "I lived off campus near Alafaya and the shuttle was reliable most of the time.",
    "My AC at the Verge went out twice over the summer, took a few days each time to fix.",
    "I did the unlimited meal plan freshman year and ate at the Union most days.",
    "We had a good run at Arden Villas, the townhouse setup gave us a lot of space.",
    "I stayed in Nike my freshman year and the community events were actually fun.",
    "My commute from downtown Orlando was about 35 minutes each way most mornings.",
    "I lived in Hercules and it was super quiet, I barely saw anyone in the halls.",
    "Our place at Boardwalk was close to campus so I could walk to class in ten minutes.",
    "I ate Pegasus dining a lot and it was hit or miss depending on the day.",
    "My roommate situation sophomore year was rough, we just had really different schedules.",
    "I rented at Tivoli and the rent was reasonable for how close it was to campus.",
    "I lived in Apollo and the location near the gym was perfect for me.",
    "My first apartment off campus, the management was slow but the unit itself was nice.",
    "I took the Knight Lynx shuttle home from the library most nights and it was convenient.",
    "We had a two bedroom at Plaza on University and split it, came out pretty affordable.",
    "I did DirectConnect from Seminole State and the transition was smoother than I expected.",
    "My dorm experience was that the laundry machines were always full on weekends.",
    "I lived at the Retreat and the cottages were nice but it was a bit of a drive to class.",
    "I had an 8am all of freshman year and somehow survived parking in Garage I.",
    "My time in UCF housing was fine overall, nothing dramatic, just normal dorm stuff.",
    "I stayed at Union West and the location right by campus made everything easy.",
    "We had roommate drama at our off-campus place but worked it out by midterms.",
    "I ate at 63 South a lot and honestly didn't mind the food.",
    "My freshman roommate and I didn't click but we stayed cordial the whole year.",
    "I lived at the Sterling and the gym there was actually decent.",
    "My parking permit paid off because I had classes spread across the whole day.",
    "I commuted and spent way more time looking for parking than I'd like to admit.",
    "I stayed in Neptune and the suite-style setup was nice for sharing a bathroom.",
    "Touring apartments was a blur for me, they all started to look the same after a while.",
    "I lived at the Lofts for two years and the location grew on me.",
    "My maintenance requests at Knights Circle usually took about a week to get handled.",
    "I did meal swaps with friends and it stretched my plan further than I expected.",
    "My freshman dorm in Libra was small but I didn't really mind it.",
    "I lived off Dean Road and the commute was short but the traffic lights were endless.",
    "My roommate kept different hours than me but we made it work with headphones.",
    "I had a great RA my first year who actually organized fun floor events.",
    "I stayed at the Pointe and the noise from the pool parties got old by spring.",
    "My transfer orientation was helpful and answered most of my questions.",
    "I lived in Towers 4 and the view of campus was honestly great.",
    "My off-campus place flooded once during a summer storm but they fixed it quickly.",
    "I parked at Research Park and took the shuttle; it added time but it worked.",
    "My dining was mostly the Union and I got tired of it by November.",
    "I lived at NorthView and the trash valet was a nice little perk.",
    "My freshman year I shared a room and it taught me a lot about compromise.",
]

complaint_or_warning = [
    "Do not wait until July to find housing, everything decent fills up and the prices spike.",
    "Avoid the Pointe if you care about sleep, the pool parties go until 2am on weekends.",
    "Parking is genuinely awful the first three weeks, leave way earlier than you think you need to.",
    "Maintenance at my complex took three weeks to fix a leaking ceiling, never again.",
    "Watch out for the hidden fees at these luxury complexes, the advertised rent is never what you actually pay.",
    "The dining hall food quality has gone downhill and the prices keep going up.",
    "Steer clear of joint leases unless you fully trust your roommates, you'll pay for their mistakes.",
    "The shuttle is unreliable during peak hours, I've waited 40 minutes more than once.",
    "Don't trust the leasing office when they say maintenance is fast, it almost never is.",
    "The parking situation near Engineering is a joke, you'll circle for half an hour.",
    "Be careful with the Verge, our security deposit disappeared into vague cleaning fees.",
    "The meal plan is overpriced for what you get, I wasted hundreds of dollars on it.",
    "Don't sign before touring, I got stuck in a unit way worse than the model.",
    "They tow aggressively at some off-campus complexes, read the parking rules carefully.",
    "The AC in my dorm broke three times in one semester and they kept patching it instead of fixing it.",
    "Do not rent at that place near Alafaya, our break-in happened within a month of moving in.",
    "The Wi-Fi in the dorms is terrible during finals when everyone's online at once.",
    "Rent went up almost 200 dollars at renewal with zero improvements, total ripoff.",
    "Warning: some complexes lock you into a 12-month lease even if you're only here for fall and spring.",
    "The Union food court is a zoo at lunch and half the spots run out of food.",
    "They nickel and dime you on everything at these places, valet trash, pest control, amenity fees.",
    "Parking permits are way too expensive for how impossible it is to actually find a spot.",
    "Avoid roommate matching if you're picky, I got paired with someone who never cleaned.",
    "The pool at my complex was closed half the summer for repairs but they never adjusted rent.",
    "Don't expect your deposit back, they'll find a reason to keep most of it.",
    "The construction noise near campus housing starts at 7am and it's miserable.",
    "Be warned, the cheaper complexes off campus often have the worst maintenance response times.",
    "They oversold parking permits again this year, it's predatory at this point.",
    "The dorm bathrooms were disgusting because nobody enforced the cleaning schedule.",
    "Avoid the Retreat if you don't have a car, the shuttle is slow and the walk is too far.",
    "My landlord ignored a mold complaint for a month, document everything because they will gaslight you.",
    "The dining options close way too early, good luck eating after 9pm on campus.",
    "Don't believe the move-in date they give you, ours got pushed back two weeks last minute.",
    "The garages flood when it rains hard and nobody warns you before you park there.",
    "Watch out for utility caps that are set artificially low so you always owe extra.",
    "The freshman dorms are way too expensive for how small and dated the rooms are.",
    "They raised the meal plan price again and removed the better dining options, classic.",
    "Don't tour only on weekends, they hide how loud the place gets on weeknights.",
    "The bus loop is constantly delayed and the app arrival times are basically fiction.",
    "Be careful subleasing, I got scammed by someone in a Facebook group, always meet in person.",
    "Parking enforcement will ticket you in two minutes but the lots are never patrolled for safety.",
    "Don't move in sight-unseen from out of state, photos lie and you'll be stuck for a year.",
    "The amenities they advertise are always broken, half the gym equipment at my place was out of order.",
    "Rent at these student complexes is climbing way faster than anything is actually improving.",
    "Warning about the Lofts: paper-thin walls, you'll hear everything your neighbors do.",
    "The leasing staff turns over constantly so nobody ever knows what's going on with your account.",
    "Avoid early morning classes if you commute, there's literally nowhere to park before 10.",
    "They charged us a re-lease fee that was never mentioned anywhere in the original contract.",
    "The dining hall ran out of basically everything good by the time my late class let out.",
    "Don't ignore the fine print on guarantor requirements, it tripped up half my friends.",
    "Pest control at my complex was useless, we had roaches the entire lease.",
    "Be careful with complexes that require renters insurance through their preferred provider, it's overpriced.",
    "Parking decals sell out and then they keep selling overflow passes anyway, it's a scam.",
    "The shuttle stopped running early during breaks with no notice and I got stranded.",
    "Don't renew without negotiating, they bank on you being too lazy to push back on the rent hike.",
    "The maintenance portal is a black hole, my tickets sat open for weeks with no response.",
]

low_info_reaction = [
    "Parking at UCF is cooked lol.",
    "Real.",
    "This is so accurate it hurts.",
    "lmao the parking struggle is eternal.",
    "Towers gang where you at.",
    "Facts.",
    "UCF housing in a nutshell.",
    "Bruh.",
    "Knights Circle slander incoming lol.",
    "Same energy every August.",
    "Crying in commuter.",
    "The shuttle never comes, can confirm.",
    "This but unironically.",
    "Charge it to the game.",
    "lol welcome to UCF.",
    "Pegasus dining strikes again.",
    "It's giving broke college student.",
    "W post.",
    "L parking situation fr.",
    "Garage A supremacy.",
    "We been knew.",
    "Pain.",
    "Not the AC breaking again.",
    "Felt this in my soul.",
    "Average UCF experience tbh.",
    "Nah this is too real.",
    "lol good luck with that.",
    "The Union at noon is a war zone.",
    "Sending thoughts and prayers to the freshmen.",
    "Skull emoji forever.",
    "UCF stands for U Can't Finish parking.",
    "Big facts.",
    "This thread is so UCF.",
    "Cooked, simply cooked.",
    "Me every single morning.",
    "Knights rise up I guess.",
    "lol rip your wallet.",
    "The audacity of these rent prices.",
    "Tell me about it.",
    "So true bestie.",
    "Honestly same.",
    "Couldn't have said it better.",
    "The shuttle app is fiction confirmed.",
    "Welcome to the jungle lol.",
    "Bro I'm done.",
    "Classic UCF moment.",
    "This is why I commute.",
    "Yeah no thanks lol.",
    "Peak Knights experience.",
    "Womp womp.",
]

LABELED = [
    ("practical_advice", practical_advice),
    ("personal_experience", personal_experience),
    ("complaint_or_warning", complaint_or_warning),
    ("low_info_reaction", low_info_reaction),
]

# Sanity check counts.
for label, items in LABELED:
    assert len(items) == len(set(items)), f"duplicate text in {label}"

# Build rows with cycled source per label.
buckets = {}
for label, items in LABELED:
    src = cycle(SOURCES[label])
    buckets[label] = [(t, label, next(src), NOTES[label]) for t in items]

# Interleave labels round-robin so classes are spread across the file.
rows = []
order = [lbl for lbl, _ in LABELED]
idx = {lbl: 0 for lbl in order}
remaining = sum(len(b) for b in buckets.values())
while remaining > 0:
    for lbl in order:
        b = buckets[lbl]
        i = idx[lbl]
        if i < len(b):
            rows.append(b[i])
            idx[lbl] += 1
            remaining -= 1

out_path = os.path.join(os.path.dirname(__file__), "takemeter_ucf_labeled.csv")
with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(["text", "label", "source", "notes"])
    w.writerows(rows)

# Report.
from collections import Counter
counts = Counter(r[1] for r in rows)
print(f"Wrote {len(rows)} rows to {out_path}")
for label, _ in LABELED:
    print(f"  {label:22s} {counts[label]}")
