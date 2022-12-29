def get_serializer_with_fields(serializer, fields):
    """
    Returns a new serializer with the specified fields.
    """

    class NewSerializer(serializer):
        def __init__(self, *args, **kwargs):
            # Don't pass the 'fields' arg up to the superclass
            fields = kwargs.pop('fields', None)
            NewSerializer.__name__ = f"Partial{serializer.__name__}"
            # Instantiate the superclass normally
            super(NewSerializer, self).__init__(*args, **kwargs)

            if fields is not None:
                # Drop any fields that are not specified in the `fields` argument.
                allowed = set(fields)
                existing = set(self.fields)
                for field_name in existing - allowed:
                    self.fields.pop(field_name)

    return NewSerializer(fields=fields)
