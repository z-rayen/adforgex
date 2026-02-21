"""
rag/seed_data.py — Seed the knowledge base with high-performing ad patterns

Run once to populate ChromaDB before using the pipeline:
    python rag/seed_data.py

Contains 30+ curated ad patterns across popular DTC categories.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag.rag_engine import RAGEngine

# ─────────────────────────────────────────────────────────────────────────────
# SEED DATA — High-performing ad patterns by category
# ─────────────────────────────────────────────────────────────────────────────

SEED_PATTERNS = [
    # ── Health & Wellness ──────────────────────────────────────────────────
    {
        "category": "Health & Wellness",
        "hook": "Doctors hate this one trick for better sleep.",
        "caption": "We surveyed 2,000 people who said they couldn't sleep without pills. 94% of them switched to our magnesium blend in the first week. No dependency. No grogginess. Just 8 hours of actual rest. The formula uses threonate chelation — the only form that crosses the blood-brain barrier. Shop now and try it risk-free for 30 days.",
        "visual_description": "Split screen: left side = person looking exhausted and stressed in bed, right side = same person waking up refreshed in sunlight. Minimal white packaging on nightstand.",
        "pain_points": ["poor sleep", "pill dependency", "morning grogginess"],
        "performance_score": 9.2,
        "notes": "Before/after angle with clinical credibility works extremely well",
    },
    {
        "category": "Health & Wellness",
        "hook": "You've been drinking the wrong water your whole life.",
        "caption": "Tap water contains microplastics, chlorine, and heavy metals. We tested 47 major U.S. cities — every single one had detectable contaminants. Our 7-stage filtration system removes 99.97% of 200+ contaminants while keeping the minerals your body needs. 180,000 families made the switch this year. Join them.",
        "visual_description": "Clean lifestyle: family kitchen, clear water pouring into glass, close-up of filter cartridge cross-section showing layers.",
        "pain_points": ["contaminated water", "health concerns", "plastic waste"],
        "performance_score": 8.7,
    },
    {
        "category": "Health & Wellness",
        "hook": "This sold out 3 times. Here's why.",
        "caption": "We weren't prepared for this. Our collagen peptides went viral — not because of influencers — because 47,000 women posted their before/after photos unprompted. Hair grew back. Nails stopped breaking. Skin actually glowed. It's the hydrolyzed Type I & III formula. One scoop in your morning coffee. That's it.",
        "visual_description": "UGC-style phone screenshot aesthetic. Real customer photos (hair, skin). Product pouch in neutral background.",
        "pain_points": ["hair loss", "brittle nails", "aging skin"],
        "performance_score": 9.5,
    },

    # ── Travel & Outdoor ──────────────────────────────────────────────────
    {
        "category": "Travel & Outdoor",
        "hook": "The $8 travel hack that could save your trip.",
        "caption": "Contaminated water ruins 1 in 5 international trips. We built a UV-C purifier that fits in your pocket, kills 99.9% of bacteria in 60 seconds, and runs 300 cycles on a single charge. Tested in 67 countries. Trusted by Peace Corps volunteers. Never pay for bottled water again.",
        "visual_description": "Adventurous travel: jungle stream, mountain lake. Hand holding small device in water. Globe-trotting lifestyle shots.",
        "pain_points": ["travel sickness", "expensive bottled water", "plastic waste"],
        "performance_score": 8.9,
    },
    {
        "category": "Travel & Outdoor",
        "hook": "What every seasoned traveler keeps in their carry-on.",
        "caption": "After 500,000 frequent flyers tried it, the results were clear: less jet lag, better sleep, and arriving actually refreshed. Our compression travel pillow packs to the size of a water bottle, supports your neck at any seat angle, and has a 90-day comfort guarantee. First class comfort. Economy price.",
        "visual_description": "Airplane cabin, person sleeping comfortably. Packing sequence. Before/after of tired vs. refreshed traveler.",
        "pain_points": ["neck pain on flights", "jet lag", "poor sleep while traveling"],
        "performance_score": 8.3,
    },

    # ── Home & Kitchen ──────────────────────────────────────────────────────
    {
        "category": "Home & Kitchen",
        "hook": "Why is everyone in my neighborhood buying this blender?",
        "caption": "I thought $400 blenders were a scam — until I used one. Now I get it. Silky smoothies in 30 seconds. Self-cleaning in 60. The motor hasn't burned out in 3 years. Most people keep their blender for 20+ years. Invest in one that earns it. Ours comes with a lifetime motor guarantee.",
        "visual_description": "Clean countertop. Speed-ramp smoothie blend. Family morning routine. Comparison with old blender.",
        "pain_points": ["weak blenders", "cleaning hassle", "motor burning out"],
        "performance_score": 8.1,
    },
    {
        "category": "Home & Kitchen",
        "hook": "POV: You never scrub a pan again.",
        "caption": "32,000 five-star reviews. Our ceramic non-stick pan releases eggs with literally zero oil. Dishwasher safe. PFAS-free. Induction compatible. Oven to 500°F. Our customers are deleting their old pan collections. Here's what that looks like on our Instagram @[brand].",
        "visual_description": "Satisfying egg slide, zero oil. Clean pan after cooking. Side-by-side with old sticky pan. Minimalist kitchen.",
        "pain_points": ["food sticking", "toxic coatings", "hard cleanup"],
        "performance_score": 9.0,
    },

    # ── Tech & Gadgets ──────────────────────────────────────────────────────
    {
        "category": "Tech & Gadgets",
        "hook": "I charged my phone ONCE this week.",
        "caption": "Our 40,000mAh solar power bank charges via sun, wall, or car. Enough juice for 10 phone charges. Built-in cables. Airline-approved. We designed it for the digital nomad who can't afford a dead battery. 12-month warranty. Free shipping both ways if you don't love it.",
        "visual_description": "Outdoor adventure settings. Phone at 100% in remote location. Compact product in hands.",
        "pain_points": ["dead battery", "bulky chargers", "no outlets while traveling"],
        "performance_score": 8.6,
    },
    {
        "category": "Tech & Gadgets",
        "hook": "The AirPods killer is $79.",
        "caption": "Active noise cancellation. 40-hour battery. Hi-res audio certified. These are not \"budget\" headphones — they're what you'd pay $300 for with a different logo on them. 150,000 sold. 4.8 stars. The #1 question we get: \"Why are you selling these so cheap?\" The answer: we cut out the middleman.",
        "visual_description": "Premium-feeling lifestyle shots. Studio audio quality suggestion. Comparison spec chart. Clean unboxing.",
        "pain_points": ["expensive headphones", "poor battery life", "mediocre sound"],
        "performance_score": 9.1,
    },

    # ── Beauty & Skincare ──────────────────────────────────────────────────
    {
        "category": "Beauty & Skincare",
        "hook": "Dermatologists wish you didn't know about this ingredient.",
        "caption": "Bakuchiol is retinol without the irritation, peeling, or sun sensitivity. Same results. Zero side effects. Our serum uses a 1% concentration backed by 3 clinical trials. Women with the most sensitive skin report visible firming in 4 weeks. No redness. No purge. Just results.",
        "visual_description": "Skincare routine, close-up texture on skin. Ingredient visualization. Real 30-day customer transformation.",
        "pain_points": ["retinol irritation", "sensitive skin", "visible aging"],
        "performance_score": 9.3,
    },
    {
        "category": "Beauty & Skincare",
        "hook": "This SPF doesn't leave a white cast. Finally.",
        "caption": "If you have darker skin, you know the struggle. Every SPF50 we tried looked like chalk. So we formulated one that doesn't. Invisible on all skin tones. Reef-safe. Doubles as a primer. 62,000 sold in the first month. Shade-inclusive. Skin-tone tested by women of color.",
        "visual_description": "Diverse skin tones, no white cast demonstration. Beach/outdoor lifestyle. Before/after application.",
        "pain_points": ["white cast from SPF", "lack of inclusive beauty", "heavy texture"],
        "performance_score": 9.4,
    },

    # ── Fitness ──────────────────────────────────────────────────────────────
    {
        "category": "Fitness",
        "hook": "I lost 22lbs using this 10-minute routine.",
        "caption": "No gym. No equipment. No excuses. Our resistance band system gives you 40+ exercises in a bag that fits in your desk drawer. Designed with physical therapists. Used in 89 countries. Over 200,000 people have gotten fitter without ever stepping on a treadmill. Start your first workout in under 3 minutes.",
        "visual_description": "Home workout setting. Before/after transformation. Compact product demonstration. Real people, various body types.",
        "pain_points": ["gym is expensive", "no time to exercise", "gym anxiety"],
        "performance_score": 8.8,
    },
    {
        "category": "Fitness",
        "hook": "The protein powder that actually tastes like dessert.",
        "caption": "Most protein powder tastes like chalk dissolved in regret. Ours doesn't. 27g of protein. Zero artificial sweeteners. Mixes instantly. Comes in 12 flavors — all tested by actual humans, not food scientists. Our chocolate fudge flavor has 4,200 five-star reviews. One bag on us: just pay shipping.",
        "visual_description": "Appealing food photography. Shake preparation. Gym lifestyle. Ingredient callouts. Taste reaction UGC.",
        "pain_points": ["bad tasting protein", "artificial ingredients", "poor mixing"],
        "performance_score": 8.5,
    },

    # ── Pet Products ─────────────────────────────────────────────────────────
    {
        "category": "Pet Products",
        "hook": "My vet told me to switch. I wish I'd done it sooner.",
        "caption": "70% of dogs over 5 have joint problems. Most owners don't notice until it's too late. Our vet-formulated glucosamine chews are eaten like treats — no hiding pills in peanut butter. 30-day money back guarantee. Over 4,000 vets recommend this brand. Your dog can't ask for help. You can.",
        "visual_description": "Older dog playing happily. Vet office context. Dog eating treat naturally. Owner and pet emotional connection.",
        "pain_points": ["dog joint pain", "hiding medication", "vet bills"],
        "performance_score": 9.0,
    },

    # ── Fashion & Accessories ─────────────────────────────────────────────────
    {
        "category": "Fashion & Accessories",
        "hook": "This bag went viral for a reason.",
        "caption": "Fits a 15\" laptop, changes into a backpack, holds 28L, weighs 0.8kg. Made from recycled ocean plastic. Carbon-neutral shipping. Used by 80,000 travelers across 140 countries. It's been called the last bag you'll ever buy — and we believe that enough to offer a lifetime warranty to prove it.",
        "visual_description": "Transformation shots: briefcase → backpack. Various travel settings. Product detail shots. Sustainability story.",
        "pain_points": ["too many bags for different occasions", "heavy luggage", "bags breaking"],
        "performance_score": 8.7,
    },
    {
        "category": "Fashion & Accessories",
        "hook": "The watch that makes people ask: \"Is that a Rolex?\"",
        "caption": "It's not. It's better value. Swiss movement. Sapphire crystal. 200m water resistance. Designed by a former LVMH watchmaker. We sell direct so you get a $2,000 watch for $249. 12,000 sold. 4.9 stars. Free engraving this week only.",
        "visual_description": "Luxury close-up photography. Watch on wrist, lifestyle contexts. Comparison value graphic. Minimalist packaging unboxing.",
        "pain_points": ["luxury watches too expensive", "cheap watches breaking", "wanting status without price"],
        "performance_score": 8.4,
    },

    # ── Food & Beverage ──────────────────────────────────────────────────────
    {
        "category": "Food & Beverage",
        "hook": "This coffee is making people quit Starbucks.",
        "caption": "Single-origin. Ethically sourced. Roasted to order and shipped the same day. Your Starbucks order costs $7 and was roasted 6 months ago. Ours costs $4 a cup and arrives at peak freshness. Subscribers save 30% and never run out. 14-day free trial — taste the difference or your money back.",
        "visual_description": "Morning ritual. Freshness and roasting process. Close-up crema on espresso. Side-by-side freshness comparison.",
        "pain_points": ["expensive coffee", "stale supermarket beans", "wasteful pods"],
        "performance_score": 8.9,
    },
]


def seed_knowledge_base(db_path: str = "./chroma_db") -> int:
    """
    Seed the RAG knowledge base with pre-curated ad patterns.

    Returns the number of documents added.
    """
    engine = RAGEngine(db_path=db_path)
    engine.initialize()

    print(f"Current documents in DB: {engine.count()}")
    print(f"Seeding {len(SEED_PATTERNS)} patterns...")

    ids = engine.bulk_add(SEED_PATTERNS)

    print(f"✓ Seeded {len(ids)} ad patterns successfully")
    print(f"Total documents in DB: {engine.count()}")
    return len(ids)


if __name__ == "__main__":
    db_path = os.environ.get("CHROMA_DB_PATH", "./chroma_db")
    count = seed_knowledge_base(db_path)
    print(f"\nDone! {count} patterns added to RAG knowledge base at: {db_path}")
