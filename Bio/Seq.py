import string, array

import Alphabet
from Alphabet import IUPAC
from Data.IUPACData import ambiguous_dna_complement, ambiguous_rna_complement
from Bio.Data import CodonTable


class Seq:
    def __init__(self, data, alphabet = Alphabet.generic_alphabet):
        # Enforce string storage
        assert (type(data) == type("") or # must use a string
                type(data) == type(u""))  # but can be a unicode string

        self.data = data                           # Seq API requirement
        self.alphabet = alphabet                   # Seq API requirement

    def __repr__(self):
        return "%s(%s, %s)" % (self.__class__.__name__,
                               repr(self.data),
                               repr(self.alphabet))
    def __str__(self):
        if len(self.data) > 60:
            s = repr(self.data[:60] + " ...")
        else:
            s = repr(self.data)
        return "%s(%s, %s)" % (self.__class__.__name__, s,
                               repr(self.alphabet))
    # I don't think I like this method...
##    def __cmp__(self, other):
##        if isinstance(other, Seq):
##            return cmp(self.data, other.data)
##        else:
##            return cmp(self.data, other)

    def __len__(self): return len(self.data)       # Seq API requirement

    def __getitem__(self, index) :                 # Seq API requirement
        #Note since Python 2.0, __getslice__ is deprecated
        #and __getitem__ is used instead.
        #See http://docs.python.org/ref/sequence-methods.html
        if isinstance(index, int) :
            #Return a single letter as a string
            return self.data[index]
        else :
            #Return the (sub)sequence as another Seq object
            return Seq(self.data[index], self.alphabet)

    def __add__(self, other):
        if type(other) == type(' '):
            return self.__class__(self.data + other, self.alphabet)
        elif self.alphabet.contains(other.alphabet):
            return self.__class__(self.data + other.data, self.alphabet)
        elif other.alphabet.contains(self.alphabet):
            return self.__class__(self.data + other.data, other.alphabet)
        else:
            raise TypeError, ("incompatable alphabets", str(self.alphabet),
                              str(other.alphabet))
        
    def __radd__(self, other):
        if self.alphabet.contains(other.alphabet):
            return self.__class__(other.data + self.data, self.alphabet)
        elif other.alphabet.contains(self.alphabet):
            return self.__class__(other.data + self.data, other.alphabet)
        else:
            raise TypeError, ("incompatable alphabets", str(self.alphabet),
                              str(other.alphabet))


    def tostring(self):                            # Seq API requirement
        return self.data

    def tomutable(self):   # Needed?  Or use a function?
        return MutableSeq(self.data, self.alphabet)
    
    def count(self, item):
        return len([x for x in self.data if x == item])

    def __maketrans(self, alphabet) :
        """Seq.__maketrans(alphabet) -> translation table.

        Return a translation table for use with complement()
        and reverse_complement().

        Compatible with lower case and upper case sequences.

        alphabet is a dictionary as implement in Data.IUPACData

        For internal use only.
        """
        before = ''.join(alphabet.keys())
        after  = ''.join(alphabet.values())
        before = before + before.lower()
        after  = after + after.lower()
        return string.maketrans(before, after)

    def complement(self):
        """Returns the complement sequence. New Seq object.
        """
        if self.alphabet in (IUPAC.ambiguous_dna, IUPAC.unambiguous_dna):
            d = ambiguous_dna_complement
        elif self.alphabet in (IUPAC.ambiguous_rna, IUPAC.unambiguous_rna):
            d = ambiguous_rna_complement
        elif 'U' in self.data:
            d = ambiguous_rna_complement
        else:
            d = ambiguous_dna_complement
        ttable = self.__maketrans(d)
        #Much faster on really long sequences than the previous loop based one.
        #thx to Michael Palmer, University of Waterloo
        s = self.data.translate(ttable)
        return Seq(s, self.alphabet)

    def reverse_complement(self):
        """Returns the reverse complement sequence. new Seq object.
        """
        if self.alphabet in (IUPAC.ambiguous_dna, IUPAC.unambiguous_dna):
            d = ambiguous_dna_complement
        elif self.alphabet in (IUPAC.ambiguous_rna, IUPAC.unambiguous_rna):
            d = ambiguous_rna_complement
        elif 'U' in self.data:
            d = ambiguous_rna_complement
        else:
            d = ambiguous_dna_complement
        ttable = self.__maketrans(d)
        #Much faster on really long sequences than the previous loop based one.
        #thx to Michael Palmer, University of Waterloo
        s = self.data[-1::-1].translate(ttable)
        return Seq(s, self.alphabet)


