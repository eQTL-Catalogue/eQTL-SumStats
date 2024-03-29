import numpy as np
from urllib.parse import unquote
from sumstats.api_v1.common_constants import *
from flask import url_for
from fastapi import Request
from sumstats.api_v1.utils.properties_handler import properties
from sumstats.api_v1.utils import properties_handler as set_p
import sumstats.api_v1.utils.argument_utils as argu
from sumstats.api_v1.utils.interval import *
import sumstats.api_v1.explorer as ex
from collections import OrderedDict
import logging
from sumstats.api_v1.utils import register_logger
from sumstats.api_v1.errors.error_classes import *
import itertools
from urllib.parse import urlsplit, parse_qs, urlencode


logger = logging.getLogger(__name__)
register_logger.register(__name__)


def set_properties():
    set_p.set_properties()


def _get_study_list(studies, start, size, request=None):
    study_list = []
    end = min(start + size, len(studies))
    for study in studies[start:end]:
        #trait = _find_study_info(study)
        #study_list.append(_create_study_info_for_trait([study], trait))
        study_list.append(_create_study_info_for_tissue([study], request=request))
    return study_list

def _get_study_list_no_info(studies, start, size):
    study_list = []
    end = min(start + size, len(studies))
    for study in studies[start:end]:
        study_list.append([{'study_accession': study}])
    return study_list


def _get_tissue_list(tissues, start, size, links=None, request=None):
    tissue_list = []
    end = min(start + size, len(tissues))
    for item in list(OrderedDict(tissues).items())[start:end]:
        tissue, tissue_name = item
        tissue_list.append(_create_info_for_tissue(tissue, tissue_name, links, request=request))
    return tissue_list

def _get_qtl_list(qtls, start, size, links=None):
    qtl_list = []
    end = min(start + size, len(qtls))
    for qtl in qtls[start:end]:
        qtl_list.append({'qtl_group': qtl})
    return qtl_list


def _create_study_info_for_trait(studies, trait=None, request=None):
    study_list = []
    for study in studies:
        study_info = _create_info_for_study(study=study, trait=trait, request=request)
        study_list.append(study_info)
    return study_list


def _create_study_info_for_tissue(studies, tissue=None, request=None):
    study_list = []
    for study in studies:
        study_info = _create_info_for_study(study=study, tissue=tissue, request=request)
        study_list.append(study_info)
    return study_list


def _create_info_for_tissue(tissue, tissue_name=None, links=None, request=None):
    tissue_info = {'tissue': tissue}
    if tissue_name:
        tissue_info['tissue_label'] = tissue_name
    if links is True:
        tissue_info['_links'] = {'self': _create_href(request=request, method_name='get_tissue', path_params={'tissue': tissue})}
        tissue_info['_links']['studies'] = _create_href(request=request, method_name='get_studies_for_tissue', path_params={'tissue': tissue})
        tissue_info['_links']['associations'] = _create_href(request=request, method_name='get_tissue_assocs', path_params={'tissue': tissue})
    return tissue_info


def _create_info_for_study(study, tissue=None, request=None):
    if tissue:
        study_info = {'study_accession': study,
                      '_links': {'self': _create_href(request=request, method_name='get_tissue_study',
                                                      path_params={'tissue': tissue, 'study': study}),
                                 'tissue': _create_href(request=request, method_name='get_tissues', params={'study_accession': study})}}

        study_info['_links'] = _add_gwas_catalog_href(info_array=study_info['_links'], study_accession=study)
        study_info['_links']['associations'] = _create_href(request=request, method_name='get_tissue_study_assocs',
                                                            path_params={'tissue': tissue, 'study': study})
    else:
        study_info = {'study_accession': study,
                      '_links': {'self': _create_href(request=request, method_name='get_tissue_study',
                                                      path_params={'study': study}),
                                 'tissue': _create_href(request=request, method_name='get_tissues', params={'study_accession': study})}}

        study_info['_links'] = _add_gwas_catalog_href(info_array=study_info['_links'], study_accession=study)
        study_info['_links']['associations'] = _create_href(request=request, method_name='get_tissue_study_assocs',
                                                            path_params={'study': study})
    return study_info


