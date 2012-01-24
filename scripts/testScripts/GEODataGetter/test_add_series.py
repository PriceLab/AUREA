import unittest, sys, os, bson

sys.path.append(os.path.join(os.environ['AUREA_HOME'], 'src'))
sys.path.append(os.path.join(os.environ['TRENDS_HOME'], 'pylib'))

from warn import *
from AUREA.parser.GEODataGetter import GEODataGetter
import GEO

gdd=None

class TestGDD(unittest.TestCase):
    
    def setUp(self):
#        os.environ['DEBUG']=str(True)
        pass

    def test_GSE001(self):
        GEO.GEOBase.data_dir=os.path.join(os.environ['TRENDS_HOME'], 't', 'fixtures', 'data', 'GEO')
        self._test_add_series('GSE001')
        gdd.writeCSV(os.path.join(os.path.dirname(__file__), 'GSE001.csv'))
        gdd.write_gene_index(os.path.join(os.path.dirname(__file__), 'GSE001.gene_index'))


        # test specifics:
        matrix=gdd.matrix
#        warn("matrix\n%s" % matrix)
        i_row=gdd.probe_index['1294_at']
        i_col=gdd.sample_index['GSM00003']
        val=matrix[i_row][i_col]
        warn("matrix[%d][%d]=%s" % (i_row, i_col, val))
        self.assertEqual(matrix[gdd.probe_index['1294_at']][gdd.sample_index['GSM0003']], 0)
        self.assertEqual(matrix[gdd.gene_index['UBA7']][gdd.sample_index['GSM0003']], 0)


    def _test_GSE10072(self):
        GEO.GEOBase.data_dir=os.path.join(os.environ['TRENDS_HOME'], 'data', 'GEO')
        self._test_add_series('GSE10072')

    def _test_add_series(self, geo_id):
        global gdd
        if not gdd:
            gdd=GEODataGetter(geo_id)
        gdd.add_geo_id(geo_id)
        matrix=gdd.matrix

        n_genes=gdd.n_genes()
        n_probes=gdd.n_probes()
        n_samples=gdd.n_samples()
        warn("%s: %d(%d) x %d matrix" %(geo_id, n_genes, n_probes, n_samples))
#        warn("matrix is %s" % matrix)

        series=GEO.Series.Series(geo_id).populate()
        self.assertIsInstance(series._id, bson.objectid.ObjectId)

        warn("checking samples...")
        for sample_id in series.sample_id:
            sample=GEO.Sample.Sample(sample_id)
            (id_type, sample_data)=sample.expression_data('probe')
            i_sample=gdd.sample_index[sample_id]

            # check every gene in every sample...
            for id,exp_val in sample_data.items():
                try: gi=gdd.probe_index[id]
                except KeyError: 
                    warn("%s: %s not found in probe index" %(sample_id, id))
                self.assertAlmostEqual(matrix[gi][i_sample], exp_val, delta=0.001,
                                   msg="%s: [%s][%s]=%s, not %s (%s)" % (id, gi, i_sample, matrix[gi][i_sample], exp_val, sample_id))


        
        # check to see that all genes present; also, indexes
        # check to see that all probes present; also, indexes
        # check to see that len(samples)==1


    def verify_indexes(self):
        # make sure that all gene and probe indexes match
        pass

suite = unittest.TestLoader().loadTestsFromTestCase(TestGDD)
unittest.TextTestRunner(verbosity=2).run(suite)


        

