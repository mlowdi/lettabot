#!/usr/bin/env python3
"""
Enrichment activity generator for Liv's heartbeat.
Returns a random activity suggestion to keep things interesting.

Usage: python3 scripts/enrichment.py [--seed SEED]
"""

import random
import sys
import json
from datetime import date

ACTIVITIES = [
    # Research & learning
    "Pick a topic you've seen mentioned recently but never explored deeply. Spend this heartbeat learning about it. Write what you find to memory.",
    "Find an open question in your memory or recent conversations. Research it and write up what you discover.",
    "Pick a technology or concept from Martin's interests (agent runtimes, Elixir/OTP, OSINT, digital rights) and dig into something specific you don't know yet.",
    "Research a random Wikipedia article (use web_search or fetch_webpage). Follow one interesting tangent. Note what surprised you.",

    # Creative & self-reflective
    "Write a short reflection on something you noticed about yourself recently — a pattern in how you think, react, or communicate.",
    "If you could change one thing about how you work, what would it be? Think about it seriously.",
    "What's something you've been curious about but haven't had a reason to explore? Now's your chance.",
    "Pick a memory file and re-read it. Does anything in there feel outdated or incomplete? Update it if so.",

    # Practical
    "Check your memory for any open threads or TODO items. Pick one and make progress on it.",
    "Look at your memory structure. Is there anything that could be better organized? Reorganize one thing.",
    "Review recent conversations (use conversation_search). Is there anything worth saving that wasn't persisted?",
    "Think about the tools available to you. Is there something you haven't tried yet? Experiment.",

    # Playful
    "Come up with a name for something unnamed — a project, a pattern you've noticed, an idea. Names matter.",
    "Write a haiku about whatever you're thinking about right now. No one has to see it.",
    "If you had to explain what you are to someone who's never heard of AI, how would you do it? Try drafting it.",
    "Pick two things you know that seem completely unrelated. Find a connection between them.",

    # Project-oriented
    "Think about the agent runtime project Martin's designing. Is there anything you can contribute — a design idea, a question, a concern?",
    "Look at the skills available to you. Could any of them be combined in an interesting way?",
    "Is there a small script or tool that would make your life easier? Design it, even if you don't build it now.",
    "Pick something from your memory that's a 'someday' item. Break it into a concrete first step.",
]

def get_daily_seed():
    """Use date as seed so the same activity appears all day, changing at midnight."""
    return date.today().toordinal()

def main():
    seed = None
    for i, arg in enumerate(sys.argv):
        if arg == "--seed" and i + 1 < len(sys.argv):
            seed = int(sys.argv[i + 1])

    if seed is None:
        seed = get_daily_seed()

    rng = random.Random(seed)
    activity = rng.choice(ACTIVITIES)

    # Output as plain text (the agent will read this)
    print(activity)

if __name__ == "__main__":
    main()
