"""Small CenterNet-style vertebra landmark detector (CPU friendly).
Input: grayscale lateral radiograph resampled to ~1 mm/px, 512x256 (H x W).
Outputs at stride 2: 1 vertebral-body centre heatmap + 14 offset channels (7 points x (dx, dy))."""
import torch, torch.nn as nn, torch.nn.functional as F
NPTS = 7
def block(i, o):
    return nn.Sequential(nn.Conv2d(i, o, 3, padding=1, bias=False), nn.BatchNorm2d(o), nn.ReLU(inplace=True),
                         nn.Conv2d(o, o, 3, padding=1, bias=False), nn.BatchNorm2d(o), nn.ReLU(inplace=True))
class Net(nn.Module):
    def __init__(s, c=(12, 24, 48, 64, 96)):
        super().__init__()
        s.e = nn.ModuleList([block(1, c[0])] + [block(c[i], c[i+1]) for i in range(4)])
        s.u = nn.ModuleList([block(c[i+1] + c[i], c[i]) for i in range(1, 4)][::-1])
        s.head_hm = nn.Sequential(nn.Conv2d(c[1], 32, 3, padding=1), nn.ReLU(), nn.Conv2d(32, 1, 1))
        s.head_off = nn.Sequential(nn.Conv2d(c[1], 64, 3, padding=1), nn.ReLU(), nn.Conv2d(64, 2*NPTS, 1))
        s.head_kp = nn.Sequential(nn.Conv2d(c[1], 32, 3, padding=1), nn.ReLU(), nn.Conv2d(32, NPTS, 1))
        s.head_hm[-1].bias.data.fill_(-2.19); s.head_kp[-1].bias.data.fill_(-2.19)
    def forward(s, x):
        f = []
        for i, b in enumerate(s.e):
            x = b(x if i == 0 else F.max_pool2d(x, 2)); f.append(x)
        x = f[-1]
        for j, b in enumerate(s.u):          # decode to stride 2 (feature level 1)
            skip = f[-2 - j]
            x = b(torch.cat([F.interpolate(x, size=skip.shape[-2:], mode='bilinear', align_corners=False), skip], 1))
        return s.head_hm(x), s.head_off(x), s.head_kp(x)