class MutableSeq:
    def __init__(self, data, alphabet = Alphabet.generic_alphabet):
        if type(data) == type(""):
            self.data = array.array("c", data)
        else:
            self.data = data   # assumes the input is an array
        self.alphabet = alphabet
    def __repr__(self):
        return "%s(%s, %s)" % (self.__class__.__name__,
                               repr(self.data),
                               repr(self.alphabet))

    def __str__(self):
        if len(self.data) > 60:
            s = repr(string.join(self.data[:60], "") + " ...")
        else:
            s = repr(string.join(self.data, ""))
        return "%s(%s, %s)" % (self.__class__.__name__, s,
                               repr(self.alphabet))
    def __cmp__(self, other):
        if isinstance(other, MutableSeq):
            x = cmp(self.alphabet, other.alphabet)
            if x == 0:
                return cmp(self.data, other.data)
            return x
        elif type(other) == type(""):
            return cmp(self.data.tostring(), other)
        elif isinstance(other, Seq):
            x = cmp(self.alphabet, other.alphabet)
            if x == 0:
                return cmp(self.data.tostring(), other.data)
            return x
        else:
            return cmp(self.data, other)

    def __len__(self): return len(self.data)

    def __getitem__(self, index) :
        #Note since Python 2.0, __getslice__ is deprecated
        #and __getitem__ is used instead.
        #See http://docs.python.org/ref/sequence-methods.html
        if isinstance(index, int) :
            #Return a single letter as a string
            return self.data[index]
        else :
            #Return the (sub)sequence as another Seq object
            return MutableSeq(self.data[index], self.alphabet)

    def __setitem__(self, index, value):
        #Note since Python 2.0, __setslice__ is deprecated
        #and __setitem__ is used instead.
        #See http://docs.python.org/ref/sequence-methods.html
        if isinstance(index, int) :
            #Replacing a single letter with a new string
            self.data[index] = value
        else :
            #Replacing a sub-sequence
            if isinstance(value, MutableSeq):
                self.data[index] = value.data
            elif isinstance(value, type(self.data)):
                self.data[index] = value
            else:
                self.data[index] = array.array("c", str(value))

    def __delitem__(self, index):
        #Note since Python 2.0, __delslice__ is deprecated
        #and __delitem__ is used instead.
        #See http://docs.python.org/ref/sequence-methods.html
        
        #Could be deleting a single letter, or a slice
        del self.data[index]
    
    def __add__(self, other):
        if self.alphabet.contains(other.alphabet):
            return self.__class__(self.data + other.data, self.alphabet)
        elif other.alphabet.contains(self.alphabet):
            return self.__class__(self.data + other.data, other.alphabet)
        else:
            raise TypeError, ("incompatable alphabets", str(self.alphabet),
                              str(other.alphabet))
    def __radd__(self, other):
        if self.alphabet.contains(other.alphabet):
            return self.__class__(other.data + self.data, self.alphabet)
        elif other.alphabet.contains(self.alphabet):
            return self.__class__(other.data + self.data, other.alphabet)
        else:
            raise TypeError, ("incompatable alphabets", str(self.alphabet),
                              str(other.alphabet))

    def append(self, c):
        self.data.append(c)
    def insert(self, i, c):
        self.data.insert(i, c)
    def pop(self, i = (-1)):
        c = self.data[i]
        del self.data[i]
        return c
    def remove(self, item):
        for i in range(len(self.data)):
            if self.data[i] == item:
                del self.data[i]
                return
        raise ValueError, "MutableSeq.remove(x): x not in list"
    def count(self, item):
        count = 0
        for c in self.data:
            if c == item:
                count = count + 1
        return count
    def index(self, item):
        for i in range(len(self.data)):
            if self.data[i] == item:
                return i
        raise ValueError, "MutableSeq.index(x): x not in list"
    def reverse(self):
        self.data.reverse()
    def complement(self):
        if self.alphabet in (IUPAC.ambiguous_dna, IUPAC.unambiguous_dna):
            d = ambiguous_dna_complement
        elif self.alphabet in (IUPAC.ambiguous_rna, IUPAC.unambiguous_rna):
            d = ambiguous_rna_complement
        elif 'U' in self.data:
            d = ambiguous_rna_complement
        else:
            d = ambiguous_dna_complement
        c = dict([(x.lower(), y.lower()) for x,y in d.iteritems()])
        d.update(c)
        self.data = map(lambda c: d[c], self.data)
        self.data = array.array('c', self.data)
        
    def reverse_complement(self):
        self.complement()
        self.data.reverse()

    ## Sorting a sequence makes no sense.
    # def sort(self, *args): self.data.sort(*args)
    
    def extend(self, other):
        if isinstance(other, MutableSeq):
            for c in other.data:
                self.data.append(c)
        else:
            for c in other:
                self.data.append(c)

    def tostring(self):
        return string.join(self.data, "")

    def toseq(self):
        return Seq(string.join(self.data, ""), self.alphabet)


