import codecs
from collections import deque,Counter
import re
import sys
import traceback
import StringIO


def readamrs (source,skipbad=False,errorbad=False):
    """Returns an iterator over AMRs constructed from source, which can be either a filename or a stream. 
       If it encounters an ill-formed AMR, raise exception if errorbad=True, or skips it if skipbad=True."""
    if (isString(source)):
        return readAMRsFromFile(source,skipbad=skipbad,errorbad=errorbad)
    else:
        return readAMRsFromStream(source,skipbad=skipbad,errorbad=errorbad)
    
def readAMRsFromFile (filename,skipbad=False,errorbad=False):
    """Takes a file, and returns an iterator over the AMRs in the file"""
    reader = AMRReader(FileIterator(filename))
    reader.skipBad = skipbad
    reader.errorBad = errorbad
    reader.autoClose = True
    return reader


def readAMRsFromStream (stream,skipbad=False,errorbad=False):
    """Takes an input stream, and returns an iterator over the ARMs in the stream""" 
    reader = AMRReader(LineIterator(stream))
    reader.skipBad   = skipbad
    reader.errorBad  = errorbad
    reader.autoClose = False
    return reader

def readAMRsFromString (string,skipbad=False,errorbad=False):
    """Takes a string; returns an iterator over AMRs in that string. 
       Keyword args skipbad and errorbad have the same meaning as elsewhere."""
    stream = StringIO.StringIO(string) 
    reader = readAMRsFromStream(stream,skipbad=skipbad,errorbad=errorbad)
    reader.autoClose = True
    return reader  
     
def readAMRFromString (string):
    """Takes a string; reads and returns a single AMR from it."""
    reader = readAMRsFromString(string,errorbad=True)
    if (reader.hasNext()):
        amr = reader.next()
    reader.close()
    if (amr is not None):
        return amr
    else:
        raise RuntimeError("Unable to read an AMR from string")    

def makeAMR (var,pred=None):
    """Takes a variable and an optional predicate, which may be either Terms or strings,
       and returns a new AMR of the form '(var / pred)'"""
    amr = AMR()
    amr.var = makeVar(var)
    if (pred is not None):
        amr.pred = makeTerm(pred,hasQuotes=False)
    return amr

def makeTerm (obj,hasQuotes=None):
    assert(obj is not None)
    if (type(obj) == Term):
        term = obj
    else:
        if (not isString(obj)):
            obj = str(obj)
        term = Term(obj)
    if (hasQuotes is not None):
        term.hasQuotes = hasQuotes
    return term      

def makeVar (obj):
    var = makeTerm(obj,hasQuotes=False)
    var.isVar = True
    return var

def isString (obj):
    """Takes an arbitrary object; returns True if it is a string (str or unicode)."""
    return (type(obj) == str or type(obj) == unicode)

def demoFunction (amr):
    print "{"
    print amr.var,"is-a",amr.pred
    for role in amr.roles:
        arg = role.filler
        if (type(arg) == AMR):
            arg = arg.var
        print amr.var,"has-a",role.name,arg
        # print amr.var,"-",role.name[1:]
        # print role.name[1:],"-",arg
        if (type(role.filler) == AMR):
            demoFunction(role.filler)
    print "}"
        

