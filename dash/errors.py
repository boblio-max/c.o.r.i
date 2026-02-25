class Error:
    def __init__(self, type):
        self.type = type
        self.error_types = {1:"Robot Not working - Error not found", 
        11:"Rotate Base not working",
        12:"Shoulder Joint not working",
        13:"Elbow Joint not working",
        14:"Wrist Joint not working",
        15:"Rotate Grabber not working",
        16:"Grabber not working"
}
    def isThrown(self:None) -> bool:
        return True
    
    def get(self:None) -> int:
        return self.error_types[self.type]
