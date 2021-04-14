import xml.etree.ElementTree as ET

from LANGUAGE_MODEL_FUNCTIONS import read_csv, sample_datasets
from flair.data import Sentence, Corpus, TARSCorpus
from flair.datasets import TREC_6, AMAZON_REVIEWS
from flair.models.multitask_model.task_model import RefactoredTARSClassifier
from flair.models.tars_tagger_model import TARSTagger
from flair.models.text_classification_model import TARSClassifier
from flair.trainers import ModelTrainer

def extract_XML(path):
    data = []
    tree = ET.parse(path)
    root = tree.getroot()
    for sentence in root.findall('sentence'):
        text = sentence.find("text").text
        flair_sentence = Sentence(text)
        for token in flair_sentence:
            token.set_label("polarity", "O")
        aspectTerms = sentence.find("aspectTerms")
        if aspectTerms:
            for aspectTerm in aspectTerms:
                _from = int(aspectTerm.get('from'))
                _to = int(aspectTerm.get('to'))
                term = aspectTerm.get("term")
                polarity = f"{aspectTerm.get('polarity')} aspect"
                _curr_from = 0
                _curr_to = 0
                for token in flair_sentence:
                    _curr_to += len(token.text) + 1
                    if _curr_from - len(term) < _from < _curr_from + len(term):
                        if _curr_to - len(term) < _to < _curr_to + len(term):
                            if term.__contains__(token.text):
                                token.set_label("polarity", polarity)
                    _curr_from = _curr_to

        data.append(flair_sentence)

    return data

def main():

    laptop_data = extract_XML('aspect_data/Laptop_Train_v2.xml')

    laptop_corpus = Corpus(laptop_data)
    tars_tagger = TARSTagger("laptop_aspect", laptop_corpus.make_tag_dictionary("polarity"), tag_type="polarity", embeddings=model)

    trainer = ModelTrainer(tars_tagger, laptop_corpus)

    trainer.train(base_path=f"testy",  # path to store the model artifacts
                  learning_rate=0.02,  # use very small learning rate
                  mini_batch_size=16,
                  mini_batch_chunk_size=8,
                  max_epochs=20,
                  embeddings_storage_mode='none')

if __name__ == "__main__":
    import flair
    flair.device = "cuda:1"
    main()