class AMR(object):
    
    """Represents an AMR expression node"""
        
    def __init__ (self):
        self.var  = None     # Term
        self.pred = None     # Term
        self.roles = []      # List of Role objects
        self.metadata = None # Metadata object or None
        
    def id (self):
        if (self.metadata is not None):
            return self.metadata.id
        return None
    
    def getRoleNames (self):
        """Returns the list of of unique role names, in order of appearence, for this AMR node"""
        unique = set()
        result = []
        for role in self.roles:
            if (role.name not in unique):
                unique.add(role.name)
                result.append(role.name)
        return result
    
    def getFillers (self,roleName):
        "Returns the complete list of fillers for the argument rolename."
        roleName = roleName.lower()
        return [role.filler for role in self.roles if role.name.lower() == roleName]
    
    def getFiller (self,roleName):
        """Gets the filler for roleName or None if there is no such role"""
        fillers = self.getFillers(roleName)
        return fillers[0] if fillers else None
    
    def getFillerRequire (self,rolename):
        filler = self.getFiller(rolename)
        if (filler is not None):
            return filler
        else:
            raise RuntimeError("No filler for required role: " + rolename)
        
    
    def convertTermsToStrings (self):
        """Replaces all Term objects, whether variable or role filler, with their 'string' fields."""
        # Check to see if the types really are Term, so that we can call this method 
        # idempotently without error
        if (type(self.var) == Term):
            self.var  = self.var.string
        if (type(self.pred) == Term):
            self.pred = self.pred.string
        for role in self.roles:
            role.alignments = []
            if (type(role.filler) == Term):
                role.filler = role.filler.string
            elif (type(role.filler) == AMR):
                role.filler.convertTermsToStrings()

    def hasTerminalRolesOnly (self):
        for role in self.roles:
            if (type(role.filler) == AMR):
                return False
        return True

    def ensureMetadata (self):
        """Ensures that there is at least a blank Metadata record at this node.  Would ordinarily only be called on top node."""
        if (self.metadata is None):
            self.metadata = Metadata()
    
    def pprintFull (self,output=sys.stdout,offset=0,pre=0):
        self.pprint(output,offset,pre,withAlign=True,withMeta=True)
        
    def pprintExprOnly (self,output=sys.stdout,offset=0,pre=0):
        self.pprint(output,offset,pre,withAlign=False,withMeta=False)
    

    def pprint (self, output=sys.stdout,offset=0,pre="",withAlign=True,withMeta=True,sortRoles=False):
        """Pretty-prints this AMR sub tree to the output stream, with the designated horizontal offset string. 
            withAlign=True (default) Print the alignments in e~ notation.  
            withMeta=True  (default) Print the metadata as a header.
            sortRules=True           Print the roles in sorted order
        """
        self.pprint0(output=output,offset=offset,pre=pre,withAlign=withAlign,withMeta=withMeta,sortRoles=sortRoles)
        output.write("\n\n")


    def pprint0 (self, output=sys.stdout,offset=0,pre="",withAlign=True,withMeta=True,sortRoles=False):
        """Pretty-prints this AMR sub tree to the output stream, with the designated horizontal offset string."""
        if (self.metadata and withMeta):
            self.metadata.pprint(output)
        indent  = " " * offset + "   "
        output.write("(%s / %s" % (toPrintString(self.var,withAlign),toPrintString(self.pred,withAlign)))
        singleLine = self.hasTerminalRolesOnly()
        roles = sortRolesByName(self.roles) if sortRoles else self.roles
        for role in roles:
            roleString = toPrintString(role,withAlign)
            addedOffset= max(10,len(roleString)+6)
            if (singleLine):
                output.write(" %s " % roleString)
            else:
                output.write("\n%s%s%s " % (pre,indent,roleString))
            filler = role.filler
            if (type(filler) == AMR):
                filler.pprint0(output,offset=offset+addedOffset,pre=pre,withAlign=withAlign,sortRoles=sortRoles)
            else:
                output.write(toPrintString(filler,withAlign))
        output.write(")")


    def addRole (self,roleName,filler,hasQuotes=None):
        """Takes a role name and a role filler; constructs a new role object and adds it to this 
           AMR.  Takes care of lifting the filler to a Term object if neccessary, enforcing hasQuotes
           on the Term if a value was supplied"""
        assert(isString(roleName))
        assert(roleName.startswith(":"))
        assert(filler is not None)
        # If the filler is not an AMR, it must be a Term or an intended Term
        if (type(filler) != AMR):
            # If not an actual Term, raise it to one
            if (type(filler) != Term):
                if (not isString(filler)):
                    filler = str(filler)
                filler = Term(filler)
            # Enforce hasQuotes if one was supplied
            if (hasQuotes is not None):
                filler.hasQuotes = hasQuotes
        # Build the role out of name and filler, and add to the roles list.
        role        = Role()
        role.name   = roleName
        role.filler = filler
        self.roles.append(role)
        
    # For use by AMRReader only               
    def unifyVariables (self,varMap=None):
        """Unifies bound and free occurrences of a variable 'x' to the bound-variable object"""
        if (varMap is None):  # Self-initializing
            varMap = self.getVarMap()
        for role in self.roles:
            if (type(role.filler) == AMR):
                role.filler.unifyVariables(varMap)    
            # Don't map a string filler like "x" in quotes to a variable Term object 
            # that happens to also have the name 'x'!
            elif (not role.filler.hasQuotes):
                mappedVar = varMap.get(role.filler.string)
                if (mappedVar is not None):
                    role.filler = mappedVar

                
    def getVarMap (self,varMap=None):
        """Returns a mapping from variable names to the corresponding variable objects (Terms). """
        if (varMap is None): # Self-initializing
            varMap = dict()
        var = self.var.string
        if (not varMap.get(var)):  # Could you ever have two bindings of the same variable?
            varMap[var] = self.var 
        for role in self.roles:
            if (type(role.filler) == AMR):
                role.filler.getVarMap(varMap)
        return varMap
        