# The transcribe, backward_transcribe, and translate functions are
# user-friendly versions of the corresponding functions in Bio.Transcribe
# and Bio.Translate. The functions work both on Seq objects, and on strings.

def transcribe(dna):
    """Transcribes a DNA sequence into RNA.

    If given a string, returns a new string object.
    Given a Seq or MutableSeq, returns a new Seq object with the same alphabet.
    """
    if isinstance(dna, Seq) or isinstance(dna, MutableSeq):
        if isinstance(dna.alphabet, Alphabet.ProteinAlphabet) :
            raise ValueError, "Proteins cannot be transcribed!"
        #TODO - Raise an error if already is RNA alphabet?
        rna = dna.tostring().replace('T','U').replace('t','u')
	if dna.alphabet==IUPAC.unambiguous_dna:
            alphabet = IUPAC.unambiguous_rna
        elif dna.alphabet==IUPAC.ambiguous_dna:
            alphabet = IUPAC.ambiguous_rna
        else:
            alphabet = Alphabet.generic_rna
        return Seq(rna, alphabet)
    else:
        rna = dna.replace('T','U').replace('t','u')
        return rna


def back_transcribe(rna):
    """Back-transcribes an RNA sequence into DNA.

    If given a string, returns a new string object.
    Given a Seq or MutableSeq, returns a new Seq object with the same alphabet.
    """
    if isinstance(rna, Seq) or sinstance(rna, MutableSeq):
        if isinstance(sequence.alphabet, Alphabet.ProteinAlphabet) :
            raise ValueError, "Proteins cannot be (back)transcribed!"
        #TODO - Raise an error if already is DNA alphabet?
        dna = rna.data.replace('U','T').replace('u','t')
	if rna.alphabet==IUPAC.unambiguous_rna:
            alphabet = IUPAC.unambiguous_dna
        elif rna.alphabet==IUPAC.ambiguous_rna:
            alphabet = IUPAC.ambiguous_dna
        else:
            alphabet = Alphabet.generic_dna
        return Seq(dna, alphabet)
    else:
        dna = rna.replace('U','T').replace('u','t')
        return dna


