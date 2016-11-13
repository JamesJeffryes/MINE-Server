/*
=head1 mineDatabaseServices

=head2 SYNOPSIS

The MINE database is fundamentally composed of two different types of documents, which are represented by the Compound
and Reaction objects. Users can use text-matching queries to access these records directly or perform two types of more
advanced queries: Mass Adduct queries and pathway queries. Mass Adduct queries return a list of compounds that might
match the m/z of an unknown compound. Pathway queries return either the shortest path or all paths between two compounds
 in the database.
*/

module mineDatabaseServices {
	/* ************************************************************************************************************** */
	/* MINE DATA TYPES */
	/* ************************************************************************************************************** */

    /* indicates true or false values, false = 0, true =1 */
	typedef int bool;

    /*  Unique ID of a compound or reaction derived from a hexdigest of the sha1 hash of a unique feature.
        Starts with C if a compound, X if a cofactor and R if a reaction.
    */
	typedef string object_id;

	/* A summery of a compound object which is returned from compound query

        object_id _id - unique ID of a compound
        string MINE_id - The a unique numerical id of a compound
        list<string> Names - common name for the compound
        string Formula - molecular formula of the compound
    */
    typedef structure {
        object_id id;
        string MINE_id;
        list<string> Names;
        string Formula;
    } comp_stub;
    
    /* A compound that is a component of a reaction as tuple of stoichiometric coefficient and _id  */
	typedef tuple<int stoic, object_id id> rxn_comp;

    /* A list of all the compounds and reactions in a pathway */
	typedef list<object_id> pathway;
    
    /* The result of a single adduct query on the database

        string adduct - the name of the mass adduct that returned the result
        string formula - the formula that was matched
        list<object_id> isomers - a list of the isomers of the formula present in the database
    */
    typedef structure {
        string adduct;
        string formula;
        list<comp_stub> isomers;
    } adduct_result;

    /* An annotated ms peak output by a batch mass adduct query

        string name - name of the peak
        float r_time - retention time
        float mz - mass to charge ratio
        bool charge - polarity of charge
        int num_forms - number of formula hits
        int num_hits - total number of compound matches
        bool native_hit - if true, one of the compounds suggested matches an native compound from the metabolic model
        list<adduct_result> adducts - the adducts that match a given peak
    */
    typedef structure {
        string name;
        int num_forms;
        int num_hits;
        bool native_hit;
        list<adduct_result> adducts;
    } peak;

    /* A putative match for a metabolomics search
        string peak_name
        string adduct
        object_id id
        string formula
        int MINE_id
        string name
        string SMILES
        string Inchikey
        bool native_hit - if true, hit is a member of the specified genomic reconstruction
        int steps_from_source - The number of transformations the hit is from a source database compound
        float logP - predicted partition coefficient
        float minKovatsRI -
        float maxKovatsRI - values of the predicted Kovats Retention Index
        float NP_likeness - the natural product likeness score of the hit
    */
    typedef structure {
        string peak_name;
        string adduct;
        object_id id;
        string formula;
        int MINE_id;
        string name;
        string SMILES;
        string Inchikey;
        bool native_hit;
        float logP;
        float minKovatsRI;
        float maxKovatsRI;
        float NP_likeness;
    } ms_hit;
    
    /* Data structures for a compound object

		Guaranteed:
		object_id id - A hexdigest of the sha1 hash of the openbabel canonical smile
		string InChI_Key - The first block of the InChI Key of a compound
		string Formula - The chemical formula of the compound
        string Stringcode - The canonical SMILE string generated by openbabel
		float Mass - The exact mass of the neutral form of a compound as calculated by openbabel
		int Charge - The total charge of the compound as calculated by ChemAxon

		Optionally:
        list<string> DB_links - links to the same compound in other databases
        list<object_id> Reactant_in - Reactions in which the compound is a reactant
        list<object_id> Product_of - Reactions in which the compound is a product
			
	*/
    typedef structure {
		object_id id;
		string InChI_Key;
		string Formula;
		string Stringcode;
		float Mass;
		int Charge;
        list<string> DB_links;
        list<object_id> Reactant_in;
        list<object_id> Product_of;
    } CompoundObject;

