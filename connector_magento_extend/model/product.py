# -*- coding: utf-8 -*-
#
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import base64
import logging
import urllib2
import xmlrpclib

from openerp.addons.connector.exception import IDMissingInBackend
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper
                                                  )
from openerp.addons.connector.unit.synchronizer import (Importer,
                                                        )

from openerp import models, fields, api
from ..backend import magentoextend
from ..connector import get_environment
from ..unit.backend_adapter import (GenericAdapter)
from ..unit.import_synchronizer import (DelayedBatchImporter, magentoextendImporter)
from ..unit.mapper import normalize_datetime

_logger = logging.getLogger(__name__)


class magentoextendProductProduct(models.Model):
    _name = 'magentoextend.product.product'
    _inherit = 'magentoextend.binding'
    _inherits = {'product.product': 'openerp_id'}
    _description = 'magentoextend product product'

    _rec_name = 'name'

    @api.model
    def product_type_get(self):
        return [
            ('simple', 'Simple Product'),
            ('configurable', 'Configurable Product'),
            # XXX activate when supported
            # ('grouped', 'Grouped Product'),
            # ('virtual', 'Virtual Product'),
            # ('bundle', 'Bundle Product'),
            # ('downloadable', 'Downloadable Product'),
        ]

    openerp_id = fields.Many2one(comodel_name='product.product',
                                 string='product',
                                 required=True,
                                 ondelete='cascade')

    backend_id = fields.Many2one(
        comodel_name='magentoextend.backend',
        string='magentoextend Backend',
        store=True,
        readonly=False,
    )

    backend_home_id = fields.Many2one(
        related='backend_id.connector_id.home_id',
        comodel_name='backend.home',
        string='Backend Home',
        store=True,
        required=False,
        ondelete='restrict',
    )

    product_type = fields.Selection(selection='product_type_get',
                                    string='Magento Product Type',
                                    default='simple',
                                    required=True)

    slug = fields.Char('Slung Name')
    credated_at = fields.Date('created_at')
    weight = fields.Float('weight')
    updated_at = fields.Datetime(string='Updated At (on Magento)',
                                 readonly=True)


@magentoextend
class ProductProductAdapter(GenericAdapter):
    _model_name = 'magentoextend.product.product'
    _magentoextend_model = 'catalog_product'

    def _call(self, method, arguments):
        try:
            return super(ProductProductAdapter, self)._call(method, arguments)
        except xmlrpclib.Fault as err:
            # this is the error in the magentoextendCommerce API
            # when the customer does not exist
            if err.faultCode == 102:
                raise IDMissingInBackend
            else:
                raise

    def search(self, filters=None, from_date=None, to_date=None):
        """ Search records according to some criteria and return a
        list of ids

        :rtype: list
        """
        if filters is None:
            filters = {}
        magentoextend_DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'
        dt_fmt = magentoextend_DATETIME_FORMAT
        if from_date is not None:
            # updated_at include the created records
            filters.setdefault('updated_at', {})
            filters['updated_at']['from'] = from_date.strftime(dt_fmt)
        if to_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['to'] = to_date.strftime(dt_fmt)

        return [int(row['product_id']) for row
                in self._call('%s.list' % self._magentoextend_model,
                              [filters] if filters else [{}])]

    def get_images(self, id, storeview_id=None):
        return self._call('catalog_product_attribute_media.list', [int(id)])

    def read_image(self, id, image_name, storeview_id=None):
        return self._call('catalog_product_attribute_media.info',
                          [int(id), image_name])


@magentoextend
class ProductBatchImporter(DelayedBatchImporter):
    """ Import the magentoextendCommerce Partners.

    For every partner in the list, a delayed job is created.
    """
    _model_name = ['magentoextend.product.product']

    def _import_record(self, magentoextend_id, priority=None):
        """ Delay a job for the import """
        super(ProductBatchImporter, self)._import_record(
            magentoextend_id, priority=priority)

    def run(self, filters=None):
        """ Run the synchronization """
        #
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)
        record_ids = self.backend_adapter.search(
            filters,
            from_date=from_date,
            to_date=to_date,
        )
        _logger.info('search for magentoextend Products %s returned %s',
                     filters, record_ids)
        if record_ids:
            self._import_record(record_ids, 30)


