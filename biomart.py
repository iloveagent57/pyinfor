import httplib, urllib
import sys
from collections import Iterable
from shlex import split as shlex_split
from collections import OrderedDict

"""
to interact with martservice through www.biomart.org

Author: Xiao Jianfeng
last updated: 2012.01.10

http://www.biomart.org/martservice.html
	
 BioMart  	 MartService

(a) Querying BioMart

To submit a query using our webservices generate an XML document conforming to our Query XML syntax. This can be achieved simply by building up your query using MartView and hitting the XML button. This XML should be posted to http://www.biomart.org/martservice attached to a single parameter of query. For example you could either:

    save your query as Query.xml and then POST this using the webExample.pl script in our biomart-perl/scripts installation.
    submit using wget: wget -O results.txt 'http://www.biomart.org/biomart/martservice?query=MY_XML' replacing MY_XML with the XML obtained above, first removing any new lines.


(b) Retrieving Meta Data

    to retrieve registry information: http://www.biomart.org/biomart/martservice?type=registry
    to retrieve datasets available for a mart: http://www.biomart.org/biomart/martservice?type=datasets&mart=ensembl
    to retrieve attributes available for a dataset: http://www.biomart.org/biomart/martservice?type=attributes&dataset=oanatinus_gene_ensembl
    to retrieve filters available for a dataset: http://www.biomart.org/biomart/martservice?type=filters&dataset=oanatinus_gene_ensembl
    to retrieve configuration for a dataset: http://www.biomart.org/biomart/martservice?type=configuration&dataset=oanatinus_gene_ensembl


  	SOAP Access
The SOAP based access is functionally equivalent to the REST style access described above. For description on BioMart SOAP based Web Service (MartServiceSoap), see:

    MartServiceSoap Endpoint (for SOAP based access only): http://www.biomart.org/biomart/martsoap
    MartServiceSoap WSDL: http://www.biomart.org/biomart/martwsdl
    MartServiceSoap XSD: http://www.biomart.org/biomart/martxsd


For more information see the web services section of our documentation.
Page last updated: 05/10/2011 15:25:40

http://www.biomart.org/faqs.html is also worth reading. Many examples how to build queries are available here!!
"""

example1 = """
output: --------------------------------------------------------------------------------------------
HGNC symbol 	Affy HC G110 	Ensembl Gene ID 	EntrezGene ID 	Ensembl Transcript ID
TAL1 	560_s_at 	ENSG00000162367 	6886 	ENST00000371884
TAL1 	560_s_at 	ENSG00000162367 	6886 	ENST00000294339
TAL1 		ENSG00000162367 	6886 	ENST00000459729
TAL1 		ENSG00000162367 	6886 	ENST00000464796
TAL1 		ENSG00000162367 	6886 	ENST00000481091
TAL1 		ENSG00000162367 	6886 	ENST00000465912
TAL1 	560_s_at 	ENSG00000162367 	6886 	ENST00000371883
CYP4A11 	1391_s_at 	ENSG00000187048 	1579 	ENST00000310638
CYP4A11 	1391_s_at 	ENSG00000187048 	1579 	ENST00000475477
CYP4A11 	1391_s_at 	ENSG00000187048 	1579 	ENST00000462347

query:  --------------------------------------------------------------------------------------------     
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE Query>
    <Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >
                            
            <Dataset name = "hsapiens_gene_ensembl" interface = "default" >
                    <Filter name = "ensembl_gene_id" value = "ENSG00000162367,ENSG00000187048"/>
                    <Attribute name = "hgnc_symbol" />
                    <Attribute name = "affy_hc_g110" />
                    <Attribute name = "ensembl_gene_id" />
                    <Attribute name = "entrezgene" />
                    <Attribute name = "ensembl_transcript_id" />
            </Dataset>
    </Query>

left side of biomart:  -------------------------------------------------------------------------------
    Dataset
    Homo sapiens genes (GRCh37.p5)
    Filters
    Ensembl Gene ID(s) [e.g. ENSG00000139618]: [ID-list specified]
    Attributes
    HGNC symbol
    Affy HC G110
    Ensembl Gene ID
    EntrezGene ID
    Ensembl Transcript ID
    """

DEBUG = False

