from fastapi import Depends

from common.infomaniak.ik_llm import IKLLM


def ik_llm_depedency():
    return IKLLM()


llm_ik = Depends(ik_llm_depedency)