    /* Data structures for a reaction object

		Guaranteed:
		object_id id - A hexdigest of the sha1 hash of the _ids of the reactants and products in sorted order
        list<string> Operators - The operator used to generate a particular reaction
        rxn_comps Reactants - Reactants of the reaction as tuples
        rxn_comps Products - Products of the reaction as tuples

        Optionally:
        float Energy - Delta G of reaction calculated by group contribution theory
        float Error - Estimated error of above energy
			
	*/
    typedef structure {
		object_id id;
		list<string> Operators;
        list<rxn_comp> Reactants;
        list<rxn_comp> Products;
        float Energy;
        float Error;
    } ReactionObject;

    /* Data structures for a operator object

		Guaranteed:
		string Name - Name of the operator
		int Reactions_predicted - The number of database reactions predicted by the operator
		list<object_id> Reaction_ids - A list of the _id hashes for the reaction

        Optionally:
        float Specificity - The fraction of predicted reactions which match known reactions
        float Avg_delta_G - The Average Delta G of all predicted reactions
	*/
    typedef structure {
		string Name;
		int Reactions_predicted;
		list<object_id> Reaction_ids;
    } OperatorObject;


    /* ************************************************************************************************************** */
	/* MINE FUNCTIONS */
	/* ************************************************************************************************************** */

    /*
		Returns a list of metabolic models that match the entered string
	*/
	funcdef model_search(string query) returns (list<string> models);

    /*
		Creates quick_search_results, a list of comp_stubs which match the query string. Searches for matches to KEGG
		Codes, Inchi Keys, Brenda IDs and Names.
	*/
	funcdef quick_search(string db, string query) returns (list<comp_stub> quick_search_results);

	/*
		Creates similarity_search_results, a list of comp_stubs shorter than the limit whose Tannimoto coefficient to
		the comp_structure (as SMILES or molfile) is greater that the user set threshold. Uses open babel FP2 or FP4
		fingerprints to perform the Tannimoto calculation. Also accepts a metabolic model with which to filter acceptable
		source compounds or reaction types.
	*/
	funcdef similarity_search(string db, string comp_structure, float min_tc, string fp_type, int limit, string parent_filter, string reaction_filter)
	returns (list<comp_stub> similarity_search_results);
	/*
		Creates structure_search_result, a list of comp_stubs in the specified database that matches the the supplied
		comp_structure. The input_format may be any format recognised by OpenBabel (i.e. mol, smi, inchi). Also accepts
		a metabolic model with which to filter acceptable source compounds or reaction types.
	*/
	funcdef structure_search(string db, string input_format, string comp_structure, string parent_filter, string reaction_filter)
	returns (list<comp_stub> structure_search_results);

	/*
		Creates substructure_search_results, a list of comp_stubs under the limit who contain the specified substructure
		(as SMILES or molfile) Also accepts a metabolic model with which to filter acceptable source compounds or reaction types.
	*/
	funcdef substructure_search(string db, string substructure, int limit, string parent_filter, string reaction_filter)
	returns (list<comp_stub> substructure_search_results);

    /*
		A general function which uses mongo's find to create database_query_results, a list of object_ids which match
		the specified json query
		Input parameters for the "database_query" function:
		string db - the database against which the query will be performed
		mongo_query query - A valid mongo query as a string
		string parent_filter - require all results originate from compounds in this specified metabolic model
		string reaction_filter - require all results originate from operators which map to reactions in this specified metabolic model
	*/
	funcdef database_query(string db, string mongo_query, string parent_filter, string reaction_filter)
	returns (list<comp_stub> database_query_results);

    /*
        Return a list of object_ids in a specified collection in a specified db
        Input parameters for the "get_ids" function:
        string db - the database from which to retrieve ids
        string collection - the collection from which to retrieve ids
		mongo_query query - A valid mongo query as a string

    */
    funcdef get_ids(string db, string collection, string query) returns (list<object_id> ids);

    /*
        Return a list of CompoundObjects that match supplied object_ids in a specified db
    */
    funcdef get_comps(string db, list<object_id> ids) returns (list<CompoundObject> objects);
    
