from fastapi import Depends

from common.infomaniak.ik_llm import get_ik_llm


def ik_llm_depedency():
    return get_ik_llm()


llm_ik = Depends(ik_llm_depedency)