def toPrintString (obj,withAlign=True):
    if (type(obj) == Term):
        string = obj.toValueString()
        if (withAlign):
            string += alignmentsToString(obj.alignments)
        return string
    elif (type(obj) == Role):
        string = obj.name
        if (withAlign):
            string += alignmentsToString(obj.alignments)
        return string
    elif (isString(obj)):
        return obj
    else:
        return str(obj)
       
class Term(object):
    
    """Represents a terminal in the AMR - either a variable, a predicate, or a non-AMR role filler. """
    
    def __init__ (self,string=None,alignments=None):
        self.string     = string
        self.alignments = alignments
        self.hasQuotes  = False
        self.isVar      = False
        
    def toValueString (self):
        result = ""
        if (self.hasQuotes):
            result += '"'
        result += self.string
        if (self.hasQuotes):
            result += '"'
        return result

    def __eq__ (self,other):
        if (isString(other)):
            return self.string == other
        elif (isinstance(other,Term)):
            return self.string == other.string and self.hasQuotes == other.hasQuotes and self.isVar == other.isVar
        else:
            return False
    
    def __str__ (self):
        return self.toValueString()
    
    def toPrintString (self):
        return self.toValueString() + alignmentsToString(self.alignments)

class Role(object):
    
    """Represents a role in AMR"""
    
    def __init__ (self,name=None):
        self.name       = name
        self.filler     = None
        self.alignments = []
        
    def toPrintString (self):
        return self.name + alignmentsToString(self.alignments)
        

    

class Metadata(object):
    
    """Represents AMR expression metadata.  Would generally only be found at the root node. """
    
    def __init__ (self):
        self.id        = None
        self.tokens    = None
        self.sent      = None
        self.date      = None
        self.annotator = None
        self.preferred = None
        self.savedate  = None
        self.file      = None
        self.other     = dict() # Any other attributes which are signalled by a "::"
    
    # ::id bolt12_64556_5627.2 ::date 2012-12-04T18:01:08 ::annotator SDL-AMR-09 ::preferred
    # ::snt Pledge to fight to the death defending the Diaoyu Islands and the related islands
    # ::save-date Wed Nov 27, 2013 ::file bolt12_64556_5627_2.txt
    
    @staticmethod  # Kind of going overboard here...    
    def makePrintLine (*tokens):
        line = ""
        for i in range(0,len(tokens),2):
            key = tokens[i]
            value = tokens[i+1]
            if (value is not None):
                if (type(value) == list):
                    value = join(value)
                line += " " + key + " " + value
        return line
        
    def pprint (self,outstream):
        line1 = Metadata.makePrintLine("::id",self.id,"::date",self.date,"::annotator",self.annotator)
        line2 = Metadata.makePrintLine("::tok",self.tokens)
        line3 = Metadata.makePrintLine("::snt",self.sent)
        line4 = Metadata.makePrintLine("::save-date",self.savedate,"::file",self.file)
        for line in [line1,line2,line3,line4]:
            if (line):
                outstream.write("#%s\n" % line)
        for key in self.other.keys():
            printKey = key if key.startswith("::") else "::"+key
            outstream.write("# %s %s\n" % (printKey,self.other[key])) 
        

def parseMetaData (line,metadata):
    # Get rid off the leading '# ' 
    line = re.sub(r'\s*#\s+',"",line)
    tokens = line.split()
    table  = dict()
    key   = None
    for token in tokens:
        if (token.startswith("::")):
            key = token
            table[key] = ""
        elif (key):
            entry = table[key]
            if (entry):
                entry += " "
            entry += token
            table[key] = entry
    for key in table.keys():
        if (key == "::id"):
            metadata.id = table[key]
        elif (key == "::tok"):
            metadata.tokens = table[key].split()
        elif (key == "::snt"):
            metadata.sent  = table[key]
        elif (key == "::date"):
            metadata.date = table[key]
        elif (key == "::annotator"):
            metadata.annotator = table[key]
        elif (key == "::preferred"):
            metadata.preferred = table[key]
        elif (key == "::save-date"):
            metadata.savedate = table[key]
        elif (key == "::file"):
            metadata.file = table[key]
        else:
            metadata.other[key] = table[key]



