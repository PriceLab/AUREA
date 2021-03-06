%pythoncode{
import dirac
class Dirac:
    """
    This is the python class that controls the execution of the 
    DIRAC algorithm.
    The format of the inputs are quite exhaustively described in the
    dirac.cpp file.
    If you are curious about DIRAC the algorithm please check out
    "Identifying Tightly Regulated and Variably Expressed Networks
    by Differential Rank Conservation" by James A. Eddy, et al
    Published in PLoS Computational Biology May 2010 | Volume 6 |
    Issue 5.
    """
    def __init__(self, data, numGenes,classSizes, geneNet, geneNetSize, numTopNetworks, netMap):
        """        
Creates a Dirac learner object
    data - DoubleVector with data
    numgenes - number of genes per sample
    classSizes = IntVector of size 2 where a[0] = class 1 size
    geneNet - an intvector that contains indices of genes that are part of a gene netwotk
    geneNetSize - Describes the size of each gene network, used to mark the start and end of networks in geneNet. (i.e. if gNS[0] = 5 that means the first five gene indices in geneNet are for network 0.
    ((geneNet, geneNetSize) = dp.getGeneNetVector('gene'))
    numTopNetworks - int, number of networks to use for classification
    
    netMap - maps a gene network to a human readable name. (dp.gene_net_map)
        """ 
        if netMap is None:
            raise Exception("You need to add the Gene Network Map")
        #copy geneNet and geneNetSize
        #hacky crap because I did not think ahead in datapackager
        #running multiple diracs on different minimum network
        #sizes screws up the mapping
        #prob need to add the min gene net size to Dirac
        self.geneNet = IntVector()
        for x in geneNet:
            self.geneNet.push_back(x)
        self.geneNetSize = IntVector()
        for x in geneNetSize:
            self.geneNetSize.push_back(x)
        self.netMap=netMap[:]
       
        self.data = data
        self.numGenes = numGenes
        self.classSizes = classSizes
        self.numTopNetworks = numTopNetworks
        if len(self.geneNet) == 0:
            raise Exception('invalid network size', 'Dirac was provided with a zero length network.')
        self.unclassified_data_vector = None
        self.unClassifiedRankMatrix = None
        self.rank_templates = None
        #lists the starting locations of each geneNetwork in the data matrix
        self.unclassifiedRankMatrix = None
        self.truth_table = IntVector()
        for i in range(4):
            self.truth_table.push_back(0)
    def train(self):
        """
        This is the method that performs the training from the provided data
        """
        self.RankMatrix = BoolVector()
        self.RankMatching = DoubleVector()
        self.RankConservation = DoubleVector()
        runDirac(self.data, self.numGenes, self.classSizes, self.geneNet, self.geneNetSize, self.RankMatrix, self.RankMatching, self.RankConservation)
    
    def classify(self):
        """
        Returns 0 or 1.
        The netStart and netEnd
        are where in the rank templates and unclassified rank vector the
        gene network you are interested in is located.

        Update: you can now set numTopNetworks in the constructor.
        Passing here should be deprecated.
        """
        numTopNetworks = self.numTopNetworks
        
        classification_list = []
        rc = self.getRankDifference()
        for x in xrange(0,numTopNetworks):
            netNum = rc[x][1]
            rms = self.getRankMatchingScores()
            classification_list.append( self.classify_network(netNum) ) 
        sum = reduce(lambda x,y:x+y, [x[0] for x in classification_list])
        if 2*sum > len(classification_list):
            return 1
        else:
            return 0

    def classify_network(self, network_index):
        """
        Returns a tuple that contains
        (classified class [0 or 1], class one percent match, 
        class two percent match)
        uses C classify function
        """
        #calling C classify
        geneNetRankStart = self.getNetworkRankStart(network_index)
        geneNetRankSize = self.getNetworkRankSize(network_index)
        geneNetStart = self.getNetworkStart(network_index)
        geneNetSize = self.geneNetSize[network_index]
        score = DoubleVector()
        res = classify(self.RankMatrix, self.classSizes[0], self.classSizes[1],
            self.unclassified_data_vector, self.geneNet, geneNetRankStart, geneNetRankSize,
            geneNetStart, geneNetSize, score)
        return (res, score[0], score[1])
            
   
    def getUnclassifiedRankTemplate(self, geneNetwork ):
        """
        Builds the rank template for the unclassified vector
        for the subset defined by the gene network at genestart
        that goes to geneEnd
        """
        unclassified_template = []
        geneStart = self.getNetworkStart( geneNetwork)
        geneEnd = geneStart + self.geneNetSize[geneNetwork]
        for i in xrange(geneStart, geneEnd-1):
            for j in xrange(i+1,geneEnd):
                gene1index = self.geneNet[i]
                gene2index = self.geneNet[j]
                #print str(gene1index) + " " + str( gene2index )
                unclassified_template.append(self.unclassified_data_vector[gene1index] < self.unclassified_data_vector[gene2index])
        return unclassified_template    

    def addUnclassified(self, unclassifiedVector):
        """
        Takes unclassified data vector and saves it
        """
        self.unclassified_data_vector = unclassifiedVector


       
    def getRankMatrix(self):
        """
        Returns the rankMatrix as a list of Bools
        [
            [class1.sample1.genenet1.gene1,  sample1.genenet1.gene2 , ... sample1.gnN,gN]
            [class1.sample2.genenet1.gene1, sample2.geneNet1.gene2, ...]
            ...
            [class2.samplen.genenet1.gene1, ...]

        ]
        """
        numCols = 0
        for i in xrange(len(self.geneNetSize)):
            numCols += self.nChooseTwo( self.geneNetSize[i] )        
        rm = self.vecToList(self.RankMatrix, numCols)
        rtColumn = 0
        for i in xrange(len(self.classSizes)):
            rtColumn += self.classSizes[i]
            del rm[rtColumn]    

        return rm
    
    def getRankTemplates(self):
        """
        Returns the rank templates for class1 class2
        [
            [class 1 rt by geneNetwork order]
            [class 2 rt by geneNetwork order]
        ]
        """
        if self.rank_templates == None:
            numCols = 0
            for i  in xrange(len(self.geneNetSize)):
                numCols += self.nChooseTwo( self.geneNetSize[i] )
            rm = self.vecToList(self.RankMatrix, numCols)
            rtColumn = 0
            rt = []
            for i in xrange(len(self.classSizes)):
                rtColumn += self.classSizes[i]
                rt.append( rm[rtColumn] )
                rtColumn += 1
        else:
            rt = self.rank_templates
        return rt    

    def getRankMatchingScores(self):
        """
        Returns a list of lists  {(2 * num genenetworks) x (number of samples)}
        containing the rank matching scores
        which describe how well a sample matches a template.
        [   
           rms of rt.c1.gN1 vs [c1.sa1.gN1, c1.sa2,gN1, ... c2.san.gN1],
                  rt.c2.gN1 vs [c1.sa1.gN1, c1.sa2,gN1, ... c2.san.gN1],
                    ...,
                  rt.c2.gNn vs [c1.sa1.gNn, c1.sa2,gNn, ... c2.san.gNn],
  
                
        ]
        """
        numClasses = 0
        for i in xrange(len(self.classSizes)):
            numClasses += self.classSizes[i]
        return self.vecToList(self.RankMatching, numClasses)

    def getRankConservation(self):
        """
        Returns a list of lists that contains the rank conservation score
        for each class and gene network
        [
            rcs for
            [gn1.class1,gn1.class2],
            [gn2.class1,gn2.class2],
            ...,
            [gnn.class1,gn2.class2]
        ] 
        """
        rc_list =  self.vecToList(self.RankConservation, 2)
        return rc_list

    def getRankDifference(self, numNets = None):
        """
        Returns a list of tuples containing (sum of matches, gene_index, distance) in sorted order
        """
        counter = 0
        conservation_list = [] 
        stack = [] 
        
        for rcV in self.getRankMatchingScores():
            #print counter
            if len(stack) == 0:
                stack.append(rcV)
            else:
                A = stack[0]
                B = rcV
                temp = []
                match1 = 0 #counts the number of correct classifications
                match2 = 0
                dist1 = 0.0# a secondary tiebreaking score - roughly the sum of distance
                dist2 = 0.0
                for i in xrange(0,self.classSizes[0]):
                    if( A[i] - B[i] > 0.00):
                        match1 += 1
                    dist1 += A[i] - B[i]
                    
                   
                for i in xrange(self.classSizes[0], self.classSizes[1]):
                    if( B[i] - A[i] > 0.00):
                        match2 += 1
                    dist2 += B[i] - A[i]
                match = self.classSizes[1] * match1 + self.classSizes[0]*match2
                dist = self.classSizes[1] * dist1 + self.classSizes[0]* dist2
                #DEBUG
                if False and match == 0:
                    print "Gene Number " + str(counter) + " had zero matches "
                conservation_list.append( (match, counter, dist) )  
                counter += 1
                stack = []
        def ourRanker(x, y):
            if x[0] == y[0]:
                if( x[2] - y[2]  > 0):
                    return 1
                else:
                    return -1
            else:
                return x[0] - y[0]
        conservation_list.sort(cmp = lambda x,y: ourRanker(y,x)) 
        if numNets is not None:
            conservation_list = conservation_list[:numNets]
        return conservation_list

    def getTopNetworks(self):
        """
        returns a list of the top networks(by name) as determined by get rank difference
        """
        #NOTE: this was changed on May 11.
        #TODO: cleanup the topNetworks and datapackage stuff in v2
        rd = self.getRankDifference( self.numTopNetworks )
        netList = [self.netMap[x[1]] for x in rd]

        return netList
 
    def getNetworkRankStart(self, network_id):
        """
        Returns the starting index of a network segment of
        a rank based data structure (template or matrix)
        """
        nrs = map(lambda x:self.nChooseTwo(x), self.geneNetSize)
        nrs.insert(0,0)#add zero as the first start
        return reduce(lambda x,y: x+y,nrs[0: network_id +1 ])

    def getNetworkRankSize(self, network_idx):
        """
        Returns the size of a network segment of
        a rank based data structure (template or matrix)
        """
        return self.nChooseTwo(self.geneNetSize[network_idx])
        

    def getNetworkStart(self, network_id):
        """
        Maps the gene network( relative to its position in geneNetSize)
        to the starting location of its data matrix entries.
        i.e finding the starting location of the gene indices in the
        data matrix tables for the 3rd gene would be getNetworkStart(3)
        """
        if network_id > 1:
            return reduce(lambda x,y: x+y, self.geneNetSize[0:network_id])
        elif network_id == 1:
            return self.geneNetSize[0]
        else:
            return 0

    def crossValidate(self,k=10, use_acc=True):
        """
        Runs the C-based cross validation
        K-Fold testing of the given data, returns Matthews correlation coefficient.
        """
        numTopNetworks = self.numTopNetworks
        
        crossValidate(self.data, self.numGenes, self.classSizes, self.geneNet, self.geneNetSize, numTopNetworks, k, self.truth_table) 

       
    def getCVAccuracy(self):
        """
        Returns the Accuracy of the last crossValidate
        """
        tpos = self.truth_table[0]
        tneg = self.truth_table[1]
        fpos = self.truth_table[2]
        fneg = self.truth_table[3] 
        return float((tpos+tneg))/(tpos+tneg+fpos+fneg)

    def getCVMCC(self):
        """
        Returns the Matthews Correlation Coefficient of the last crossValidate
        """
        import math
        tpos = self.truth_table[0]
        tneg = self.truth_table[1]
        fpos = self.truth_table[2]
        fneg = self.truth_table[3] 
        den = math.sqrt(float((tpos+fpos)*(tpos+fneg)*(tneg+fpos)*(tneg+fneg)))
        if den < .000001:
            den = 1.0
        return float(tpos*tneg - fpos*fneg)/den


    def testAll(self):
        """
        Some testing for debugging purposes
        """
        test = []
        dm = self.vecToList(self.data, self.numGenes)
        if len(dm) != (self.classSizes[0]+self.classSizes[1]):
            print "data parses incorrectly"
        rt = []
        counter = 0
        for x in self.geneNetSize:
            #for each network
            start = self.getNetworkStart(counter)
            rt.append(([],[]))
            for i in xrange(x-1):
                gene1 = self.geneNet[start + i]
                for j in xrange(i+1, x):
                    gene2 = self.geneNet[start + j]
                    if(gene1 == gene2) and False:
                        print "gene net number " + str(counter) + " has duplicate genes "
                        test.append(counter)
                    rt[-1][0].append(0)
                    for samp in xrange(0,self.classSizes[0]):
                        if dm[samp][gene1] < dm[samp][gene2]:
                            rt[-1][0][-1] += 1
                    
                    rt[-1][1].append(0)
                    for samp in xrange(self.classSizes[0], self.classSizes[0] + self.classSizes[1]):
                        if dm[samp][gene1] < dm[samp][gene2]:
                            rt[-1][1][-1] += 1
                   
 
            counter += 1
        drt = self.getRankTemplates()
        mismatch = 0
        mycounter = 0
        first = rt[1]
        ns = self.getNetworkRankStart(1)
        ne = self.getNetworkRankStart(2)

        print len(first[0])
        print map(lambda x: x > 25/2,  first[0])
        print drt[0][ns:ne]
        print map(lambda x: x > 18/2, first[1])
        print drt[1][ns:ne]
        myrt1 = [] 
        myrt2 = []
        for network in rt:
            precounter = mycounter
            for gene in network[0]:
                myrt1.append(gene > self.classSizes[0]/2)
            for gene in network[1]:
                myrt2.append(gene > self.classSizes[1]/2)
        counter = 0
        for val in myrt1:
            if val != drt[0][counter]:
                mismatch+=1 
            counter += 1
        counter = 0
        for val in myrt2:
            if val != drt[1][counter]:
                mismatch+=1 
            counter += 1
 
        return (mismatch, len(drt[0]))

    def nChooseTwo(self, n ):
        return (n*(n-1))/2

    def vecToList(self, vector, numRows):
        """
        Takes a vector and turns it into a list of lists with the inner lists
        having len(numRows)
        """
        newList = []
        counter = 0
        newList.append([])
        for x in xrange(len(vector)):
            if counter == numRows:
                counter = 0
                newList.append([])
            newList[-1].append(vector[x])
            counter += 1
        return newList
}
