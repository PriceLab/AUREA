import os
from warn import *
from GEO.Sample import Sample
from GEO.Dataset import Dataset
from GEO.Series import Series
from AUREA.parser.affyprobe2genesymbol import AffyProbe2GeneSymbol

class GEODataGetter(object):
    def __init__(self):
        self.geo_ids=[]
        self.matrix=[]
        self.probe_index={}
        self.gene_index={}
        self.samples=[]
        self.af2gs=AffyProbe2GeneSymbol()

	# need to set:
	# self.dt_id
	# self.samples (list of sample names)
	# self.sample_descriptions (list of sample descriptions, each of which might be a list of lines)
	# self.genes (list of gene names)
	# self.probes (list of probe names)
	# self.matrix (2D data matrix: [gene/probe index][sample_index]
	# self.subsets (as necessary) (subsets set but not used by DataTable, others might access)

    def add_geo_id(self, geo_id):
        if geo_id not in self.geo_ids: 
            self.geo_ids.append(geo_id)

    def add_geo_ids(self, geo_ids):
        for geo_id in geo_ids:
            self.add_geo_id(geo_id)

    def expand_geo_ids(self):
        '''
        convert all geo_ids to sample geo_ids (eg dataset ids or series ids)
        '''
        sample_ids=[]
        for geo_id in self.geo_ids:
            id_class=self.get_id_class(geo_id)
            geo=id_class(geo_id)
            sample_ids.extend(geo.sample_ids)
        self.geo_ids=sample_ids
                
    def table(self):
        try: return self._table
        except AttributeError: return self._build_table()

    def _build_table(self):
        # have to make sure that the gene/probe lists correspond exactly to 
        # the order of data in the table
        self.expand_geo_ids()
        for sample_id in self.geo_ids: # they're all sample ids after above call
            self.add_sample(Sample(sample_id))

        self._table=table
        return table

    ########################################################################
    # Build self.table, self.gene_index, self.probe_index, self.sample_index

    def add_sample(self, sample): # sample is a GEO.Sample object
        # need to populate: new column to self.data_table, self.genes or self.probes, 
        # self.samples, self.gene_index or self.probe_index
        # and maybe more, like self.sample_description

        # ok, some sanity checking first: 
        if not isinstance(sample, Sample):
            raise Exception("%s: not a Sample object", sample)
        if not re.search('^gene|probe$', id_type):
            raise Exception('id_type must be one of "gene" or "probe"')
        if sample.geo_id in self.samples: # sample.geo_id is used as the sample name
            return

        # get the data as a vector hash (pass on exceptions)
        try:
            (id_type, sample_data)=sample.expression_data(id_type='gene')
        except:
            (id_type, sample_data)=sample.expression_data(id_type='probe')
            
        # add genes in sample to matrix, backfilling new genes:
        for (gene_id, exp_val) in sample_data.items():
            if id_type == 'probe':
                probe_id=gene_id
                gene_id=self.probe2gene(gene_id)
            try:             i=id2index[gene_id]
            except KeyError: i=self._backfill(gene_id)
            self.matrix[i].append(exp_val)
        
        # for any genes in the table but not in the sample, set their value to 0
        for gene_id in self.genes:
            if gene_id not in sample_data:
                i=self.gene_index[gene_id]
                j=self.sample_index[sample.geo_id]
                self.matrix[i][j]=0.0
        

        
    def probe2gene(self, probe_id):
        return self.af2gs.p2g(probe_id)

    def gene2probes(self, gene_id):
        return self.af2gs.g2ps(gene_id)


    def _backfill(self, gene_id):
        gene_index=self.gene_index
        i=len(gene_index)
        gene_index[gene_id]=i

        for probe_id in self.gene2probes(gene_id):
            self.probe_index[probe_id]=i
        return i







'''        
        # set the sample list and index:
        self.samples.append(sample.geo_id)
        self.sample_index[sample.geo_id]=len(self.samples)-1
        try: self.sample_description[geo_id]=sample.description
        except AttributeError: pass
        n_samples=len(self.samples)

        # get the proper (gene or probe) id_list and index to use:
        exp_data=sample.expression_data(id_type)
        ids=self.genes if id_type == 'gene' else self.probes
        if not ids: ids=[]
        index=self.gene_index if id_type == 'gene' else self.probe_index
        if not index: index={}

        # add any of sample's genes to self.genes as needed, and rebuild the index:
        #  fixme: have to back-fill missing genes for previous samples
        ids_added=False
        if not hasattr(self, 'data_table'): self.data_table=[]
        for key_id in exp_data.keys():
            if key_id not in index:
                ids.append(key_id)
                ids_added=True
                backfill_list=[0.0]*(n_samples-1)
                self.data_table.append(backfill_list)

        if id_type == 'gene': 
            self.genes=ids      # add additions back in
            if ids_added: self.buildGeneIndex()
            index=self.gene_index
            n_ids=len(self.genes)
        else: 
            self.probes=ids
            if ids_added: self.buildProbeIndex()
            index=self.probe_index
            n_ids=len(self.probes)

        # create a column of data according to gene_ or probe_index, and add to self:
        # self.data_table[index[gene]] [index[sample]]
#        if not hasattr(self, 'data_table'): self.data_table=[list(x) for x in [[]]*n_ids]

        for (gene_id, value) in sample.data[id_type].items(): # (gene_id might be a probe_id)
            try: i=index[gene_id]
            except KeyError: raise Exception("unknown gene- or probe_id %s" % gene_id)
            gene_list=self.data_table[i]
            gene_list.append(value)



'''
