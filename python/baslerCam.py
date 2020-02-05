import asyncio
# test
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
        # reverse Y so that image in ds9 displays correctly
        cam.ReverseY = True
        cam.PixelFormat = "Mono12"
        cam.Gain = cam.Gain.Min
        cam.Width = cam.Width.Max
        cam.Height = cam.Height.Max
        cam.BinningHorizontal = 2
        cam.BinningVertical = 2
        cam.BinningVerticalMode = "Sum"
        cam.BinningHorizontalMode = "Sum"

        self.device = cam

    async def _disconnect_internal(self):
        """Close connection to camera.
        """
        self.device.Close()

    async def _expose_internal(self, exposure):
        """Expose the camera exptime in seconds
        """

        # basler takes exptime in micro second integers
        exptime_ms = int(numpy.floor(exposure.exptime * 1e6))
        self._notify(CameraEvent.EXPOSURE_INTEGRATING)

        result = await self.loop.run_in_executor(None, self.device.GrabOne, exptime_ms)

        exposure.data = numpy.array(result.Array)
        print("exposure data shape", exposure.data.shape)

        # append headers
        addHeaders = [
            ("BinX", self.device.BinningHorizontal, "Horizontal Bin Factor"),
            ("BinY", self.device.BinningVertical, "Vertical Bin Factor"),
            ("Gain", self.device.Gain, "Gain [dB]"),
            ("Width", self.device.Width, "Pixel Columns"),
            ("Height", self.device.Height, "Pixel Rows"),
            ("ReverseY", self.device.ReverseY, "Reverse Rows"),
            ("ReverseX", self.device.ReverseX, "Reverse Columns"),
            ("VertBinMode", self.device.BinningVerticalMode),
            ("HorizBinMode", self.device.BinningHorizontalMode)
        ]
        for header in addHeaders:
            exposure.fits_model[0].header_model.append(header)
        return


async def takeOne():
    serialNum = "23197801"
    config = {
        'cameras': {
            'my_camera': {
                'uid': serialNum,
                'connection_params': {
                    'uid': serialNum
                }
            }
        }
    }
    cs = BaslerCameraSystem(BaslerCamera, camera_config=config)
    cam = await cs.add_camera(uid=serialNum, autoconnect=True)
    print("cameras", cs.cameras)
    print("cam", cam)
    # cam.connect()

    # availableCams = cs.list_available_cameras()
    # print("availablecams", availableCams)
    # cam = await cs.add_camera(
    #     name=availableCams[0],
    #     uid=availableCams[0],
    #     autoconnect=False
    # )
    # print("connection params", cam.camera_config.get('connection_params', {}).copy())
    # await cam.connect({"uid": availableCams[0]})
    # print("cam type", type(cam))

    exp = await cam.expose(0.001)
    exp.write()
    print("filename", exp.filename)

if __name__ == "__main__":
    asyncio.run(takeOne())




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
