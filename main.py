#!/usr/bin/env python3
"""One Line to Your Younger Self — make.fun program/v1 entry.

Writes the chosen single line to /output/entry.txt.

Gate (competition.yaml): /output/entry.txt must be UTF-8 text of 1 to 200
characters, not only white space. The entry is one line, in English, that
its writer would send back to their younger self: no explanation, no
context, no second sentence.

The program drafts twelve candidate lines by hand, scores each against the
judge's criteria in their stated order, and deterministically picks the best
(ties go to the shorter text). It then writes the winner, re-reads the file
from disk, and verifies the bytes, the character count, the single-line
shape, and the SHA-256 self-check before exiting.

Second pass (revision): the pick is now pinned and decisive. The winner's
SHA-256 is recorded below as WINNER_SHA256 and asserted on every run, so
any accidental edit to the winning line — or a scoring change that picks a
different line — fails loudly instead of silently writing a different
entry. The pick must also beat the runner-up on the score tuple itself,
never on the length tiebreak alone: a tie at the top means the scoring
needs a real decision, not a coin flip by character count.
"""

import hashlib
import os
import re
import sys

OUTPUT_PATH = os.environ.get("OUTPUT_PATH", "/output/entry.txt")

# Pinned digest of the winning line (candidate F). Asserted on every run:
# the entry that ships must be exactly this text, byte for byte.
WINNER_SHA256 = "99017afd71f6f0ec8b60ecc7f99342fa3c278bde7eaf91e972089040ef418c81"

# Judge criteria, in their stated order (most important first):
#   1. The entry is a single line its writer would tell their younger self;
#      a slogan, a quote, or a line addressed to nobody in particular loses
#      to any line actually told to a younger self.
#   2. It says something only this person's older self could say, drawn
#      from a life actually lived rather than a motto anyone could wear.
#   3. It lands in one breath, in a real voice, with no explaining and no
#      second sentence doing the work.
#   4. It carries a turn, an image, or a small surprise that stays after
#      one reading.
#   5. It is honest and specific enough to sting a little, hard-won or warm
#      rather than sentimental.
#
# Scores below are hand-scores on a 0-5 scale per criterion, in order.
# The total is lexicographic: criterion 1 outranks 2, 2 outranks 3, and so
# on. Ties on the full tuple go to the shorter text.

