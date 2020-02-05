import numpy

from pypylon import pylon

from basecam import CameraSystem, BaseCamera, CameraEvent


class BaslerCameraSystem(CameraSystem):

    __version__ = "0.0.1"

    def list_available_cameras(self):
        serialNums = []
        for dev in pylon.TlFactory.GetInstance().EnumerateDevices():
            serialNums.append(dev.GetSerialNumber())
        return serialNums

class BaslerCamera(BaseCamera):

    async def _connect_internal(self, uid):
        """Connect to a camera uid is serial number
        """
        info = pylon.DeviceInfo()
        info.SetSerialNumber(uid)
        cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(info))
        cam.Open()
        self.device = cam

    async def _disconnect_internal(self):
        """Close connection to camera.
        """
        self.device.Close()

    async def _expose_internal(self, exposure):
        """Expose the camera exptime in seconds
        """

        # basler takes exptime in micro seconds
        exptime_ms = exposure.exptime * 1e6
        self._notify(CameraEvent.EXPOSURE_INTEGRATING)

        result = self.device.GrabOne(exptime_ms)

        exposure.data = numpy.array(result.Array)
        print("exposure data shape", exposure.data.shape)
        return


if __name__ == "__main__":
    cs = BaslerCameraSystem(BaslerCamera)
    availableCams = cs.list_available_cameras()
    cam = await cs.add_camera(
        name=avalableCams[0],
        uid=availableCams[0],
        autoconnect=True
    )
    print("cam type", type(cam))

    exp = await cam.expose(0.001)
    exp.write()
    print("filename", exp.filename)




# # list devices:
# def listDevices():
#     serialNums = []
#     for dev in pylon.TlFactory.GetInstance().EnumerateDevices():
#         serialNums.append(dev.GetSerialNumber())
#     return serialNums

# def openDevice(serialNumber):
#     info = pylon.DeviceInfo()
#     info.SetSerialNumber(serialNumber)
#     cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(info))
#     cam.Open()
#     return cam

# devs = listDevices()
# print("found devices", devs)
# cam = openDevice(devs[0])
# print("horizontal bin", cam.BinningHorizontal.Value)
