#!/usr/bin/env python3

from typing import Any, List

from pydantic import model_validator


def oneof(fields: List[str]):
    def validator(cls, data: Any) -> Any:
        non_none_fields = [k for k, v in data.items() if v is not None and k in fields]
        if len(non_none_fields) > 1:
            field_str = "\n    ".join(non_none_fields)
            raise ValueError(f"Multiple oneof fields set:\n    {field_str}\n")
        if len(non_none_fields) == 0:
            field_str = "\n    ".join(fields)
            raise ValueError(f"Oneof the following fields must be set:\n    {field_str}\n")

        return data

    return model_validator(mode="before")(validator)
