from django.shortcuts import get_object_or_404

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.permissions import permission_document_type_view
from mayan.apps.documents.serializers.document_type_serializers import DocumentTypeSerializer
from mayan.apps.rest_api import generics
from mayan.apps.rest_api.api_view_mixins import (
    AsymmetricSerializerAPIViewMixin, ExternalObjectAPIViewMixin
)

from ..models.index_template_models import IndexTemplate
from ..permissions import (
    permission_index_template_create, permission_index_template_delete,
    permission_index_template_edit, permission_index_template_rebuild,
    permission_index_template_view
)
from ..serializers import (
    DocumentTypeAddSerializer, DocumentTypeRemoveSerializer,
    IndexTemplateSerializer, IndexTemplateNodeSerializer,
    IndexTemplateNodeWriteSerializer
)
from ..tasks import task_index_template_rebuild


class APIIndexTemplateListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the defined indexes template.
    post: Create a new index template.
    """
    mayan_object_permissions = {'GET': (permission_index_template_view,)}
    mayan_view_permissions = {'POST': (permission_index_template_create,)}
    ordering_fields = ('enabled', 'id', 'label', 'slug')
    queryset = IndexTemplate.objects.all()
    serializer_class = IndexTemplateSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }


class APIIndexTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected index template.
    get: Returns the details of the selected index template.
    patch: Partially edit an index template.
    put: Edit an index template.
    """
    lookup_url_kwarg = 'index_template_id'
    mayan_object_permissions = {
        'GET': (permission_index_template_view,),
        'PUT': (permission_index_template_edit,),
        'PATCH': (permission_index_template_edit,),
        'DELETE': (permission_index_template_delete,)
    }
    queryset = IndexTemplate.objects.all()
    serializer_class = IndexTemplateSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }


class APIIndexTemplateDocumentTypeListView(
    ExternalObjectAPIViewMixin, generics.ListAPIView
):
    """
    get: Returns a list of the document types associated with this index template.
    """
    external_object_class = IndexTemplate
    external_object_pk_url_kwarg = 'index_template_id'
    mayan_external_object_permissions = {
        'GET': (permission_index_template_view,)
    }
    mayan_object_permissions = {'GET': (permission_document_type_view,)}
    serializer_class = DocumentTypeSerializer

    def get_queryset(self):
        return self.external_object.document_types.all()


class APIIndexTemplateDocumentTypeAddView(generics.ObjectActionAPIView):
    """
    post: Add a document type to an index template.
    """
    lookup_url_kwarg = 'index_template_id'
    mayan_object_permissions = {
        'POST': (permission_index_template_edit,)
    }
    serializer_class = DocumentTypeAddSerializer
    queryset = IndexTemplate.objects.all()

    def object_action(self, request, serializer):
        document_type = serializer.validated_data['document_type']
        self.object._event_actor = self.request.user
        self.object.document_types_add(queryset=[document_type])


class APIIndexTemplateDocumentTypeRemoveView(generics.ObjectActionAPIView):
    """
    post: Remove a document type from an index template.
    """
    lookup_url_kwarg = 'index_template_id'
    mayan_object_permissions = {
        'POST': (permission_index_template_edit,)
    }
    serializer_class = DocumentTypeRemoveSerializer
    queryset = IndexTemplate.objects.all()

    def object_action(self, request, serializer):
        document_type = serializer.validated_data['document_type']
        self.object._event_actor = self.request.user
        self.object.document_types_remove(queryset=[document_type])


class APIIndexTemplateNodeViewMixin(AsymmetricSerializerAPIViewMixin):
    object_permissions = {
        'GET': permission_index_template_view,
        'PATCH': permission_index_template_edit,
        'PUT': permission_index_template_edit,
        'POST': permission_index_template_edit,
        'DELETE': permission_index_template_edit
    }
    read_serializer_class = IndexTemplateNodeSerializer
    write_serializer_class = IndexTemplateNodeWriteSerializer

    def get_serializer(self, *args, **kwargs):
        if not self.request:
            return None

        return super().get_serializer(*args, **kwargs)

    def get_index_template(self):
        if 'index_template_id' in self.kwargs:
            permission = self.object_permissions[self.request.method]

            queryset = AccessControlList.objects.restrict_queryset(
                permission=permission, queryset=IndexTemplate.objects.all(),
                user=self.request.user
            )

            return get_object_or_404(
                klass=queryset, pk=self.kwargs['index_template_id']
            )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['index_template'] = self.get_index_template()
        return context


class APIIndexTemplateNodeListView(
    APIIndexTemplateNodeViewMixin, generics.ListCreateAPIView
):
    """
    get: Returns a list of all the template nodes for the selected index.
    post: Create a new index template node.
    """
    ordering_fields = ('enabled', 'id', 'link_documents')

    def get_queryset(self):
        return self.get_index_template().index_template_root_node.get_children()


class APIIndexTemplateNodeDetailView(
    APIIndexTemplateNodeViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    """
    delete: Delete the selected index template node.
    get: Returns the details of the selected index template node.
    patch: Partially edit an index template node.
    put: Edit an index template node.
    """
    lookup_url_kwarg = 'index_template_node_id'

    def get_queryset(self):
        return self.get_index_template().index_template_nodes.all()


class APIIndexTemplateRebuildView(generics.ObjectActionAPIView):
    """
    post: Rebuild the selected index template.
    """
    lookup_url_kwarg = 'index_template_id'
    mayan_object_permissions = {
        'POST': (permission_index_template_rebuild,)
    }
    queryset = IndexTemplate.objects.all()

    def object_action(self, request, serializer):
        task_index_template_rebuild.apply_async(
            kwargs={
                'index_id': self.object.pk
            }
        )


class APIIndexTemplateResetView(generics.ObjectActionAPIView):
    """
    post: Reset the selected index template.
    """
    lookup_url_kwarg = 'index_template_id'
    mayan_object_permissions = {
        'POST': (permission_index_template_rebuild,)
    }
    queryset = IndexTemplate.objects.all()

    def object_action(self, request, serializer):
        self.object.reset()
