# Generates diff.patch file, reads the dataset row of the instance and createa a new entry in infereces.jsol file.
# Entry schema:
# {
#     "instance_id": "<Unique task instance ID>",
#     "model_patch": "<.patch file content string>",
#     "model_name_or_path": "<Model name here (i.e. SWE-Llama-13b)>",
# }