def alignmentsToString (alignments):
    """Takes a list of word positions, and returns the corresponding '~e.d,d,d' representation, or 
       the empty string if the list of word positions is empty."""
    if (alignments):
        return "~e."+join(alignments,",")
    else:
        return ""

def sortRolesByName (roles):
    """Takes a list of roles and returns them sorted by name, with upcase roles like :ARG0 coming first."""
    upcase = [role for role in roles if re.match(r':[A-Z]',role.name)]
    lcase  = [role for role in roles if re.match(r':[^A-Z]',role.name)]
    upcase.sort(key = lambda role: role.name)
    lcase.sort(key = lambda role: role.name)
    sortedRoles = upcase
    sortedRoles.extend(lcase)
    return sortedRoles


class AMRReader(object):
    
    """An iterator over AMRs that is constructed on an iterator over lines"""
    
    def __init__ (self,lineSource):
        
        # Creation fields
        self.lineSource = lineSource
        self.skipBad    = False # Whether to skip a bad AMR
        self.errorBad   = False # Whether to error out for a bad AMR
        self.autoClose  = False # Whether I should close my internal stream when it is empty 

        # State fields
        self.nextAMR    = None     # The next AMR object I will deliver
        self.metadata   = None     # The Metadata object that will go on top node of nextAMR
        self.state      = "PRE_AMR"
        self.amrStack   = []
        self.roleStack  = []
        self.errorCount  = 0       # Number of times an error has been encountered.


    def __iter__ (self):
        """Is its own iterator"""
        return self
        
    def hasNext (self):
        """Returns true if there are more AMRs; i.e. if a call to next() would not raise StopIteration""" 
        if (self.nextAMR is None):
            self.readNextAMR()
        return (self.nextAMR != None)
    
    def next (self):
        """Returns the next AMR in the stream, or raises StopIteration if there are no more"""
        if (self.nextAMR == None):
            self.readNextAMR()
        if (self.nextAMR):
            result = self.nextAMR
            self.nextAMR = None
            return result
        else:
            raise StopIteration()  
        
    def close (self):
        """Closes my stream"""
        self.lineSource.close()   
     
    # EXTERNAL USERS OF AMRReader: DON'T INVOKE ANY METHODS BELOW THIS LINE!
    # THEY ARE NOT FOR YOU.
       
    def clearDataStructures (self):
        """Flushes the reader, e.g. to recover from a bad expression."""
        del self.amrStack[:]
        del self.roleStack[:]
        self.metadata = None
        
    def readNextAMR (self):
        """The top level for the reading. Is a place to handle exceptions"""
        while (self.lineSource.hasNext()): # (not self.lineSource.isClosed):
            try:
                self.nextAMR = self.readNextAMR0()
                # Make sure there is at least an empty metadata object at top node
                if (self.nextAMR is not None):
                    self.nextAMR.ensureMetadata()
                return
            # Handle BadToken with a message, and internal state clear, and transition to ERROR.
            # Loop back and try to read the next AMR.
            except BadToken as e:
                print "On line",self.lineSource.getLineNumber(),": ",e.message,e.token
                self.errorCount += 1
                if (self.errorBad):
                    raise e
                else:                
                    dummy = makeBadAMR(self.metadata)       
                    self.clearDataStructures()
                    self.state = "ERROR"
                    if (not self.skipBad):
                        self.nextAMR = dummy
                        return
            # Other exceptions mean something is really wrong, and it's best to just bail.
            except Exception as e:
                self.errorCount += 1
                traceback.print_exc(e)
                print "Got",e,"on line",self.lineSource.getLineNumber(),"unable to continue"
                raise e    

    def readNextAMR0 (self):
        """Does the real work of reading"""
        while (self.lineSource.hasNext()):
            line = self.lineSource.next()
            if (not line.endswith("\n")):  # Make sure line ends with \n
                line += "\n"
            # If we are in error state, and hit a blank line or metadata line, return to PRE_AMR
            if (self.state == "ERROR" and (isBlankLine(line) or isMetaDataLine(line))):
                print "Clearing error state after","blank line" if isBlankLine(line) else line
                self.state = "PRE_AMR"
            # Special handling for metadata lines like '# ::id"
            if (isMetaDataLine(line)):
                if (self.amrStack or self.roleStack):
                    print "Possible unclosed AMR above line",self.lineSource.getLineNumber(),"flushing"
                    self.clearDataStructures()
                    self.state = "PRE_AMR"
                if (self.metadata == None):
                    self.metadata = Metadata()
                parseMetaData(line,self.metadata)
            # Flush a non-metadata comment line, or any line if we are in the ERROR state.
            elif (line.startswith("#") or self.state == "ERROR"):
                pass 
            else: 
                toks = StringTok(line,' \t\n\r()"')
                while (toks.hasNext()):
                    tok = toks.next()
                    # print self.state,tok
                    if (self.state == "STRING_FILLER"):
                        if (tok == '"'):
                            role = self.roleStack.pop()
                            # print "Popped",role.name
                            self.state = "POST_STRING"
                        elif (tok == "\n"):
                            raise BadToken("String not completed before end-of-line","")
                        else:
                            self.roleStack[-1].filler.string += tok
                    elif (self.state == "POST_STRING"):
                        if (hasRoleForm(tok) or tok == ")"): # Loop back
                            toks.putBack(tok)
                            self.state = "ROLE_NAME"
                        elif (isWhiteSpace(tok)):
                            self.state = "ROLE_NAME"
                        elif (tok.startswith("~")):  # Assume this specifies the alignments of the role filler
                            self.amrStack[-1].roles[-1].filler.alignments = parseAlignments(tok)
                            self.state = "ROLE_NAME"
                        else:  # TODO: All of this is balderdash
                            print "Possible embedded double-quote in line",self.lineSource.getLineNumber()
                            toks.putBack(tok)
                            role = self.amrStack[-1].roles[-1]
                            print "Bringing back",role.name
                            self.roleStack.append(role)
                            role.filler.string += '"'
                            self.state = "STRING_FILLER"
                    elif (isWhiteSpace(tok)):
                        pass
                    elif (self.state == "PRE_AMR"):
                        if (tok == "("):
                            self.amrStack.append(AMR())
                            self.state = "VAR"
                        else:
                            raise BadToken("Anomalous token; not a '('",tok)
                    elif (self.state == "VAR"):
                        self.amrStack[-1].var = parseVar(tok)
                        self.state = "SLASH"
                    elif (self.state == "SLASH"):
                        if (tok == "/"):
                            self.state = "PRED"
                        else:
                            raise BadToken("Not a slash",tok)
                    elif (self.state == "PRED"):
                        self.amrStack[-1].pred = parsePredicate(tok)
                        self.state = "ROLE_NAME"
                    elif (self.state == "ROLE_NAME"):
                        if (tok == ")"):
                            amr = self.amrStack.pop()
                            if (len(self.amrStack) == 0):
                                amr.metadata = self.metadata
                                amr.unifyVariables()
                                self.metadata = None  
                                self.state = "PRE_AMR"   
                                return amr
                            else:
                                role = self.roleStack.pop()
                                # print "Popped",role.name
                                role.filler = amr                      
                        else:
                            role = parseRoleString(tok)
                            # print "Pushing",role.name
                            self.roleStack.append(role)
                            self.amrStack[-1].roles.append(role)
                            self.state = "ROLE_FILLER"
                    elif (self.state == "ROLE_FILLER"):
                        if (tok == '"'):
                            self.state = "STRING_FILLER"
                            self.roleStack[-1].filler = Term("")
                            self.roleStack[-1].filler.hasQuotes = True
                        elif (tok == "("):
                            self.amrStack.append(AMR())
                            self.state = "VAR"
                        elif (tok == ")"):
                            raise BadToken("Got a close paren before filler for role:",self.roleStack[-1].name)
                        else:
                            role = self.roleStack.pop()
                            # print "Popped",role.name
                            role.filler = parseTerminal(tok)
                            self.state = "ROLE_NAME" 
                    else:
                        raise RuntimeError(format("What is this state: %s" % self.state))    
        if (self.roleStack or self.amrStack):
            raise BadToken("End of file before AMR completed","")                

