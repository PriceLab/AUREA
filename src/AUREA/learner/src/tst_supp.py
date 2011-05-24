%pythoncode{

class TST:
    """
    Top Scoring Triplets class.
    
    This class runs the top scoring triplets algorithm described in The ordering
    of expression among a few genes can provide simple cancer biomarkers
    and signal BRCA I mutations by Lin et al in BMC Bioinformatics 2009, 10:256
    http://www.biomedcentral.com/1471-2105/10/256

    This code uses slightly modified code from 
    https://jshare.johnshopkins.edu/dnaiman1/public_html/rxa/ which is 
    the code described in the above mentioned paper.
    """
    def __init__(self, data, numGenes, classSizes, filter):
        """
        Initializes the object. 
        data is an IntVector containing the microarray data and should be
        generated by the dataPackager class. classSizes is an intvector 
        containing the size of the 2 classes, class 1 and class 2 respectively.

        """
        self.data = data
        self.numGenes = numGenes
        self.classSizes = classSizes
        for i, x in enumerate(sorted([x for x in filter])):
            #sort filters for c code
            filter[i] = x
        self.filter = filter
        self.numSamples = 0
        for i in xrange(0,len(classSizes)):
            self.numSamples += classSizes[i]

    def train(self):
        """
        Runs the c code tst algorithm.
        fills the self.maxScore1,2,3 with the triplets.
        May have multiple so self.maxScore1[0] is the first element of the 
        first triplet, self.maxScore1[1] is the first element of the second
        triplet, etc.
        """
        self.maxScore1 = IntVector()
        self.maxScore2 = IntVector()
        self.maxScore3 = IntVector()
        runTST(self.data, self.numGenes, self.classSizes, self.filter, self.maxScore1, self.maxScore2, self.maxScore3)
        self.compute_ptable()

    def compute_ptable(self):
        """
        Stores the counts for the various orderings(in the case of multiple orderings) in their respective class
        generates self.ptable which is ordered:
        [
            ordering1[
                        class1 [p(1,2,3), p(1,3,2), p(2,1,3), p(2,3,1), p(3,1,2), p(3,2,1)],
                        class2 [p(1,2,3), p(1,3,2), p(2,1,3), p(2,3,1), p(3,1,2), p(3,2,1)]
            ]
            ordering2 [
                ....
            ],
            ...
        ]
        """
        con = self.convertToDataIndex
        self.ptable = []
        for msi in xrange(0, len(self.maxScore1)):#foreach maxscore triplet
            loc_ptable = [[],[]]
            for x in xrange(0,6):
                loc_ptable[0].append(0.0)
                loc_ptable[1].append(0.0)
            
            ptind = 0 #which classes ptable
            for i in xrange(0, self.numSamples):
                if i == self.classSizes[0]:
                    ptind = 1#in the second class
                s1 = self.data[con(i, self.maxScore1[msi])]
                s2 = self.data[con(i, self.maxScore2[msi])]
                s3 = self.data[con(i, self.maxScore3[msi])]
            
                et = self.ptable_entry(s1,s2,s3)
                if len(et) == 1:
                    loc_ptable[ptind][et[0]] += 1.0
                else:
                    #there is an equality
                    for index in et:
                        loc_ptable[ptind][index] += 1.0/len(et)

            prob = []    
            classind = 0
            for aClass in loc_ptable:
                prob.append(map(lambda x: x/self.classSizes[classind] ,aClass))
                classind += 1                

            self.ptable.append(prob)
                
    
    

    def ptable_entry(self, s1, s2, s3):
        """
        Builds a list that contains the index of matching orderings.
        If there is an equality then the list could be longer than 1.
        """
        #this whole equality thing bugs me
        entry_table = []
        if s1 <= s2 <= s3:
            entry_table.append(0)
        if s1 <= s3 <= s2:
            entry_table.append(1)
        if s2 <= s1 <= s3:
            entry_table.append(2)
        if s2 <= s3 <= s1:
            entry_table.append(3)
        if s3 <= s1 <= s2:
            entry_table.append(4)
        if s3 <= s2 <= s1:
            entry_table.append(5)
        return entry_table


           
    def convertToDataIndex(self, sample_index, gene_index):
        """
        This translates the sample_index and gene index into a self.data index
        """
        return sample_index * self.numGenes + gene_index

    def getMaxScores(self):
        """
        Returns a list of the top scoring triplets indices
        """
        maxScores = []
        for x in xrange(0,len(self.maxScore1) ):
            maxScores.append((self.maxScore1[x], self.maxScore2[x], self.maxScore3[x]))
        return maxScores

    

    def classify(self):
        """
        Returns a list of classifications based on the maxscores.
        0 means the first class, 1 means the second class.
        """
        ms = self.getMaxScores()
        classification_ptable = []
        for x in xrange(0, len(ms)):
            index1 =  ms[x][0]
            index2 =  ms[x][1]
            index3 =  ms[x][2]

            udv = self.unclassified_data_vector
            u = self.ptable_entry(udv[index1],udv[index2],udv[index3])
            ucptable = [] 
            for x in xrange(0,6):
                ucptable.append(0.0)

            for entry in u:
                ucptable[entry] = 1.0/len(u)
            classification_ptable.append(ucptable)

        classification = []
        for x in xrange(0,len(classification_ptable)):
            #kinda think we might like to have this info, hmm
            d1 = self.distance(classification_ptable[x],self.ptable[x][0])
            d2 = self.distance(classification_ptable[x],self.ptable[x][1])
            if d1<d2:
                classification.append(0)
            elif d1>d2:
                classification.append(1)
            else:
                classification.append(.5)#tie, not happy with this solution
        sum = reduce(lambda x,y:x+y, classification)
        if 2*sum > len(ms):
            return 1
        else:
            return 0

    def crossValidate(self, k=10):
        """
        Performs k-fold cross validation (k is an integer [2,samplesize])
        Returns the Matthews correlation coefficient.(-1.0, 1.0)
        """
        return crossValidate(self.data, self.numGenes, self.classSizes, self.filter, k)

    def distance(self, v1, v2):
        """
        Returns the square of the euclidian distance between v1 and v2
        """
        sum = 0.0
        for x in xrange(0,6):
            sum += (v1[x]-v2[x])**2
        return sum
        

    def addUnclassified(self, unclassifiedVector):
        """
        Stores unclassified vector as self.unclassified_data_vector
        """
        self.unclassified_data_vector = unclassifiedVector
}