from langsmith import traceable


@traceable(
    name="ATS Scoring"
)
def trace_ats_score(
    func,
    *args,
    **kwargs
):

    return func(
        *args,
        **kwargs
    )