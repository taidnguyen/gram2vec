from dataclasses import dataclass



@dataclass
class TestSentence:
    truth:str
    text:str


PATTERNS = {
"it-cleft": r"\([^-]*-be-[^-]*-ROOT.*\([iI]t-it-PRP-nsubj\).*\([^-]*-[^-]*-NN[^-]*-attr.*\([^-]*-[^-]*-VB[^-]*-relcl",
"psuedo-cleft": r"\([^-]*-be-[^-]*-ROOT.*\([^-]*-[^-]*-(WP|WRB)-(dobj|advmod)",
"all-cleft" : r"(\([^-]*-be-[^-]*-[^-]*\([^-]*-all-(P)?DT-[^-]*.*)|(\([^-]*-all-(P)?DT-[^-]*.*\([^-]*-be-VB[^-]*-[^-]*)",
"there-cleft": r"\([^-]*-be-[^-]*-[^-]*.*\([^-]*-there-EX-expl.*\([^-]*-[^-]*-[^-]*-attr",
"if-because-cleft" : r"\([^-]*-be-[^-]*-ROOT\([^-]*-[^-]*-[^-]*-advcl\([^-*]*-if-IN-mark",
"passive" : r"\([^-]*-[^-]*-(NN[^-]*|PRP)-nsubjpass.*\([^-]*-be-[^-]*-auxpass"
}

template = [
    TestSentence("TRUE", ""),
    TestSentence("TRUE", ""),
    TestSentence("TRUE", ""),
    TestSentence("TRUE", ""),
    TestSentence("TRUE", ""),
    TestSentence("TRUE", ""),
    TestSentence("FALSE", ""),
    TestSentence("FALSE", ""),
    TestSentence("FALSE", ""),
]

psuedo_cleft_sents = [
    TestSentence("TRUE", "What I want is some peace and quiet!"),
    TestSentence("TRUE", "What you need to do is to rest for a while."),
    TestSentence("TRUE", "Where I want to go is a place so far away from here."),
    TestSentence("TRUE", "How she paid for her food was with her credit card."),
    TestSentence("TRUE", "Some peace and quiet is what I want."),
    TestSentence("TRUE", "A place so far away from here is where I want to go."),
    TestSentence("FALSE", "I want a hamburger."),
    TestSentence("FALSE", "Where did I put that potato?"),
    TestSentence("FALSE", "I like having peace and quiet"),
    TestSentence("FALSE", "What I need is none of your business."),
]

all_cleft_sents = [
    TestSentence("TRUE", "All Jimmy wants for Christmas is a brand new bicycle."),
    TestSentence("TRUE", "All the girl does is complain about everything"),
    TestSentence("TRUE", "Was all she wanted a good job?"),
    TestSentence("TRUE", "Was all Jeff saw blue and yellow?"),
    TestSentence("TRUE", "Was all she saw blue and yellow?"),
    TestSentence("TRUE", "Was all the dog saw blue and yellow?"),
    TestSentence("TRUE", "Was all Jeff saw the moon?"),
    TestSentence("TRUE", "All the dog in the tree knew was that the bone was on the grass."),
    TestSentence("TRUE", "While riding her bike, all Sarah thought about was seeing her friends at the ball game."),
    TestSentence("FALSE", "I want all of these shirts"),
    TestSentence("FALSE", "The boxes were all filled with potatoes"),
    TestSentence("FALSE", "In all of this time, I have never seen a goose."),
]

there_cleft_sents = [
    TestSentence("TRUE", "There's this orphan kid that I'm trying to adopt."),
    TestSentence("TRUE", "There is a new car Camille wanted to buy"),
    TestSentence("TRUE", "There are five ducks swimming in the pool"),
    TestSentence("TRUE", "There is a new James Bond movie that I want to watch tomorrow."),
    TestSentence("TRUE", "Is there a new TV show that Mary wants to watch?"),
    TestSentence("FALSE","I want to walk over there"),
    TestSentence("FALSE", "Cindy and Mindy go there everyday."),
    TestSentence("FALSE", "In the future, I will eat lunch over there"),
    TestSentence("FALSE", "There is a unicorn in the garden"),
]

if_because_cleft_sents = [
    TestSentence("TRUE", "If he wants to be a millionaire, it's because he wants to help poor children"),
    TestSentence("TRUE", "If it seems that she is meddling, it's just because she's just trying to help the family."),
    TestSentence("TRUE", "If the dog in the tree is crying, it's only because he is hungry."),
    TestSentence("TRUE", "If Sam and Tom are married, it's because they're in love"),
    TestSentence("TRUE", "If she wanted to drive to Florida, it's because she hates flying."),
    TestSentence("TRUE", "If I ate the chicken, it's because I like meat."),
    TestSentence("FALSE", "If I wanted to, I could go to the mall"),
    TestSentence("FALSE", "Because I am young, I can do anything"),
    TestSentence("FALSE", "Sarah ate the ham sandwhich because she was hungry"),
]

passive_sents = [
    TestSentence("TRUE", "The lion was killed by the hunter."),
    TestSentence("TRUE", "English is spoken all over the world"),
    TestSentence("TRUE", "The book which was given to me by Mary was really interesting."),
    TestSentence("TRUE", "The book given to me by Mary was really interesting"),
    TestSentence("TRUE", "The windows have been cleaned"),
    TestSentence("TRUE", "The work will be finished soon"),
    TestSentence("TRUE", "They might have been invited to the party"),
    TestSentence("TRUE", "John might have been invited to the party"),
    TestSentence("FALSE", "The cat is chasing the rat"),
    TestSentence("FALSE", "He is always doing things by the books"),
    TestSentence("FALSE", "The dwarf is sitting by the fire"),
]

