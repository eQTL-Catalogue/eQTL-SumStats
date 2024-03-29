import simplejson
import json
import logging
from flask import request
from collections import OrderedDict
import sumstats.api_v1.explorer as ex
import sumstats.api_v1.controller as search
from sumstats.api_v1.utils.properties_handler import properties
from sumstats.dependencies.error_classes import *
from sumstats.api_v1.errors.error_classes import *
import sumstats.api_v1.server.api_utils as apiu
import sumstats.api_v1.utils.sqlite_client as sq


def root(request):
    response = {
        '_links': OrderedDict([
            ('associations', apiu._create_href(method_name='get_assocs', request=request)),
            ('molecular_phenotypes', apiu._create_href(method_name='get_traits', request=request)),
            ('studies', apiu._create_href(method_name='get_studies', request=request)),
            ('tissues', apiu._create_href(method_name='get_tissues', request=request)),
            ('qtl_groups', apiu._create_href(method_name='get_qtl_groups', request=request)),
            ('genes', apiu._create_href(method_name='get_genes', request=request)),
            ('chromosomes', apiu._create_href(method_name='get_chromosomes', request=request))
        ])
    }
    return response


def associations(request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method, snp, tissue, gene, study, trait, paginate, links, qtl_group = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/associations. " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)
    datasets, index_marker, paginate = searcher.search(start=start, size=size, pval_interval=pval_interval, quant_method=quant_method, 
            tissue=tissue, gene=gene, study=study, trait=trait, paginate=paginate, qtl_group=qtl_group, snp=snp)

    data_dict = apiu._get_array_to_display(request=request, datasets=datasets, links=links)
    params = dict(p_lower=p_lower, p_upper=p_upper, quant_method=quant_method, tissue=tissue, gene_id=gene, study=study, molecular_trait_id=trait, qtl_group=qtl_group, variant_id=snp, links=links)
    response = apiu._create_response(method_name='get_assocs', start=start, size=size, index_marker=index_marker,
                                     data_dict=data_dict, params=params, request=request)

    return response


def traits(request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    #need to add in study to url if present
    try:
        start, size = apiu._get_start_size(args)
        study = apiu._retrieve_endpoint_arguments(args, "study")
    except ValueError as error:
        logging.error("/molecular_phenotypes. " + (str(error)))
        raise BadUserRequest(str(error))
    explorer = ex.Explorer(apiu.properties)
    if study:
        traits = explorer.get_trait_of_study(study_to_find=study)
        trait_list = apiu._get_trait_list(traits=traits, request=request)

        response = apiu._create_response(collection_name='molecular_trait_id', method_name='get_traits', params={'study': study},
                                         start=start, size=size, index_marker=size, data_dict=trait_list, request=request)
    else:
        traits = explorer.get_list_of_traits()
        trait_list = apiu._get_trait_list(traits=traits, start=start, size=size, request=request)

        response = apiu._create_response(collection_name='molecular_trait_id', method_name='get_traits',
                                         start=start, size=size, index_marker=size, data_dict=trait_list, request=request)
    return response


def trait(trait, request_args=None, request=None):
    try:
        explorer = ex.Explorer(config_properties=properties)
        if explorer.has_trait(trait):
            response = apiu._create_info_for_trait(trait, request)
            return response
    except NotFoundError as error:
        logging.error("/molecular_phenotypes/" + trait + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def trait_associations(trait, request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method, snp, tissue, gene, study, _ , paginate, links, qtl_group = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/molecular_phenotypes/" + trait + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker, paginate = searcher.search(trait=trait, start=start, size=size, pval_interval=pval_interval, quant_method=quant_method, 
                tissue=tissue, gene=gene, study=study, snp=snp, paginate=paginate, qtl_group=qtl_group)

        data_dict = apiu._get_array_to_display(request=request, datasets=datasets, links=links)
        path_params = {'molecular_trait_id': trait}
        params = dict(p_lower=p_lower, p_upper=p_upper, quant_method=quant_method, tissue=tissue, gene_id=gene, study=study, variant_id=snp, qtl_group=qtl_group, links=links)
        response = apiu._create_response(method_name='get_trait_assocs', start=start, size=size,
                                         index_marker=index_marker,
                                         data_dict=data_dict, params=params, request=request, path_params=path_params)

        return response

    except NotFoundError as error:
        logging.error("/molecular_phenotypes/" + trait + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def studies(request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        logging.error("/studies. " + (str(error)))
        raise BadUserRequest(str(error))

    explorer = ex.Explorer(apiu.properties)
    studies = explorer.get_list_of_studies()
    study_list = apiu._get_study_list(studies=studies, start=start, size=size, request=request)

    response = apiu._create_response(collection_name='studies', method_name='get_studies',
                                     start=start, size=size, index_marker=size, 
                                     request=request, data_dict=study_list)

    return response


def study_list():
    args = request.args.to_dict()
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        logging.error("/study_list. " + (str(error)))
        raise BadUserRequest(str(error))

    explorer = ex.Explorer(apiu.properties)
    studies = explorer.get_list_of_studies()

    # default size is max unless specified:
    if 'size' not in args:
        size = len(studies)

    study_list = apiu._get_study_list_no_info(studies=studies, start=start, size=size)

    response = apiu._create_response(collection_name='studies', method_name='api.get_studies',
                                     start=start, size=size, index_marker=size, data_dict=study_list)

    return simplejson.dumps(response)


def studies_for_tissue(tissue, request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        logging.error("/tissues/" + tissue + "/studies. " + (str(error)))
        raise BadUserRequest(str(error))

    try:
        explorer = ex.Explorer(apiu.properties)
        studies = explorer.get_studies_of_tissue(tissue)
        study_list = apiu._create_study_info_for_tissue(studies, tissue, request=request)
        end = min(start + size, len(study_list))
        response = apiu._create_response(collection_name='studies', method_name='get_studies_for_tissue', request=request,
                                         start=start, size=size, index_marker=size, data_dict=study_list, path_params=dict(tissue=tissue))

        return response
    except NotFoundError as error:
        logging.error("/tissues/" + tissue + "/studies. " + (str(error)))
        raise RequestedNotFound(str(error))


def tissue_associations(tissue, request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method, snp, _, gene, study, trait, paginate, links, qtl_group = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/tissues/" + tissue + ". " + (str(error)))
        raise BadUserRequest(str(error))

    try:
        #trait = apiu._find_study_info(study=study, trait=trait)
        searcher = search.Search(apiu.properties)

        datasets, index_marker, paginate = searcher.search(tissue=tissue, start=start, size=size, pval_interval=pval_interval, quant_method=quant_method, 
                gene=gene, study=study, trait=trait, snp=snp, paginate=paginate, qtl_group=qtl_group)

        data_dict = apiu._get_array_to_display(request=request, datasets=datasets, links=links)
        #params = dict(trait=trait, study=study, p_lower=p_lower, p_upper=p_upper)
        path_params = {'tissue': tissue}
        params = dict(p_lower=p_lower, p_upper=p_upper, quant_method=quant_method, gene_id=gene, study=study, molecular_trait_id=trait, variant_id=snp, qtl_group=qtl_group, links=links)
        response = apiu._create_response(method_name='get_tissue_assocs', start=start, size=size,
                                         index_marker=index_marker, request=request,
                                         data_dict=data_dict, params=params, path_params=path_params)

        return response

    except (NotFoundError, SubgroupError) as error:
        logging.error("/tissues/" + tissue + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def tissue_study(study, tissue=None, request=None):
    try:
        explorer = ex.Explorer(apiu.properties)
        if explorer.check_study(study):
            response = apiu._create_info_for_study(study=study, tissue=tissue, request=request)
            return response
        else:
            raise RequestedNotFound("Study: {}.".format(study))
    except (NotFoundError, SubgroupError) as error:
        logging.error("/studies/" + study + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def tissue_study_associations(study, tissue=None, request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method, snp, _, gene, _, trait, paginate, links, qtl_group = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/studies/" + study + ". " + (str(error)))
        raise BadUserRequest(str(error))

    try:
        #trait = apiu._find_study_info(study=study, trait=trait)
        searcher = search.Search(apiu.properties)

        #datasets, index_marker = searcher.search_study(trait=trait, study=study,
        #                                               start=start, size=size, pval_interval=pval_interval)

        if tissue:
            datasets, index_marker, paginate = searcher.search(tissue=tissue, study=study, trait=trait, gene=gene, snp=snp,
                                                     start=start, size=size, pval_interval=pval_interval,
                                                     quant_method=quant_method, paginate=paginate, qtl_group=qtl_group)

            data_dict = apiu._get_array_to_display(request=request, datasets=datasets, links=links)

            path_params = dict(tissue=tissue, study=study)
            params = dict(molecular_trait_id=trait,  variant_id=snp, p_lower=p_lower, p_upper=p_upper, gene_id=gene, quant_method=quant_method, qtl_group=qtl_group, links=links)
        else:
            datasets, index_marker, paginate = searcher.search(study=study, gene=gene, snp=snp, trait=trait, start=start, size=size, 
                    pval_interval=pval_interval, quant_method=quant_method, paginate=paginate, qtl_group=qtl_group)

            data_dict = apiu._get_array_to_display(request=request, datasets=datasets, links=links)

            path_params = dict(study=study)
            params = dict(study=study, p_lower=p_lower, p_upper=p_upper,  variant_id=snp, gene_id=gene, molecular_trait_id=trait, quant_method=quant_method, qtl_group=qtl_group, links=links)


        response = apiu._create_response(method_name='get_tissue_study_assocs', start=start, size=size,
                                         index_marker=index_marker, request=request,
                                         data_dict=data_dict, path_params=path_params, params=params)

        return response

    except (NotFoundError, SubgroupError) as error:
        logging.error("/studies/" + study + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def chromosomes(request=None):
    chromosomes = []
    #for chromosome in range(1, (properties.available_chromosomes + 1)):
    try:
        explorer = ex.Explorer(apiu.properties)
        chrom_list = explorer.get_list_of_chroms()
        for chromosome in chrom_list:
            # adding plus one to include the available_chromosomes number
            chromosome_info = _create_chromosome_info(chromosome, request=request)
            chromosomes.append(chromosome_info)
    except NotFoundError:
        logging.debug("Chromosome %s does not have data...", str(chromosomes))

    response = OrderedDict({'_embedded': {'chromosomes': chromosomes}})
    return response


def chromosome(chromosome, request=None):
    try:
        response = _create_chromosome_info(chromosome, request=request)
        return response
    except NotFoundError as error:
        logging.error("/chromosomes/" + chromosome + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def chromosome_associations(chromosome, request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method, snp, tissue, gene, study, trait, paginate, links, qtl_group = apiu._get_basic_arguments(args)
        bp_lower, bp_upper, bp_interval = apiu._get_bp_arguments(args)
    except ValueError as error:
        logging.error("/chromosomes/" + chromosome + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker, paginate = searcher.search(chromosome=chromosome,
                                                            start=start, size=size, study=study, snp=snp,
                                                            pval_interval=pval_interval, bp_interval=bp_interval, 
                                                            quant_method=quant_method, tissue=tissue, gene=gene, 
                                                            trait=trait, paginate=paginate, qtl_group=qtl_group)
        data_dict = apiu._get_array_to_display(request=request, datasets=datasets, chromosome=chromosome, links=links)
        return _create_chromosome_response(search_info=dict(chromosome=chromosome, data_dict=data_dict, start=start, size=size,
                                                index_marker=index_marker, bp_lower=bp_lower, bp_upper=bp_upper, variant_id=snp,
                                                p_lower=p_lower, p_upper=p_upper, study=study, quant_method=quant_method, 
                                                tissue=tissue, gene=gene, trait=trait, qtl_group=qtl_group, links=links), request=request)

    except NotFoundError as error:
        logging.error("/chromosomes/" + chromosome + ". " + (str(error)))
        raise RequestedNotFound(str(error))
    except SubgroupError:
        # we have not found bp in chromosome, return empty collection
        data_dict = {}
        index_marker = 0
        return _create_chromosome_response(search_info=dict(chromosome=chromosome, data_dict=data_dict, start=start, size=size,
                                                index_marker=index_marker, bp_lower=bp_lower, bp_upper=bp_upper, variant_id=snp,
                                                p_lower=p_lower, p_upper=p_upper, study=study, quant_method=quant_method, 
                                                tissue=tissue, gene=gene, trait=trait, qtl_group=qtl_group, links=links), request=request)


def variants(variant, request_args=None, request=None, chromosome=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method, _, tissue, gene, study, trait, paginate, links, qtl_group  = apiu._get_basic_arguments(args)
        #if study is not None:
        #    return variant_resource(variant=variant, chromosome=chromosome)
    except ValueError as error:
        logging.debug("/chromosomes/" + chromosome + "/associations/" + variant + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker, paginate = searcher.search(snp=variant, chromosome=chromosome, start=start, size=size,
                                                     pval_interval=pval_interval, study=study, quant_method=quant_method, 
                                                     tissue=tissue, gene=gene, trait=trait, paginate=paginate, qtl_group=qtl_group)

        data_dict = apiu._get_array_to_display(request=request, datasets=datasets, variant=variant, links=links)
        path_params = {'variant_id': variant}
        params = {'p_lower': p_lower, 'p_upper': p_upper, 'study': study, 'quant_method': quant_method, 'tissue': tissue, 'gene_id': gene, 'molecular_trait_id': trait, 'qtl_group': qtl_group, 'links': links}
        if chromosome is None:
            method_name = 'get_variant'
        else:
            path_params['chromosome'] = chromosome
            method_name = 'get_chromosome_variants'

        response = apiu._create_response(method_name=method_name, start=start, size=size,
                                         index_marker=index_marker,
                                         data_dict=data_dict, params=params, path_params=path_params, request=request)

        return response
    except (NotFoundError, SubgroupError) as error:
        logging.debug(str(error))
        raise RequestedNotFound(str(error))


def variant_resource(variant, chromosome=None):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method, _, tissue, gene, study, trait, paginate, links, qtl_group = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.debug("/chromosomes/" + chromosome + "/associations/" + variant + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker, paginate = searcher.search(snp=variant, chromosome=chromosome, start=start, size=size,
                                                     pval_interval=pval_interval, study=study, quant_method=quant_method, 
                                                     tissue=tissue, gene=gene, trait=trait, paginate=paginate, qtl_group=qtl_group)
        data_dict = apiu._get_array_to_display(request=request, datasets=datasets, variant=variant, links=links)
        params = {'variant_id': variant, 'study': study, 'quant_method': quant_method, 'tissue': tissue, 'gene_id': gene, 'molecular_trait_id': trait, 'qtl_group': qtl_group, 'links': links}

        if chromosome is not None:
            params['chromosome'] = chromosome
        response = apiu._create_resource_response(data_dict=data_dict, params=params)
        print(response)
        return simplejson.dumps(response, ignore_nan=True)
    except (NotFoundError, SubgroupError) as error:
        logging.debug(str(error))
        raise RequestedNotFound(str(error))


def tissues(request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method, snp, _, gene, study, trait, paginate, links, qtl_group = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/tissues. " + (str(error)))
        raise BadUserRequest(str(error))

    explorer = ex.Explorer(apiu.properties)
    tissue_dict = explorer.get_tissue_ont_dict()
    tissue_list = apiu._get_tissue_list(tissues=tissue_dict, start=start, size=size, links=links, request=request)
    response = apiu._create_response(collection_name='tissues', method_name='get_tissues', request=request,
                                     start=start, size=size, index_marker=size, data_dict=tissue_list)

    return response


def tissue(tissue, request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        explorer = ex.Explorer(config_properties=properties)
        if explorer.get_studies_of_tissue(tissue):
            response = apiu._create_info_for_tissue(tissue)
            return response
        else:
            raise RequestedNotFound("Tissue: {} not found".format(tissue))
    except NotFoundError as error:
        logging.error("/tissue/" + tissue + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def qtl_groups(request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method, snp, _, gene, study, trait, paginate, links, qtl_group = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/qtl_groups. " + (str(error)))
        raise BadUserRequest(str(error))

    explorer = ex.Explorer(apiu.properties)
    qtls = explorer.get_qtl_list()
    qtl_list = apiu._get_qtl_list(qtls=qtls, start=start, size=size, links=links)
    response = apiu._create_response(collection_name='qtl_groups', method_name='get_qtl_groups', request=request,
                                     start=start, size=size, index_marker=size, data_dict=qtl_list)

    return response


def qtl_group(qtl_group):
    try:
        explorer = ex.Explorer(config_properties=properties)
        if explorer.get_studies_of_tissue(tissue):
            response = apiu._create_info_for_tissue(tissue)
            return simplejson.dumps(response, ignore_nan=True)
        else:
            raise RequestedNotFound("Tissue: {} not found".format(tissue))
    except NotFoundError as error:
        logging.error("/tissue/" + tissue + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def genes(request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        logging.error("/genes. " + (str(error)))
        raise BadUserRequest(str(error))
    explorer = ex.Explorer(apiu.properties)
    genes = explorer.get_list_of_genes()
    gene_list = apiu._get_gene_list(genes=genes, start=start, size=size, request=request)

    response = apiu._create_response(collection_name='gene', method_name='get_genes', request=request,
                                     start=start, size=size, index_marker=size, data_dict=gene_list)
    return response


def gene(gene, request=None):
    try:
        explorer = ex.Explorer(config_properties=properties)
        if explorer.has_gene(gene):
            response = apiu._create_info_for_gene(gene, request=request)
            return response
    except NotFoundError as error:
        logging.error("/genes/" + gene + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def gene_associations(gene, request_args=None, request=None):
    args = request_args.dict() if request_args is not None else {}
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method, snp, tissue, _, study, trait, paginate, links, qtl_group = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/traits/" + trait + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker, paginate = searcher.search(gene=gene, start=start, size=size, pval_interval=pval_interval, snp=snp,
                quant_method=quant_method, tissue=tissue, study=study, trait=trait, paginate=paginate, qtl_group=qtl_group)

        data_dict = apiu._get_array_to_display(request=request, datasets=datasets, links=links)
        path_params = dict(gene_id=gene)
        params = dict(p_lower=p_lower, p_upper=p_upper, quant_method=quant_method, tissue=tissue, variant_id=snp, study=study, molecular_trait_id=trait, qtl_group=qtl_group, links=links)
        response = apiu._create_response(method_name='get_gene_assocs', start=start, size=size,
                                         index_marker=index_marker, request=request, path_params=path_params,
                                         data_dict=data_dict, params=params)
        return response
    except NotFoundError as error:
        logging.error("/genes/" + gene + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def _create_chromosome_info(chromosome, request=None):
    chromosome_info = {'chromosome': chromosome,
                           '_links': {'self': apiu._create_href(method_name='get_chromosome',
                                                                path_params={'chromosome': chromosome},
                                                                request=request),
                                      'associations': apiu._create_href(method_name='get_chromosome_assocs',
                                                                        path_params={'chromosome': chromosome},
                                                                        request=request)}}
    return chromosome_info


def _create_chromosome_response(search_info, request=None):
    params = dict(p_lower=search_info['p_lower'], p_upper=search_info['p_upper'],
                  bp_lower=search_info['bp_lower'], bp_upper=search_info['bp_upper'],
                  study=search_info['study'], links=search_info['links'])
    path_params = dict(chromosome=search_info['chromosome'])
    response = apiu._create_response(method_name='get_chromosome_assocs', start=search_info['start'], size=search_info['size'],
                                     index_marker=search_info['index_marker'], request=request,
                                     data_dict=search_info['data_dict'], path_params=path_params, params=params)

    return response