def _get_trait_list(traits, start, size, request=None):
    trait_list = []
    end = min(start + size, len(traits))
    for trait in traits[start:end]:
        trait_info = _create_info_for_trait(trait, request)
        trait_list.append(trait_info)
    return trait_list


def _get_gene_list(genes, start, size, request=None):
    gene_list = []
    end = min(start + size, len(genes))
    for gene in genes[start:end]:
        gene_info = _create_info_for_gene(gene, request=request)
        gene_list.append(gene_info)
    return gene_list


def _create_info_for_trait(trait, request):
    trait_info = {'molecular_trait_id': trait,
                  '_links': {'self': _create_href(method_name='get_trait', request=request, path_params={'molecular_trait_id': trait})}}
    #trait_info['_links']['studies'] = _create_href(request=request, method_name='api.get_studies_for_trait', params={'trait': trait})
    trait_info['_links']['associations'] = _create_href(method_name='get_trait_assocs', request=request, path_params={'molecular_trait_id': trait})
    return trait_info

def _create_info_for_gene(gene, request=None):
    gene_info = {'gene': gene,
                  '_links': {'self': _create_href(request=request, method_name='get_gene', path_params={'gene_id': gene})}}
    #gene_info['_links']['studies'] = _create_href(request=request, method_name='api.get_studies_for_gene', params={'gene': gene})
    gene_info['_links']['associations'] = _create_href(request=request, method_name='get_gene_assocs', path_params={'gene_id': gene})
    return gene_info

def _add_ontology_href(info_array, trait):
    info_array['ols'] = {'href': str(properties.ols_terms_ocation + trait)}
    return info_array


def _add_gwas_catalog_href(info_array, study_accession):
    if study_accession.startswith(GWAS_CATALOG_STUDY_PREFIX):
        info_array['gwas_catalog'] = {'href': str(properties.gwas_study_location + study_accession)}
    return info_array


def _get_array_to_display(datasets, variant=None, chromosome=None, links=False, request=None):
    if datasets is None: return {}
    if len(datasets[REFERENCE_DSET]) <= 0: return {}

    #mantissa_dset = datasets.pop(MANTISSA_DSET)
    #exponent_dset = datasets.pop(EXP_DSET)
    #datasets[PVAL_DSET] = _reconstruct_pvalue(mantissa_dset=mantissa_dset, exp_dset=exponent_dset)

    #trait_to_study_cache = {}
    data_dict = {}
    length = len(datasets[PVAL_DSET])

    for index in range(length):
        # elements are numpy types, they need to be python types to be json serializable
        element_info = OrderedDict()
        for dset, dataset in datasets.items():
            element_info = _add_element_depending_on_view(info_array=element_info, dset_name=dset, dataset=dataset, index=index)

        # when we are constructing each element's _links we need variant and/or chromosome information for them. If they
        # where not provided in the query, we can find out what they are for each element (index) here.


        specific_variant = _evaluate_variable(variable=variant, datasets=datasets, dset_name=SNP_DSET, traversal_index=index)
        specific_chromosome = _evaluate_variable(variable=chromosome, datasets=datasets, dset_name=CHR_DSET, traversal_index=index)

        element_info = _add_missing_variables(variable=variant, datasets=datasets, dset_name=SNP_DSET, element_info=element_info)
        element_info = _add_missing_variables(variable=chromosome, datasets=datasets, dset_name=CHR_DSET, element_info=element_info)

        study = datasets[STUDY_DSET][index]

        #trait, trait_to_study_cache = _get_trait_for_study(study, trait_to_study_cache)
        trait = datasets[PHEN_DSET][index]
        gene = datasets[GENE_DSET][index]
        tissue = datasets[TISSUE_DSET][index]

        element_info[PHEN_DSET] = trait
        element_info[GENE_DSET] = gene
        element_info[TISSUE_DSET] = tissue
        element_info[SE_DSET] = element_info[SE_DSET] if SE_DSET in element_info.keys() else None

        if links:
            element_info['_links'] = {'self': _create_href(request=request, method_name='get_chromosome_variants', path_params={'variant_id': specific_variant, 'chromosome': specific_chromosome},
                                                           params={'study_accession': datasets[STUDY_DSET][index]})}
            element_info['_links']['variant'] = _create_href(request=request, method_name='get_chromosome_variants',
                                                             path_params={'variant_id': specific_variant, 'chromosome': specific_chromosome})
            element_info['_links']['study'] = _create_href(request=request, method_name='get_tissue_study',
                                                           path_params={'study': study})
            element_info['_links']['tissue'] = _create_href(request=request, method_name='get_tissue', path_params={'tissue': tissue})

        data_dict[index] = element_info
    return data_dict


