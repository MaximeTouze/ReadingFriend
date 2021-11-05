import math
import os
import re
import fse
import gensim
import gensim.downloader as api
import nltk
import numpy as np
import pandas as pd
from fse import SplitIndexedList
from fse.models import uSIF
from nltk.corpus import stopwords
from sklearn import metrics
from sklearn.metrics.pairwise import cosine_similarity
import logging
import re
import unicodedata
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from nltk.tokenize import word_tokenize
from transformers import BertForQuestionAnswering, BertTokenizer

nltk.download('wordnet')
nltk.download('stopwords')

pd.set_option('display.max_colwidth', -1)

# Reading in the dataset
df1 = pd.read_csv('./dataset/S08_question_answer_pairs.txt', sep='\t')
df2 = pd.read_csv('./dataset/S09_question_answer_pairs.txt', sep='\t')
df3 = pd.read_csv('./dataset/S10_question_answer_pairs.txt', sep='\t', encoding = 'ISO-8859-1')
frames = [df1, df2, df3]
df = pd.concat(frames)

def getArticleText(file):
    fpath = './dataset/text_data/'+file+'.txt.clean'
    try:
        f = open(fpath, 'r')
        text = f.read()
    except UnicodeDecodeError:
        f = open(fpath, 'r', encoding = 'ISO-8859-1')
        text = f.read()
    return text

df = df.dropna(subset=['ArticleFile'])
df = df.dropna(subset=['Answer'])
df['ArticleText'] = df['ArticleFile'].apply(lambda x: getArticleText(x))
df['ArticleText'] = df['ArticleText'].apply(lambda x: re.sub(r'(\n)+', '. ', x))
df = df.drop(['DifficultyFromQuestioner', 'DifficultyFromAnswerer', 'ArticleFile'], axis='columns')

# stop_words = set(stopwords.words('english'))
def cleanQuestion(text):
    text = str(text)
    # wnl = nltk.stem.WordNetLemmatizer()
    text = text.lower()
    words = re.sub(r'[^\w\s]', '', text).split()
    # words = [word for word in words if not word in stop_words]
    return " ".join([word for word in words])

def cleanAnswer(text):
    text = str(text)
    # wnl = nltk.stem.WordNetLemmatizer()
    text = text.lower()
    words = re.sub(r'[^\w\s]', '', text).split()
    # words = [word for word in words if not word in stop_words]
    return " ".join([word for word in words])

def cleanText(text):
    text = str(text)
    # wnl = nltk.stem.WordNetLemmatizer()
    text = text.lower()
    words = re.sub(r'[^\w\s\.\?]', '', text).split()
    # words = [word for word in words if not word in stop_words]
    return " ".join([word for word in words])

df['Question'] = df['Question'].apply(lambda x: cleanQuestion(x))
df['Answer'] = df['Answer'].apply(lambda x: cleanAnswer(x))
df['ArticleText'] = df['ArticleText'].apply(lambda x: cleanText(x))



# SIF



from fse.models import uSIF

glove = api.load("glove-wiki-gigaword-100")
model_sif = uSIF(glove, workers=2, lang_freq="en")

def getSim(q, x):
    x = (str(x).split(), 0)
    sim = metrics.pairwise.cosine_similarity(model_sif.infer([q]), model_sif.infer([x]))
    return sim

def getBestAnswer(question, potentials):
    q = (str(question).split(), 0)
    c = pd.DataFrame(potentials)
    c['sim'] = c[0].apply(lambda x: getSim(q, x))
    max = c.sort_values(by='sim', ascending=False).iloc[:3]
    return max[0]



# BERT with SIF



use_cuda = True

if(not(os.path.isfile("./model/pytorch_model.bin"))):
    #tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    model_bert = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    #tokenizer.save_pretrained('./model')
    model_bert.save_pretrained('./model')
else:
    #tokenizer = BertTokenizer.from_pretrained('./model')
    model_bert = BertForQuestionAnswering.from_pretrained('./model')

model_sif.train(SplitIndexedList(list(df['ArticleText'])))

