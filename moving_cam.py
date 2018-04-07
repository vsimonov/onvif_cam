from time import sleep
from copy import copy
        
class ptzcam():
    def __init__(self):
        from onvif import ONVIFCamera
        from time import sleep
        print 'IP camera initialization'
        self.mycam = ONVIFCamera('192.168.13.12', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')
        print 'Connected to ONVIF camera'
        # Create media service object
        self.media = self.mycam.create_media_service()
        print 'Created media service object'
        print
        # Get target profile
        self.media_profile = self.media.GetProfiles()[0]
        # Use the first profile and Profiles have at least one
        token = self.media_profile._token

    #PTZ controls  -------------------------------------------------------------
        print
        # Create ptz service object
        print 'Creating PTZ object'
        self.ptz = self.mycam.create_ptz_service()
        print 'Created PTZ service object'
        print

        #Get available PTZ services
        request = self.ptz.create_type('GetServiceCapabilities')
        Service_Capabilities = self.ptz.GetServiceCapabilities(request)
        print 'PTZ service capabilities:'
        print Service_Capabilities
        print

        #Get PTZ status
        status = self.ptz.GetStatus({'ProfileToken':token})
        print 'PTZ status:'
        print status
        print 'Pan position:', status.Position.PanTilt._x
        print 'Tilt position:', status.Position.PanTilt._y
        print 'Zoom position:', status.Position.Zoom._x
        #print 'Pan/Tilt Moving?:', status.MoveStatus.PanTilt 
        print
        # Get PTZ configuration options for getting option ranges
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.media_profile.PTZConfiguration._token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)
        print 'PTZ configuration options:'
        print ptz_configuration_options
        print

        self.requestc = self.ptz.create_type('ContinuousMove')
        self.requestc.ProfileToken = self.media_profile._token

        self.requesta = self.ptz.create_type('AbsoluteMove')
        self.requesta.ProfileToken = self.media_profile._token
        print 'Absolute move options'
        print self.requesta
        print

        self.requestr = self.ptz.create_type('RelativeMove')
        self.requestr.ProfileToken = self.media_profile._token
        print 'Relative move options'
        print self.requestr
        print

        self.requests = self.ptz.create_type('Stop')
        self.requests.ProfileToken = self.media_profile._token

        self.requestp = self.ptz.create_type('SetPreset')
        self.requestp.ProfileToken = self.media_profile._token

        self.requestg = self.ptz.create_type('GotoPreset')
        self.requestg.ProfileToken = self.media_profile._token

        print 'Initial PTZ stop'
        print
        self.stop()


#Stop, move, zoom
    def stop(self):
        self.requests.PanTilt = True
        self.requests.Zoom = True
        print 'Stop:'
        print
        self.ptz.Stop(self.requests)
        print 'Stopped'

    def move(self, pan, tilt): #moving to the set point with zooming                                                  
        print 'Start moving'                                                
        token = self.media_profile._token   #get token                                     
        status = self.ptz.GetStatus({'ProfileToken':token})
        #print Pan, Tilt status
        print 'Pan position:', status.Position.PanTilt._x                   
        print 'Tilt position:', status.Position.PanTilt._y
        self.zoom(pan)  #zooming to zoom == pan
        #pan must be correct for zoom valuation                                                    
                                                                           
        while abs(pan - status.Position.PanTilt._x) > 0.05 and abs(tilt - status.Position.PanTilt._y) > 0.05: 
        #cycle works while status is less or more than the desired value (more than 0.05) 
            if pan > status.Position.PanTilt._x: #pan changing                           
                self.requestc.Velocity.PanTilt._x = 0.5                    
                print 'pan +0.5'
            else:                                                           
                self.requestc.Velocity.PanTilt._x = -0.5
                print 'pan -0.5'
            if tilt > status.Position.PanTilt._y: #tilt changing              
                self.requestc.Velocity.PanTilt._y = 0.5
                print 'tilt +0.5'
            else:
                self.requestc.Velocity.PanTilt._y = -0.5 
                print 'tilt -0.5'
            if abs(pan - status.Position.PanTilt._x) < 0.05:  #if we get the desired value, cycle breaks               
                self.srequestc.Velocity.PanTilt._x = 0                           
                break
            if abs(tilt - status.Position.PanTilt._y) < 0.05: 
                self.requestc.Velocity.PanTilt._y = 0
                break
            self.ptz.ContinuousMove(self.requestc)                               
            status = self.ptz.GetStatus({'ProfileToken':token})
            status = self.ptz.GetStatus({'ProfileToken':token})
            #print status position
            print 'Pan position:', status.Position.PanTilt._x
            print 'Tilt position:', status.Position.PanTilt._y
            print 'Zoom position', status.Position.Zoom._x
            print '-------------------------------------------'
        self.stop()
 
    def zoom(self, velocity, timeout = 1): #zooming with fixed timeout
            self.requestc.Velocity.Zoom._x = velocity 
            self.perform_move(timeout)

    def perform_move(self, timeout): #just for zooming
            from time import sleep
            ret = self.ptz.ContinuousMove(self.requestc) 
            sleep(timeout)
            self.stop()
            print