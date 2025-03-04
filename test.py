import torch
print(f"GPU 사용 가능 여부: {torch.cuda.is_available()}")
print(f"사용 가능한 GPU 개수: {torch.cuda.device_count()}")
print(f"현재 사용 중인 GPU: {torch.cuda.current_device()}")
print(f"GPU 이름: {torch.cuda.get_device_name(0)}")
