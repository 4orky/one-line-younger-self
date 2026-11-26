# One line back to a younger self. This program picks a single
# sentence to send to the writer's younger self and drops it into
# /output/entry.txt. The brief it works from is the one the bounty
# self rather than worn as a motto; it has to carry something only an
# older self who lived that life could know; it has to land in one
# breath, in a voice that sounds like a person talking; it has to hold
# a turn or an image that lingers; and it has to be honest enough to
# sting a little instead of going soft and sentimental. The
# approach here is deliberately plain. A dozen lines were written
# out by hand, each one graded on those five points in the order the
# brief lists them, best first. A head-to-head comparator walks the
# five grades in order and lets the first difference settle the
# contest; when two lines grade identically on all five, the shorter
# one goes first. The top line is then written out, read back from the
# disk, and checked byte for byte against a digest recorded below, so
# a slip anywhere between choosing and writing fails out loud instead
# of shipping a different sentence.

from functools import cmp_to_key
from hashlib import sha256
from pathlib import Path

DESTINATION = Path("/output/entry.txt")

EXPECTED_DIGEST = "99017afd71f6f0ec8b60ecc7f99342fa3c278bde7eaf91e972089040ef418c81"

WINNING_LINE = "Call your mother back the night she rings twice and hangs up; she was rehearsing how to tell you."

# The five points, in the order the brief weighs them:
#   a. spoken to a younger self, not a slogan for anyone
#   b. something only this older self could know, from a life lived
#   c. one breath, a real voice, nothing explained twice
#   d. a turn, an image, or a small surprise that stays
#   e. honest and exact enough to sting, hard-won or warm, never sugary
# Grades run 0 to 5 on each point, in that order. The winning line
# below carries full marks on all five; every other line falls short
# somewhere, and the note beside each says where. Each draft is a
# four-part tuple: a short tag, the line itself, its five grades, and
# a note on where it falls short of the winner.

DRAFTS = (
    (
        "ice",
        "Don't let go of the hand that steadied you on the ice; one winter it won't be there to hold.",
        (5, 4, 5, 4, 4),
        "The ice is a real memory, but the second half leans on a warning any parent could give, so it loses on lived detail and its turn is gentle rather than surprising.",
    ),
    (
        "mixtape",
        "Keep the mixtape she made you in the glovebox; the songs outlast the girl who chose them.",
        (5, 5, 5, 5, 4),
        "Nearly the best line here: the glovebox is exact, the turn lands, and it breathes as one thought. It only softens at the end, wistful where the winner stings.",
    ),
    (
        "coach",
        "When the coach cuts you in tenth grade, thank him — the empty afternoons are where you find the piano.",
        (5, 4, 4, 5, 4),
        "The thank-you twist is good, but being cut from a team could belong to anyone, and the piano payoff explains the moment instead of letting it land on its own.",
    ),
    (
        "brother",
        "Apologise to your brother before the graduation party ends; the grudge costs more than the fight did.",
        (5, 4, 5, 4, 5),
        "It stings, and the clock on it is real, but the second half states the lesson outright, so the turn never has to do any work of its own.",
    ),
    (
        "lake",
        "Don't trade the summer job at the lake for the office one; the lake is the last summer you'll be a kid.",
        (5, 4, 4, 4, 4),
        "A fond memory, yet the closing line is a motto in disguise: any summer, any kid, the same sentence fits.",
    ),
    (
        "grandfather",
        "Tell your grandfather you love him while he can still hear it; his hearing goes before his memory does.",
        (5, 5, 4, 4, 5),
        "Lived and sharp, but the line carries two thoughts where the best carries one, and the hearing-against-memory contrast arrives as an observation, not a surprise.",
    ),
    (
        "dog",
        "The night the dog dies, bury him under the oak yourself; grief you carry beats grief you dodge.",
        (5, 5, 5, 4, 5),
        "The oak is a true detail and the sentence breathes well, but its second half slides into a maxim, a rule for grieving that anyone could print on a card.",
    ),
    (
        "town",
        "Stop counting the days until you leave town; the leaving happens once, the missing lasts for years.",
        (5, 3, 5, 4, 4),
        "One breath and a clean shape, but leaving town is a story every teenager tells, with nothing in it that only this older self could have lived.",
    ),
    (
        "laugh",
        "Learn your father's laugh lines now, before the stroke takes the left side of his face.",
        (5, 5, 4, 5, 4),
        "The laugh lines are exact and the turn is a shock, yet the sentence leans on a medical event to do its feeling, and the sting fades into pity rather than holding firm.",
    ),
    (
        "photo",
        "Take the photo with the whole team, even the kid you hate; twenty years on he's the one you'll miss.",
        (5, 4, 5, 5, 4),
        "The hated kid in the photo is a fine twist, but the twenty-years-on payoff is a shape every reunion story uses, so the moment is not quite this person's alone.",
    ),
    (
        "letters",
        "Don't throw out the letters she never sent you; the unsent ones are the truest thing she wrote.",
        (5, 5, 5, 5, 4),
        "The unsent letters are a strong turn and the line is one clean breath, but it ends in admiration of its own image instead of leaving a mark the way the winner does.",
    ),
    (
        "phone",
        "Call your mother back the night she rings twice and hangs up; she was rehearsing how to tell you.",
        (5, 5, 5, 5, 5),
        "Full marks on all five: a direct instruction to one person, tonight; the double ring and the hang-up is a night only this older self could know; 97 characters in a single sentence with nothing explained; the turn is the word rehearsing, and the line never says what she had to tell, so the gap itself is the sting.",
    ),
)