def get_split(text1):

    #Reference: https://medium.com/@armandj.olivares/using-bert-for-classifying-documents-with-long-texts-5c3e7b04573d

    l_total = []
    l_parcial = []
    if len(text1.split())//150 >0:
        n = len(text1.split())//150
    else:
        n = 1
    for w in range(n):
        if w == 0:
            l_parcial = text1.split()[:250]
            l_total.append(" ".join(l_parcial))
        else:
            l_parcial = text1.split()[w*150:w*150 + 250]
            l_total.append(" ".join(l_parcial))
    return l_total

def getAnswerBert(question, context):

    # print('Query Context has {} tokens.'.format(len(tokenizer.encode(context))))

    context_list = get_split(context)

    ans = []

    for c in context_list:

        encoding = tokenizer.encode_plus(text=question,text_pair=c)

        inputs = encoding['input_ids']  #Token embeddings
        token_type_id = encoding['token_type_ids']  #Segment embeddings
        tokens = tokenizer.convert_ids_to_tokens(inputs) #input tokens

        output = model_bert(input_ids=torch.tensor([inputs]), token_type_ids=torch.tensor([token_type_id]))
        start_index = torch.argmax(output.start_logits)
        end_index = torch.argmax(output.end_logits)

        answer = ' '.join(tokens[start_index:end_index+1])

        ans.append(answer)
    print('Question: ', question)

    potentials = []
    for i in ans:
        if ('SEP' not in i) and ('CLS' not in i):
            potentials.append(re.sub('(#)+', '', i))

    answer = getBestAnswer(question, potentials)

    # print('Potential Answers: \n')
    # print(answer.head())
    return answer