mart_host = "www.biomart.org"
mart_url_prefix = "/biomart/martservice?"

#-----------------------------------------------------------------
def reporthook(blocks_read, block_size, total_size):
    """
    could be used to report progress while downloading.

    url = 'http://www.biomart.org/biomart/martservice?'
    query4 = '<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "1" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >

        <Dataset name = "hsapiens_gene_ensembl" interface = "default" >
                <Attribute name = "ensembl_gene_id" />
                <Attribute name = "ensembl_transcript_id" />
                <Attribute name = "external_gene_id" />
                <Attribute name = "external_transcript_id" />
                <Attribute name = "hgnc_id" />
                <Attribute name = "hgnc_transcript_name" />
                <Attribute name = "hgnc_symbol" />
        </Dataset>
</Query>
'
    b = urllib.urlretrieve(url=url, data=urllib.urlencode(dict(query=query4)), reporthook=biomart.reporthook)

    But it would be difficult to set timeout for this method.
    """

    if DEBUG:
        print >> sys.stderr, blocks_read, block_size, total_size,
    if not blocks_read:
     print >> sys.stderr, 'Opened',
     return
    if total_size < 0:
     # Unknown size
     print >> sys.stderr, '\rRead %d blocks' % blocks_read,
    else:
     amount_read = blocks_read * block_size
     print >> sys.stderr, '\rRead %d blocks, or %d/%d' % (blocks_read, amount_read, total_size),

    return

#-----------------------------------------------------------------
def build_query(dataset, attributes, filters=None, formatter="TSV"):
    """
    Only dataset, filters, and attributes are needed to build a query, while database is not needed.
    I guess this is because the dataset name is enough to identify itself.

    dataset: table name
    filters: should be a dict
    attributes: should be list

    formatter: TSV or FASTA
    """

    mart_query_dataset = """\t<Dataset name = "%s" interface = "default" >\n""" % dataset

    if formatter == 'TSV':
        #Note: if header = "0" --> no header; header = "1" or "ture" --> with header
        # limit = N could also be added 
        mart_query_header = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE Query>
        <Query  virtualSchemaName = "default" formatter = "TSV" header = "1" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >\n"""
    elif formatter == 'FASTA':
        mart_query_header = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE Query>
        <Query  virtualSchemaName = "default" formatter = "FASTA" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >\n"""
    else:
        raise Exception("Currently only 'TSV' and 'FASTA' are supported as formatter")
        
    mart_query_tail = "\t</Dataset>\n</Query>"

    if filters:  # filters may be None
        filter_buffer = []
        for k, v in filters.items():
            if not isinstance(v, Iterable):
                raise Exception("%s should be iterable" % v)
            if not isinstance(v, basestring): # v is a list or tuple of string, else, v is string
                v = ",".join(v)
            item_str = """\t\t<Filter name = "%s" value = "%s"/>\n""" % (k, v)
            filter_buffer.append(item_str)
        mart_query_filter = "".join(filter_buffer)
    else:
        mart_query_filter = ""

    if isinstance(attributes, basestring): # if attributes is a single value, make it a list
        attributes = [attributes]
    mart_query_attributes = "".join("""\t\t<Attribute name = "%s" />\n""" % s for s in attributes)

    xml =  mart_query_header +\
            mart_query_dataset + mart_query_filter + mart_query_attributes +\
            mart_query_tail 

    return xml