class VarIndex:

    """Gets you a new variable in the preferred AMR style."""

    def __init__ (self):
        self.varCounts = Counter()

    def newAMR (self,predicate):
        if (type(predicate) == Term):
            predicate = predicate.string
        return makeAMR(getNewVar(predicate),
                       predicate)

    def getNewVarName (self,predicate):
        assert(isString(predicate))
        predicate = predicate.lower()
        assert(re.match(r'[a-z]',predicate))
        first = predicate[0:1]
        count = self.varCounts[first]
        if (count == 0):
            varName = first
        else:
            varName = first + str(count+1)
        self.varCounts[first] += 1
        return varName

    def getNewVar (self,predicate):
        return makeVar(self.getNewVarName(predicate))

    def reset (self):
        self.varCounts.clear()

    def clear (self):
        """Alternative name for reset."""
        self.reset()

        

def parseRoleString (tok):
    """Parses a rolename string like ':ARG2' or ':ARG2~e.11' into a Role object, attaching the appropriate
       word positions to it if it has a '~e.n,n' attachment. Returns the resulting Role object as value."""
    if (not tok.startswith(":")):
        raise BadToken("Doesn't start with a ':', so it doesn't look like a role:",tok)
    (name,alignments) = parseTerminalString(tok)
    role            = Role()
    role.name       = name
    role.alignments = alignments
    return role

