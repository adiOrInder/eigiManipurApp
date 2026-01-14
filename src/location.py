# NOT COMPLETE

import time
import objc
from CoreLocation import CLLocationManager
from Foundation import NSObject, NSRunLoop, NSDate


class LocationManager(NSObject):

    def init(self):
        self = objc.super(LocationManager, self).init()
        if self is None:
            return None

        self.manager = CLLocationManager.alloc().init()
        self.manager.setDelegate_(self)
        return self

    def get_location(self):
        print("Requesting permission...")
        self.manager.requestWhenInUseAuthorization()

        print("Starting location updates...")
        self.manager.startUpdatingLocation()

        # keep runloop alive
        while True:
            NSRunLoop.currentRunLoop().runUntilDate_(
                NSDate.dateWithTimeIntervalSinceNow_(0.1)
            )

    def locationManager_didUpdateLocations_(self, manager, locations):
        loc = locations[-1]

        print("\nLOCATION RECEIVED")
        print("Latitude :", loc.coordinate().latitude)
        print("Longitude:", loc.coordinate().longitude)

        manager.stopUpdatingLocation()
        exit()


lm = LocationManager.alloc().init()
lm.get_location()