def translate(sequence, table = "Standard", stop_symbol = "*"):
    try:
        id = int(table)
    except:
        id = None
    if isinstance(sequence, Seq) or isinstance(sequence, MutableSeq):
        if isinstance(sequence.alphabet, Alphabet.ProteinAlphabet) :
            raise ValueError, "Proteins cannot be translated!"
        if sequence.alphabet==IUPAC.unambiguous_dna:
            if id==None:
                table = CodonTable.unambiguous_dna_by_name[table]
            else:
                table = CodonTable.unambiguous_dna_by_id[id]
        elif sequence.alphabet==IUPAC.ambiguous_dna:
            if id==None:
                table = CodonTable.ambiguous_dna_by_name[table]
            else:
                table = CodonTable.ambiguous_dna_by_id[id]
        elif sequence.alphabet==IUPAC.unambiguous_rna:
            if id==None:
                table = CodonTable.unambiguous_rna_by_name[table]
            else:
                table = CodonTable.unambiguous_rna_by_id[id]
        elif sequence.alphabet==IUPAC.ambiguous_rna:
            if id==None:
                table = CodonTable.ambiguous_rna_by_name[table]
            else:
                table = CodonTable.ambiguous_rna_by_id[id]
        else:
            if id==None:
                table = CodonTable.generic_by_name[table]
            else:
                table = CodonTable.generic_by_id[id]
        sequence = sequence.tostring().upper()
        n = len(sequence)
        get = table.forward_table.get
        protein = [get(sequence[i:i+3], stop_symbol) for i in xrange(0,n-n%3,3)]
        protein = "".join(protein)
        alphabet = Alphabet.HasStopCodon(table.protein_alphabet)
        return Seq(protein, alphabet)
    else:
        if id==None:
            table = CodonTable.generic_by_name[table]
        else:
            table = CodonTable.generic_by_id[id]
        get = table.forward_table.get
        sequence = sequence.upper()
        n = len(sequence)
        protein = [get(sequence[i:i+3], stop_symbol) for i in xrange(0,n-n%3,3)]
        protein = "".join(protein)
        return protein


def reverse_complement(sequence):
    """Returns the reverse complement sequence of a nucleotide string

    If given a string, returns a new string object.
    Given a Seq or a MutableSeq, returns a new Seq object with the same alphabet.

    NOTE - Currently only supports unambiguous nucleotide sequences
    """
    #TODO - Take complement of ambiguous nucleotides (as best possible)
    if 'U' in sequence:
        ttable = string.maketrans("ACGUacgu","UGCAugca")
    else:
        ttable = string.maketrans("ACGTacgt","TGCAtgca")
    if isinstance(sequence, Seq) or isinstance(sequence, MutableSeq):
        if isinstance(sequence.alphabet, Alphabet.ProteinAlphabet) :
            raise ValueError, "Proteins do not have complements!"
        #Important - want to use the pthon string object's translate method here:
        return Seq(sequence.tostring()[-1::-1].translate(ttable), \
                   sequence.alphabet)
    else :
        #String
        return sequence[-1::-1].translate(ttable)

if __name__ == "__main__" :
    print "Quick Self Test"

    test_seqs = [Seq("ATGAAACTG"), 
                 Seq("AUGAAACUG", Alphabet.generic_dna), 
                 Seq("ATGAAACTG", Alphabet.generic_rna), 
                 Seq("ATGAAACTG", Alphabet.generic_nucleotide),
                 Seq("ATGAAACUG", Alphabet.generic_nucleotide), #U and T (!)
                 MutableSeq("ATGAAACTG", Alphabet.generic_rna),
                 Seq("ACTGTCGTCT", Alphabet.generic_protein)]

    print
    print "Transcribe DNA into RNA"
    print "======================="
    for nucleotide_seq in test_seqs:
        try :
            print "%s -> %s" \
            % (repr(nucleotide_seq) , repr(transcribe(nucleotide_seq)))
        except ValueError, e :
            print "%s -> %s" \
            % (repr(nucleotide_seq) , str(e))

    print
    print "Back-transcribe RNA into DNA"
    print "============================"
    for nucleotide_seq in test_seqs:
        try :
            print "%s -> %s" \
            % (repr(nucleotide_seq) , repr(transcribe(nucleotide_seq)))
        except ValueError, e :
            print "%s -> %s" \
            % (repr(nucleotide_seq) , str(e))

            
    print
    print "Reverse Complement"
    print "=================="
    for nucleotide_seq in test_seqs:
        try :
            print "%s -> %s" \
            % (repr(nucleotide_seq) , repr(reverse_complement(nucleotide_seq)))
        except ValueError, e :
            print "%s -> %s" \
            % (repr(nucleotide_seq) , str(e))
            
    print
    print "Translating"
    print "==========="
    for nucleotide_seq in test_seqs:
        try :
            print "%s -> %s" \
            % (repr(nucleotide_seq) , repr(translate(nucleotide_seq)))
        except ValueError, e :
            print "%s -> %s" \
            % (repr(nucleotide_seq) , str(e))
        

    print "Done"
