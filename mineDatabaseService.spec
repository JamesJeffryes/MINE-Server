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
		fingerprints to perform the Tannimoto calculation.
	*/
	funcdef similarity_search(string db, string comp_structure, float min_tc, string fp_type, int limit)
	returns (list<comp_stub> similarity_search_results);
	/*
		Creates structure_search_result, a list of comp_stubs in the specified database that matches the the supplied
		comp_structure. The input_format may be any format recognised by OpenBabel (i.e. mol, smi, inchi)
	*/
	funcdef structure_search(string db, string input_format, string comp_structure)
	returns (list<comp_stub> structure_search_results);

	/*
		Creates substructure_search_results, a list of comp_stubs under the limit who contain the specified substructure
		(as SMILES or molfile)
	*/
	funcdef substructure_search(string db, string substructure, int limit)
	returns (list<comp_stub> substructure_search_results);

    /*
		A general function which uses mongo's find to create database_query_results, a list of object_ids which match
		the specified json query
		Input parameters for the "database_query" function:
		string db - the database against which the query will be performed
		mongo_query query - A valid mongo query as a string
	*/
	funcdef database_query(string db, string mongo_query) returns (list<comp_stub> database_query_results);

    /*
        Return a list of CompoundObjects that match supplied object_ids in a specified db
    */
    funcdef get_comps(string db, list<object_id> ids) returns (list<CompoundObject> objects);
    
    /*
        Returns a list of ReactionObjects that match supplied object_ids in a specified db
    */
    funcdef get_rxns(string db, list<object_id> ids) returns (list<ReactionObject> objects);

    /*
        Returns a list of SEED models available to be set as native metabolites as tuples of SEED id and name
    */
    funcdef get_models() returns (list<tuple<string id, string name>> models);

    /*
        Returns a tuple of lists of positive and negative mass adducts names that may be used for querying the databases
    */
    funcdef get_adducts() returns (tuple<list<string>, list<string>> adducts);

	/*
		DEPRECATED - Use mz_search

		Creates output, a list of adduct, formula and isomer combinations that match the supplied parameters

		Input parameters for the "mass_adduct_query" function:
		string db - the database in which to search for M/S matches
		string text - the user supplied text
		string text_type - if an uploaded file, the file extension. if list of m/z values, "form"
        float tolerance - the desired mass precision
        list<adduct> adduct_list - the adducts to consider in the query.
        list<string> models - the models in SEED that will be considered native metabolites(can be empty)
        bool ppm - if true, precision is supplied in parts per million. Else, precision is in Daltons
        bool charge - the polarity for molecules if not specified in file. 1 = +, 0 = -
        bool halogens - if false, compounds containing Cl, Br, and F will be excluded from results
    */
	funcdef batch_ms_adduct_search(string db, string text, string text_type, float tolerance, list<string> adduct_list,
	                    list<string> models, bool ppm, bool charge, bool halogens) returns (list<peak> batch_output);

	/*
		Parameters for the mz search function:

		Input parameters for the "mass_adduct_query" function:
		string db - the database in which to search for M/S matches
        float tolerance - the desired mass precision
        list<adduct> adduct_list - the adducts to consider in the query.
        list<string> models - the models in SEED that will be considered native metabolites(can be empty)
        tuple<float,float> logP - a tuple specifying the minimum and maximum values of logP values
        tuple<float,float> kovats - a tuple specifying the minimum and maximum values of Kovats RI
        bool ppm - if true, precision is supplied in parts per million. Else, precision is in Daltons
        bool charge - the polarity for molecules if not specified in file. 1 = +, 0 = -
        bool halogens - if false, compounds containing Cl, Br, and F will be excluded from results
    */

    typedef structure {
		string db;
        float tolerance;
        list<adduct> adducts;
        list<string> models;
        tuple<float,float> logP;
        tuple<float,float> kovats;
        bool ppm;
        bool charge;
        bool halogen;
    } mzParams;

    /*  New function replacing batch_ms_adduct_search */

	funcdef mz_search(string text, string text_type, mzParams mz_params) returns (list<peak> batch_output);

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
