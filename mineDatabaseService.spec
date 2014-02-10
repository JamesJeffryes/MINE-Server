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
        string Formula - molecular formula of the compound
        float Mass - exact mass of the compound
        string Inchi_key - the Inchi Key of the compound
    */
    typedef structure {
        object_id id;
        string Formula;
        float Mass;
        string Inchi_key;
    } comp_stub;
    
    /* A compound that is a component of a reaction as tuple of stoichiometric coefficient and _id  */
	typedef tuple<int stoic, object_id id> rxn_comp;

    /* A list of all the compounds and reactions in a pathway */
	typedef list<object_id> pathway;
    
    /* An annotated ms peak output by a batch mass adduct query(not yet implemented)

        string name - name of the peak
        int num_forms - number of formula hits
        int num_hits - total number of compound matches
    */
    typedef structure {
        string name;
        int num_forms;
        int num_hits;
    } peak;

    /* The result of a single adduct query on the database

        string adduct - the name of the mass adduct that returned the result
        string formula; - the formula that was matched
        list<object_id> - a list of the isomers of the formula present in the database
    */
    typedef structure {
        string adduct;
        string formula;
        list<object_id> isomers;
    } adduct_result;
    
    /* Data structures for a compound object

		Guaranteed:
		object_id id - A hexdigest of the sha1 hash of the openbabel canonical smile
		string InChI_Key - The first block of the InChI Key of a compound
		string Formula - The chemical formula of the compound
        string Stringcode - The canonical SMILE string generated by openbabel
		float Mass - The exact mass of the neutral form of a compound as calculated by openbabel
		int Charge - The total charge of the compound as calculated by ChemAxon

		Optionally:
		list<string> KEGG_Code - KEGG compound codes
        list<string> BRENDA_Name - Names from the BRENDA repository
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
		list<string> KEGG_Code;
        list<string> BRENDA_Name;
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
		Creates quick_search_results, a list of comp_stubs which match the query string. Searches for matches to KEGG
		Codes, Inchi Keys, Brenda IDs and Names.
	*/
	funcdef quick_search(string db, string query) returns (list<comp_stub> quick_search_results);

	/*
		Creates similarity_search_results, a list of comp_stubs whose Tannimoto coefficient to the search smiles is
		greater that the user set threshold. Uses open babel FP2 fingerprints to match.
	*/
	funcdef similarity_search(string db, string smiles, float min_tc) returns (list<comp_stub> similarity_search_results);
    
    /* Input parameters for the "database_query" function.
	
		string db - the database against which the query will be performed
        string field - the field of the database to match
        string value - the value to match
        bool regex - if true the value will be processed as a regular expression
	*/
	typedef structure { 
		string db;
        string field;
        string value;
        bool regex;
	} database_query_params;

    /*
		Creates database_query_results, a list of object_ids which match the json query string
	*/
	funcdef database_query(database_query_params params) returns (list<comp_stub> database_query_results);

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
    
    /* Input parameters for the "mass_adduct_query" function.
	
		string db - the database in which to search for mass spec matches
		float mz - the experimental mass per charge ratio
        float tolerance - the desired mass precision
        list<adduct> adduct_list - the adducts to consider in the query.
        list<string> models - the models in SEED that will be considered native metabolites
        string charge - the polarity for molecules if not specified by file
        bool ppm - if true, precision is supplied in parts per million. Else, precision is in Daltons
        bool halogens - if false, compounds containing Cl, Br, and F will be excluded from results
	*/
	typedef structure { 
		string db;
		float mz;
		float tolerance;
        list<string> adduct_list;
        list<string> models;
		bool ppm;
		bool charge;
        bool halogens;
	} mass_adduct_query_params;
    
    /*
		Creates output, a list of adduct, formula and isomer combinations that match the supplied parameters
    */
	funcdef adduct_db_search(mass_adduct_query_params params) returns (list<adduct_result> output);

    /* Input parameters for the "pathway_search" function.
	
		string db - the database in which to search for pathways
		object_id start_comp - the compound to begin the search from
        object_id end_comp - the compound that that a pathway will end with if successful
        int len_limit - the max number of intermediate reactions permitted in a path.
        bool all_paths - if true, the script returns all paths less that the limit not just the shortest path
        float np_min - Set a floor on the minimum natural product likeness of any one compound in a pathway
        float gibbs_cap - Set a cap on the gibbs free energy of any one reaction in a pathway
	*/
	typedef structure {
	    string db;
		object_id start_comp;
		object_id end_comp;
        int len_limit;
        bool all_paths;
        float np_min;
        float gibbs_cap;
	} pathway_query_params;
    
    /*
		Creates pathway_query_results, a list of valid pathways (length one unless all_paths is true)
	*/
	funcdef pathway_search(pathway_query_params) returns (list<pathway> pathway_query_results);
};
