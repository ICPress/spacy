from flask import Flask
from flask import request
import json
import spacy

class TextInfo:
  def __init__(self, nouns, verbs, entities):
    self.nouns = nouns
    self.verbs = verbs
    self.entities = entities

app = Flask(__name__)
nlp_en = spacy.load("en_core_web_lg")
nlp_en.add_pipe("coreferee")

@app.route("/spacy",  methods = ['POST'])
def analyze():
    data = request.data.decode("utf-8")
    result = analyze(nlp_en,data)
    return json.dumps(result, default=vars), 200, {'ContentType':'application/json'}

def build_tree(token):
    return {
        "text": token.text,
        "lemma": token.lemma_,
        "dep": token.dep_,
        "pos": token.pos_,
        "children": [build_tree(child) for child in token.children]
    }

def resolve_subject(token, doc):
    resolved = doc._.coref_chains.resolve(token)
    if token.pos_ == "PRON" and resolved:
        return ", ".join([t.text for t in resolved])
    return token.text

  
@app.route("/spacyfull", methods=["POST"])
def analyzefull():
    text = request.data.decode("utf-8").strip()
    if not text:
        return jsonify({"error": "Empty input"}), 400

    doc = nlp_en(text)
    results = []

    for sent in doc.sents:
        root = sent.root
        subject = None
        obj = None

        # Find subject anywhere under ROOT
        for token in root.subtree:
            if token.dep_ in ("nsubj", "nsubjpass"):
                subject = resolve_subject(token,doc)

        # Find object candidates
        for token in root.subtree:
            if token.dep_ in ("dobj", "attr", "acomp", "pobj", "xcomp"):
                obj = token.text

        if subject and obj:
            results.append({
                "subject": subject,
                "object": obj,
                "predicate": root.lemma_,
                "sentence": sent.text,
                "root": build_tree(root)
            })

    return json.dumps(results, default=vars), 200, {'ContentType':'application/json'}

def analyze(nlp_lib, data):
    doc = nlp_lib(data)
    return TextInfo([chunk.text for chunk in doc.noun_chunks],[token.lemma_ for token in doc if token.pos_ == "VERB"], [entity.text for entity in doc.ents])

