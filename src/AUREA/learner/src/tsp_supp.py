%pythoncode{
class TSP:
    """
    Top Scoring Pairs class.
    
    This class runs the top scoring pairs algorithm described in The ordering
    of expression among a few genes can provide simple cancer biomarkers
    and signal BRCA I mutations by Lin et al in BMC Bioinformatics 2009, 10:256
    http://www.biomedcentral.com/1471-2105/10/256
    
    TSP was originally introduces by Geman,D. et al. (2004) Classifying 
    gene expression proles from pairwise mRNA comparisons. 
    Statistical Applications in Genetics and Molecular Biology Vol 3
    [2004], Issue 1 Article 19. 
    This code uses slightly modified code from 
    https://jshare.johnshopkins.edu/dnaiman1/public_html/rxa/ which is 
    the code described in the above mentioned paper.
    """

    def __init__(self, data, numGenes, classSizes, filter):
        """
        Initializes the object. 
        data is an IntVector containing the microarray data and should be
        generated by the dataPackager class. 
        numGenes is an integer containing the number of genes/probes per sample
            in the data table
        classSizes is an intvector containing the size of the 2 classes, 
            class 1 and class 2 respectively.
        filter (a two item IntVector) causes only the genes with the wilcoxon scores >= 
        the the filterth best wilcoxon scores to be considered
        """
        self.data = data
        self.numGenes = numGenes
        self.classSizes = classSizes
            
        if filter[1] < filter[0]:#need to be in order for c program
            #so swap
            temp = filter[1]
            filter[1] = filter[0]
            filter[0] = temp
        self.filter = filter
        self.unclassified_data_vector = None
        self.maxScore1 = None
        self.maxScore2 = None
        self.truth_table = IntVector()
        for i in range(4):
            self.truth_table.push_back(0)
    def train(self):
        """
        Trains on the given data.
        """
        self.maxScore1 = IntVector()
        self.maxScore2 = IntVector()

        runTSP(self.data, self.numGenes, self.classSizes, self.filter, self.maxScore1, self.maxScore2)

    def getMaxScores(self):
        """
        Returns a list of the top scoring pairs indices
        """
        maxScores = []
        for x in xrange(0,len(self.maxScore1) ):
            maxScores.append((self.maxScore1[x], self.maxScore2[x]))
        return maxScores

    def addUnclassified(self, unclassifiedVector):
        self.unclassified_data_vector = unclassifiedVector

    def classify(self):
        ms = self.getMaxScores()
        classification = []
        for pair in ms:
            index1 =  pair[0]
            index2 =  pair[1]
            if( self.unclassified_data_vector[index1] > self.unclassified_data_vector[index2] ):
                classification.append(0)
            elif self.unclassified_data_vector[index1] < self.unclassified_data_vector[index2]:
                classification.append(1)
            else:
                classification.append(.5)#tie, not happy with this solution
        sum = reduce(lambda x,y:x+y, classification)
        if 2*sum > len(ms):
            return 1
        else:
            return 0

    def crossValidate(self, k=10, use_acc=True):
        """
        Runs the C-based cross validation
        K-fold testing of the given data, returns the Matthews correlation coefficient [-1.0, 1.0].
        """
        return crossValidate(self.data, self.numGenes, self.classSizes, self.filter,self.truth_table, k)

    def _makeList(self, vector):
        temp_list = []
        for x in xrange(len(vector)):
            temp_list.append(vector[x])
        return temp_list
    def _makeVector(self, aList, vtype):
        if vtype == 'd':
            myVector = DoubleVector()
        else:
            myVector = IntVector()
        for x in aList:
            myVector.push_back(x)
        return myVector

    def __getstate__(self):
        print "HERE"
        odict = self.__dict__.copy()
        odict['data'] = self._makeList(self.data) 
        odict['classSizes'] = self._makeList(self.classSizes)
        odict['filter'] = self._makeList(self.filter)

        if self.unclassified_data_vector is not None:
            odict['unclassified_data_vector'] = self._makeList(self.unclassified_data_vector)

        if self.maxScore1 is not None:
            odict['maxScore1'] = self._makeList(self.maxScore1)
        if self.maxScore2 is not None:
            odict['maxScore2'] = self._makeList(self.maxScore2)
        return odict

    def __setState__(self, odict):
        odict['data'] = self._makeVector(odict['data'], 'd') 
        odict['classSizes'] = self._makeVector(odict['classSizes'], 'i')
        odict['filter'] = self._makeVector(odict['filter'])

        if odict['unclassified_data_vector'] is not None:
            odict['unclassified_data_vector'] = self._makeVector(odict['unclassified_data_vector'])

        if self.maxScore1 is not None:
            odict['maxScore1'] = self._makeVector(odict['maxScore1'])
        if self.maxScore2 is not None:
            odict['maxScore2'] = self._makeVector(odict['maxScore2'])
        self.__dict__.update(odict)
       
        
}
