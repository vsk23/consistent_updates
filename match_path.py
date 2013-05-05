class match_path(object):
    def __init__(self,selfmatch,selfpath):
        self.lastswitchmatch=selfmatch
        self.path=selfpath
    def __len__(self):
        return len(self.path)
    def match_from_match_path(self):
        return self.lastswitchmatch
    def path_from_match_path(self):
        return self.path
