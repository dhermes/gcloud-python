# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""High-level wrapper for datastore queries."""

from google.cloud.ndb import _exceptions
from google.cloud.ndb import model


__all__ = [
    "Cursor",
    "QueryOptions",
    "RepeatedStructuredPropertyPredicate",
    "ParameterizedThing",
    "Parameter",
    "ParameterizedFunction",
    "Node",
    "FalseNode",
    "ParameterNode",
    "FilterNode",
    "PostFilterNode",
    "ConjunctionNode",
    "DisjunctionNode",
    "AND",
    "OR",
    "Query",
    "gql",
    "QueryIterator",
]


Cursor = NotImplemented  # From `google.appengine.datastore.datastore_query`


class QueryOptions:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class RepeatedStructuredPropertyPredicate:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class ParameterizedThing:
    """Base class for :class:`Parameter` and :class:`ParameterizedFunction`.

    This exists purely for :func:`isinstance` checks.
    """

    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        return not self == other


class Parameter(ParameterizedThing):
    """Represents a bound variable in a GQL query.

    ``Parameter(1)`` corresponds to a slot labeled ``:1`` in a GQL query.
    ``Parameter('xyz')`` corresponds to a slot labeled ``:xyz``.

    The value must be set (bound) separately by calling :meth:`set`.

    Args:
        key (Union[str, int]): The parameter key.

    Raises:
        TypeError: If the ``key`` is not a string or integer.
    """

    def __init__(self, key):
        if not isinstance(key, (int, str, bytes)):
            raise TypeError(
                "Parameter key must be an integer or string, not {}".format(
                    key
                )
            )
        self._key = key

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self._key)

    def __eq__(self, other):
        if not isinstance(other, Parameter):
            return NotImplemented

        return self._key == other._key

    @property
    def key(self):
        """Retrieve the key."""
        return self._key

    def resolve(self, bindings, used):
        """Resolve the current parameter from the parameter bindings.

        Args:
            bindings (dict): A mapping of parameter bindings.
            used (Dict[Union[str, int], bool]): A mapping of already used
                parameters. This will be modified if the current parameter
                is in ``bindings``.

        Returns:
            Any: The bound value for the current parameter.

        Raises:
            .BadArgumentError: If the current parameter is not in ``bindings``.
        """
        key = self._key
        if key not in bindings:
            raise _exceptions.BadArgumentError(
                "Parameter :{} is not bound.".format(key)
            )
        value = bindings[key]
        used[key] = True
        return value


class ParameterizedFunction(ParameterizedThing):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class Node:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class FalseNode(Node):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class ParameterNode(Node):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class FilterNode(Node):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class PostFilterNode(Node):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class ConjunctionNode(Node):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class DisjunctionNode(Node):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError


# AND and OR are preferred aliases for these.
AND = ConjunctionNode
OR = DisjunctionNode


class Query:
    """Query object.

    .. note::

        A query is usually constructed by calling :meth:`Model.query`.

    When any of the operators ``!=``, ``IN`` or ``OR`` is used, a
    "multi-query" is produced. However, not  all operations on queries are
    supported by "multi-query" instances.

    Args:
        kind (Optional[str]): The kind being queried.
        ancestor (Optional[Key]): The ancestor key for the query.
        filters (Optional[Node]): A single node representing a filter
            expression tree.
        orders (Optional[Any]): Low-level ``Order`` object.
        app (Optional[str]): The Google Cloud Platform project (previously on
            Google App Engine, this was called the Application ID).
        namespace (Optional[str]): namespace.
        default_options (Optional[QueryOptions]): The options for this query.
        projection (Optional[Iterable[Property]]): Properties to project.
        group_by (Optional[Iterable[Property]]): Properties to group by.
    """

    def __init__(
        self,
        *,
        kind=None,
        ancestor=None,
        filters=None,
        orders=None,
        app=None,
        namespace=None,
        default_options=None,
        projection=None,
        group_by=None
    ):
        self._kind = kind
        self._ancestor = self._validate_ancestor(ancestor, app, namespace)
        self._filters = self._validate_filters(filters)
        self._orders = self._validate_orders(orders)
        self._app = app
        self._namespace = self._validate_namespace(namespace, ancestor)
        self._default_options = self._validate_default_options(default_options)
        self._projection = self._validate_projection(projection, self._kind)
        self._group_by = self._validate_group_by(group_by, self._kind)

    @staticmethod
    def _validate_ancestor(ancestor, app, namespace):
        if ancestor is None:
            return ancestor

        if isinstance(ancestor, ParameterizedThing):
            if (
                isinstance(ancestor, ParameterizedFunction)
                and ancestor.func != "key"
            ):
                raise TypeError(
                    "ancestor cannot be a GQL function other than KEY"
                )

            return ancestor

        if not isinstance(ancestor, model.Key):
            raise TypeError(
                "ancestor must be a Key; received {!r}".format(ancestor)
            )

        if not ancestor.id():
            raise ValueError("ancestor cannot be an incomplete key")

        if app is not None and app != ancestor.app():
            raise TypeError("app/ancestor mismatch")

        if namespace is not None and namespace != ancestor.namespace():
            raise TypeError("namespace/ancestor mismatch")

        return ancestor

    @staticmethod
    def _validate_filters(filters):
        if filters is not None and not isinstance(filters, Node):
            raise TypeError(
                "filters must be a query Node or None; received {!r}".format(
                    filters
                )
            )
        return filters

    @staticmethod
    def _validate_orders(orders):
        if orders is not None:
            raise NotImplementedError("Missing datastore_query.Order")
        return orders

    @staticmethod
    def _validate_default_options(default_options):
        if default_options is not None:
            raise NotImplementedError(
                "Missing datastore_rpc.BaseConfiguration"
            )
        return default_options

    @staticmethod
    def _validate_namespace(namespace, ancestor):
        if namespace is None and isinstance(ancestor, model.Key):
            namespace = ancestor.namespace()
        return namespace

    @staticmethod
    def _to_property_names(properties):
        if not isinstance(properties, (list, tuple)):
            properties = [properties]  # It will be type-checked below.
        fixed = []
        for prop in properties:
            if isinstance(prop, str):
                fixed.append(prop)
            elif isinstance(prop, model.Property):
                fixed.append(prop._name)
            else:
                raise TypeError(
                    "Unexpected property ({!r}); should be string "
                    "or Property".format(prop)
                )

        return fixed

    @staticmethod
    def _check_properties(fixed, kind, **kwargs):
        modelclass = model.Model._kind_map.get(kind)
        if modelclass is not None:
            modelclass._check_properties(fixed, **kwargs)

    def _validate_projection(self, projection, kind):
        if projection is None:
            return None

        if not projection:
            raise TypeError("projection argument cannot be empty")
        if not isinstance(projection, (tuple, list)):
            raise TypeError(
                "projection must be a tuple, list or None; "
                "received {!r}".format(projection)
            )
        self._check_properties(self._to_property_names(projection), kind)
        return tuple(projection)

    def _validate_group_by(self, group_by, kind):
        if group_by is None:
            return None

        if not group_by:
            raise TypeError("group_by argument cannot be empty")
        if not isinstance(group_by, (tuple, list)):
            raise TypeError(
                "group_by must be a tuple, list or None; "
                "received {!r}".format(group_by)
            )
        self._check_properties(self._to_property_names(group_by), kind)
        return tuple(group_by)


def gql(*args, **kwargs):
    raise NotImplementedError


class QueryIterator:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError
