import unittest
from subprocess import Popen, PIPE, CalledProcessError
import sys
from os import linesep


def run_script(args):
    cmd = [sys.executable, "decorate_ydk.py", "test_readme_examples_card_info.json"] + args.split(" ")
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    p.wait()
    output, error = p.communicate()
    if p.returncode != 0 or error:
        raise CalledProcessError("Subprocess failed %d %s %s" % (p.returncode, output, error))
    # On Windows, the linesep in the output will be \r\n rather than \n
    #   which python uses internally
    return output.decode(sys.stdout.encoding).replace(linesep, "\n")


class ReadmeExamplesTests(unittest.TestCase):

    def test_example_in(self):
        output = run_script("in --input_file test_readme_examples_card_list.ydk")
        self.assertEqual(output, """Here are my cards:
32274490 Skull Servant
28933734 Mask of Darkness
28933734 Mask of Darkness
20228463 Ceremonial Bell
55144522 Pot of Greed
81439173 Foolish Burial
81439173 Foolish Burial
""")

    def test_example_n(self):
        # This test is not the exact same as the README
        # It runs on the input rather than the output
        output = run_script("i --input_file test_readme_examples_card_list.ydk")
        self.assertEqual(output, """Here are my cards:
32274490
28933734
28933734
20228463
55144522
81439173
81439173
""")

    def test_example_nitarsld(self):
        output = run_script("nitarsld --input_file test_readme_examples_card_list.ydk")
        self.assertEqual(output, """Here are my cards:
Skull Servant    32274490 Normal Monster      DARK  Zombie      300/200 Lv1 A skeletal ghost that isn't strong but can mean trouble in large numbers.
Mask of Darkness 28933734 Flip Effect Monster DARK  Fiend       900/400 Lv2 FLIP: Target 1 Trap in your GY; add that target to your hand.
Mask of Darkness 28933734 Flip Effect Monster DARK  Fiend       900/400 Lv2 FLIP: Target 1 Trap in your GY; add that target to your hand.
Ceremonial Bell  20228463 Effect Monster      LIGHT Spellcaster 0/1850  Lv3 Both players must keep their hands revealed.
Pot of Greed     55144522 Spell Card                Normal                  Draw 2 cards.
Foolish Burial   81439173 Spell Card                Normal                  Send 1 monster from your Deck to the GY.
Foolish Burial   81439173 Spell Card                Normal                  Send 1 monster from your Deck to the GY.
""")
