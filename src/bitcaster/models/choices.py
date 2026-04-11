FILTERING_NONE = 1
FILTERING_CONTEXT = 2
FILTERING_EXTERNAL = 3
FILTERING_DYNAMIC = 4
FILTERING = (
    (FILTERING_NONE, "No Custom Filtering. Forward to distibution list"),
    (FILTERING_CONTEXT, "Context based filtering. Enable Notification based on context values"),
    (FILTERING_EXTERNAL, "External ruled filtering. Do not use DistributionList, filter users by API rules"),
    (FILTERING_DYNAMIC, "Fixed ruled filtering. "),
)
