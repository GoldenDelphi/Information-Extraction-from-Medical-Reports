from flask import Flask, request, render_template
import pandas as pd
import re
import joblib
from flaskext.markdown import Markdown

app = Flask(__name__)
Markdown(app)

@app.route('/', methods=['GET', 'POST'])
def main():
    
    if request.method == "POST":
        data = True;
        nlp = joblib.load("nlp.pkl")
        
        transcription = request.form.get("transcription")
        transcription = re.sub('(\.,)', ". ", transcription)
        
        doc = nlp(transcription)

        from spacy import displacy
        body = displacy.render(doc, style='ent', options = {"ents": ['DISEASE', 'CHEMICAL'], "colors": {"DISEASE": "#7fc8a9", "CHEMICAL": "#E98563"}}, page=True) 
        body = body.replace("\n\n","\n")

        regex_doc = re.compile(r'(doctor|dr|doc|dr.).?\s([a-z]+)\s?([a-z]+)?', re.IGNORECASE)
        regex_location = re.compile(r'(location|loc|city|state|address|add.).?\s([a-z]+)', re.IGNORECASE)
        regex_date = re.compile(r'(date|year|year).?\s([\d]{1,2}/[\d]{1,2}/[\d]{2,4})', re.IGNORECASE)

        doctors = []
        doctor = regex_doc.search(transcription)
        try:
            doctors.append(doctor.group(2) + " " + doctor.group(3))
        except:
            doctors.append("No Doctor Found")
        locations = []
        location = regex_location.search(transcription)
        try:
            locations.append(location.group(2))
        except:
            locations.append("No Location Found")
        date = regex_date.search(transcription)
        try:
            date = date.group(2)
        except:
            date = "No date found"

        # print("DOCS: ", doctors)
        # print("LOCATIONS: ", locations)

        from spacy.matcher import Matcher
        pattern = [{'ENT_TYPE':'CHEMICAL'}, {'LIKE_NUM': True}, {'IS_ASCII': True}]
        matcher = Matcher(nlp.vocab)
        matcher.add("DRUG_DOSE", [pattern])

        matches = matcher(doc)
        medications = []
        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]  
            span = doc[start:end]  
            medications.append(span.text)
        # print("THIS IS MEDICATIONS", medications)
        if not medications:
            medications.append("No Medications Found")


        pattern = [{'ENT_TYPE':'DISEASE'}]
        matcher = Matcher(nlp.vocab)
        matcher.add("DIAGNOSIS", [pattern])
        
        matches = matcher(doc)
        
        diseases = []
        for ent in doc.ents:
            if(ent.label_ == "DISEASE"):
                diseases.append(ent.text)
        # print("THIS IS DISEASES", diseases)
        if not diseases:
            diseases.append("No Diseases Found")

        
    else:
        data = False;
        doctors = ["Not given"]
        locations = ["Not given"]
        date= "Not given"
        body = "Your output will appear here"
        diseases = ["No diseases found"]
        medications = ["No medications found"]
        
    return render_template("index.html", data = data, body = body, doctors = doctors, docLength = len(doctors), locations = locations, locLength = len(locations), date = date, diseases = diseases, disLength = len(diseases), medications = medications, medLength = len(medications))

if __name__ == '__main__':
    app.run(debug = True)
