from __future__ import division
"""
Python incremental word or partial-word search library

Much improvement necessary
"""
import collections
import math

class Searcher:
    def __init__(self, documents, hash_field=0):
        """
        Initialize the searcher with the given documents

        documents - list of values or tuples representing document data
        """
        self.hf = hash_field
        self.docs = dict((hash(doc[hash_field]), doc) for doc in documents)
        self.index = {}
        self.index_docs()

    def index_docs(self):
        """Index the documents"""
        for doc_id in self.docs:
            self.index_doc(doc_id)

    def index_doc(self, doc_id):
        """
        Index a specific document

        Uses term-frequencies in a vector space model
        """
        self.index[doc_id] = []
        doc = self.docs[doc_id]
        for i, field in enumerate(doc):
            terms = collections.defaultdict(int)
            for term in doc[i].split():
                terms[term] += 1
            self.index[hash(doc[self.hf])].append(terms)

    def add(self, document):
        """Add a document to the searcher"""
        self.docs[hash(document[self.hf])] = document
        self.index_doc(hash(document[self.hf]))
        return hash(document[self.hf])

    def remove(self, doc_id):
        """Remove a document from the searcher -- must be an exact match"""
        del self.docs[doc_id]
        del self.index[doc_id]

    def mag(self, m):
        """Return magnitude of a vector model"""
        return math.sqrt(sum([m[term]**2 for term in m]))

    def compare(self, m1, m2):
        """Compare two documents using cosine similarity"""
        return sum(m1[term] * m2[term] for term in m1) / (self.mag(m1) * self.mag(m2))
            
    def search(self, query):
        """Search, rank, and filter the documents using query"""
        query_model = collections.defaultdict(int)
        for term in query.split():
            query_model[term] += 1

        rankings = []
        for doc_id in self.index:
            rankings.append((self.match(doc_id, query_model), doc_id))

        rankings.sort()
        rankings.reverse() # highest ranked document first

        # return documents, not ids if there is *any* match (r[0] > 0)
        return [self.docs[r[1]] for r in rankings if r[0] > 0]

    def match(self, doc_id, query_model):
        """Compare query model and a document's model"""
        result = []
        for i, field in enumerate(self.index[doc_id]):
            result.append(self.compare(query_model, self.index[doc_id][i]))
    
        # TODO 18/11/2011 find way to make a more general formula for combining field values
        return sum(result)
