import spacy
nlp = spacy.load("en_ner_bc5cdr_md")


import joblib

joblib.dump(nlp, "nlp.pkl")