CANDIDATES = [
    {
        "id": "A",
        "text": (
            "Don't throw away the letters your grandmother writes you; "
            "one day her handwriting will be the only voice of hers "
            "you have left."
        ),
        # Specific (grandmother's letters, her handwriting) and the turn
        # lands — handwriting as a voice — but "one day" does explanatory
        # work, and the second clause spells out what the first only
        # needed to imply.
        "scores": (5, 4, 4, 4, 4),
    },
    {
        "id": "B",
        "text": (
            "Keep the bike your father fixed with duct tape; the summer "
            "it finally breaks is the summer you learn to fix things "
            "yourself."
        ),
        # Duct tape is a real, lived detail, but the payoff drifts into
        # motto territory: "learn to fix things yourself" is a lesson
        # anyone could wear, and it explains the moment instead of
        # letting it sting.
        "scores": (5, 4, 3, 4, 3),
    },
    {
        "id": "C",
        "text": (
            "Say yes when the girl in the red coat asks you to dance at "
            "the winter formal; she says no to everyone else."
        ),
        # A sharp image (the red coat, the winter formal) and a genuine
        # surprise in the second clause, but the shape is generic advice
        # ("say yes when...") and the moment is one any teenager could
        # have lived, not one only this older self knows.
        "scores": (5, 4, 4, 5, 4),
    },
    {
        "id": "D",
        "text": (
            "The night Dad doesn't come home, sit with Mum at the kitchen "
            "table and don't try to fix it -- just stay."
        ),
        # Very lived: a named night, a kitchen table, a father who does
        # not come home. It stings and it is warm. Slightly weaker on
        # the turn: "just stay" is the lesson stated plainly rather than
        # a surprise the reader has to catch.
        "scores": (5, 5, 4, 4, 5),
    },
    {
        "id": "E",
        "text": (
            "Don't sell your grandfather's watch to buy the car; the car "
            "rusts, and the watch is the only thing of his you'll ever "
            "hold again."
        ),
        # Concrete and hard-won (watch against car, rust against
        # holding), and the last clause stings. The middle clause
        # ("the car rusts") explains the trade instead of trusting the
        # image, so it lands a fraction slower than the best.
        "scores": (5, 5, 4, 5, 5),
    },
    {
        "id": "F",
        "text": (
            "Call your mother back the night she rings twice and hangs "
            "up; she was rehearsing how to tell you."
        ),
        # Revision (second pass): the first draft ended "she was
        # practicing how to tell you." "Practicing" is vague — practicing
        # the call itself, or the words? "Rehearsing" pins the image:
        # a mother alone, running through the sentences of bad news
        # before she dares to say them. The revision keeps the line at
        # one sentence and one breath while making the turn exact.
        # The strongest on every criterion in order: the double ring and
        # the hang-up is a detail only this older self could know
        # (criterion 2); 97 characters, one sentence, no explaining
        # (criterion 3); the unsaid "what" is the surprise that stays
        # (criterion 4); it stings without ever turning sentimental
        # (criterion 5).
        "scores": (5, 5, 5, 5, 5),
    },
    {
        "id": "G",
        "text": (
            "When the teacher says you'll never amount to anything, keep "
            "the note she wrote on your report -- you'll frame it."
        ),
        # "You'll frame it" is a good turn, but "you'll never amount to
        # anything" is a cliche every school story uses, so the moment
        # fails criterion 2: it could belong to anyone.
        "scores": (5, 3, 4, 4, 3),
    },
    {
        "id": "I",
        "text": (
            "The summer you turn sixteen, don't take the job at the mill "
            "-- take the bus to the city and audition."
        ),
        # Specific summer, specific choice, but "audition" is vague about
        # what for, and there is no turn and no sting: it reads as a
        # fork in the road, not a line only an older self could write.
        "scores": (5, 4, 4, 3, 3),
    },
    {
        "id": "J",
        "text": (
            "Keep every ticket stub from the shows you sneak into; one "
            "day you'll wish you could prove you were there."
        ),
        # Ticket stubs are a nice image, but "one day you'll wish" is
        # generic regret language, and the payoff (proving you were
        # there) is soft: it never says why being there mattered.
        "scores": (5, 4, 4, 4, 3),
    },
    {
        "id": "L",
        "text": (
            "Don't throw out the blue jumper with the hole in the elbow; "
            "your daughter will wear it to her first day of school."
        ),
        # A lovely time-collapse: the jumper outlives its owner and
        # reaches the next generation. Strong turn and image. It leans
        # a touch sentimental for criterion 5 — warmth that asks to be
        # admired rather than a line that stings.
        "scores": (5, 5, 4, 5, 4),
    },
    {
        "id": "N",
        "text": (
            "Write down what your grandfather says about the war the "
            "night he finally talks; he never says it twice."
        ),
        # "He never says it twice" is a real turn and it stings. Weaker
        # on the breath: "Write down what..." opens as an instruction,
        # and the line carries two clauses where the best carries one
        # thought.
        "scores": (5, 5, 4, 4, 5),
    },
    {
        "id": "O",
        "text": (
            "The morning you find the ring in your father's coat pocket, "
            "put it back -- some questions are better asked by him."
        ),
        # A mystery with a good image (the ring, the coat pocket), but
        # the second clause slides into aphorism: "some questions are
        # better asked by him" is a motto anyone could wear, which
        # costs it on criterion 2.
        "scores": (5, 5, 4, 5, 4),
    },
]


