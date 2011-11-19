import os
import babel.dates
import datetime
import isearch

# TODO TODO
NOTES_FOLDER = "/home/nicholasschiefer/Dropbox/note"

class Database:
    """Wrapper for interacting with the notes on the file system and the isearch library"""

    def __init__(self, path):
        self.path = path
        self.refresh()
        self.searcher = isearch.Searcher(self.dict.items())

    def _file_name(self, key):
        """Return the file name of a note with the key"""
        return os.path.join(self.path, key)

    def _format_date(self, key):
        """Format the Bable date for the file naem with the key"""
        timestamp = os.path.getmtime(self._file_name(key))
        return babel.dates.format_datetime(datetime.datetime.fromtimestamp(timestamp))

    def search(self, query):
        """Return the ranked and filtered notes in the correct format for the GUI"""
        if query == "":
            return self.all()
        
        results = self.searcher.search(query)
        
        return [(data[0], self._format_date(data[0])) for data in results]

    def all(self):
        """
        Return all notes in the correct format for the GUI

        Correct format is (title, date_modified)
        """
        modified = [self._format_date(key) for key in self.dict]
        return zip(self.dict.keys(), modified)

    def refresh(self):
        """Refresh the notes' keys and their values from the filesystem"""
        keys = os.listdir(self.path)
        self.dict = {}
        for key in keys:
            self.dict[key] = open(self._file_name(key)).read()

    def __getitem__(self, key):
        """Return the text stored in the note with title key"""
        return self.dict[key]

    def __setitem__(self, key, value):
        """Update the note with title key in the dictionary, on the file system, and in the search index"""
        if len(key) > 0 and not (key in self.dict and self.dict[key] == value):
            # store old value and delete old key from search index
            old_val = self.dict[key]
            self.searcher.remove(hash(key))
            
            # update dictionary value and re-add note to search index
            self.dict[key] = value
            self.searcher.add((key, value))
            
            # write modified note to disk
            f = open(os.path.join(self.path, key), 'w')
            f.write(self.dict[key])
            f.close()

    def add(self, key):
        """Create a new note with title key"""
        self.dict[key] = ""
        self.searcher.add((key, ""))

    def __delitem__(self, key):
        """Delete a note with title key"""
        # delete from file system, then search index, then dictionary
        os.remove(self._file_name(key))
        self.searcher.remove(hash(key))
        del self.dict[key]

