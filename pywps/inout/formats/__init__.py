##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


"""List of know mimetypes"""

# List of known complex data formats
# you can use any other, but thise are widly known and supported by popular
# software packages
# based on Web Processing Service Best Practices Discussion Paper, OGC 12-029
# http://opengeospatial.org/standards/wps

from lxml.builder import ElementMaker
from collections import namedtuple
import mimetypes
from pywps.validator.mode import MODE
from pywps.validator.base import emptyvalidator


_FORMATS = namedtuple('FORMATS', 'GEOJSON, JSON, SHP, GML, GEOTIFF, WCS,'
                                 'WCS100, WCS110, WCS20, WFS, WFS100,'
                                 'WFS110, WFS20, WMS, WMS130, WMS110,'
                                 'WMS100, TEXT, NETCDF, LAZ, LAS')


class Format(object):
    """Input/output format specification

    Predefined Formats are stored in :class:`pywps.inout.formats.FORMATS`

    :param str mime_type: mimetype definition
    :param str schema: xml schema definition
    :param str encoding: base64 or not
    :param function validate: function, which will perform validation. e.g.
    :param number mode: validation mode
    :param str extension: file extension
    """

    def __init__(self, mime_type,
                 schema=None, encoding=None,
                 validate=emptyvalidator, mode=MODE.SIMPLE,
                 extension=None):
        """Constructor
        """

        self._mime_type = None
        self._encoding = None
        self._schema = None
        self._extension = None

        self.mime_type = mime_type
        self.encoding = encoding
        self.schema = schema
        self.validate = validate
        self.extension = extension

    @property
    def mime_type(self):
        """Get format mime type
        :rtype: String
        """

        return self._mime_type

    @mime_type.setter
    def mime_type(self, mime_type):
        """Set format mime type
        """
        try:
            # support Format('GML')
            frmt = getattr(FORMATS, mime_type)
            self._mime_type = frmt.mime_type
        except AttributeError:
            # if we don't have this as a shortcut, assume it's a real mime type
            self._mime_type = mime_type
        except NameError:
            # TODO: on init of FORMATS, FORMATS is not available. Clean up code!
            self._mime_type = mime_type

    @property
    def encoding(self):
        """Get format encoding
        :rtype: String
        """

        if self._encoding:
            return self._encoding
        else:
            return ''

    @encoding.setter
    def encoding(self, encoding):
        """Set format encoding
        """

        self._encoding = encoding

    @property
    def schema(self):
        """Get format schema
        :rtype: String
        """
        if self._schema:
            return self._schema
        else:
            return ''

    @schema.setter
    def schema(self, schema):
        """Set format schema
        """
        self._schema = schema

    @property
    def extension(self):
        """Get format extension
        :rtype: String
        """
        if self._extension:
            return self._extension
        else:
            return ''

    @extension.setter
    def extension(self, extension):
        """Set format extension
        """
        self._extension = extension

    def same_as(self, frmt):
        """Check input frmt, if it seems to be the same as self
        """
        return all([frmt.mime_type == self.mime_type,
                    frmt.encoding == self.encoding,
                    frmt.schema == self.schema])

    def describe_xml(self):
        """Return describe process response element
        """

        elmar = ElementMaker()
        doc = elmar.Format(
            elmar.MimeType(self.mime_type)
        )

        if self.encoding:
            doc.append(elmar.Encoding(self.encoding))

        if self.schema:
            doc.append(elmar.Schema(self.schema))

        return doc

    @property
    def json(self):
        """Get format as json
        :rtype: dict
        """
        return {
            'mime_type': self.mime_type,
            'encoding': self.encoding,
            'schema': self.schema,
            'extension': self.extension
        }

    @json.setter
    def json(self, jsonin):
        """Set format from json
        :param jsonin:
        """

        self.mime_type = jsonin['mime_type']
        self.encoding = jsonin['encoding']
        self.schema = jsonin['schema']
        self.extension = jsonin['extension']


FORMATS = _FORMATS(
    Format('application/vnd.geo+json', extension='.geojson'),
    Format('application/json', extension='.json'),
    Format('application/x-zipped-shp', extension='.zip'),
    Format('application/gml+xml', extension='.gml'),
    Format('image/tiff; subtype=geotiff', extension='.tiff'),
    Format('application/xogc-wcs', extension='.xml'),
    Format('application/x-ogc-wcs; version=1.0.0', extension='.xml'),
    Format('application/x-ogc-wcs; version=1.1.0', extension='.xml'),
    Format('application/x-ogc-wcs; version=2.0', extension='.xml'),
    Format('application/x-ogc-wfs', extension='.xml'),
    Format('application/x-ogc-wfs; version=1.0.0', extension='.xml'),
    Format('application/x-ogc-wfs; version=1.1.0', extension='.xml'),
    Format('application/x-ogc-wfs; version=2.0', extension='.xml'),
    Format('application/x-ogc-wms', extension='.xml'),
    Format('application/x-ogc-wms; version=1.3.0', extension='.xml'),
    Format('application/x-ogc-wms; version=1.1.0', extension='.xml'),
    Format('application/x-ogc-wms; version=1.0.0', extension='.xml'),
    Format('text/plain', extension='.txt'),
    Format('application/x-netcdf', extension='.nc'),
    Format('application/octet-stream', extension='.laz'),
    Format('application/octet-stream', extension='.las'),
)


def _get_mimetypes():
    """Add FORMATS to system wide mimetypes
    """
    mimetypes.init()
    for pywps_format in FORMATS:
        mimetypes.add_type(pywps_format.mime_type, pywps_format.extension, True)


_get_mimetypes()


def get_format(frmt, validator=None):
    """Return Format instance based on given pywps.inout.FORMATS keyword
    """
    # TODO this should be probably removed, it's used only in tests

    outfrmt = None

    if frmt in FORMATS._asdict():
        outfrmt = FORMATS._asdict()[frmt]
        outfrmt.validate = validator
        return outfrmt
    else:
        return Format('None', validate=validator)