def hasRoleForm (tok):
    """Returns true if token is plausibly a role name; i.e. starts with ':' and has additional characters have that"""
    return tok.startswith(":") and len(tok) > 1

def parsePredicate (tok):
    return parseTerminal(tok)

def parseVar (tok):
    var = parseTerminal(tok)
    var.isVar = True
    return var    

def isWhiteSpace (tok):
    return tok.isspace()     

def isMetaDataLine (line):
    """Returns true if line matches '# ::'"""
    return re.match(r'\s*#\s+::',line)

def isBlankLine (line):
    return line.isspace()

def parseAlignments (string):
    m = re.match(r'~[e4]\.(\d+(,\d+)*)',string)
    if (m):
        numString   = m.group(1)
        wordIndices = []
        for item in numString.split(','):
            if (item != ""):
                wordIndices.append(int(item))
        return wordIndices
    else:
        raise BadToken("Not a valid alignment",string)


def parseTerminalString (string):
    m = re.match(r'(.+?)(~[e4]\.(\d+(,\d+)*))?$',string)
    if (m):
        name = m.group(1)
        numString = m.group(3)
        wordIndices= []
        if (numString != None):
            for item in numString.split(','):
                if (item != ""):
                    wordIndices.append(int(item))
        return (name,wordIndices)
    else:
        raise BadToken("Not a valid terminal",string)
    
def parseTerminal (string):
    (name,alignments) = parseTerminalString(string)
    return Term(name,alignments)

def makeBadAMR (metadata):
    amr          = AMR()
    amr.var      = Term("x")
    amr.pred     = Term("BAD-AMR")
    amr.metadata = metadata if metadata is not None else Metadata()
    return amr
                    


class BadToken(BaseException):
    
    """Represents an error"""
    
    def __init__ (self,message=None,token=None):
        self.message = message
        self.token = token
        

class FileIterator(object):
    
    """Takes a file and turns it into a stream of lines."""
    
    def __init__(self,filename):
        self.iter  = LineIterator(codecs.open(filename,"r","utf-8"))
        self.iter.autoClose = True
        
    def hasNext (self):
        return self.iter.hasNext()
    
    def next (self):
        return self.iter.next()
    
    def close (self):
        self.iter.close()
        
    def getLineNumber (self):
        return self.iter.lineNumber

    def putBack (self,string):
        self.iter.putBack(string)
        

       

class LineIterator(object):

    """Takes a text stream and constructs sort of a java style iterator around it"""

    def __init__(self,stream):
        self.stream   = stream   # The stream I am constructed around
        self.nextLine = None     # The next line I am going to give out
        self.queue    = deque()
        self.lineNumber = 0      # The line number I have given out
        self.autoClose  = False  # Whether to close my internal stream when it is empty.

    def putBack (self, string):
        """Put the argument string back into the stream (in a virtual sense)."""
        self.lineNumber -= 1
        self.queue.append(string)

    def hasNext (self):
        """Returns true if there are more lines to be read."""
        # If no next line is cached, try to get another one
        if (self.nextLine == None):
            self.fetchNextLine()
        # If successful, return true
        if (self.nextLine != None):
            return True
        # Otherwise, return false
        else:
            return False

    def next (self):
        # If no next line is cached, try to get another one
        if (self.nextLine is None):
            self.fetchNextLine()
        # 
        if (self.nextLine is None):
            raise StopIteration()
        else:
            result = self.nextLine
            self.lineNumber += 1
            self.nextLine = None
            return result


    def fetchNextLine (self):
        if (len(self.queue) > 0):
            self.nextLine = self.queue.pop()
        else:
            self.nextLine = self.stream.readline()
            # An empty string is Python's end-of-file indicator
            if (self.nextLine == ""):
                # Close the stream if we have authority to do that.
                if (self.autoClose):
                    self.stream.close()
                self.nextLine = None

    def close (self):
        """Explicit close function,should one be desired"""
        self.stream.close() 