#-----------------------------------------------------------------
class BioMart:

    def __init__(self, mart=None, dataset=None, timeout=1000):
        """ it seems mart is necessary to query biomart, dataset+[filters+]attributes is enough"""

        self.con = httplib.HTTPConnection(mart_host, timeout=timeout)
        self.mart = mart
        self.dataset = dataset

    def use_mart(self, mart):
        """set the value of mart
        This method is the same with use_database"""
        self.mart = mart

    def use_database(self, database):
        self.mart = database

    def use_dataset(self, dataset):
        self.dataset = dataset

    def easy_response(self, params_dict, echo=False):
        params = urllib.urlencode(params_dict)
        self.con.request(method="POST", url=mart_url_prefix, body=params)
        response = self.con.getresponse()
        print "submit:", response.status, response.reason
        data = response.read()
        if echo:
            print data
        return response.status, response.reason, data

    def query(self, xml=None, dataset=None, filters=None, attributes=None):
        """ To query biomart.
        query(xml) or query(dataset, filters, attributes)

        xml: a str of xml 

        dataset: table name
        filters: should be a dict
        attributes: should be list
        """

        if xml is None:
            xml = build_query(dataset=dataset, attributes=attributes, filters=filters)
        params_dict = {"query": xml}
        return self.easy_response(params_dict)

    def registry_information(self):
        """
        actually list all available databases

        "name" filed in retrieved information could be used to retrieve available datasets.

        Example:

<MartRegistry>
  <MartURLLocation database="ensembl_mart_65" default="1" displayName="ENSEMBL GENES 65 (SANGER UK)" host="www.biomart.org" includeDatasets="" martUser="" name="ensembl" path="/biomart/martservice" port="80" serverVirtualSchema="default" visible="1" />
  <MartURLLocation database="snp_mart_65" default="0" displayName="ENSEMBL VARIATION 65 (SANGER UK)" host="www.biomart.org" includeDatasets="" martUser="" name="snp" path="/biomart/martservice" port="80" serverVirtualSchema="default" visible="1" />
  <MartURLLocation database="functional_genomics_mart_65" default="0" displayName="ENSEMBL REGULATION 65 (SANGER UK)" host="www.biomart.org" includeDatasets="" martUser="" name="functional_genomics" path="/biomart/martservice" port="80" serverVirtualSchema="default" visible="1" />
  ...
</MartRegistry>
        """

        params_dict = {"type":"registry"}

        status, reason, data = self.easy_response(params_dict, echo=False)

        # parse the output to make it more readable
        databases = []
        for line in data.strip().split('\n'):
            ln = shlex_split(line)
            ln_dict = dict(item.split('=') for item in ln if '=' in item)
            if 'name' in ln_dict and 'displayName' in ln_dict:
                databases.append(OrderedDict(biomart=ln_dict['name'], version=ln_dict['displayName']))
        name_max_len = max(len(d['biomart']) for d in databases)
        version_max_len = max(len(d['version']) for d in databases)

        print "".ljust(5), 'biomart'.rjust(name_max_len+1), 'version'.rjust(version_max_len+1)
        for i, d in enumerate(databases):
            print str(i+1).ljust(5), d['biomart'].rjust(name_max_len+1), d['version'].rjust(version_max_len+1)

        return databases

    def available_databases(self):

        return self.registry_information()

    def available_datasets(self, mart=None):
        """
TableSet	oanatinus_gene_ensembl	Ornithorhynchus anatinus genes (OANA5)	1	OANA5	200	50000	default	2011-09-07 22:26:09
TableSet	tguttata_gene_ensembl	Taeniopygia guttata genes (taeGut3.2.4)	1	taeGut3.2.4	200	50000	default	2011-09-07 22:26:36
TableSet	cporcellus_gene_ensembl	Cavia porcellus genes (cavPor3)	1	cavPor3	200	50000	default	2011-09-07 22:27:40
(......)

The second column could be used in self.available_attributes() and self.available_filters() to retrieve available attributes and filters for a given dataset.
"""

        mart = mart if mart else self.mart
        if mart is None:
            raise Exception("mart in available_databases() and self.mart couldn't be all None")
        print "Mart being used is: ", mart

        params_dict = {"type":"datasets", "mart":mart}

        status, reason, data = self.easy_response(params_dict, echo=False)

        # parse the output to make it more readable
        data2 = [ln.split('\t') for ln in data.strip().split('\n') if ln.strip()]
        data3 = [[ln[1], ln[2], ln[4]] for ln in data2] # dataset, description, version
        datasets = [OrderedDict(dataset=ln[0], description=ln[1], version=ln[2]) for ln in data3]
        max_len_dataset = max(len(d['dataset']) for d in datasets)
        max_len_description = max(len(d['description']) for d in datasets)
        max_len_version = max(len(d['version']) for d in datasets)

        print "".ljust(5), 'dataset'.rjust(max_len_dataset+1), 'description'.rjust(max_len_description+1), 'version'.rjust(max_len_version+1)
        for i, d in enumerate(datasets):
            print str(i+1).ljust(5), d['dataset'].rjust(max_len_dataset+1), d['description'].rjust(max_len_description+1), d['version'].rjust(max_len_version+1)

        return datasets

    def available_attributes(self, dataset=None):
        """
        To retrieve available attributes for a given dataset.

        dataset is a valid dataset, for example: hsapiens_gene_ensembl, oanatinus_gene_ensembl, tguttata_gene_ensembl
        dataset could be retrived by self.available_datasets()
        """

        dataset = dataset if dataset else self.dataset
        if dataset is None:
            raise Exception("dataset in available_attributes() and self.dataset couldn't be all None")
        print "Dataset being used is: ", dataset

        params_dict = {"type":"attributes", "dataset":dataset}
        status, reason, data = self.easy_response(params_dict, echo=False)

        # parse the output to make it more readable
        data2 = [ln.split('\t') for ln in data.strip().split('\n')]
        attributes = [OrderedDict(name=ln[0], description=ln[1], long_description=ln[2]) for ln in data2]

        max_len_name = max(len(f['name']) for f in attributes)
        max_len_description = max(len(f['description']) for f in attributes)

        print "".ljust(5), 'name'.rjust(max_len_name+1), 'description'.rjust(max_len_description+1)
        for i, d in enumerate(attributes):
            print str(i+1).ljust(5), d['name'].rjust(max_len_name+1), d['description'].rjust(max_len_description+1)

        return attributes

    def available_filters(self, dataset=None):
        """
        To retrieve available filters for a given dataset.
        """

        dataset = dataset if dataset else self.dataset
        if dataset is None:
            raise Exception("dataset in available_filters() and self.dataset couldn't be all None")
        print "Dataset being used is: ", dataset

        params_dict = {"type":"filters", "dataset":dataset}
        status, reason, data = self.easy_response(params_dict, echo=False)

        # parse the output to make it more readable
        data2 = [ln.split('\t') for ln in data.strip().split('\n')]
        filters = [OrderedDict({'name': ln[0], 'description': ln[1], 'possible_data': ln[2]}) for ln in data2]

        max_len_name = max(len(f['name']) for f in filters)
        max_len_description = max(len(f['description']) for f in filters)

        print "".ljust(5), 'name'.rjust(max_len_name+1), 'description'.rjust(max_len_description+1)
        for i, d in enumerate(filters):
            print str(i+1).ljust(5), d['name'].rjust(max_len_name+1), d['description'].rjust(max_len_description+1)

        return filters

    def configuration(self, dataset=None):
        """
        To get configuration for a dataset.
        """

        dataset = dataset if dataset else self.dataset
        if dataset is None:
            raise Exception("dataset in configuration() and self.dataset couldn't be all None")
        print "Dataset being used is: ", dataset

        params_dict = {"type":"configuration", "dataset":dataset}

        return self.easy_response(params_dict, echo=True)

    def test_query(self):
        # mart_query_database = 'ensembl'  # not needed, as the dataset name itself is enough to identify itself.
        # could be one dataset or more, how to explain multiple datasets remains to be determined
        mart_query_dataset = 'hsapiens_gene_ensembl'
        mart_query_filters = {"chromosome_name": "Y"}
        mart_query_attributes = ["ensembl_gene_id", "ensembl_transcript_id", 
                                 "external_gene_id", "external_transcript_id",
                                 "hgnc_id", "hgnc_transcript_name", "hgnc_symbol"]

        xml = build_query(dataset=mart_query_dataset, attributes=mart_query_attributes, filters=mart_query_filters)
        print xml
        params_dict = {"query": xml}

        return self.easy_response(params_dict)

    def test(self):

        mart_query_example = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >
                        
        <Dataset name = "hsapiens_gene_ensembl" interface = "default" >
                <Filter name = "ensembl_gene_id" value = "ENSG00000162367,ENSG00000187048"/>
                <Attribute name = "hgnc_symbol" />
                <Attribute name = "affy_hc_g110" />
                <Attribute name = "ensembl_gene_id" />
                <Attribute name = "entrezgene" />
                <Attribute name = "ensembl_transcript_id" />
        </Dataset>