ProductBatchImporter = ProductBatchImporter


@magentoextend
class ProductProductImporter(magentoextendImporter):
    _model_name = ['magentoextend.product.product']

    def _import_dependencies(self):
        """ Import the dependencies for the record"""

    def _create(self, data):
        openerp_binding = super(ProductProductImporter, self)._create(data)
        return openerp_binding

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        image_importer = self.unit_for(ProductImageImporter)
        image_importer.run(self.magentoextend_id, binding.id)
        return


ProductProductImport = ProductProductImporter


@magentoextend
class ProductImageImporter(Importer):
    """ Import images for a record.

    Usually called from importers, in ``_after_import``.
    For instance from the products importer.
    """
    _model_name = ['magentoextend.product.product',
                   ]

    def _get_images(self, storeview_id=None):
        return self.backend_adapter.get_images(self.magentoextend_id)

    def _sort_images(self, images):
        """ Returns a list of images sorted by their priority.
        An image with the 'image' type is the the primary one.
        The other images are sorted by their position.

        The returned list is reversed, the items at the end
        of the list have the higher priority.
        """
        if not images:
            return {}

        # place the images where the type is 'image' first then
        # sort them by the reverse priority (last item of the list has
        # the the higher priority)

        def priority(image):
            primary = 'image' in image['types']
            try:
                position = int(image['position'])
            except ValueError:
                position = sys.maxint
            return (primary, -position)

        return sorted(images, key=priority)

    def _get_binary_image(self, image_data):
        url = image_data['url'].encode('utf8')
        try:
            param = self.env[self.backend_record.connector_id.line_id.type_id.model_name].search(
                [('line_id', '=', self.backend_record.connector_id.line_id.id)])
            request = urllib2.Request(url)
            if param.use_http:
                base64string = base64.encodestring(
                    '%s:%s' % (param.http_user,
                               param.http_pwd))
                request.add_header("Authorization", "Basic %s" % base64string)
            binary = urllib2.urlopen(request)
        except urllib2.HTTPError as err:
            if err.code == 404:
                # the image is just missing, we skip it
                return
            else:
                # we don't know why we couldn't download the image
                # so we propagate the error, the import will fail
                # and we have to check why it couldn't be accessed
                raise
        else:
            return binary.read()

    def run(self, magentoextend_id, binding_id):
        self.magentoextend_id = magentoextend_id
        images = self._get_images()
        images = self._sort_images(images)
        binary = None
        while not binary and images:
            binary = self._get_binary_image(images.pop())
        if not binary:
            return
        model = self.model.with_context(connector_no_export=True)
        binding = model.browse(binding_id)
        binding.write({'image': base64.b64encode(binary)})

@magentoextend
class ProductProductImportMapper(ImportMapper):
    _model_name = 'magentoextend.product.product'

    direct = [('name', 'name'),
              ('description', 'description'),
              ('weight', 'weight'),
              ('cost', 'standard_price'),
              ('short_description', 'description_sale'),
              ('sku', 'default_code'),
              ('type_id', 'product_type'),
              (normalize_datetime('created_at'), 'created_at'),
              (normalize_datetime('updated_at'), 'updated_at'),
              ]

    @mapping
    def is_active(self, record):
        # return {'active': (record.get('status') == '1')}
        return {'active': True}

    @mapping
    def price(self, record):
        """ The price is imported at the creation of
        the product, then it is only modified and exported
        from OpenERP """
        return {'list_price': record.get('price', 0.0)}

    @mapping
    def type(self, record):
        if record['type_id'] == 'simple':
            return {'type': 'product'}
        return

    @mapping
    def magentoextend_id(self, record):
        return {'magentoextend_id': record['product_id']}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def owner_id(self, record):
        return {'owner_id': self.backend_record.connector_id.home_id.partner_id.id}


@job(default_channel='root.magentoextend')
def product_import_batch(session, model_name, backend_id, filters=None):
    """ Prepare the import of product modified on magentoextend """
    if filters is None:
        filters = {}
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(ProductBatchImporter)
    importer.run(filters=filters)


class ResPartnerBackend(models.Model):
    _inherit = 'product.product'

    owner_id = fields.Many2one('res.partner', string=u"Owner")