class StringTok(object):

    """Takes a string and a string of delimiter characters; returns tokens consisting of either a single delimiter character,
       or the token between two delimiters (or begin/end of the string)."""

    def __init__ (self,string, delims=" \t\n\r"):
        self.string = string
        self.delims = delims
        self.startPos = 0;
        self.endPos   = 0;
        self.queue    = deque()

    def hasNext (self):
        if (len(self.queue) == 0):
            self.fetchNext()
        return (len(self.queue) > 0)
   
    def next (self):
        """Returns the next token, or raises StopIteration if there are none left. """
        if (len(self.queue) == 0):
            self.fetchNext()
        if (len(self.queue) > 0):
            return self.queue.popleft()
        else:
            raise StopIteration()
    
    def fetchNext (self):
        while (self.startPos < len(self.string)):
            self.endPos += 1
            if (self.endPos == len(self.string) or self.hasDelim(self.startPos) or self.hasDelim(self.endPos)):
                result = self.string[self.startPos:self.endPos]
                self.startPos = self.endPos
                self.queue.append(result)
                return result
    
    def putBack (self,tok):
        self.queue.append(tok)

    def hasDelim (self, n):
        "Returns true if the n'th character in my string is a delimiter"
        char = self.string[n]
        return (self.delims.find(char) != -1)
    
    
def join (objects,delim=" "):
    string = ""
    for idx,obj in enumerate(objects):
        if (idx > 0):
            string += delim
        string += unicode(obj)
    return string
    
def testStringTok ():
    it = StringTok("hello how are you()"," ()")
    toks = [it.next(),it.next(),it.next()]
    for tok in toks:
        print "Putting back",tok
        it.putBack(tok)
    
    while (it.hasNext()):
        tok = it.next()
        sys.stdout.write("'%s'\n" % tok)



def testParseTerminal ():
    align = "~e.3,7,10,15"
    # align = "~e.30"
    string = ":arg0"+align
    # string = ":arg0~e.3"
#     (name,words) = parseTerminalString(string)
#     print "name: '%s'" % name
#     print "words",words
#     print "align words",parseAlignments(align)  
    term = parseTerminal(string)
    print term.string,term.alignments

teststr = """
(x5 / rescue-01
      :ARG0 (x1 / express-03
            :ARG2 (x2 / enzyme
                  :mod (x3 / wild-type)
                  :name (x4 / name :op1 "Gab1")
                  :xref (x22 / xref :value "UNIPROT:GAB1_HUMAN" :prob "0.604")))
      :ARG1 (x14 / activate-01
            :ARG2-of (x8 / induce-01
                  :ARG0 (x6 / protein
                        :name (x7 / name :op1 "EGF")
                        :xref (x / xref :value "UNIPROT:EGF_HUMAN" :prob "1.004")))
            :ARG1 (x11 / and
                  :op1 (x10 / kinase
                        :name (x9 / name :op1 "PI-3")
                        :xref (x21 / xref :value "UNIPROT:ELAF_HUMAN" :prob "1.002"))
                  :op2 (x12 / enzyme
                        :name (x13 / name :op1 "Akt")
                        :xref (x23 / xref :value "UNIPROT:AKT1_HUMAN" :prob "0.203"))))
      :location (x17 / protein
            :mod (x15 / protein
                  :name (x16 / name :op1 "Gab1")
                  :xref (x20 / xref :value "UNIPROT:GAB1_HUMAN" :prob "0.604"))
            :ARG2-of (x18 / mutate-01 :mod "-/-")
            :name (x19 / name :op1 "mef")
            :xref (x24 / xref :value "UNIPROT:ELF4_HUMAN" :prob "0.602")))
"""


if (__name__ == "__main__"):
    # testParseTerminal()
    amr = readAMRFromString(teststr)
    demoFunction(amr)

    
