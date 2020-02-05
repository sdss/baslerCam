from pypylon import pylon

from basecam import CameraSystem, BaseCamera, CameraEvent





# list devices:
def listDevices():
    serialNums = []
    for dev in pylon.TlFactory.GetInstance().EnumerateDevices():
        serialNums.append(dev.GetSerialNumber())
    return serialNums

def openDevice(serialNumber):
    info = pylon.DeviceInfo()
    info.SetSerialNumber(serialNumber)
    cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(info))
    cam.Open()
    return cam

devs = listDevices()
print("found devices", devs)
cam = openDevice(devs[0])
print("horizontal bin", cam.BinningHorizontal.Value)
