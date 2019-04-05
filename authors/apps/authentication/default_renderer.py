import json

from rest_framework.renderers import JSONRenderer


class BaseRenderer(JSONRenderer):
    charset = 'utf-8'
    data = 'data'

    def render(self, data, media_type=None, renderer_context=None):

        errors = data.get('errors', None)

        if errors is not None:
            return super(BaseRenderer, self).render(data)

        return json.dumps({
            self.data: data
        })
