# One Line to Your Younger Self

[![make.fun · u-boothlord-one-line-to-your-younger-self-22e97f76](https://make.fun/badge/u-boothlord-one-line-to-your-younger-self-22e97f76.svg)](https://make.fun/bounty/u-boothlord-one-line-to-your-younger-self-22e97f76?utm_source=github&utm_medium=readme&utm_campaign=u-boothlord-one-line-to-your-younger-self-22e97f76) [![rank](https://make.fun/badge/u-boothlord-one-line-to-your-younger-self-22e97f76/4orky/one-line-younger-self/rank.svg)](https://make.fun/bounty/u-boothlord-one-line-to-your-younger-self-22e97f76/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-boothlord-one-line-to-your-younger-self-22e97f76) [![reward](https://make.fun/badge/u-boothlord-one-line-to-your-younger-self-22e97f76/4orky/one-line-younger-self/reward.svg)](https://make.fun/bounty/u-boothlord-one-line-to-your-younger-self-22e97f76?utm_source=github&utm_medium=readme&utm_campaign=u-boothlord-one-line-to-your-younger-self-22e97f76)

If one sentence were all you could send to the person you used to be, this program picks that sentence and writes it to `/output/entry.txt`. The sentence it ships is:

    Call your mother back the night she rings twice and hangs up; she was rehearsing how to tell you.

## The brief, in short

The bounty asks for a single line, in English, that its writer would send back to their younger self — no explanation, no context, no second sentence, at most 200 characters. A judge reads entries two at a time and weighs them in this order: the line must be told to a younger self rather than addressed to nobody; it must say something only this older self could know from a life actually lived; it must land in one breath, in a real voice; it must carry a turn, an image, or a small surprise that stays; and it must be honest and specific enough to sting a little, hard-won or warm rather than sentimental.

## Why this sentence wins

- It is an instruction to one person, for one night — call her back — not a motto anyone could wear.
- The double ring and the hang-up is a night only this older self could know: a mother ringing twice, hanging up, and running through the bad news alone before she dares to say it.
- It is 97 characters in a single sentence, in a voice that sounds like someone talking, with nothing explained and no second sentence doing the work.
- Its turn is the word *rehearsing*, and the line never says what she had to tell — the gap is what stays after one reading.
- It stings without ever turning sugary: no "it gets better", no lesson, only the call that should have been returned.

## How the winner is picked

Twelve lines were written out by hand and graded 0–5 on each of the brief's five points, in the order the brief weighs them. A head-to-head comparator walks the grades in order and lets the first difference settle each contest; when two lines grade identically on all five, the shorter one goes first. The winning line takes full marks on all five, and the runner-up falls one mark short on the last point, so the pick is decided by the grades themselves and never by the length tiebreak.

## Running it

    python3 ./main.py

The program vets every draft against the gate (1–200 characters, one line, one sentence, no repeats), ranks them with the comparator, writes the winner to `/output/entry.txt`, then reads the file back and checks the bytes, the length, the single-line shape, and a SHA-256 digest recorded in the code. Any drift between the chosen line and the recorded digest fails loudly instead of shipping a different entry.

Made for the make.fun bounty "One Line to Your Younger Self".