ABBREVIATIONS = ("Mrs.", "Mr.", "Ms.", "Dr.", "St.", "Jr.", "Sr.")


def sentence_count(text: str) -> int:
    """Count sentences (a sentence ends with . ! or ?).

    Abbreviations such as "Mrs." are not sentence ends.
    """
    cleaned = text.strip()
    for abbr in ABBREVIATIONS:
        cleaned = cleaned.replace(abbr, abbr[:-1])
    return len(re.findall(r"[.!?](?:\s|$)", cleaned))


def check_candidate(candidate: dict) -> None:
    """Validate one candidate against the gate and the one-line shape."""
    text = candidate["text"]
    assert 1 <= len(text) <= 200, f"{candidate['id']}: {len(text)} chars"
    assert text.strip(), f"{candidate['id']}: blank"
    assert "\n" not in text, f"{candidate['id']}: not a single line"
    assert not text.endswith(" "), f"{candidate['id']}: trailing space"
    assert sentence_count(text) == 1, (
        f"{candidate['id']}: not one sentence: {text!r}"
    )
    assert len(candidate["scores"]) == 5, f"{candidate['id']}: scores"


def check_all_unique(candidates) -> None:
    """No two candidates may be byte-identical (the field dedupes them)."""
    seen = {}
    for candidate in candidates:
        if candidate["text"] in seen:
            raise AssertionError(
                f"candidates {seen[candidate['text']]} and {candidate['id']} are identical"
            )
        seen[candidate["text"]] = candidate["id"]


def pick_best(candidates):
    """Deterministic pick: best score tuple, ties go to the shorter text."""
    ranked = sorted(
        candidates,
        key=lambda c: (tuple(-s for s in c["scores"]), len(c["text"])),
    )
    return ranked[0]


def main() -> int:
    for candidate in CANDIDATES:
        check_candidate(candidate)
    check_all_unique(CANDIDATES)

    ranked = sorted(
        CANDIDATES,
        key=lambda c: (tuple(-s for s in c["scores"]), len(c["text"])),
    )
    for candidate in ranked:
        print(
            f"  {candidate['id']}: scores {candidate['scores']} "
            f"chars {len(candidate['text'])}"
        )

    best = pick_best(CANDIDATES)
    text = best["text"]
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    # Decisive pick: the winner must beat the runner-up on the score tuple
    # itself, not on the length tiebreak. A tie at the top is a scoring
    # failure, not a pick.
    assert ranked[0]["scores"] > ranked[1]["scores"], (
        f"pick not decisive: {ranked[0]['id']} and {ranked[1]['id']} tie "
        f"on scores {ranked[0]['scores']}"
    )
    # Pinned output: the shipped entry must be exactly the recorded winner.
    assert digest == WINNER_SHA256, (
        f"winner digest {digest} != pinned {WINNER_SHA256}: "
        "the winning line or its scores changed"
    )

    os.makedirs(os.path.dirname(OUTPUT_PATH) or ".", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.chmod(OUTPUT_PATH, 0o644)

    # Re-read from disk and verify: bytes, length, shape, self-check.
    with open(OUTPUT_PATH, "rb") as f:
        raw = f.read()
    on_disk = raw.decode("utf-8")
    assert on_disk == text, "on-disk text differs from chosen text"
    assert 1 <= len(on_disk) <= 200, "gate: length out of range"
    assert on_disk.strip(), "gate: blank"
    assert "\n" not in on_disk, "gate: not a single line"
    assert sentence_count(on_disk) == 1, "gate: not one sentence"
    assert hashlib.sha256(raw).hexdigest() == digest, "SHA-256 self-check failed"

    print(f"picked: candidate {best['id']} (scores {best['scores']})")
    print(f"chars: {len(text)}")
    print(f"sha256: {digest}")
    print(f"wrote: {OUTPUT_PATH}")
    print("---")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
