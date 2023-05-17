from cleantext import clean
from os.path import isfile
from pickle import load as pickle_load, dump as pickle_dump
from sys import argv
from torch.cuda import is_available as cuda_is_available
from transformers import pipeline as transformers_pipeline

class Cache:

    def __init__(self, cache_name):
        self.cache = None if cache_name is None else (pickle_load(open(cache_name, "rb")) if isfile(cache_name) else {})
        self.cache_name = cache_name

    def set(self, key, value):
        if self.cache is not None:
            self.cache[key] = value
            if self.cache_name:
                pickle_dump(self.cache, open(self.cache_name, "wb"))

    def get(self, key, default=None):
        return default if self.cache is None else self.cache.get(key, default)


class BaseTranslator:

    def __init__(self, device=None, model_name=None, service_url=None, cache_name=None):
        self.device = ("cuda:0" if cuda_is_available() else "cpu") if device is None else device
        if model_name is None and service_url is None:
            raise RuntimeError("Neither model name nor service URL provided!")
        self.pipeline = None if model_name is None else transformers_pipeline("translation", model_name, device=device)
        self.service_url = service_url
        self.cache = Cache(cache_name)

    def translate_text(self, text):
        if cached_text := self.cache.get(text):
            return cached_text
        if self.pipeline is not None:
            new_sentences = []
            sentences = clean(text, lang="da", lower=False).split(". ")
            for i in range(len(sentences)):
                sentence = sentences[i]
                if i+1 < len(sentences):
                    sentence += "."
                new_sentence = self.pipeline(sentence)[0]['translation_text'] if any((c.isalpha() for c in sentence)) else sentence
                print("REPR",repr(sentence), repr(new_sentence))
                new_sentences.append(new_sentence)
            new_text = " ".join(new_sentences)
        self.cache.set(text, new_text)
        return new_text

    def runs_compatible(self, r1, r2):
        raise NotImplementedError("Please use a subclass of BaseTranslator!")

    def add_run(self, para, run, new_text):
        raise NotImplementedError("Please use a subclass of BaseTranslator!")

    def translate_para(self, para):
        runs = list(para.runs)
        print("OLD","|".join((run.text for run in runs)))
        new_runs = []
        while runs:
            run, runs = runs[0], runs[1:]
            text = run.text
            while runs and self.runs_compatible(run, runs[0]):
                text += runs[0].text
                runs = runs[1:]
            run.text = text
            new_runs.append(run)
        para.clear()
        for run in new_runs:
            new_text = self.translate_text(run.text)
            self.add_run(para, run, new_text)
        print("NEW","|".join((run.text for run in para.runs)))

    def translate_document(self, document):
        raise NotImplementedError("Please use a subclass of BaseTranslator!")

    def load_document(self, document_name):
        raise NotImplementedError("Please use a subclass of BaseTranslator!")

    def save_document(self, document, document_name):
        raise NotImplementedError("Please use a subclass of BaseTranslator!")

    def translate(self, in_file_name, out_file_name):
        document = self.load_document(in_file_name)
        self.translate_document(document)
        self.save_document(document, out_file_name)