</Query>"""
        mart_example_output = """ HGNC symbol 	Affy HC G110 	Ensembl Gene ID 	EntrezGene ID 	Ensembl Transcript ID
TAL1 	560_s_at 	ENSG00000162367 	6886 	ENST00000371884
TAL1 	560_s_at 	ENSG00000162367 	6886 	ENST00000294339
TAL1 		ENSG00000162367 	6886 	ENST00000459729
TAL1 		ENSG00000162367 	6886 	ENST00000464796
TAL1 		ENSG00000162367 	6886 	ENST00000481091
TAL1 		ENSG00000162367 	6886 	ENST00000465912
TAL1 	560_s_at 	ENSG00000162367 	6886 	ENST00000371883
CYP4A11 	1391_s_at 	ENSG00000187048 	1579 	ENST00000310638
CYP4A11 	1391_s_at 	ENSG00000187048 	1579 	ENST00000475477
CYP4A11 	1391_s_at 	ENSG00000187048 	1579 	ENST00000462347
"""

        params_dict = {"query": mart_query_example}

        return self.easy_response(params_dict)

    def test_list(self):
        """
        filters: affy_hg_u133a_2: ("202763_at","209310_s_at","207500_at")
        attributes: ["ensembl_gene_id", "ensembl_transcript_id", "affy_hg_u133a_2"]
        dataset: hsapiens_gene_ensembl

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >
			
	<Dataset name = "hsapiens_gene_ensembl" interface = "default" >
		<Filter name = "affy_hg_u133a_2" value = "202763_at,209310_s_at,207500_at"/>
		<Attribute name = "ensembl_gene_id" />
		<Attribute name = "ensembl_transcript_id" />
		<Attribute name = "affy_hg_u133_plus_2" />
	</Dataset>
