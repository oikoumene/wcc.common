from logging import getLogger
logger = getLogger('wcc.policy.patches')

def _patch_canonicals_cleanup():
    from plone.multilingual.storage import CanonicalStorage
    from plone.app.uuid.utils import uuidToObject   

    if getattr(CanonicalStorage, '__wcc_canonical_cleanup_patch', False):
        return
    logger.info('Patching with canonical cleanup patch')

    _orig_get_canonicals = CanonicalStorage.get_canonicals
    def get_canonicals(self):
        canonicals = _orig_get_canonicals(self)
        for c in canonicals:
            obj = uuidToObject(c)
            if obj is None:
                self.remove_canonical(c)
        return _orig_get_canonicals(self)
    CanonicalStorage.get_canonicals = get_canonicals
    CanonicalStorage.__wcc_canonical_cleanup_patch = True

_patch_canonicals_cleanup()

def _patch_dont_compress_types():
    from ZPublisher.HTTPResponse import HTTPResponse
    NO_COMPRESSION_TYPES=['application/x-shockwave-flash']

    if getattr(HTTPResponse, '__inigo_dont_compress_types_patch', False):
        return 
    logger.info('Patching with exclude mimetype for compression patch')

    _orig_enableHTTPCompression = HTTPResponse.enableHTTPCompression
    def enableHTTPCompression(self, *args, **kwargs):
        if self.headers.get('content-type', '') in NO_COMPRESSION_TYPES:
            return 0
        return _orig_enableHTTPCompression(self, *args, **kwargs)

    HTTPResponse.enableHTTPCompression = enableHTTPCompression
    HTTPResponse.__inigo_dont_compress_types_patch = True

_patch_dont_compress_types()


def _patch_catalogcontentlisting_titleid():
    from plone.app.contentlisting.catalog import CatalogContentListingObject

    if getattr(CatalogContentListingObject,'pretty_title_or_id',False):
        return

    def pretty_title_or_id(self):
        return self._brain.pretty_title_or_id

    CatalogContentListingObject.pretty_title_or_id = pretty_title_or_id

_patch_catalogcontentlisting_titleid()



def _patch_collectiveinterface_reindex():
    from collective.interfaces.browser import InterfacesView

    if getattr(InterfacesView, '__inigo_collectiveinterfaces_reindex_patched',
            False):
        retrurn 

    _orig_call = InterfacesView.__call__
    def __call__(self):
        _orig_call(self)
        self.context.reindexObject(['object_provides'])

    InterfacesView.__call__ = __call__
    InterfacesView.__inigo_collectiveinterfaces_reindex_patched = True

_patch_collectiveinterface_reindex()


def _patch_collectivecontentleadimageblob_languageindependent():
    try:
        from collective.contentleadimage.extender import HAS_BLOB
        from collective.contentleadimage.extender import LeadImageBlobExtender
    except:
        return

    for f in LeadImageBlobExtender.fields:
        if f.__name__ == 'leadImage':
            f.languageIndependent = True

_patch_collectivecontentleadimageblob_languageindependent()


def _patch_multilingual_catalog_singlelang():
    from plone.app.multilingual import catalog

    if getattr(catalog, '__inigo_patched_singlelang', False):
        return

    _orig_language_filter = catalog.language_filter
    def language_filter(query):
        old_path = query.get('path', None)
        if isinstance(old_path, dict) and 'query' in old_path:
            if not old_path['query']:
                query['Language'] = 'all'
        return _orig_language_filter(query)

    catalog.language_filter = language_filter
    catalog.__inigo_patched_singlelang = True

_patch_multilingual_catalog_singlelang()
