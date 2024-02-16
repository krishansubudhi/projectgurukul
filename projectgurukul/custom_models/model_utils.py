import torch
def get_device_and_dtype():
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
        device = "mps"
        dtype = torch.float16
    else:
        device = "auto"
        dtype = "auto"
    return device, dtype