class AbstractDatabaseObject:
    table_name, field_list, json_field_list = None, None, None

    """
    constructor for any DatabaseObject
    for subclasses, recommend overriding this __init__ with pre-populated table_name and field_list
    and pass args as list/tuple (no need for starred notation)
    must be constructed with either
    - len(args) == len(field_list) (__initialized flag will be set to True, all fields will be populated)
    - len(args) == 0 (blank object, __initialized flag will be set to False, and all fields to None)
    """

    def __init__(self, args) -> None:
        super().__init__()
        if len(self.field_list) != len(args):
            raise KeyError(f"{self.table_name} object expected {len(self.field_list)} attributes, provided {len(args)}")
        for f in self.field_list:
            setattr(self, f, args[f])

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.json_field_list is None:
            return f'{{"obj_type": "{self.table_name}",' \
                + ','.join([f'"{f}": "{getattr(self, f)}"' for f in self.field_list]) + '}'
        else:
            return f'{{"obj_type": "{self.table_name}",' \
                + ','.join([f'"{f}": "{getattr(self, f)}"' for f in self.json_field_list]) + '}'

    @classmethod
    def get_query(cls, field_sublist: list[str]) -> str:
        query = f"select * from {cls.table_name} where "
        if "active" in cls.field_list and "active" not in field_sublist:
            query = query + "active = True"
            if len(field_sublist) > 0:
                query = query + " and "
        return query + " and ".join([f"{k} = %s" for k in field_sublist])