</Query>

Ensembl Gene ID 	Ensembl Transcript ID 	Affy HG U133-PLUS-2 probeset
ENSG00000196954 	ENST00000525116 	209310_s_at
ENSG00000196954 	ENST00000444739 	209310_s_at
ENSG00000196954 	ENST00000393150 	209310_s_at
ENSG00000196954 	ENST00000529565 	213596_at
ENSG00000196954 	ENST00000529565 	209310_s_at
ENSG00000196954 	ENST00000533730 	209310_s_at
ENSG00000196954 	ENST00000534356 	209310_s_at
ENSG00000196954 	ENST00000355546 	209310_s_at
ENSG00000137757 	ENST00000438448 	207500_at
ENSG00000137757 	ENST00000260315 	207500_at
"""

        attributes=['affy_hg_u133_plus_2', 'hgnc_symbol', 'chromosome_name','start_position','end_position']
        filters={"affy_hg_u133_plus_2": ("202763_at","209310_s_at","207500_at")}
        dataset="hsapiens_gene_ensembl"
        data = self.query(attributes=attributes,filters=filters, dataset=dataset)[2]
        print data

        data2 = [ln.split('\t') for ln in data.strip().split('\n')]
        colnames = data2[0]
        results = [OrderedDict(zip(colnames, ln)) for ln in data2[1:]]

        return results

    def get_BM(self, attributes, filters=None, dataset=None, filename=None, return_raw=False):
        """
        example:
            filters: affy_hg_u133a_2: ("202763_at","209310_s_at","207500_at")
            attributes: ["ensembl_gene_id", "ensembl_transcript_id", "affy_hg_u133a_2"]
            dataset: hsapiens_gene_ensembl
        """

        if dataset is None:
            dataset = self.dataset

        data = self.query(dataset=dataset, attributes=attributes,filters=filters)[2]
        if filename is not None:
            open(filename, 'w').write(data)
        else:
            sys.stdout.write(data)

        if return_raw:
            return data

        # This only works for TSV format with header
        data2 = [ln.split('\t') for ln in data.strip().split('\n')]
        colnames = data2[0]
        results = [OrderedDict(zip(colnames, ln)) for ln in data2[1:]]

        return results

#TODO:
# 1) to write some examples similar with biomaRt in bioconductor.
# 2) clean the parameter list of all functions

#-----------------------------------------------------------------------
# main
#-----------------------------------------------------------------------
if __name__ == '__main__':
    print BioMart().test()
    print BioMart().test_query()
    raw_input("look")