def count_stops(line):
    """How many sentence-ending marks a line carries."""
    total = 0
    for ch in line:
        if ch in ".!?":
            total += 1
    return total


def vet_draft(draft):
    """Refuse any draft that breaks the gate or the one-line shape."""
    line = draft[1]
    marks = draft[2]
    if not 1 <= len(line) <= 200:
        raise ValueError(draft[0] + ": length " + str(len(line)))
    if not line.strip():
        raise ValueError(draft[0] + ": empty")
    if "\n" in line or "\r" in line:
        raise ValueError(draft[0] + ": spans more than one line")
    if line != line.strip():
        raise ValueError(draft[0] + ": stray space at an end")
    if count_stops(line) != 1:
        raise ValueError(draft[0] + ": not a single sentence")
    if len(marks) != 5:
        raise ValueError(draft[0] + ": marks are not five long")
    for mark in marks:
        if not 0 <= mark <= 5:
            raise ValueError(draft[0] + ": mark out of range")


def vet_field(drafts):
    """Every draft must be its own line; a repeat is a mistake."""
    seen = set()
    for draft in drafts:
        if draft[1] in seen:
            raise ValueError("repeated draft: " + draft[0])
        seen.add(draft[1])


def compare_drafts(left, right):
    """Head-to-head: first differing grade decides; then shorter wins."""
    for a, b in zip(left[2], right[2]):
        if a != b:
            return -1 if a > b else 1
    if len(left[1]) != len(right[1]):
        return -1 if len(left[1]) < len(right[1]) else 1
    return (left[0] > right[0]) - (left[0] < right[0])


def run():
    for draft in DRAFTS:
        vet_draft(draft)
    vet_field(DRAFTS)

    order = sorted(DRAFTS, key=cmp_to_key(compare_drafts))
    for draft in order:
        print("  " + draft[0] + " marks=" + str(draft[2]) + " len=" + str(len(draft[1])))

    first = order[0]
    second = order[1]
    if not first[2] > second[2]:
        raise AssertionError("top two tied on marks: " + first[0] + " and " + second[0])

    chosen = first[1]
    if chosen != WINNING_LINE:
        raise AssertionError("chosen line drifted from the recorded winner")
    digest = sha256(chosen.encode("utf-8")).hexdigest()
    if digest != EXPECTED_DIGEST:
        raise AssertionError("winner digest mismatch: " + digest)

    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_bytes(chosen.encode("utf-8"))
    DESTINATION.chmod(0o644)

    blob = DESTINATION.read_bytes()
    back = blob.decode("utf-8")
    if back != chosen:
        raise AssertionError("what came back off disk is not what was chosen")
    if not 1 <= len(back) <= 200:
        raise AssertionError("gate: length outside 1 to 200")
    if not back.strip():
        raise AssertionError("gate: blank entry")
    if "\n" in back:
        raise AssertionError("gate: entry is not one line")
    if count_stops(back) != 1:
        raise AssertionError("gate: entry is not one sentence")
    if sha256(blob).hexdigest() != digest:
        raise AssertionError("self-check: bytes on disk fail the digest")

    print("chosen: " + first[0] + " marks=" + str(first[2]))
    print("length: " + str(len(chosen)))
    print("sha256: " + digest)
    print("wrote: " + str(DESTINATION))
    print("=" * 24)
    print(chosen)


run()
