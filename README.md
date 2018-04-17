# winMonitor

* License          : GNU GPL v3
* Author           : Allard Chris - University Grenoble Alpes

## Dependencies

* Windows 10 (only tested on this OS)
* Python ≥ 3.x

## How to use

Import winMonitor to your project and create a new Monitors object to have a list of all available monitors.
What is Windows virtual screen : [Links](https://msdn.microsoft.com/en-us/library/windows/desktop/dd145136(v=vs.85).aspx)

### Monitor : 

Class who defined a single monitor

#### Attributes :
- __name__: Name of the monitor inside windows peripheral manager, default by windows is Generic Pnp Monitor (update your drivers to have the good name).
- __id__: Hardware identification numbers.
- __flags__: Flags : 0 Virtual, 1 Primary, 2 Other
- __scale__: Scale defined inside windows viewing parameters.
- __width__: real width resolution.
- __height__: real height resolution.
- __vwidth__: virtual width resolution after windows scaling.
- __vheight__: virtual height resolution after Windows scaling.
- __top__: top pixel inside windows virtual screen.
- __left__: left pixel inside windows virtual screen.
- __right__: right pixel inside windows virtual screen.
- __bottom__: bottom pixel inside windows virtual screen.

#### Functions :
- __getMonitorResolution()__: Return real monitor resolution currently in use.
- __getMonitorVirtualResolution()__: Return virtual monitor resolution currently in use, after windows scaling.
- __getMonitorPosition()__: Return position of the monitor inside the virtual screen.
- __printMonitorInfo()__: Print all attributes
- __takeScreenshot()__: Take screenshot and save it into clipboard

### Monitors : 

Class that contains all the monitors

#### Attributes :
- __monitors__: List of all monitor objects. Updated when object created.
- __nbMonitors__: Number of display monitors on desktop without the virtual one.