    /*
        Returns a list of ReactionObjects that match supplied object_ids in a specified db
    */
    funcdef get_rxns(string db, list<object_id> ids) returns (list<ReactionObject> objects);

    /*
        Returns a list of OperatorObjects that match supplied operator_names in a specified db
    */
    funcdef get_ops(string db, list<string> operator_names) returns (list<OperatorObject> objects);

    /*
        Returns a OperatorObject with it's reaction IDs that matches supplied operator_name in a specified db
    */
    funcdef get_operator(string db, string operator_name) returns (OperatorObject operator);

    /*
        Returns a tuple of lists of positive and negative mass adducts names that may be used for querying the databases
    */
    funcdef get_adducts() returns (tuple<list<string>, list<string>> adducts);

	/*
		Parameters for the ms adduct search function:

		Input parameters for the "mass_adduct_query" function:
		string db - the database in which to search for M/S matches
        float tolerance - the desired mass precision
        list<string> adduct_list - the adducts to consider in the query.
        list<string> models - the models in SEED that will be considered native metabolites(can be empty)
        tuple<float,float> logP - a tuple specifying the minimum and maximum values of logP values
        tuple<float,float> kovats - a tuple specifying the minimum and maximum values of Kovats RI
        bool ppm - if true, precision is supplied in parts per million. Else, precision is in Daltons
        bool charge - the polarity for molecules if not specified in file. 1 = +, 0 = -
        bool halogens - if false, compounds containing Cl, Br, and F will be excluded from results
        string parent_filter - require all results originate from compounds in this specified metabolic model
		string reaction_filter - require all results originate from operators which map to reactions in this specified metabolic model
    */

    typedef structure {
		string db;
        float tolerance;
        list<string> adducts;
        list<string> models;
        tuple<float,float> logP;
        tuple<float,float> kovats;
        bool ppm;
        bool charge;
        bool halogen;
    } mzParams;

    /*  New function replacing batch_ms_adduct_search */

	funcdef ms_adduct_search(string text, string text_type, mzParams ms_params) returns (list<ms_hit> ms_adduct_output);

    /*
		Parameters for the ms2 adduct search function:

		Input parameters for the "mass_adduct_query" function:
		string db - the database in which to search for M/S matches
        float tolerance - the desired mass precision
        list<string> adduct_list - the adducts to consider in the query.
        list<string> models - the models in SEED that will be considered native metabolites(can be empty)
        tuple<float,float> logP - a tuple specifying the minimum and maximum values of logP values
        tuple<float,float> kovats - a tuple specifying the minimum and maximum values of Kovats RI
        string scoring_function - The name of the scoring function which will be used to score the spectra
        float energy_level - an integer from 0-2 specifying the fragmentation energy of the predicted spectra
        bool ppm - if true, precision is supplied in parts per million. Else, precision is in Daltons
        bool charge - the polarity for molecules if not specified in file. 1 = +, 0 = -
        bool halogens - if false, compounds containing Cl, Br, and F will be excluded from results
        string parent_filter - require all results originate from compounds in this specified metabolic model
		string reaction_filter - require all results originate from operators which map to reactions in this specified metabolic model
    */

    typedef structure {
		string db;
        float tolerance;
        list<string> adducts;
        list<string> models;
        tuple<float,float> logP;
        tuple<float,float> kovats;
        string scoring_function;
        float energy_level;
        bool ppm;
        bool charge;
        bool halogen;
    } ms2Params;

    /*  performs a ms adduct search but also scores hits using the supplied ms2 data */

	funcdef ms2_search(string text, string text_type, ms2Params ms_params) returns (list<ms_hit> ms_adduct_output);

    /*
		Creates pathway_query_results, a list of valid pathways (length one unless all_paths is true)

		Input parameters for the "pathway_search" function:
		string db - the database in which to search for pathways
		object_id start_comp - the compound to begin the search from
        object_id end_comp - the compound that that a pathway will end with if successful
        int len_limit - the max number of intermediate reactions permitted in a path.
        bool all_paths - if true, the script returns all paths less that the limit not just the shortest path
	*/
	funcdef pathway_search(string db, object_id start_comp, object_id end_comp, int len_limit, bool all_paths)
	returns (list<pathway> pathway_query_results);
};
