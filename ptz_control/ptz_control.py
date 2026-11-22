from onvif import ONVIFCamera
from zeep.transports import Transport

class ptzControl(object):
    def __init__(self, IP, username, password, port=80, timeout=5):
        # Initialize the ONVIF camera connection (設定 timeout，避免攝影機離線時介面卡死)
        transport = Transport(timeout=timeout, operation_timeout=timeout)
        self.mycam = ONVIFCamera(IP, port, username, password, transport=transport)
        self.media = self.mycam.create_media_service()
        self.ptz = self.mycam.create_ptz_service()
        self.media_profile = self.media.GetProfiles()[0]
        self.movement_step_size = 0.05

        # Get PTZ configuration options
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

        # Set up continuous move request
        self.requestc = self.ptz.create_type('ContinuousMove')
        self.requestc.ProfileToken = self.media_profile.token
        if self.requestc.Velocity is None:
            self.requestc.Velocity = self.ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position
            self.requestc.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
            self.requestc.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI

        # Set up stop request
        self.requests = self.ptz.create_type('Stop')
        self.requests.ProfileToken = self.media_profile.token
        self.stop()

    def stop(self):
        # Stop all PTZ movements
        self.requests.PanTilt = True
        self.requests.Zoom = True
        self.ptz.Stop(self.requests)

    def move_up(self):
        # Move the camera up
        status = self.ptz.GetStatus({'ProfileToken': self.media_profile.token})
        pan = status.Position.PanTilt.x
        tilt = status.Position.PanTilt.y
        zoom = status.Position.Zoom.x

        # Ensure tilt doesn't exceed 1
        new_tilt = min(tilt + self.movement_step_size, 1.0)

        self.requesta = self.ptz.create_type('AbsoluteMove')
        self.requesta.ProfileToken = self.media_profile.token
        self.requesta.Position = status.Position
        self.requesta.Position.PanTilt.x = pan
        self.requesta.Position.PanTilt.y = new_tilt
        self.requesta.Position.Zoom.x = zoom
        self.ptz.AbsoluteMove(self.requesta)

    def move_down(self):
        # Move the camera down
        status = self.ptz.GetStatus({'ProfileToken': self.media_profile.token})
        pan = status.Position.PanTilt.x
        tilt = status.Position.PanTilt.y
        zoom = status.Position.Zoom.x

        # Ensure tilt doesn't go below -1
        new_tilt = max(tilt - self.movement_step_size, -1.0)

        self.requesta = self.ptz.create_type('AbsoluteMove')
        self.requesta.ProfileToken = self.media_profile.token
        self.requesta.Position = status.Position
        self.requesta.Position.PanTilt.x = pan
        self.requesta.Position.PanTilt.y = new_tilt
        self.requesta.Position.Zoom.x = zoom
        self.ptz.AbsoluteMove(self.requesta)

    def move_left(self):
        # Move the camera left
        status = self.ptz.GetStatus({'ProfileToken': self.media_profile.token})
        pan = status.Position.PanTilt.x
        tilt = status.Position.PanTilt.y
        zoom = status.Position.Zoom.x

        # Ensure pan doesn't go below -1
        new_pan = max(pan - self.movement_step_size, -1.0)

        self.requesta = self.ptz.create_type('AbsoluteMove')
        self.requesta.ProfileToken = self.media_profile.token
        self.requesta.Position = status.Position
        self.requesta.Position.PanTilt.x = new_pan
        self.requesta.Position.PanTilt.y = tilt
        self.requesta.Position.Zoom.x = zoom
        self.ptz.AbsoluteMove(self.requesta)

    def move_right(self):
        # Move the camera right
        status = self.ptz.GetStatus({'ProfileToken': self.media_profile.token})
        pan = status.Position.PanTilt.x
        tilt = status.Position.PanTilt.y
        zoom = status.Position.Zoom.x

        # Ensure pan doesn't exceed 1
        new_pan = min(pan + self.movement_step_size, 1.0)

        self.requesta = self.ptz.create_type('AbsoluteMove')
        self.requesta.ProfileToken = self.media_profile.token
        self.requesta.Position = status.Position
        self.requesta.Position.PanTilt.x = new_pan
        self.requesta.Position.PanTilt.y = tilt
        self.requesta.Position.Zoom.x = zoom
        self.ptz.AbsoluteMove(self.requesta)

    def zoom_in(self):
        # Zoom in the camera
        status = self.ptz.GetStatus({'ProfileToken': self.media_profile.token})
        pan = status.Position.PanTilt.x
        tilt = status.Position.PanTilt.y
        zoom = status.Position.Zoom.x

        # Ensure zoom doesn't exceed 1
        new_zoom = min(zoom + self.movement_step_size, 1.0)

        self.requesta = self.ptz.create_type('AbsoluteMove')
        self.requesta.ProfileToken = self.media_profile.token
        self.requesta.Position = status.Position
        self.requesta.Position.PanTilt.x = pan
        self.requesta.Position.PanTilt.y = tilt
        self.requesta.Position.Zoom.x = new_zoom
        self.ptz.AbsoluteMove(self.requesta)

    def zoom_out(self):
        # Zoom out the camera
        status = self.ptz.GetStatus({'ProfileToken': self.media_profile.token})
        pan = status.Position.PanTilt.x
        tilt = status.Position.PanTilt.y
        zoom = status.Position.Zoom.x

        # Ensure zoom doesn't go below 0
        new_zoom = max(zoom - self.movement_step_size, 0.0)

        self.requesta = self.ptz.create_type('AbsoluteMove')
        self.requesta.ProfileToken = self.media_profile.token
        self.requesta.Position = status.Position
        self.requesta.Position.PanTilt.x = pan
        self.requesta.Position.PanTilt.y = tilt
        self.requesta.Position.Zoom.x = new_zoom
        self.ptz.AbsoluteMove(self.requesta)

    def move_to_position(self, pan=None, tilt=None, zoom=None):
        # Move the camera to a specific position
        current_pan, current_tilt, current_zoom = self.get_current_position()
        if pan is None:
            pan = current_pan
        if tilt is None:
            tilt = current_tilt
        if zoom is None:
            zoom = current_zoom

        # Ensure values are within valid range: [-1, 1] for pan and tilt, [0, 1] for zoom
        pan = max(min(pan, 1.0), -1.0)
        tilt = max(min(tilt, 1.0), -1.0)
        zoom = max(min(zoom, 1.0), 0.0)

        self.requesta = self.ptz.create_type('AbsoluteMove')
        self.requesta.ProfileToken = self.media_profile.token
        self.requesta.Position = self.ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position
        self.requesta.Position.PanTilt.x = pan
        self.requesta.Position.PanTilt.y = tilt
        self.requesta.Position.Zoom.x = zoom
        self.ptz.AbsoluteMove(self.requesta)

    def get_current_position(self):
        # Get the current position of the camera
        status = self.ptz.GetStatus({'ProfileToken': self.media_profile.token})
        pan = status.Position.PanTilt.x
        tilt = status.Position.PanTilt.y
        zoom = status.Position.Zoom.x
        return pan, tilt, zoom