def _add_element_depending_on_view(info_array, dset_name, dataset, index):
    if dset_name not in TO_DISPLAY_DEFAULT:
        # if reveal not set we don't want to include the original fields, only the default ones
        return info_array
    else:
        # if reveal not set we don't want to include the original fields, only the default ones
        # but we still want to remove the 'hm_' prefix from the harmonised fields
        dset_name = dset_name.replace(HARMONISATION_PREFIX, '')

    return _add_dset_index(info_array=info_array, dset_name=dset_name, dataset=dataset, index=index)


def _add_dset_index(info_array, dset_name, dataset, index):
    if index >= len(dataset):
        dataset.append(None)
    if dataset[index] == 'nan':
        # string elements that where empty are saved as the string 'nan'
        # and as such need to be converted and displayed as null like the numbers
        dataset[index] = None
    info_array[dset_name] = np.ndarray.item(np.array(dataset[index]))
    return info_array


def _get_trait_for_study(study, trait_to_study_cache):
    if study in trait_to_study_cache:
        return trait_to_study_cache[study], trait_to_study_cache
    else:
        trait = _find_study_info(study)
        trait_to_study_cache[study] = trait
    return trait, trait_to_study_cache


def _find_study_info(study, trait=None):
    if trait is None:
        explorer = ex.Explorer(config_properties=properties)
        trait = explorer.get_trait_of_study(study)
    return trait


def _reconstruct_pvalue(mantissa_dset, exp_dset):
    pval_array = np.empty(len(mantissa_dset), dtype=vlen_dtype)
    for index, mantissa in enumerate(mantissa_dset):
        pval_array[index] = (str(mantissa) + "e" + str(exp_dset[index]))
    return pval_array.tolist()


def _evaluate_variable(variable, datasets, dset_name, traversal_index):
    """
    Used to find (in the datasets) the variable that/if it is missing (if it's not passed as None)
    :param variable: None or the value of the variable
    :param datasets: the dictionary of datasets containing the information
    :param dset_name: the name of the dataset that the variable will retrieved from
    :param traversal_index: the index of the datasets that we are currently traversing and want the value to come from
    :return: either what was passed in as the 'variable' value, or what is in the dataset called dset_name, at
    index traversal_index
    """
    if variable is not None:
        return variable
    return datasets[dset_name][traversal_index]


def _add_missing_variables(variable, datasets, dset_name, element_info):
    if variable is not None:
        dset_type = DSET_TYPES[dset_name]
        if DSET_TYPES[dset_name] == object:
            dset_type = str
        element_info.update({dset_name: dset_type(variable)})
    return element_info


def _create_response(method_name, start, size, index_marker, data_dict, params=None, path_params={}, collection_name=None, request=None):
    if collection_name is None:
        collection_name = 'associations'
    params = params or {}
    return OrderedDict([('_embedded', {collection_name: data_dict}), ('_links', _create_next_links(
        method_name=method_name, start=start, size=size, index_marker=index_marker,
        size_retrieved=len(data_dict),
        params=params, path_params=path_params, request=request
    ))])


