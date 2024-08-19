#!/usr/bin/env python3

import pydantic


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
