# coding: utf-8
##    winMonitor: Lib allowing to acquire monitors under Windows
##
##    Copyright (C) 2018  Allard Chris - University Grenoble Alpes
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
winMonitor
@author: Chris Allard
@license: University Grenoble Alpes
@contact: lyon.allard.chris@gmail.com
"""

# Import directives
import ctypes
import math
import re

# Mapping with Windows dll
win32   = ctypes.windll.user32
shcore  = ctypes.windll.shcore
gdi32   = ctypes.windll.gdi32

# Constants statement
_SM_CXVIRTUALSCREEN         = 78
_SM_CYVIRTUALSCREEN         = 79
_SM_XVIRTUALSCREEN          = 76
_SM_YVIRTUALSCREEN          = 77
_SM_CMONITORS               = 80
_MONITOR_DEFAULTTONEAREST   = 2
_CF_BITMAP                  = 2
_SRCCOPY                    = 13369376

class POINT(ctypes.Structure):
    # https://msdn.microsoft.com/en-us/library/system.windows.point.point(v=vs.110).aspx
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]

class DEVICE_SCALE_FACTOR(ctypes.Structure):
    # https://msdn.microsoft.com/en-us/library/windows/desktop/hh706892(v=vs.85).aspx
    _fields_ = [("value", ctypes.c_int)]

class RECT(ctypes.Structure):
    # https://msdn.microsoft.com/en-us/library/windows/desktop/dd162897(v=vs.85).aspx
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

class tagMONITORINFOEX(ctypes.Structure):
    # https://msdn.microsoft.com/en-us/library/windows/desktop/dd145066(v=vs.85).aspx
    _fields_ = [("cbSize", ctypes.c_ulong),
                ("rcMonitor", RECT),
                ("rcWork", RECT),
                ("dwFLags", ctypes.c_ulong),
                ("szDevice", ctypes.c_wchar * 32)]

class DISPLAY_DEVICE(ctypes.Structure):
    # https://msdn.microsoft.com/en-us/library/windows/desktop/dd183569(v=vs.85).aspx
    _fields_ = [("cb", ctypes.c_ulong),
                ("DeviceName",ctypes.c_wchar * 32),
                ("DeviceString",ctypes.c_wchar * 128),
                ("StateFlags", ctypes.c_ulong),
                ("DeviceID", ctypes.c_wchar * 128),
                ("DeviceKey", ctypes.c_wchar * 128)]

class Monitor():
    # Class who defined a single monitor
    name    = None  # Name : Name of the monitor inside windows peripheral manager, default by windows is Generic Pnp Monitor
    id      = None  # ID : Hardware identification numbers
    flags   = None  # Flags : 0 Virtual, 1 Primary, 2 Other
    scale   = 0     # Scale : Scale defined inside windows viewing parameters
    width   = 0     # Width : real width resolution
    height  = 0     # Height : real height resolution
    vwidth  = 0     # vWidth : virtual width resolution after windows scaling
    vheight = 0     # vHeight : virtual height resolution after Windows scaling
    top     = 0     # top : top pixel inside windows virtual screen
    left    = 0     # left : left pixel inside windows virtual screen
    right   = 0     # right : right pixel inside windows virtual screen
    bottom  = 0     # bottom : bottom pixel inside windows virtual screen

    def getMonitorResolution(self):
        return (self.width, self.height)
    
    def getMonitorVirtualResolution(self):
        return (self.vwidth, self.vheight)

    def getMonitorPosition(self):
        return(self.top, self.left, self.right, self.bottom)
    
    def printMonitorInfo(self):
        print('{0:8} : {1:32}'.format('name', self.name))
        print('{0:8} : {1:32}'.format('id', self.id))
        print('{0:8} : {1:4d}'.format('flags', self.flags))
        print('{0:8} : {1:4d}'.format('scale', self.scale))
        print('{0:8} : {1:4d}'.format('width', self.width))
        print('{0:8} : {1:4d}'.format('height', self.height))
        print('{0:8} : {1:4d}'.format('vwidth', self.vwidth))
        print('{0:8} : {1:4d}'.format('vheight', self.vheight))
        print('{0:8} : {1:4d}'.format('top', self.top))
        print('{0:8} : {1:4d}'.format('left', self.left))
        print('{0:8} : {1:4d}'.format('right', self.right))
        print('{0:8} : {1:4d}'.format('bottom', self.bottom))

    def takeScreenshot(self):
        # Copy screen into a bitmap
        hScreen = win32.GetDC(None)
        hDC     = gdi32.CreateCompatibleDC(hScreen)
        hBitmap = gdi32.CreateCompatibleBitmap(hScreen, self.width, self.height)
        old_obj = gdi32.SelectObject(hDC, hBitmap)

        # Save bitmap inside clipboard
        gdi32.BitBlt(hDC, 0, 0, self.width, self.height, hScreen, self.left, self.top, _SRCCOPY)
        win32.OpenClipboard(None)
        win32.EmptyClipboard()
        win32.SetClipboardData(_CF_BITMAP, hBitmap)
        win32.CloseClipboard()

        # Clean bitmap
        gdi32.SelectObject(hDC, old_obj)
        gdi32.DeleteDC(hDC)
        win32.ReleaseDC(None, hScreen)
        gdi32.DeleteObject(hBitmap)

class Monitors():
    # Class that contains all the monitors
    monitors    = [] # List of all monitor objects
    nbMonitors  = win32.GetSystemMetrics(_SM_CMONITORS) # Number of display monitors on desktop without the virtual one

    def __init__(self):  

        # Loop on all available displays
        MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(RECT), ctypes.c_double)
        def InfoEnumProc(hMonitor, hdcMonitor, lprcMonitor, dwData):
            # Set structures
            screenOrigin    = POINT()
            screenInfo      = tagMONITORINFOEX()
            screenScale     = DEVICE_SCALE_FACTOR()
            screenDevice    = DISPLAY_DEVICE()
            currentScreen   = Monitor()

            # Initiate structures before calling them
            screenOrigin.x      = lprcMonitor.contents.left
            screenOrigin.y      = lprcMonitor.contents.top
            screenInfo.cbSize   = ctypes.sizeof(tagMONITORINFOEX)
            screenDevice.cb     = ctypes.sizeof(DISPLAY_DEVICE)

            # Update structures
            monitor = win32.MonitorFromPoint(screenOrigin, _MONITOR_DEFAULTTONEAREST) # Get monitor under the screenOrigin
            shcore.GetScaleFactorForMonitor(monitor, ctypes.byref(screenScale)) # Get scale for this monitor
            win32.GetMonitorInfoW(monitor, ctypes.byref(screenInfo)) # Get resolution for this monitor
            win32.EnumDisplayDevicesW(screenInfo.szDevice, None, ctypes.byref(screenDevice), 0) # Get name and id for this monitor

            # Udate monitor object
            currentScreen.name  = screenDevice.DeviceString
            currentScreen.id    = re.search(r'(?<=\\)(.*?)(?=\\)', screenDevice.DeviceID).group(0)
            
            if (screenInfo.dwFLags == 1): # If it's a primary screen
                currentScreen.flags     = 1
            else: currentScreen.flags   = 2
            
            currentScreen.scale     = screenScale.value
            currentScreen.left      = screenInfo.rcMonitor.left
            currentScreen.top       = screenInfo.rcMonitor.top
            currentScreen.right     = screenInfo.rcMonitor.right
            currentScreen.bottom    = screenInfo.rcMonitor.bottom
            currentScreen.vwidth    = int(math.fabs(math.fabs(currentScreen.right) - currentScreen.left))
            currentScreen.vheight   = int(math.fabs(math.fabs(currentScreen.bottom) - currentScreen.top))
            currentScreen.width     = int(math.fabs(math.fabs(currentScreen.right) - currentScreen.left) * (currentScreen.scale / 100))
            currentScreen.height    = int(math.fabs(math.fabs(currentScreen.bottom) - currentScreen.top) * (currentScreen.scale / 100))
            self.monitors.append(currentScreen)
            return 1
        win32.EnumDisplayMonitors(0, 0, MonitorEnumProc(InfoEnumProc), 0)

        # Set Virtual Windows Screen with previous monitors informations
        virtualScreen = Monitor()
        virtualScreen.name      = "Virtual monitor"
        virtualScreen.id        = "Windows"
        virtualScreen.flags     = 0
        virtualScreen.scale     = 0
        virtualScreen.top, virtualScreen.left, virtualScreen.right, virtualScreen.bottom = self._getMostCorner()
        virtualScreen.width     = int(math.fabs(math.fabs(virtualScreen.right) - virtualScreen.left))
        virtualScreen.height    = int(math.fabs(math.fabs(virtualScreen.bottom) - virtualScreen.top))
        virtualScreen.vwidth    = 0
        virtualScreen.vheight   = 0
        self.monitors.append(virtualScreen)

    def _getMostCorner(self):
        ''' Get the top/left/right/bottom-most point for all monitors
        Only used for the virtual screen'''
        mostTopPos = 0
        mostLeftPos = 0
        mostRightPos = 0
        mostBottomPos = 0
        for monitor in self.monitors:
            if (monitor.getMonitorPosition()[0] < mostTopPos):
                mostTopPos      = monitor.getMonitorPosition()[0]
            if (monitor.getMonitorPosition()[1] < mostLeftPos):
                mostLeftPos     = monitor.getMonitorPosition()[1]
            if ((monitor.getMonitorPosition()[1] + monitor.getMonitorResolution()[0]) > mostRightPos):
                mostRightPos    = (monitor.getMonitorPosition()[1] + monitor.getMonitorResolution()[0])
            if ((monitor.getMonitorPosition()[0] + monitor.getMonitorResolution()[1]) > mostBottomPos):
                mostBottomPos   = (monitor.getMonitorPosition()[0] + monitor.getMonitorResolution()[1])
        return (mostTopPos, mostLeftPos, mostRightPos, mostBottomPos)

if __name__ == "__main__":
    monitors = Monitors()
    print("You have currently :", monitors.nbMonitors, " monitors connected\n")
    for monitor in monitors.monitors:
        monitor.printMonitorInfo()
        monitor.takeScreenshot()
        print("Screenshot saved into clipboard")
        input('Press Enter to continue\n')