def _create_resource_response(data_dict, params):
    if len(data_dict) == 1:
        return data_dict[0]
    elif len(data_dict) == 0:
        raise NotFoundError("Request for resource with parameters " + str(params))


def _create_next_links(method_name, start, size, index_marker, size_retrieved, params={}, path_params={}, request=None):
    prev = max(0, start - size)
    start_new = start + index_marker

    response = OrderedDict([('self', _create_href(method_name=method_name, params=params, path_params=path_params, request=request))])
    params['start'] = 0
    params['size'] = size
    response['first'] = _create_href(method_name=method_name, params=params, path_params=path_params, request=request)
    params['start'] = prev
    # response['prev'] = _create_href(request=request, method_name=method_name, params=params)

    if size_retrieved == size:
        params['start'] = start_new
        response['next'] = _create_href(method_name=method_name, params=params, path_params=path_params, request=request)

    return response


def _create_href(method_name, params={}, path_params={}, request=None):
    params = {k: v for k, v in params.items() if v is not None}
    url = unquote(request.url_for(method_name, **path_params))
    url_w_params = _replace_query_params(url, params)
    return {'href': url_w_params}

def _replace_query_params(url: str, query: dict) -> str:
    _url = urlsplit(url)
    _query = parse_qs(_url.query)
    _query.update(query)
    querystr = urlencode(_query, doseq=True)
    return _url._replace(query=querystr).geturl()


def _get_bp_arguments(args):
    bp_lower = _retrieve_endpoint_arguments(args, "bp_lower")
    bp_upper = _retrieve_endpoint_arguments(args, "bp_upper")
    bp_interval = _get_interval(lower=bp_lower, upper=bp_upper, interval=IntInterval)
    return bp_lower, bp_upper, bp_interval


def _get_basic_arguments(args):
    start, size = _get_start_size(args)
    p_lower = _retrieve_endpoint_arguments(args, "p_lower")
    p_upper = _retrieve_endpoint_arguments(args, "p_upper")
    pval_interval = _get_interval(lower=p_lower, upper=p_upper, interval=FloatInterval)
    quant_method = _retrieve_endpoint_arguments(args, "quant_method", None)
    snp = _retrieve_endpoint_arguments(args, "variant_id", None)
    tissue = _retrieve_endpoint_arguments(args, "tissue", None)
    gene = _retrieve_endpoint_arguments(args, "gene_id", None)
    study = _retrieve_endpoint_arguments(args, "study", None)
    trait = _retrieve_endpoint_arguments(args, "molecular_trait_id", None)
    paginate = argu.str2bool(_retrieve_endpoint_arguments(args, "paginate", True))
    links = argu.str2bool(_retrieve_endpoint_arguments(args, "links", False))
    qtl_group = _retrieve_endpoint_arguments(args, "qtl_group", None)
    links = False if not paginate else links # links must not be made if unpaginated for performance sake.
    
    return start, size, p_lower, p_upper, pval_interval, quant_method, snp, tissue, gene, study, trait, paginate, links, qtl_group


def _get_start_size(args):
    start = int(_retrieve_endpoint_arguments(args, "start", 0))
    size = int(_retrieve_endpoint_arguments(args, "size", 20))
    return start, size


def _retrieve_endpoint_arguments(args, argument_name, value_if_empty=None):
    try:
        argument = args[argument_name]
    except KeyError:
        argument = value_if_empty
    return argument


def _get_interval(lower, upper, interval):
    if (lower is None) and upper is None:
        return None
    interval = interval().set_tuple(lower_limit=lower, upper_limit=upper)
    if lower is not None and upper is not None:
        if interval.floor() > interval.ceil():
            raise ValueError("Lower limit (%s) is bigger than upper limit (%s)." %(lower, upper))
    return interval
