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

    def __init__(self, model_name, service_url, cache_name, device, clean_text, original_language, result_language):
        self.device = ("cuda:0" if cuda_is_available() else "cpu") if device is None else device
        if model_name is None and service_url is None:
            raise RuntimeError("Neither model name nor service URL provided!")
        self.l1, self.l2 = original_language, result_language
        self.pipeline = None if model_name is None else transformers_pipeline("translation", f"{model_name}-{self.l1}-{self.l2}", device=device)
        self.service_url = service_url
        self.cache = Cache(cache_name)
        self.clean_text = clean_text

    def translate_text(self, text):
        if cached_text := self.cache.get((self.l1, self.l2, text)):
            return cached_text
        new_sentences = []
        if self.clean_text:
            text = clean(text, lang="da", lower=False)
        sentences = text.split(". ")
        for i in range(len(sentences)):
            sentence = sentences[i]
            if i+1 < len(sentences):
                sentence += "."
            if not sentence:
                new_sentence = sentence
            elif self.pipeline is not None:
                new_sentence = self.pipeline(sentence)[0]['translation_text'] if any((c.isalpha() for c in sentence)) else sentence
            else:
                from requests import post
                new_sentence = post(
                    self.service_url,
                    json = {
                        "l1": self.l1,
                        "l2": self.l2,
                        "sentences": [sentence]
                    }
                ).json()["translations"][0]["l2"][0]
            print("REPR",repr(sentence), repr(new_sentence))
            new_sentences.append(new_sentence)
        new_text = " ".join(new_sentences)
        self.cache.set((self.l1, self.l2, text), new_text)
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
