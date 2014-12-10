import json

from .exceptions import StackException
from .http import HttpMixin, endpoint
from .version import accepted_versions, deprecated


class BlueprintMixin(HttpMixin):

    @endpoint("blueprints/")
    def create_blueprint(self, blueprint, provider="ec2"):
        """Create a blueprint"""

        # check the provided blueprint to see if we need to look up any ids
        for host in blueprint["hosts"]:
            if isinstance(host["size"], basestring):
                host["size"] = self.get_instance_id(host["size"], provider)

            if isinstance(host["zone"], basestring):
                host["zone"] = self.get_zone_id(host["zone"], provider)

            if isinstance(host["cloud_profile"], basestring):
                host["cloud_profile"] = self.get_profile_id(host["cloud_profile"], title=True)

            for component in host["formula_components"]:
                if not component.get("sls_path") and isinstance(component["id"], (tuple, list)):
                    formula_id = self.get_formula_id(component["id"][0])

                    component["id"] = self.get_component_id(
                        self.get_formula(formula_id),
                        component["id"][1])

        return self._post(endpoint, data=json.dumps(blueprint), jsonify=True)

    @endpoint("blueprints/")
    def list_blueprints(self):
        """Return info for a specific blueprint_id"""
        return self._get(endpoint, jsonify=True)['results']

    @endpoint("blueprints/{blueprint_id}/")
    def get_blueprint(self, blueprint_id):
        """Return info for a specific blueprint_id"""
        return self._get(endpoint, jsonify=True)

    @endpoint("blueprints/")
    def search_blueprints(self, **kwargs):
        """Return info for a specific blueprint_id"""
        return self._get(endpoint, params=kwargs, jsonify=True)['results']

    @endpoint("blueprints/{blueprint_id}")
    def delete_blueprint(self, blueprint_id):
        return self._delete(endpoint, jsonify=True)

    @deprecated
    @accepted_versions("<0.7")
    def get_blueprint_id(self, title):
        """Get the id for a blueprint that matches title"""

        blueprints = self.search_blueprints(title=title)

        if not len(blueprints):
            raise StackException("Blueprint %s not found" % title)

        return blueprints[0]['id']