text = """
We were in class when the head-master came in, followed by a “new fellow,” not wearing the school uniform, and a school servant carrying a large desk. Those who had been asleep woke up, and every one rose as if just surprised at his work.
The head-master made a sign to us to sit down. Then, turning to the class-master, he said to him in a low voice—
“Monsieur Roger, here is a pupil whom I recommend to your care; he’ll be in the second. If his work and conduct are satisfactory, he will go into one of the upper classes, as becomes his age.”
The “new fellow,” standing in the corner behind the door so that he could hardly be seen, was a country lad of about fifteen, and taller than any of us. His hair was cut square on his forehead like a village chorister’s; he looked reliable, but very ill at ease. Although he was not broad-shouldered, his short school jacket of green cloth with black buttons must have been tight about the arm-holes, and showed at the opening of the cuffs red wrists accustomed to being bare. His legs, in blue stockings, looked out from beneath yellow trousers, drawn tight by braces, He wore stout, ill-cleaned, hob-nailed boots.
We began repeating the lesson. He listened with all his ears, as attentive as if at a sermon, not daring even to cross his legs or lean on his elbow; and when at two o’clock the bell rang, the master was obliged to tell him to fall into line with the rest of us.
When we came back to work, we were in the habit of throwing our caps on the ground so as to have our hands more free; we used from the door to toss them under the form, so that they hit against the wall and made a lot of dust: it was “the thing.”
But, whether he had not noticed the trick, or did not dare to attempt it, the “new fellow,” was still holding his cap on his knees even after prayers were over. It was one of those head-gears of composite order, in which we can find traces of the bearskin, shako, billycock hat, sealskin cap, and cotton night-cap; one of those poor things, in fine, whose dumb ugliness has depths of expression, like an imbecile’s face. Oval, stiffened with whalebone, it began with three round knobs; then came in succession lozenges of velvet and rabbit-skin separated by a red band; after that a sort of bag that ended in a cardboard polygon covered with complicated braiding, from which hung, at the end of a long thin cord, small twisted gold threads in the manner of a tassel. The cap was new; its peak shone.
“Rise,” said the master.
He stood up; his cap fell. The whole class began to laugh. He stooped to pick it up. A neighbor knocked it down again with his elbow; he picked it up once more.
“Get rid of your helmet,” said the master, who was a bit of a wag.
There was a burst of laughter from the boys, which so thoroughly put the poor lad out of countenance that he did not know whether to keep his cap in his hand, leave it on the ground, or put it on his head. He sat down again and placed it on his knee.
“Rise,” repeated the master, “and tell me your name.”
The new boy articulated in a stammering voice an unintelligible name.
“Again!”
The same sputtering of syllables was heard, drowned by the tittering of the class.
“Louder!” cried the master; “louder!”
The “new fellow” then took a supreme resolution, opened an inordinately large mouth, and shouted at the top of his voice as if calling someone in the word “Charbovari.”
A hubbub broke out, rose in crescendo with bursts of shrill voices (they yelled, barked, stamped, repeated “Charbovari! Charbovari”), then died away into single notes, growing quieter only with great difficulty, and now and again suddenly recommencing along the line of a form whence rose here and there, like a damp cracker going off, a stifled laugh.
However, amid a rain of impositions, order was gradually re-established in the class; and the master having succeeded in catching the name of “Charles Bovary,” having had it dictated to him, spelt out, and re-read, at once ordered the poor devil to go and sit down on the punishment form at the foot of the master’s desk. He got up, but before going hesitated.
“What are you looking for?” asked the master.
“My c-a-p,” timidly said the “new fellow,” casting troubled looks round him.
“Five hundred lines for all the class!” shouted in a furious voice stopped, like the Quos ego[1], a fresh outburst. “Silence!” continued the master indignantly, wiping his brow with his handkerchief, which he had just taken from his cap. “As to you, ‘new boy,’ you will conjugate ‘ridiculus sum’[2] twenty times.”
[1] A quotation from the Aeneid signifying a threat.

[2] I am ridiculous.

Then, in a gentler tone, “Come, you’ll find your cap again; it hasn’t been stolen.”
Quiet was restored. Heads bent over desks, and the “new fellow” remained for two hours in an exemplary attitude, although from time to time some paper pellet flipped from the tip of a pen came bang in his face. But he wiped his face with one hand and continued motionless, his eyes lowered.
In the evening, at preparation, he pulled out his pens from his desk, arranged his small belongings, and carefully ruled his paper. We saw him working conscientiously, looking up every word in the dictionary, and taking the greatest pains. Thanks, no doubt, to the willingness he showed, he had not to go down to the class below. But though he knew his rules passably, he had little finish in composition. It was the cure of his village who had taught him his first Latin; his parents, from motives of economy, having sent him to school as late as possible.
His father, Monsieur Charles Denis Bartolome Bovary, retired assistant-surgeon-major, compromised about 1812 in certain conscription scandals, and forced at this time to leave the service, had taken advantage of his fine figure to get hold of a dowry of sixty thousand francs that offered in the person of a hosier’s daughter who had fallen in love with his good looks. A fine man, a great talker, making his spurs ring as he walked, wearing whiskers that ran into his moustache, his fingers always garnished with rings and dressed in loud colours, he had the dash of a military man with the easy go of a commercial traveller.
Once married, he lived for three or four years on his wife’s fortune, dining well, rising late, smoking long porcelain pipes, not coming in at night till after the theatre, and haunting cafes. The father-in-law died, leaving little; he was indignant at this, “went in for the business,” lost some money in it, then retired to the country, where he thought he would make money.
But, as he knew no more about farming than calico, as he rode his horses instead of sending them to plough, drank his cider in bottle instead of selling it in cask, ate the finest poultry in his farmyard, and greased his hunting-boots with the fat of his pigs, he was not long in finding out that he would do better to give up all speculation.
For two hundred francs a year he managed to live on the border of the provinces of Caux and Picardy, in a kind of place half farm, half private house; and here, soured, eaten up with regrets, cursing his luck, jealous of everyone, he shut himself up at the age of forty-five, sick of men, he said, and determined to live at peace.
His wife had adored him once on a time; she had bored him with a thousand servilities that had only estranged him the more. Lively once, expansive and affectionate, in growing older she had become (after the fashion of wine that, exposed to air, turns to vinegar) ill-tempered, grumbling, irritable. She had suffered so much without complaint at first, until she had seem him going after all the village drabs, and until a score of bad houses sent him back to her at night, weary, stinking drunk. Then her pride revolted. After that she was silent, burying her anger in a dumb stoicism that she maintained till her death. She was constantly going about looking after business matters. She called on the lawyers, the president, remembered when bills fell due, got them renewed, and at home ironed, sewed, washed, looked after the workmen, paid the accounts, while he, troubling himself about nothing, eternally besotted in sleepy sulkiness, whence he only roused himself to say disagreeable things to her, sat smoking by the fire and spitting into the cinders.
When she had a child, it had to be sent out to nurse. When he came home, the lad was spoilt as if he were a prince. His mother stuffed him with jam; his father let him run about barefoot, and, playing the philosopher, even said he might as well go about quite naked like the young of animals. As opposed to the maternal ideas, he had a certain virile idea of childhood on which he sought to mould his son, wishing him to be brought up hardily, like a Spartan, to give him a strong constitution. He sent him to bed without any fire, taught him to drink off large draughts of rum and to jeer at religious processions. But, peaceable by nature, the lad answered only poorly to his notions. His mother always kept him near her; she cut out cardboard for him, told him tales, entertained him with endless monologues full of melancholy gaiety and charming nonsense. In her life’s isolation she centered on the child’s head all her shattered, broken little vanities. She dreamed of high station; she already saw him, tall, handsome, clever, settled as an engineer or in the law. She taught him to read, and even, on an old piano, she had taught him two or three little songs. But to all this Monsieur Bovary, caring little for letters, said, “It was not worth while. Would they ever have the means to send him to a public school, to buy him a practice, or start him in business? Besides, with cheek a man always gets on in the world.” Madame Bovary bit her lips, and the child knocked about the village.
He went after the labourers, drove away with clods of earth the ravens that were flying about. He ate blackberries along the hedges, minded the geese with a long switch, went haymaking during harvest, ran about in the woods, played hop-scotch under the church porch on rainy days, and at great fetes begged the beadle to let him toll the bells, that he might hang all his weight on the long rope and feel himself borne upward by it in its swing. Meanwhile he grew like an oak; he was strong on hand, fresh of colour.
When he was twelve years old his mother had her own way; he began lessons. The curé took him in hand; but the lessons were so short and irregular that they could not be of much use. They were given at spare moments in the sacristy, standing up, hurriedly, between a baptism and a burial; or else the curé, if he had not to go out, sent for his pupil after the Angelus[3]. They went up to his room and settled down; the flies and moths fluttered round the candle. It was close, the child fell asleep, and the good man, beginning to doze with his hands on his stomach, was soon snoring with his mouth wide open. On other occasions, when Monsieur le Curé, on his way back after administering the viaticum to some sick person in the neighbourhood, caught sight of Charles playing about the fields, he called him, lectured him for a quarter of an hour and took advantage of the occasion to make him conjugate his verb at the foot of a tree. The rain interrupted them or an acquaintance passed. All the same he was always pleased with him, and even said the “young man” had a very good memory.
[3] A devotion said at morning, noon, and evening, at the sound of a bell. Here, the evening prayer.

Charles could not go on like this. Madame Bovary took strong steps. Ashamed, or rather tired out, Monsieur Bovary gave in without a struggle, and they waited one year longer, so that the lad should take his first communion.
Six months more passed, and the year after Charles was finally sent to school at Rouen, where his father took him towards the end of October, at the time of the St. Romain fair.
It would now be impossible for any of us to remember anything about him. He was a youth of even temperament, who played in playtime, worked in school-hours, was attentive in class, slept well in the dormitory, and ate well in the refectory. He had in loco parentis[4] a wholesale ironmonger in the Rue Ganterie, who took him out once a month on Sundays after his shop was shut, sent him for a walk on the quay to look at the boats, and then brought him back to college at seven o’clock before supper. Every Thursday evening he wrote a long letter to his mother with red ink and three wafers; then he went over his history note-books, or read an old volume of “Anarchasis” that was knocking about the study. When he went for walks he talked to the servant, who, like himself, came from the country.
[4] In place of a parent.

By dint of hard work he kept always about the middle of the class; once even he got a certificate in natural history. But at the end of his third year his parents withdrew him from the school to make him study medicine, convinced that he could even take his degree by himself.
His mother chose a room for him on the fourth floor of a dyer’s she knew, overlooking the Eau-de-Robec. She made arrangements for his board, got him furniture, table and two chairs, sent home for an old cherry-tree bedstead, and bought besides a small cast-iron stove with the supply of wood that was to warm the poor child.
Then at the end of a week she departed, after a thousand injunctions to be good now that he was going to be left to himself.
The syllabus that he read on the notice-board stunned him; lectures on anatomy, lectures on pathology, lectures on physiology, lectures on pharmacy, lectures on botany and clinical medicine, and therapeutics, without counting hygiene and materia medica—all names of whose etymologies he was ignorant, and that were to him as so many doors to sanctuaries filled with magnificent darkness.
He understood nothing of it all; it was all very well to listen—he did not follow. Still he worked; he had bound note-books, he attended all the courses, never missed a single lecture. He did his little daily task like a mill-horse, who goes round and round with his eyes bandaged, not knowing what work he is doing.
To spare him expense his mother sent him every week by the carrier a piece of veal baked in the oven, with which he lunched when he came back from the hospital, while he sat kicking his feet against the wall. After this he had to run off to lectures, to the operation-room, to the hospital, and return to his home at the other end of the town. In the evening, after the poor dinner of his landlord, he went back to his room and set to work again in his wet clothes, which smoked as he sat in front of the hot stove.
On the fine summer evenings, at the time when the close streets are empty, when the servants are playing shuttle-cock at the doors, he opened his window and leaned out. The river, that makes of this quarter of Rouen a wretched little Venice, flowed beneath him, between the bridges and the railings, yellow, violet, or blue. Working men, kneeling on the banks, washed their bare arms in the water. On poles projecting from the attics, skeins of cotton were drying in the air. Opposite, beyond the roots spread the pure heaven with the red sun setting. How pleasant it must be at home! How fresh under the beech-tree! And he expanded his nostrils to breathe in the sweet odours of the country which did not reach him.
He grew thin, his figure became taller, his face took a saddened look that made it nearly interesting. Naturally, through indifference, he abandoned all the resolutions he had made. Once he missed a lecture; the next day all the lectures; and, enjoying his idleness, little by little, he gave up work altogether. He got into the habit of going to the public-house, and had a passion for dominoes. To shut himself up every evening in the dirty public room, to push about on marble tables the small sheep bones with black dots, seemed to him a fine proof of his freedom, which raised him in his own esteem. It was beginning to see life, the sweetness of stolen pleasures; and when he entered, he put his hand on the door-handle with a joy almost sensual. Then many things hidden within him came out; he learnt couplets by heart and sang them to his boon companions, became enthusiastic about Beranger, learnt how to make punch, and, finally, how to make love.
Thanks to these preparatory labours, he failed completely in his examination for an ordinary degree. He was expected home the same night to celebrate his success. He started on foot, stopped at the beginning of the village, sent for his mother, and told her all. She excused him, threw the blame of his failure on the injustice of the examiners, encouraged him a little, and took upon herself to set matters straight. It was only five years later that Monsieur Bovary knew the truth; it was old then, and he accepted it. Moreover, he could not believe that a man born of him could be a fool.
So Charles set to work again and crammed for his examination, ceaselessly learning all the old questions by heart. He passed pretty well. What a happy day for his mother! They gave a grand dinner.
Where should he go to practice? To Tostes, where there was only one old doctor. For a long time Madame Bovary had been on the look-out for his death, and the old fellow had barely been packed off when Charles was installed, opposite his place, as his successor.
But it was not everything to have brought up a son, to have had him taught medicine, and discovered Tostes, where he could practice it; he must have a wife. She found him one—the widow of a bailiff at Dieppe—who was forty-five and had an income of twelve hundred francs. Though she was ugly, as dry as a bone, her face with as many pimples as the spring has buds, Madame Dubuc had no lack of suitors. To attain her ends Madame Bovary had to oust them all, and she even succeeded in very cleverly baffling the intrigues of a pork-butcher backed up by the priests.
Charles had seen in marriage the advent of an easier life, thinking he would be more free to do as he liked with himself and his money. But his wife was master; he had to say this and not say that in company, to fast every Friday, dress as she liked, harass at her bidding those patients who did not pay. She opened his letter, watched his comings and goings, and listened at the partition-wall when women came to consult him in his surgery.
She must have her chocolate every morning, attentions without end. She constantly complained of her nerves, her chest, her liver. The noise of footsteps made her ill; when people left her, solitude became odious to her; if they came back, it was doubtless to see her die. When Charles returned in the evening, she stretched forth two long thin arms from beneath the sheets, put them round his neck, and having made him sit down on the edge of the bed, began to talk to him of her troubles: he was neglecting her, he loved another. She had been warned she would be unhappy; and she ended by asking him for a dose of medicine and a little more love.
"""

question = "What's Charles Bovary's father's job ?"

print("début")

print(getAnswerBert(question, text))
