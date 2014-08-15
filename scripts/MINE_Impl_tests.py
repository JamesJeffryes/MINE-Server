__author__ = 'JGJeffryes'
from lib.biokbase.mine_database.Impl import mineDatabaseServices
import time

test_db = 'EcoCycexp2'
glucose = {u'Formula': u'C6H12O6', u'_id': u'Cb5b3273ab083d77ed29fbef8f7e464929af29c13',
           u'Names': [u'D-Glucose', u'Grape sugar', u'Dextrose', u'Glucose']}
test_molfile = open("./scripts/xanthine.mol", "r").read()

class Options():
    def __init__(self):
        self.adduct_file = "lib/All Adducts.txt"
        self.kbase_db = 'KBase'
        self.test_db = '1GenEcoCyc'

        self.positive_adduct_file = "lib/Positive Adducts full.txt"
        self.negative_adduct_file = "lib/Negative Adducts full.txt"
        self.adduct_list = ['M+H', 'M-H']
        self.tolerance = 2
        self.ppm = False
        self.ms_file = "lib/Unknowns.txt"
        self.halogens = True

config = Options()
services = mineDatabaseServices(None)

def test_quick_search():
    #print services.quick_search(config.test_db, 'WQZGKKKJIJFFOK-GASJEMHNSA-N')
    #assert services.quick_search(config.test_db, 'C00031') == ['Cb5b3273ab083d77ed29fbef8f7e464929af29c13']
    assert glucose in services.quick_search(test_db, 'Glucose')[0]


def test_database_query():
    #assert services.database_query('admin', '', '', False) == ['Illegal query']
    #assert services.database_query(test_db, 'KEGG_code', 'C00031', False) == [glucose]
    print services.database_query(test_db, "{'Names': 'Glucose'}")


def test_get_comps():
    print services.get_comps(config.test_db, ['Cb5b3273ab083d77ed29fbef8f7e464929af29c13'])


def test_get_models():
    meh = services.get_models()[0]
    assert meh[2] == (u'kb|fm.3375', u'Escherichia coli 97.0264')
    assert len(meh) == 2356


def test_get_adducts():
    meh = services.get_adducts()[0]
    assert len(meh[0]) == 33
    assert len(meh[1]) == 30
    assert meh[0][2] == 'M+Na '


def test_adduct_db_search():
    meh = services.adduct_db_search(test_db, 164.0937301, 2, ['M+H'], [], False, True, False)
    assert len(meh) == 4
    assert len(meh[1]) == 3


def test_pathway_search():
    meh = services.pathway_search(test_db, 'C1b443383bfb0f99f1afe6a37f3ff2dadc3dbaff1',
                                                       'C89b394fd02e5e5e60ae1e167780ea7ab3276288e', 3, False)
    assert len(meh) == 1
    assert meh[0] == ['C1b443383bfb0f99f1afe6a37f3ff2dadc3dbaff1', u'Rab0dd7bc1c91b88c6f6ba90362413cb31fe00a42',
                         u'C4d1c9d1a3841a799052b6e347f1a9553ed088092', u'R4cfa8ce3f06297e2282b42ad69356815ee18d94f',
                         u'C89b394fd02e5e5e60ae1e167780ea7ab3276288e']
    assert len(services.pathway_search(test_db, 'C1b443383bfb0f99f1afe6a37f3ff2dadc3dbaff1',
                                       'C89b394fd02e5e5e60ae1e167780ea7ab3276288e', 3, True)) == 9

def test_similarity_search():
    print services.similarity_search('EcoCycexp', 'O=C1CC(OC1COP(=O)(OP(=O)(O)O)O)n1cc(C)c(nc1=O)O', 0.8, 'FP2', 100)
    print services.similarity_search('EcoCycexp', test_molfile, 0.8, 'FP4', 100)

def test_structure_search():
    print services.structure_search("EcoCycexp", "smi", 'O=C1CC(OC1COP(=O)(OP(=O)(O)O)O)n1cc(C)c(nc1=O)O')
    print services.structure_search("EcoCycexp", "mol", test_molfile)

def test_substructure_search():
    print services.substructure_search('EcoCycexp', 'O=C1CC(OC1COP(=O)(OP(=O)(O)O)O)n1cc(C)c(nc1=O)O', 20)
    print services.substructure_search('KEGGexp', test_molfile, 20)

def test_batch_ms_adduct_search():
    result = services.batch_ms_adduct_search('KEGGexp', "181.071188116\n0.0", "form", 2.0, ['M+H'], ['eco'], False, True, False)
    #assert len(result) == 2
    print result
    meh = result[0]['adducts']
    assert len(meh) == 4
    assert isinstance(meh[1]['isomers'], list)

test_batch_ms_adduct_search()

"""
#positive
up_result = services.batch_ms_adduct_search("EcoCycexp", open("./scripts/Up_mz_Pos").read(), "form", 0.003, ['M+H', 'M+'], [], False, True, False)[0]
down_result = services.batch_ms_adduct_search("EcoCycexp", open("./scripts/Down_mz_Pos").read(), "form", 0.003, ['M+H', 'M+'], [], False, True, False)[0]

#negative
#up_result = services.batch_ms_adduct_search("EcoCycexp", open("./scripts/Up_mz_Neg").read(), "form", 0.003, ['M-', 'M+CH3COO'], [], False, True, False)[0]
#down_result = services.batch_ms_adduct_search("EcoCycexp", open("./scripts/Down_mz_Neg").read(), "form", 0.003, ['M-', 'M+CH3COO'], [], False, False, False)[0]


in_sillico_confidence = 0

up_maps = []
down_maps = []
for key in set(up_result[0].keys() + up_result[1].keys()):
    meh = len(up_result[0][key]) - len(down_result[0][key]) + in_sillico_confidence * (len(up_result[1][key]) - len(down_result[1][key]))
    if meh >= 1:
        up_maps.append((key, meh))

for key in set(down_result[0].keys() + down_result[1].keys()):
    meh = len(down_result[0][key]) - len(up_result[0][key]) + in_sillico_confidence * (len(down_result[1][key]) - len(up_result[1][key]))
    if meh >= 1:
        down_maps.append((key, meh))
print "Up Maps"
for x in sorted(up_maps, key=lambda x: -x[1]):
    print x
print "Down maps"
for x in sorted(down_maps, key=lambda x: -x[1]):
    print x
map = "map00340"
for comp in up_result[0][map]+up_result[1][map]:
    print services.database_query("EcoCycexp", "{'_id':'%s'}" %comp)
    """